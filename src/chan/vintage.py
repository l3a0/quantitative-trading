"""Record a series as a vintage, immutable once written, and resolve one to read.

A vintage is one download of one series, identified by vendor, symbol, span,
download date, and which price the series carries. Losing one is the failure
[docs/design.md](../../docs/design.md) is built around: everything else here
recomputes, and a number whose series nobody kept is a number nobody can
check, including its author.

So this module writes two things and refuses rather than overwrite either. The
series becomes a file under ``data/``, and a line in ``data/vintages.jsonl``
records the five identity fields plus the file's path, row count and sha256.
That manifest is the record and the file is its shadow, which is why the entry
is appended first: a crash between the two then leaves an entry with no file,
which a verifier reports, rather than a file with no entry, which is how an
uncommitted download reaches a result unnoticed.

The download happens somewhere else. :func:`record_vintage` takes rows and
writes them, so every rule it enforces is exercised with no network. It writes
them in the order it is handed them, because the file is meant to be what the
vendor returned, while the span in the entry is the smallest and largest date
rather than the first and last row.

Reading is the other half and it runs the record backwards.
:func:`resolve_vintage` turns identity fields into the one entry that names
them, and :func:`read_vintage` hands back that entry's bytes once they hash to
what the record says. A run reads a committed vintage or it does not run, so a
file that no longer matches its entry stops the run and names itself rather
than producing a number from bytes nobody recorded. Nothing here parses a
series: that costs pandas, and a module the whole repo reads through is worth
keeping on the standard library.

Three limits are decisions rather than omissions.

One writer at a time. Appending a line survives two writers and the rollback
below does not, because it replaces the whole manifest. Nothing runs this
concurrently and nothing is planned to, so the assumption is written down here
instead of defended in code.

Only a download is recorded. Four of the committed vintages carry ``saved_date``
because they are columns lifted from Ernest Chan's workbooks, and no caller can
produce one of those through this module. Reading them back is supported and
writing a new one is not, since the thing that would write it does not exist.

The identity fields are compared as strings, so one source needs one spelling.
Case is normalised and the price basis is one of the two terms the design doc's
vocabulary defines, because ``raw`` against ``unadjusted`` would otherwise be
two vintages of one download. Which word names a vendor is a convention rather
than a rule, and the manifest's existing rows are what carry it.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from chan import paths

MANIFEST_NAME = "vintages.jsonl"
CHECKSUMS_NAME = "checksums.sha256"

#: The two price bases in the design doc's vocabulary. A third spelling of
#: either one is a second vintage of the same download.
PRICE_BASES = ("raw", "adjusted")

# A name joins the five identity fields with underscores, so no field may hold
# one. Beyond that the patterns keep a field from reaching outside the data
# directory or carrying whitespace. They are not an allowlist of shapes anybody
# has seen, because the vendors and tickers this repo will want are not known
# yet: a leading caret is how every index is written, and an equals sign is how
# futures and currency pairs are.
VENDOR_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9^][A-Z0-9.=^-]*$")

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class VintageUnavailable(Exception):
    """A run asked for a committed vintage and did not get one.

    Separate from :class:`VintageRefused`, which is the writer's and says a
    vintage was not written because writing it would replace a record. This one
    says a run could not read one, which is the opposite operation, so sharing
    the exception would hand the next person a docstring describing something
    that did not happen.

    The message names which vintage and which state. Absent, unreadable and
    altered are three different problems with three different fixes, and one
    message for all of them sends the reader to the wrong one.
    """


class VintageRefused(Exception):
    """A vintage was not written, because writing it would replace a record.

    The message names the path and which condition fired, because "the file
    exists" sends a reader to the wrong fix when the real state is a manifest
    entry whose file was deleted.
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

    @property
    def obtained(self) -> str:
        """The one date this entry carries, whichever of the two fields holds it.

        ``__post_init__`` guarantees exactly one is set, so a caller that wants
        to tell two vintages of one series apart asks here rather than picking a
        field and finding ``None`` on half the manifest.
        """
        return self.download_date if self.download_date is not None else self.saved_date

    @property
    def obtained_verb(self) -> str:
        """``downloaded`` or ``saved``, so a report names what the date means.

        Nothing was fetched on a saved date, and printing it under the word
        "downloaded" would state a wrong fact about where the series came from.
        """
        return "downloaded" if self.download_date is not None else "saved"

    def as_json(self) -> str:
        """The entry as one JSON object, with the unset date field left out.

        Keys are sorted, so a line's text is decided by the entry rather than by
        the order the fields happen to be declared in.
        """
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

    A manifest that is there but cannot be read says that instead, because the
    two are different problems with different fixes and one message for both
    sends the reader to the wrong one. A line that will not parse names its own
    number, since a manifest is read to find out what went wrong.
    """
    manifest = _manifest_path(data_dir)
    if not manifest.exists():
        raise FileNotFoundError(f"no vintage manifest at {manifest}")
    if not manifest.is_file():
        raise OSError(f"the vintage manifest at {manifest} is not a readable file")

    entries = []
    for number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(VintageEntry(**json.loads(line)))
        except (json.JSONDecodeError, TypeError, ValueError) as unreadable:
            raise ValueError(f"{manifest} line {number} is not a vintage entry") from unreadable
    return entries


def record_vintage(
    rows: Iterable[tuple[str, float]],
    *,
    vendor: str,
    symbol: str,
    price_basis: str,
    download_date: str,
    data_dir: Path | None = None,
) -> VintageEntry:
    """Write ``rows`` as a vintage and record it, or refuse and leave no trace.

    ``rows`` pairs an ISO date with a close, and is written in the order it is
    given. The download date comes from the caller because this function does
    not fetch, so it cannot know when a fetch happened, and reading a clock
    would make the field that identifies the vintage differ on every run.

    Once the file verifies, the vintage is recorded and nothing undoes it. The
    projection into ``data/checksums.sha256`` is regenerated after that, and a
    failure there is reported as what it is rather than as a failed record,
    because the record is already true and rerunning would be refused.

    ``data_dir`` defaults to :data:`chan.paths.DATA_DIR`. A test passes its own
    directory, the way :func:`chan.regime_figure.make_regime_figure` takes an
    output path, so a run cannot write into the committed vintages.
    """
    directory = paths.DATA_DIR if data_dir is None else data_dir
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

    payload = _serialize(rows)
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
    except FileExistsError as taken:
        # Nothing was created here, so nothing is removed. The check above asks
        # `Path.exists`, which reports a dangling symlink as absent and leaves a
        # window a second writer can take. The exclusive create is what actually
        # decides, and losing to it must not delete whatever won.
        _drop_entry(directory, entry)
        raise VintageRefused(
            f"{name}: the path was taken before the write could claim it"
        ) from taken
    except BaseException:
        # Anything else means this call may have created the file, so the
        # partial goes with the entry. Removing only the file would leave an
        # entry the refusal honours forever, and one transient error would
        # retire this path.
        path.unlink(missing_ok=True)
        _drop_entry(directory, entry)
        raise

    try:
        write_checksums(directory)
    except OSError as unwritable:
        raise OSError(
            f"{name}: the vintage is recorded and verified, and {CHECKSUMS_NAME} could not be "
            f"regenerated from the manifest. Recording it again will be refused, which is "
            f"right. Regenerate the projection instead."
        ) from unwritable
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
    directory = paths.DATA_DIR if data_dir is None else data_dir
    entries = sorted(read_manifest(directory), key=lambda entry: entry.path)
    lines = [f"{entry.sha256}  {entry.path}\n" for entry in entries]
    (directory / CHECKSUMS_NAME).write_text("".join(lines), encoding="utf-8")


def resolve_vintage(
    *,
    vendor: str,
    symbol: str,
    price_basis: str,
    dated: str | None = None,
    data_dir: Path | None = None,
) -> VintageEntry:
    """The one manifest entry these fields name, or a refusal saying why not.

    ``vendor``, ``symbol`` and ``price_basis`` are the identity fields a caller
    knows without looking at the data directory. They select exactly one of the
    eight committed vintages today, and they stop being enough the moment a
    second download of one series is recorded, which :func:`record_vintage` was
    built to allow.

    ``dated`` is what tells those two apart. It is compared against whichever
    date field the entry carries, so it names a download and it names one of
    the four series lifted from Ernest Chan's workbooks, which carry a saved
    date and no download date at all. An argument named for the download date
    could only name four of the eight.

    Ambiguity refuses rather than picking. A rule that the latest date wins
    would let a new download move a pinned number with nothing in the diff to
    explain it, which is the failure ``docs/design.md``'s register cut under
    "Reading a clock for a vintage's download date", arriving through the
    manifest instead of through a clock. So a triple matching two entries stops
    the run and names both, and the caller says which one it meant.
    """
    directory = _directory(data_dir)
    entries = read_manifest(directory)
    if not entries:
        raise VintageUnavailable(
            f"the manifest at {directory / MANIFEST_NAME} records no vintages at all. A record "
            f"holding nothing is a lost record, which is a different problem from a download "
            f"nobody made."
        )

    asked = f"{vendor} {symbol} {price_basis}" + ("" if dated is None else f" dated {dated}")
    matches = [
        entry
        for entry in entries
        if entry.vendor == vendor
        and entry.symbol == symbol
        and entry.price_basis == price_basis
        and (dated is None or entry.obtained == dated)
    ]
    if not matches:
        raise VintageUnavailable(
            f"no committed vintage is recorded for {asked}.{_unrecorded_note(directory, entries)}"
        )
    if len(matches) > 1:
        candidates = ", ".join(
            f"{entry.path} ({entry.obtained_verb} {entry.obtained})" for entry in matches
        )
        raise VintageUnavailable(
            f"{asked} names {len(matches)} recorded vintages: {candidates}. Name which one with "
            f"the date it was {matches[0].obtained_verb}, because choosing here would move a "
            f"pinned number with nothing in the diff to explain it."
        )
    return matches[0]


def read_vintage(entry: VintageEntry, data_dir: Path | None = None) -> bytes:
    """The vintage's bytes, once they are shown to be the bytes the record describes.

    One read answers both questions. Hashing the file and then handing a parser
    the path checks one read and uses another, which is the look-then-act shape
    :func:`record_vintage` already rejected on the writing side.

    Nothing is cached. Hashing all eight committed vintages takes 0.9 ms
    against a 5 s suite, so a cache would save nothing measurable and would add
    a second answer to the question of what is on disk right now.
    """
    path = _directory(data_dir) / entry.path
    try:
        payload = path.read_bytes()
    except FileNotFoundError as absent:
        # Asked after the open failed rather than before it, so this diagnoses a
        # refusal that already happened instead of guarding one. `Path.exists`
        # calls a dangling symlink absent and `open` agrees by raising this, so
        # without the lstat here a broken link reads as a download nobody made.
        if path.is_symlink():
            raise VintageUnavailable(
                f"{entry.path}: {path} is a symlink and nothing is at its target "
                f"{os.readlink(path)!r}. Something is at the path, so this is not the same "
                f"state as a vintage that was never committed."
            ) from absent
        raise VintageUnavailable(
            f"{entry.path}: the manifest records this vintage and no file is at {path}. The "
            f"record outlived the series, which is the state the recorder leaves when it is "
            f"interrupted between the two."
        ) from absent
    except OSError as unreadable:
        # Narrower than the `except OSError` that would sit around the whole
        # read. FileNotFoundError is an OSError too, so catching the parent
        # alone is what actually turns unreadable into absent.
        raise VintageUnavailable(
            f"{entry.path}: the file at {path} is there and could not be read: {unreadable}"
        ) from unreadable

    digest = hashlib.sha256(payload).hexdigest()
    if digest != entry.sha256:
        raise VintageUnavailable(
            f"{entry.path}: the bytes at {path} hash to {digest} and the manifest records "
            f"{entry.sha256}. The file is not the file the record describes, so the run stops "
            f"rather than computing a number from it."
        )
    return payload


def unrecorded_files(data_dir: Path | None = None) -> list[str]:
    """Every ``*.csv`` in the data directory that no manifest entry names.

    The mirror of an entry with no file, and the more dangerous half. An entry
    with no file stops a run that asks for it. A file with no entry is how an
    uncommitted download reaches a result with nobody noticing which series
    produced it.
    """
    directory = _directory(data_dir)
    return _unrecorded(directory, read_manifest(directory))


def _manifest_path(data_dir: Path | None) -> Path:
    return _directory(data_dir) / MANIFEST_NAME


def _directory(data_dir: Path | None) -> Path:
    """The data directory a call works against, read at call time.

    ``chan.paths.DATA_DIR`` is the single switch that says where the vintages
    sit, and looking it up through the module rather than binding it at import
    keeps it the only one.
    """
    return paths.DATA_DIR if data_dir is None else data_dir


def _unrecorded(directory: Path, entries: list[VintageEntry]) -> list[str]:
    recorded = {entry.path for entry in entries}
    try:
        present = sorted(found.name for found in directory.glob("*.csv"))
    except OSError:
        return []
    return [name for name in present if name not in recorded]


def _unrecorded_note(directory: Path, entries: list[VintageEntry]) -> str:
    """The other half of rule 8, said only when there is something to say."""
    unrecorded = _unrecorded(directory, entries)
    if not unrecorded:
        return ""
    return (
        f" No entry names {', '.join(unrecorded)} either, and a series the manifest does not "
        f"record is a download nobody can check."
    )


def _validated_rows(rows: Iterable[tuple[str, float]]) -> list[tuple[str, float]]:
    materialized = []
    for day, value in rows:
        _validated_date(day, "row date")
        try:
            close = float(value)
        except (TypeError, ValueError) as unusable:
            raise ValueError(f"the close on {day} is not a number: {value!r}") from unusable
        if not math.isfinite(close):
            raise ValueError(
                f"the close on {day} is not a finite number: {value!r}. A vendor value too "
                f"large to parse arrives as an infinity and a missing bar arrives as a NaN, "
                f"and freezing either into a vintage records an artifact as a price."
            )
        materialized.append((day, close))

    if not materialized:
        raise ValueError("an empty series has no span, so it cannot be identified as a vintage")
    repeated = sorted(
        day for day, seen in Counter(day for day, _ in materialized).items() if seen > 1
    )
    if repeated:
        raise ValueError(f"one date carries more than one close: {', '.join(repeated)}")
    return materialized


def _validated_identity(vendor: str, symbol: str, price_basis: str) -> tuple[str, str, str]:
    if not isinstance(vendor, str) or not isinstance(symbol, str):
        raise ValueError(f"vendor and symbol are strings, not {type(vendor)} and {type(symbol)}")
    vendor, symbol = vendor.lower(), symbol.upper()
    if not VENDOR_PATTERN.match(vendor):
        raise ValueError(f"vendor {vendor!r} carries a character a path cannot")
    if not SYMBOL_PATTERN.match(symbol):
        raise ValueError(f"symbol {symbol!r} carries a character a path cannot")
    if price_basis not in PRICE_BASES:
        raise ValueError(f"price basis {price_basis!r} is not one of {PRICE_BASES}")
    return vendor, symbol, price_basis


def _validated_date(value: str, label: str) -> None:
    if not isinstance(value, str) or not _ISO_DATE.match(value):
        raise ValueError(f"{label} {value!r} is not an ISO calendar date")
    try:
        date.fromisoformat(value)
    except ValueError as impossible:
        raise ValueError(f"{label} {value!r} is not a day that exists") from impossible


def _serialize(rows: list[tuple[str, float]]) -> bytes:
    """The file's bytes, one header row and then the series.

    The bytes are the record, so the format is part of the contract. A close is
    written as Python's shortest round-trip repr, which is what produced the
    committed files, and lines end in a single newline.

    The header names the two columns and nothing else. The eight vintages
    committed before this module existed carry yfinance's three-row multi-index
    header instead, and writing that shape for every vendor would put a line
    reading ``Price,Close`` at the top of a series no vendor of that name
    returned. ``load_close`` drops every leading row whose first field is not a
    date, so it reads either.
    """
    lines = ["Date,Close"]
    lines.extend(f"{day},{value!r}" for day, value in rows)
    return ("\n".join(lines) + "\n").encode("utf-8")


def _append_entry(data_dir: Path, entry: VintageEntry) -> None:
    """Add one line, after making sure the file ends in one.

    A manifest whose last line has no newline would otherwise have this entry
    glued onto it. That loses both lines rather than one, and leaves the file
    unreadable to everything that opens it afterwards, including the rollback.
    """
    manifest = _manifest_path(data_dir)
    existing = manifest.read_bytes()
    with open(manifest, "a", encoding="utf-8") as handle:
        if existing and not existing.endswith(b"\n"):
            handle.write("\n")
        handle.write(entry.as_json() + "\n")


def _drop_entry(data_dir: Path, entry: VintageEntry) -> None:
    """Take one entry back out, comparing on the whole entry rather than a field.

    Two downloads of one span share a sha256 and differ only in their download
    date and path, so a narrower comparison would roll back the wrong line.
    """
    _rewrite_manifest(data_dir, [kept for kept in read_manifest(data_dir) if kept != entry])


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
