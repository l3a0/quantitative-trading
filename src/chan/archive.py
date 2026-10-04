"""Vintages whose bytes live in the owner's data archive rather than in ``data/``.

Every other vintage here is committed, because the premise in
[docs/design.md](../../docs/design.md) says a number computed from a series
nobody kept is a number nobody can check. Alpha Vantage's one-minute GLD and
GDX bars are the first series the repo does not commit: the vendor's terms grant
personal, non-commercial use, and no vendor priced for
[issue 23](https://github.com/l3a0/quantitative-trading/issues/23) allowed
publishing raw bars. The owner chose on 2026-10-03 that the archive keeps the
bytes and this repo commits only their hashes, so the series is still kept and
the record still names exactly which bytes a result rests on.

So this module reads a second manifest, ``data/archive_vintages.jsonl``, one
JSON object per archive file, and hands back a file's bytes only once they hash
to what that line records. It mirrors :func:`chan.vintage.read_vintage` on
purpose: a run reads the series the record names or it does not run.

Two refusals, because the two situations ask different things of the reader.

1. :class:`ArchiveUnavailable` means this machine has no archive, or the file
   is not in it. That is every public clone and every CI run, so a test that
   meets it skips with this message as its reason rather than failing.
2. :class:`ArchiveRefused` means the file is present and its bytes are not the
   bytes recorded. That is a failure wherever it happens, because a number
   computed from those bytes would rest on a series nobody recorded.

Where the archive is comes from the machine, never from a tracked file, per
``docs/design.md``'s Configuration section. ``QT_ARCHIVE_DIR`` names it for one
run, and otherwise ``~/.config/quantitative-trading/archive_dir`` holds the path
on one line. :data:`chan.paths.DATA_DIR` stays the single switch for the
committed vintages, and this is the archive's own root, which is the answer
that module's docstring records.

The archive copy is the only kept copy of these bytes. The archive's own
``README.txt`` marks both files as pinned by hash here, so a refresh writes a
new file name and never rewrites one this manifest names.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from chan import paths

#: The second manifest, beside ``data/vintages.jsonl``.
ARCHIVE_MANIFEST_NAME = "archive_vintages.jsonl"

#: The environment variable that names the archive for one run.
ARCHIVE_DIR_ENV = "QT_ARCHIVE_DIR"

#: The machine-local file holding the archive's path on one line.
ARCHIVE_DIR_CONFIG = Path("~/.config/quantitative-trading/archive_dir")

_FIELDS = (
    "vendor",
    "symbol",
    "price_basis",
    "download_date",
    "path",
    "row_count",
    "sha256",
    "first_date",
    "last_date",
    "vendor_call",
)
_SHA256 = re.compile(r"[0-9a-f]{64}")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_BARE_NAME = re.compile(r"[A-Za-z0-9_.-]+")


class ArchiveUnavailable(Exception):
    """This machine has no archive, or the archive lacks the file the record names."""


class ArchiveRefused(Exception):
    """The archive file is present and its bytes do not hash to the recorded sha256."""


@dataclass(frozen=True)
class ArchiveEntry:
    """One line of ``data/archive_vintages.jsonl``.

    ``path`` is a bare file name inside the archive, never a path with a
    directory in it, so a line cannot point a read outside the archive.
    ``row_count`` counts the file's data rows, extended-hours bars included,
    and ``first_date`` and ``last_date`` are the calendar days of its first and
    last bar. ``vendor_call`` names the request that produced the bars, because
    the same vendor answers differently with ``adjusted`` set either way.
    """

    vendor: str
    symbol: str
    price_basis: str
    download_date: str
    path: str
    row_count: int
    sha256: str
    first_date: str
    last_date: str
    vendor_call: str


def read_archive_manifest(data_dir: Path | None = None) -> list[ArchiveEntry]:
    """Every entry in ``data/archive_vintages.jsonl``, refusing a malformed line by number."""
    directory = paths.DATA_DIR if data_dir is None else data_dir
    manifest = directory / ARCHIVE_MANIFEST_NAME
    entries: list[ArchiveEntry] = []
    for number, line in enumerate(manifest.read_bytes().split(b"\n"), start=1):
        if not line.strip():
            continue
        entries.append(_entry_from_line(manifest, number, line))
    symbols = [entry.symbol for entry in entries]
    repeated = sorted({symbol for symbol in symbols if symbols.count(symbol) > 1})
    if repeated:
        raise ValueError(
            f"{manifest} names {', '.join(repeated)} more than once, so a read by symbol "
            f"could not say which archive file it meant"
        )
    return entries


def archive_dir(environ: Mapping[str, str] | None = None, config: Path | None = None) -> Path:
    """The archive's directory here, or :class:`ArchiveUnavailable` naming both ways to set it."""
    environ = os.environ if environ is None else environ
    config = ARCHIVE_DIR_CONFIG.expanduser() if config is None else config
    named = environ.get(ARCHIVE_DIR_ENV, "").strip()
    if not named and config.is_file():
        named = config.read_text(encoding="utf-8").strip()
    if not named:
        raise ArchiveUnavailable(
            f"no data archive is configured on this machine. Set {ARCHIVE_DIR_ENV}, or write "
            f"the archive's path on one line to {ARCHIVE_DIR_CONFIG}"
        )
    directory = Path(named).expanduser()
    if not directory.is_dir():
        raise ArchiveUnavailable(f"the configured data archive {directory} is not a directory")
    return directory


