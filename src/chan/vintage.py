"""Record a downloaded series as a vintage, immutable once written.

A vintage is one download of one series, identified by vendor, symbol, span,
download date, and which price the series carries. Losing one is the failure
[docs/design.md](../../docs/design.md) is built around: everything else here
recomputes, and a number whose series nobody kept is a number nobody can
check, including its author.

So this module writes two things and refuses rather than overwrite either. The
series becomes a file under ``data/``, and a line in ``data/vintages.jsonl``
records the five identity fields plus the file's path, row count and sha256.
The manifest is the record and the file is its shadow, which is why the entry
is appended first: a crash between the two then leaves an entry with no file,
which a verifier reports, rather than a file with no entry, which is how an
uncommitted download reaches a result unnoticed.

The download happens somewhere else. :func:`record_vintage` takes rows and
writes them, so every rule it enforces is exercised with no network.

Two things the identity fields carry that a filename cannot be trusted to
carry. The price basis is one of ``raw`` or ``adjusted``, the two terms the
design doc's vocabulary defines, because a refusal compares strings and
``raw`` against ``unadjusted`` would be two vintages of one download. Which
word names a vendor is a convention rather than a rule, and the manifest's
existing rows are what carry it.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from chan.paths import DATA_DIR

MANIFEST_NAME = "vintages.jsonl"
CHECKSUMS_NAME = "checksums.sha256"

#: The two price bases in the design doc's vocabulary. A third spelling of
#: either one is a second vintage of the same download.
PRICE_BASES = ("raw", "adjusted")

#: Lower case and filename-safe, so one source has one spelling in the path.
VENDOR_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")

#: Upper case after normalisation. Dots and carets appear in real tickers.
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.^-]*$")

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class VintageRefused(Exception):
    """A vintage was not written, because writing it would replace a record.

    Raised before anything is written. The message names the path and which of
    the two conditions fired, because "the file exists" sends a reader to the
    wrong fix when the real state is a manifest entry whose file was deleted.
    """


@dataclass(frozen=True)
class VintageEntry:
    """One line of ``data/vintages.jsonl``.

    Exactly one of ``download_date`` and ``saved_date`` is set. A download
    carries the first. The four ``*_chan.csv`` files carry the second, because
    their date is when Ernest Chan last saved the workbook a column was lifted
    from and nothing was fetched on that day. Putting a save date in a field
    named for a download would hand the next reader a wrong fact in the field
    that identifies the vintage.
    """

    vendor: str
    symbol: str
    price_basis: str
    first_date: str
    last_date: str
    path: str
    row_count: int
    sha256: str
    download_date: str | None = None
    saved_date: str | None = None

    def __post_init__(self) -> None:
        if (self.download_date is None) == (self.saved_date is None):
            raise ValueError(
                f"{self.path}: an entry carries a download date or a saved date, not both and "
                f"not neither"
            )

    def as_json(self) -> str:
        """The entry as one JSON object, with the unset date field left out."""
        fields = {key: value for key, value in asdict(self).items() if value is not None}
        return json.dumps(fields, sort_keys=True)


def vintage_filename(
    *,
    vendor: str,
    symbol: str,
    price_basis: str,
    first_date: str,
    last_date: str,
    download_date: str,
) -> str:
    """The path a recorded vintage takes, carrying all five identity fields.

    Four of the five is not enough. Two downloads with no new bar between them,
    over a weekend or a holiday or after a delisting, agree on vendor, symbol,
    span and price basis, and the second would be refused as a duplicate of the
    first. That pair is exactly what a test of the premise needs.
    """
    span = f"{first_date}_{last_date}"
    return f"{vendor}_{symbol.lower()}_{price_basis}_{span}_dl{download_date}.csv"


def read_manifest(data_dir: Path | None = None) -> list[VintageEntry]:
    """Every entry in ``data/vintages.jsonl``, in the order it was written.

    An absent manifest raises rather than reading as an empty one. A manifest
    that is moved or lost would otherwise turn every path new again, and the
    refusal in :func:`record_vintage` would stop refusing without saying so.
    """
    manifest = _manifest_path(data_dir)
    if not manifest.is_file():
        raise FileNotFoundError(f"no vintage manifest at {manifest}")
    return [
        VintageEntry(**json.loads(line))
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def record_vintage(
    rows: Iterable[tuple[str, float]],
    *,
    vendor: str,
    symbol: str,
    price_basis: str,
    download_date: str,
    data_dir: Path | None = None,
) -> VintageEntry:
    """Write ``rows`` as a vintage and record it, or refuse and write nothing.

    ``rows`` pairs an ISO date with a close. The download date comes from the
    caller because this function does not fetch, so it cannot know when a fetch
    happened, and reading a clock would make the field that identifies the
    vintage differ on every run.

    ``data_dir`` defaults to :data:`chan.paths.DATA_DIR`. A test passes its own
    directory, the way :func:`chan.regime_figure.make_regime_figure` takes an
    output path, so a run cannot write into the committed vintages.
    """
    directory = DATA_DIR if data_dir is None else data_dir
    rows = _validated_rows(rows)
    vendor, symbol, price_basis = _validated_identity(vendor, symbol, price_basis)
    _validated_date(download_date, "download date")

    days = [day for day, _ in rows]
    first_date, last_date = min(days), max(days)
    name = vintage_filename(
        vendor=vendor,
        symbol=symbol,
        price_basis=price_basis,
        first_date=first_date,
        last_date=last_date,
        download_date=download_date,
    )

    # Both refusals run before anything is written. Checking only the file on
    # disk would re-record a vintage whose file was deleted and leave two
    # entries for one path.
    entries = read_manifest(directory)
    path = directory / name
    if any(entry.path == name for entry in entries):
        raise VintageRefused(f"{name}: the manifest already holds an entry for it")
    if path.exists():
        raise VintageRefused(f"{name}: the file is already on disk with no manifest entry")

    payload = _serialize(symbol, rows)
    entry = VintageEntry(
        vendor=vendor,
        symbol=symbol,
        price_basis=price_basis,
        first_date=first_date,
        last_date=last_date,
        download_date=download_date,
        path=name,
        row_count=len(rows),
        sha256=hashlib.sha256(payload).hexdigest(),
    )

    _append_entry(directory, entry)
    try:
        _write_new_file(path, payload)
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry.sha256:
            raise OSError(f"{name}: the file on disk does not match the bytes that were hashed")
    except BaseException:
        # Removing only the file would leave an entry the refusal above
        # honours forever, so one transient error would retire this path.
        path.unlink(missing_ok=True)
        _rewrite_manifest(directory, [kept for kept in read_manifest(directory) if kept != entry])
        raise

    write_checksums(directory)
    return entry


def write_checksums(data_dir: Path | None = None) -> None:
    """Regenerate ``data/checksums.sha256`` from the manifest.

    The manifest owns the hash and this file is a projection of it, so the
    ``shasum -a 256 -c`` path that ``data/README.md`` documents keeps working
    without a second surface anyone has to remember to update.

    Rows are ordered by path rather than by hash, which is the order the file
    was kept in by hand. Regenerating it over the vintages it already held is
    therefore a no-op diff, which is what says the projection reproduces the
    record rather than replacing it.
    """
    directory = DATA_DIR if data_dir is None else data_dir
    entries = sorted(read_manifest(directory), key=lambda entry: entry.path)
    lines = [f"{entry.sha256}  {entry.path}\n" for entry in entries]
    (directory / CHECKSUMS_NAME).write_text("".join(lines), encoding="utf-8")


def _manifest_path(data_dir: Path | None) -> Path:
    return (DATA_DIR if data_dir is None else data_dir) / MANIFEST_NAME


def _validated_rows(rows: Iterable[tuple[str, float]]) -> list[tuple[str, float]]:
    materialized = [(day, float(value)) for day, value in rows]
    if not materialized:
        raise ValueError("an empty series has no span, so it cannot be identified as a vintage")
    days = [day for day, _ in materialized]
    for day in days:
        _validated_date(day, "row date")
    duplicates = sorted({day for day in days if days.count(day) > 1})
    if duplicates:
        raise ValueError(f"one date carries more than one close: {', '.join(duplicates)}")
    return materialized


def _validated_identity(vendor: str, symbol: str, price_basis: str) -> tuple[str, str, str]:
    if not VENDOR_PATTERN.match(vendor):
        raise ValueError(f"vendor {vendor!r} is not lower case and filename-safe")
    symbol = symbol.upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(f"symbol {symbol!r} carries a character a path cannot")
    if price_basis not in PRICE_BASES:
        raise ValueError(f"price basis {price_basis!r} is not one of {PRICE_BASES}")
    return vendor, symbol, price_basis


def _validated_date(value: str, label: str) -> None:
    if not _ISO_DATE.match(value):
        raise ValueError(f"{label} {value!r} is not an ISO calendar date")
    date.fromisoformat(value)


def _serialize(symbol: str, rows: list[tuple[str, float]]) -> bytes:
    """The file's bytes, in the three-row header shape every committed vintage uses.

    The bytes are the record, so the format is part of the contract. A close is
    written as Python's shortest round-trip repr, which is what produced the
    committed files, and lines end in a single newline.
    """
    lines = ["Price,Close", f"Ticker,{symbol}", "Date,"]
    lines.extend(f"{day},{value!r}" for day, value in rows)
    return ("\n".join(lines) + "\n").encode("utf-8")


def _append_entry(data_dir: Path, entry: VintageEntry) -> None:
    with open(_manifest_path(data_dir), "a", encoding="utf-8") as handle:
        handle.write(entry.as_json() + "\n")


def _write_new_file(path: Path, payload: bytes) -> None:
    """Claim the path and write it, or fail because something already holds it.

    An exclusive create rather than a check followed by a write. ``Path.exists``
    reports a file that cannot be opened as absent, and a check leaves a window
    the write can lose.
    """
    with open(path, "xb") as handle:
        handle.write(payload)


def _rewrite_manifest(data_dir: Path, entries: list[VintageEntry]) -> None:
    """Replace the manifest, which only the rollback ever does.

    Every other write appends. This one goes through a temporary file beside
    the manifest and a rename, so a failure part way through cannot truncate
    the entries that were already there.
    """
    manifest = _manifest_path(data_dir)
    temporary = manifest.with_name(manifest.name + ".rewriting")
    temporary.write_text("".join(entry.as_json() + "\n" for entry in entries), encoding="utf-8")
    temporary.replace(manifest)
