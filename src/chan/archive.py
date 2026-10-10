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

The owner extended the exception on 2026-10-04 to Alpha Vantage's daily closes
for the S&P 600 cross-section, which
[issue 335](https://github.com/l3a0/quantitative-trading/issues/335) records,
and the same day to the S&P 500's members on the same terms, which
[issue 373](https://github.com/l3a0/quantitative-trading/issues/373) records.
A cross-section is a set of daily files fetched under one name, one file and one
manifest line per symbol, because the design doc's register cut one vintage per
cross-section on
[issue 88](https://github.com/l3a0/quantitative-trading/issues/88). Such a line
carries a ``cross_section`` field, and a line without one is a standalone
vintage like the minute bars. :data:`CROSS_SECTIONS` lists the names the owner
has ruled in, so a panel nobody ruled on is refused rather than recorded.
:func:`record_archive_file` writes one symbol's file and line, and
:func:`read_cross_section` reads a cross-section back. The download happens in
:mod:`chan.fetch_alphavantage`, so every rule here runs with no network.

Two refusals, because the two situations ask different things of the reader.

1. :class:`ArchiveUnavailable` means this machine has no archive, or the file
   is not in it. That is every public clone and every CI run, so a test that
   meets it skips with this message as its reason rather than failing.
2. :class:`ArchiveRefused` means the file is present and its bytes are not the
   bytes recorded. That is a failure wherever it happens, because a number
   computed from those bytes would rest on a series nobody recorded.

Writing has a third, :class:`ArchiveRecordRefused`, for a file or a line that
writing would replace.

Where the archive is comes from the machine, never from a tracked file, per
``docs/design.md``'s Configuration section. ``QT_ARCHIVE_DIR`` names it for one
run, and otherwise ``~/.config/quantitative-trading/archive_dir`` holds the path
on one line. :data:`chan.paths.DATA_DIR` stays the single switch for the
committed vintages, and this is the archive's own root, which is the answer
that module's docstring records.

The archive copy is the only kept copy of these bytes. The archive's own
``README.txt`` marks the two minute-bar files as pinned by hash here, and a
recorded path is never rewritten, so a refresh writes a new file name, or for a
cross-section a new cross-section name, which needs its own ruling before
:data:`CROSS_SECTIONS` accepts it.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from chan import paths
from chan.vintage import SYMBOL_PATTERN

#: The second manifest, beside ``data/vintages.jsonl``.
ARCHIVE_MANIFEST_NAME = "archive_vintages.jsonl"

#: The environment variable that names the archive for one run.
ARCHIVE_DIR_ENV = "QT_ARCHIVE_DIR"

#: The machine-local file holding the archive's path on one line.
ARCHIVE_DIR_CONFIG = Path("~/.config/quantitative-trading/archive_dir")

#: The cross-sections the owner has ruled into the archive exception.
#:
#: The rulings of 2026-10-04 cover the S&P 600 and the S&P 500's members and
#: nothing wider, and the premise says a later licensed series needs its own
#: decision. So a new name joins this tuple in the pull request that writes its
#: ruling into the design doc, where a reviewer sees the two side by side.
CROSS_SECTIONS = ("sp600", "sp500")

#: The first line of Alpha Vantage's ``TIME_SERIES_DAILY_ADJUSTED`` as CSV, from
#: the vendor's documentation. It was not measured when this was written,
#: because the public demo key answered every request with an ``Information``
#: body, so the owner's first run is what confirms it. A file whose first line
#: differs is refused, which makes a changed endpoint fail loudly.
DAILY_HEADER = (
    "timestamp,open,high,low,close,adjusted_close,volume,dividend_amount,split_coefficient"
)

#: The columns :func:`read_cross_section` returns, named as the vendor names them.
DAILY_COLUMNS = ("close", "adjusted_close", "volume")

#: The request every cross-section line records, one per symbol.
DAILY_VENDOR_CALL = "TIME_SERIES_DAILY_ADJUSTED, outputsize=full, datatype=csv"

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
_OPTIONAL = "cross_section"
_SHA256 = re.compile(r"[0-9a-f]{64}")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_BARE_NAME = re.compile(r"[A-Za-z0-9_.-]+")


class ArchiveUnavailable(Exception):
    """This machine has no archive, or the archive lacks the file the record names."""


class ArchiveRefused(Exception):
    """The archive file is present and its bytes do not hash to the recorded sha256."""


class ArchiveRecordRefused(Exception):
    """A cross-section file or line was not written, because writing it would replace one.

    Separate from :class:`ArchiveRefused`, which is the reading side's and says
    a file's bytes do not match its line. Sharing it would describe something
    that did not happen, which is the argument
    :class:`chan.vintage.VintageUnavailable` makes for the committed side.
    """


@dataclass(frozen=True)
class ArchiveEntry:
    """One line of ``data/archive_vintages.jsonl``.

    A standalone line's ``path`` is a bare file name inside the archive, and a
    cross-section line's is exactly ``<cross_section>/daily_<SYMBOL>.csv``, so
    no line can point a read outside the archive. ``row_count`` counts the
    file's data rows, extended-hours bars included, and ``first_date`` and
    ``last_date`` are the calendar days of its earliest and latest row.
    ``vendor_call`` names the request that produced the rows, because the same
    vendor answers differently with ``adjusted`` set either way.
    ``cross_section`` is ``None`` on a standalone line, and the line written
    for one then carries no such key, so the minute bars' lines keep their
    bytes.
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
    cross_section: str | None = None

    def as_json(self) -> str:
        """The line as the manifest holds it, keys sorted and no ``cross_section`` when unset."""
        fields = asdict(self)
        if fields[_OPTIONAL] is None:
            del fields[_OPTIONAL]
        return json.dumps(fields, sort_keys=True)


def daily_path(cross_section: str, symbol: str) -> str:
    """Where one symbol's daily file sits in the archive.

    The ``daily_`` prefix is there because Windows, and OneDrive with it,
    refuses a file whose name before the first dot is ``CON``, ``PRN``, ``AUX``,
    ``NUL``, ``COM0`` to ``COM9`` or ``LPT0`` to ``LPT9``. That is Microsoft's
    documented restriction rather than a measurement. A suffix would not help,
    because a symbol such as ``CON.A`` still begins ``CON.``, and a recorded
    path is never rewritten, so the name had to be right before the first line.
    """
    return f"{cross_section}/daily_{symbol}.csv"


def require_ruled(cross_section: str) -> None:
    """A ``ValueError`` unless :data:`CROSS_SECTIONS` holds the name, said one way everywhere."""
    if cross_section not in CROSS_SECTIONS:
        raise ValueError(
            f"the owner has not ruled {cross_section!r} into the archive exception, whose "
            f"cross-sections are {', '.join(CROSS_SECTIONS)}"
        )


def read_archive_manifest(data_dir: Path | None = None) -> list[ArchiveEntry]:
    """Every entry in ``data/archive_vintages.jsonl``, refusing a malformed line by number.

    No two lines may share a cross-section and a symbol. One symbol may sit on
    its own and in a cross-section, or in two cross-sections.
    """
    manifest = _manifest_path(data_dir)
    entries: list[ArchiveEntry] = []
    for number, line in enumerate(manifest.read_bytes().split(b"\n"), start=1):
        if not line.strip():
            continue
        entries.append(_entry_from_line(manifest, number, line))
    keys = [_label(entry) for entry in entries]
    repeated = sorted({key for key in keys if keys.count(key) > 1})
    if repeated:
        raise ValueError(
            f"{manifest} names {', '.join(repeated)} more than once, so a read could not "
            f"say which archive file it meant"
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
    """The one standalone archive entry for ``symbol``, compared case-insensitively.

    Cross-section lines are left out, so ``minute_bars("GLD")`` reads the same
    line it reads today even if GLD later joins a cross-section.
    """
    wanted = symbol.strip().upper()
    matches = [
        entry
        for entry in read_archive_manifest(data_dir)
        if entry.cross_section is None and entry.symbol == wanted
    ]
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


def daily_span(payload: bytes) -> tuple[int, str, str]:
    """The row count, first date and last date of one daily file, or a ``ValueError``.

    The first line must be :data:`DAILY_HEADER`, at least one row must follow,
    every row must open on an ISO date that exists, and no date may appear
    twice. The dates are the smallest and the largest rather than the first and
    last row, because Alpha Vantage writes the newest row first.
    """
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeDecodeError as undecoded:
        raise ValueError("the body is not UTF-8 text") from undecoded
    if not lines or lines[0].strip() != DAILY_HEADER:
        first = lines[0].strip()[:80] if lines else ""
        raise ValueError(f"the first line is {first!r}, not the daily header")
    dates = [row.split(",", 1)[0].strip() for row in lines[1:] if row.strip()]
    if not dates:
        raise ValueError("the daily header has no rows under it")
    undated = [day for day in dates if not _calendar_day(day)]
    if undated:
        raise ValueError(
            f"{len(undated)} rows do not open on an ISO date, the first {undated[0]!r}"
        )
    # Counted once rather than with list.count per row, which took 1.6 seconds
    # on one stock's full history and set the pace of a fetch of 1,800 stocks.
    repeated = sorted(day for day, seen in Counter(dates).items() if seen > 1)
    if repeated:
        # Two rows for one day would make every later read of the cross-section
        # fail on a duplicate index, and a recorded line is never rewritten.
        raise ValueError(f"{len(repeated)} dates appear twice, the first {repeated[0]}")
    return len(dates), min(dates), max(dates)


def _calendar_day(text: str) -> bool:
    """Whether the text is an ISO date that exists, which the pattern alone does not check."""
    if not _DATE.fullmatch(text):
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def record_archive_file(
    cross_section: str,
    symbol: str,
    payload: bytes,
    *,
    download_date: str,
    data_dir: Path | None = None,
    directory: Path | None = None,
) -> ArchiveEntry:
    """Write one symbol's daily file into the archive, then its line into the manifest.

    The file is written before the line, which is the reverse of
    :mod:`chan.vintage`. That module puts the record first because a file in
    ``data/`` with no line can reach a result unnoticed. An archive file
    cannot, because every archive read goes through a manifest line.
    Writing the line first would leave a line with no file, which a resumed fetch
    skips forever and which makes :func:`read_cross_section` refuse the whole
    cross-section. So the file comes first, and only a hard crash between the
    two can leave a file with no line, which the next fetch names.

    Anything short of a hard crash is rolled back. A failure or an interrupt
    after the file is written and before its line lands removes the file, as
    :func:`chan.vintage.record_vintage` removes a partial on ``BaseException``.
    The file is read back and hashed before the line is written, as that
    function does, because the archive sits in a synced folder and the bytes on
    disk are what the line vouches for.

    One writer at a time, for the reason :mod:`chan.vintage` writes down rather
    than defends.
    """
    require_ruled(cross_section)
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise ValueError(
            f"{symbol!r} is not a symbol written as chan.vintage.SYMBOL_PATTERN allows"
        )
    if not _DATE.fullmatch(download_date):
        raise ValueError(f"{download_date!r} is not an ISO calendar date")
    row_count, first_date, last_date = daily_span(payload)
    entry = ArchiveEntry(
        vendor="alphavantage",
        symbol=symbol,
        price_basis="adjusted",
        download_date=download_date,
        path=daily_path(cross_section, symbol),
        row_count=row_count,
        sha256=hashlib.sha256(payload).hexdigest(),
        first_date=first_date,
        last_date=last_date,
        vendor_call=DAILY_VENDOR_CALL,
        cross_section=cross_section,
    )
    manifest = _manifest_path(data_dir)
    if any(_label(kept) == _label(entry) for kept in read_archive_manifest(data_dir)):
        raise ArchiveRecordRefused(f"{manifest} already records {_label(entry)}")
    directory = archive_dir() if directory is None else directory
    path = directory / entry.path
    path.parent.mkdir(exist_ok=True)
    try:
        handle = open(path, "xb")
    except FileExistsError as taken:
        # Nothing was created here, so nothing is removed.
        raise ArchiveRecordRefused(
            f"the archive already holds {path} and no manifest line names it. Move it aside "
            f"to fetch {symbol} again"
        ) from taken
    line = (entry.as_json() + "\n").encode("utf-8")
    try:
        with handle:
            handle.write(payload)
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry.sha256:
            raise OSError(f"{path}: the file on disk does not match the bytes that were hashed")
        _append_line(manifest, line)
    except BaseException:
        # The exclusive create succeeded, so this call owns the file from here,
        # a partial write included. The line may already be on disk if the
        # interrupt landed after the append returned, and then the file stays
        # with it. Otherwise the file goes, so a transient error does not
        # retire this symbol.
        try:
            landed = line in manifest.read_bytes()
        except OSError:
            landed = False
        if not landed:
            path.unlink(missing_ok=True)
        raise
    return entry


def read_cross_section(
    name: str,
    *,
    column: str = "adjusted_close",
    symbols: Iterable[str] | None = None,
    data_dir: Path | None = None,
    directory: Path | None = None,
) -> tuple[list[ArchiveEntry], pd.DataFrame]:
    """One cross-section's entries, and a date-by-symbol frame of one of its columns.

    It mirrors :func:`chan.series.load_panel`. The entries are the lines whose
    ``cross_section`` is ``name``, sorted by symbol, and narrowed to
    ``symbols`` when it is given. A requested symbol with no line is left out
    of both, so a caller compares the entries with its own list to find what is
    missing. The frame's columns follow the entries, and its index is the union
    of the files' dates in ascending order, so a symbol with no row on a day is
    NaN there. ``column`` is ``close``, the raw close, ``adjusted_close``, or
    ``volume``, which issue 336 reads to find a series' last row that traded.

    Every file is hashed through :func:`read_archive_vintage` before it is
    parsed. A recorded file missing from the archive raises
    :class:`ArchiveUnavailable` for the whole read, because a panel missing a
    member is a different panel. A name with no line at all is a
    ``LookupError``.
    """
    if column not in DAILY_COLUMNS:
        raise ValueError(f"column must be one of {', '.join(DAILY_COLUMNS)}, not {column!r}")
    entries = sorted(
        (entry for entry in read_archive_manifest(data_dir) if entry.cross_section == name),
        key=lambda entry: entry.symbol,
    )
    if not entries:
        raise LookupError(f"data/{ARCHIVE_MANIFEST_NAME} records no cross-section named {name}")
    if symbols is not None:
        wanted = {symbol.strip().upper() for symbol in symbols}
        entries = [entry for entry in entries if entry.symbol in wanted]
    directory = archive_dir() if directory is None else directory
    series: dict[str, pd.Series] = {}
    for entry in entries:
        payload = read_archive_vintage(entry, directory)
        first = payload.split(b"\n", 1)[0].decode("utf-8", "replace").strip()
        if first != DAILY_HEADER:
            raise ValueError(f"{entry.path} opens with {first[:80]!r}, not the daily header")
        frame = pd.read_csv(io.BytesIO(payload), parse_dates=["timestamp"], index_col="timestamp")
        if len(frame) != entry.row_count:
            raise ArchiveRefused(
                f"{entry.path} parses to {len(frame)} rows, not the {entry.row_count} its "
                f"entry records"
            )
        series[entry.symbol] = frame[column].sort_index()
    panel = pd.DataFrame(series, columns=[entry.symbol for entry in entries]).sort_index()
    panel.index.name = "date"
    return entries, panel


def _manifest_path(data_dir: Path | None) -> Path:
    return (paths.DATA_DIR if data_dir is None else data_dir) / ARCHIVE_MANIFEST_NAME


def _label(entry: ArchiveEntry) -> str:
    """How a line is named in a refusal: the symbol, or the cross-section and the symbol."""
    if entry.cross_section is None:
        return entry.symbol
    return f"{entry.cross_section}/{entry.symbol}"


def _append_line(manifest: Path, line: bytes) -> None:
    """Add one line, after making sure the manifest ends in a newline.

    :func:`chan.vintage._append_entries` holds the same guard, but it always
    appends to ``vintages.jsonl``, so it is written again here rather than
    called.
    """
    existing = manifest.read_bytes()
    with open(manifest, "ab") as handle:
        handle.write((b"\n" if existing and not existing.endswith(b"\n") else b"") + line)


def _entry_from_line(manifest: Path, number: int, line: bytes) -> ArchiveEntry:
    try:
        parsed = json.loads(line)
    except ValueError as unparsed:
        raise ValueError(f"{manifest} line {number} is not JSON") from unparsed
    allowed = (set(_FIELDS), set(_FIELDS) | {_OPTIONAL})
    if not isinstance(parsed, dict) or set(parsed) not in allowed:
        raise ValueError(
            f"{manifest} line {number} does not carry exactly {', '.join(_FIELDS)}, "
            f"and optionally {_OPTIONAL}"
        )
    if _OPTIONAL in parsed and not isinstance(parsed[_OPTIONAL], str):
        # A null would read as a standalone line whose written form drops the key.
        raise ValueError(f"{manifest} line {number} carries a {_OPTIONAL} that is not a name")
    entry = ArchiveEntry(**parsed)
    problems = []
    if not isinstance(entry.row_count, int) or entry.row_count <= 0:
        problems.append("a row_count that is not a positive whole number")
    if not isinstance(entry.sha256, str) or not _SHA256.fullmatch(entry.sha256):
        problems.append("a sha256 that is not 64 lowercase hex digits")
    if entry.symbol != str(entry.symbol).strip().upper():
        problems.append("a symbol not written in upper case")
    if entry.cross_section is None:
        bare = isinstance(entry.path, str) and _BARE_NAME.fullmatch(entry.path) is not None
        if not bare or entry.path in {".", ".."}:
            problems.append("a path that is not a bare file name")
        if entry.price_basis != "raw":
            problems.append("a price_basis other than raw")
    else:
        if entry.cross_section not in CROSS_SECTIONS:
            problems.append(
                f"a cross_section the owner has not ruled into the archive, which are "
                f"{', '.join(CROSS_SECTIONS)}"
            )
        if not isinstance(entry.symbol, str) or not SYMBOL_PATTERN.fullmatch(entry.symbol):
            problems.append("a symbol chan.vintage.SYMBOL_PATTERN does not allow")
        elif entry.path != daily_path(str(entry.cross_section), entry.symbol):
            problems.append("a path other than <cross_section>/daily_<symbol>.csv")
        if entry.price_basis != "adjusted":
            problems.append("a cross-section price_basis other than adjusted")
    for label in ("download_date", "first_date", "last_date"):
        if not isinstance(getattr(entry, label), str) or not _DATE.fullmatch(getattr(entry, label)):
            problems.append(f"a {label} that is not an ISO calendar date")
    if problems:
        raise ValueError(f"{manifest} line {number} carries {'; '.join(problems)}")
    return entry