def resolve_archive_vintage(symbol: str, data_dir: Path | None = None) -> ArchiveEntry:
    """The one archive entry for ``symbol``, compared case-insensitively."""
    wanted = symbol.strip().upper()
    matches = [entry for entry in read_archive_manifest(data_dir) if entry.symbol == wanted]
    if not matches:
        raise LookupError(f"data/{ARCHIVE_MANIFEST_NAME} records no archive vintage for {wanted}")
    return matches[0]


def read_archive_vintage(entry: ArchiveEntry, directory: Path | None = None) -> bytes:
    """The archive file's bytes, once they hash to the sha256 its entry records."""
    directory = archive_dir() if directory is None else directory
    path = directory / entry.path
    if not path.is_file():
        raise ArchiveUnavailable(f"the data archive {directory} holds no {entry.path}")
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != entry.sha256:
        raise ArchiveRefused(
            f"{path} hashes to {actual}, not the {entry.sha256} that data/{ARCHIVE_MANIFEST_NAME} "
            f"records, so it is not the series this repo's results rest on. Restore the "
            f"recorded file rather than re-recording this one"
        )
    return payload


def minute_bars(
    symbol: str, *, data_dir: Path | None = None, directory: Path | None = None
) -> pd.DataFrame:
    """Every bar of one archive vintage, indexed by the minute it opens, in file order.

    The columns are ``open``, ``high``, ``low``, ``close`` and ``volume``. The
    frame's ``attrs["vintage"]`` carries the entry, so a report names the bytes
    its numbers came from without resolving them a second time.
    """
    entry = resolve_archive_vintage(symbol, data_dir)
    payload = read_archive_vintage(entry, directory)
    raw = gzip.decompress(payload) if entry.path.endswith(".gz") else payload
    frame = pd.read_csv(io.BytesIO(raw), parse_dates=["timestamp"], index_col="timestamp")
    if list(frame.columns) != ["open", "high", "low", "close", "volume"]:
        raise ValueError(f"{entry.path} carries columns {list(frame.columns)}, not open to volume")
    if len(frame) != entry.row_count:
        raise ArchiveRefused(
            f"{entry.path} parses to {len(frame)} rows, not the {entry.row_count} its entry records"
        )
    frame.attrs["vintage"] = entry
    return frame


def _entry_from_line(manifest: Path, number: int, line: bytes) -> ArchiveEntry:
    try:
        parsed = json.loads(line)
    except ValueError as unparsed:
        raise ValueError(f"{manifest} line {number} is not JSON") from unparsed
    if not isinstance(parsed, dict) or sorted(parsed) != sorted(_FIELDS):
        raise ValueError(f"{manifest} line {number} does not carry exactly {', '.join(_FIELDS)}")
    entry = ArchiveEntry(**parsed)
    problems = []
    if not isinstance(entry.row_count, int) or entry.row_count <= 0:
        problems.append("a row_count that is not a positive whole number")
    if not isinstance(entry.sha256, str) or not _SHA256.fullmatch(entry.sha256):
        problems.append("a sha256 that is not 64 lowercase hex digits")
    bare = isinstance(entry.path, str) and _BARE_NAME.fullmatch(entry.path) is not None
    if not bare or entry.path in {".", ".."}:
        problems.append("a path that is not a bare file name")
    if entry.symbol != str(entry.symbol).strip().upper():
        problems.append("a symbol not written in upper case")
    if entry.price_basis != "raw":
        problems.append("a price_basis other than raw")
    for label in ("download_date", "first_date", "last_date"):
        if not isinstance(getattr(entry, label), str) or not _DATE.fullmatch(getattr(entry, label)):
            problems.append(f"a {label} that is not an ISO calendar date")
    if problems:
        raise ValueError(f"{manifest} line {number} carries {'; '.join(problems)}")
    return entry
