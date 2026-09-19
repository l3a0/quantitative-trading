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

Every write here takes bytes rather than text, which covers the series file,
the manifest entry, the rollback's rewrite and ``data/checksums.sha256``. A
text-mode write with no ``newline`` argument translates every newline to
``os.linesep``, which is CRLF on Windows. The record would then hold bytes the
code did not build, and a projection whose lines end in a carriage return fails
``shasum -a 256 -c`` on every vintage it names.

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

Only a download is recorded. The committed ``*_chan.csv`` vintages carry
``saved_date`` and ``source_workbook`` because they are columns lifted from
Ernest Chan's workbooks, and no caller can produce one of those through this
module. Reading them back is supported and writing one is not, which stays a
decision now that ``spy_chan.csv`` has arrived and shown that such a vintage
still gets typed in by hand. ``docs/design.md``'s register carries the price a
saved-date parameter would charge, which is a second naming convention and the
check that asserts the first one. What holds a hand-typed line instead is the
identity pinned for it in ``tests/support/committed_vintages.py`` and the
``Ticker,`` header row its own bytes carry.

The identity fields are compared as strings, so one source needs one spelling.
Case is normalised and the price basis is one of the two terms the design doc's
vocabulary defines, because ``raw`` against ``unadjusted`` would otherwise be
two vintages of one download. Which word names a vendor is a convention rather
than a rule, and the manifest's existing rows are what carry it.

Normalising happens on the writing side only, and a line already in the manifest
is refused when its spelling is not the one the recorder would have written.
Refused rather than repaired, because a record one surface rewrites while
another writes it plainly is a record two surfaces disagree about. The refusal
is worth more than its odds suggest. Without it a misspelled field left the
entry naming its own file, so :func:`resolve_vintage` answered that no such
vintage was committed and listed nothing as unrecorded, which is a wrong fact
rather than a stopped run. With it the line stops the read and names itself.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import MISSING, asdict, dataclass, fields
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
#
# They decide what the record may hold and not only what the recorder accepts,
# because :class:`VintageEntry` runs them over a line read back as well. So
# tightening either one refuses the committed vintages it newly excludes, and
# one refused line refuses the whole manifest rather than the line, which means
# a tightening that newly excludes a single entry takes down every vintage in
# the record.
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

    Exactly one of ``download_date`` and ``saved_date`` is set, and whichever
    one it is holds an ISO calendar date. A download carries the first. The
    ``*_chan.csv`` files carry the second, because their date is when Ernest
    Chan last saved the workbook a column was lifted from and nothing was
    fetched on that day. Putting a save date in a field named for a download
    would hand the next reader a wrong fact in the field that identifies the
    vintage.

    Both rules are checked wherever an entry is built, which includes the line
    :func:`read_manifest` reads back, and so are ``vendor``, ``symbol`` and
    ``price_basis``, the three fields :func:`resolve_vintage` matches an ask
    against. A hand-edited or badly-merged line is how a value
    ``record_vintage`` would have refused reaches the record, and a record whose
    reader takes such a value is weaker than the writer that filled it. Checking
    the three is also what makes their ``str`` annotations true of an entry read
    back, since the line is free to hold a list where the class says a string.

    ``source_workbook`` names the spreadsheet a column was lifted from, and the
    ``*_chan.csv`` entries are the only ones carrying it. It is recorded
    rather than derived because a symbol does not carry it. Chan's
    ``example6_2.xls`` holds a SPY column, and a ``SPY.xls`` in the same mirror
    holds a different series, so a filename joined from the symbol would name a
    real workbook about the wrong data. ``docs/design.md``'s vocabulary calls
    this manifest the authority for a vintage's provenance, and the workbook a
    column came from is provenance.

    Which lines may carry it is a rule and the name itself is not, which is two
    decisions rather than one.

    The rule is that a workbook implies a saved date, checked below. A download
    has no workbook, so demanding one on every line would refuse every vintage a
    vendor returned, and allowing one anywhere would let a line claim a series a
    vendor returned came out of a spreadsheet. That is a provenance claim in the
    field that says where a series came from, written permanently into a record
    nothing rewrites. It is stated against ``saved_date`` rather than against
    the vendor, because which word names a vendor is a convention this module
    does not enforce, while the date fields are already an invariant it does.

    The name is not checked, because no rule here can confirm a filename in a
    mirror this repo does not hold. What holds it instead is ``data/README.md``'s
    table, which states the same workbook in the same spelling, and the
    assertion in ``tests/test_vintage.py`` that compares the two.

    Like ``saved_date``, it is a field :func:`record_vintage` can never write,
    since the recorder takes rows and a download date and no workbook at all.

    The span is not checked here, because nothing in ``src/`` reads it. The path
    is [issue 2](https://github.com/l3a0/quantitative-trading/issues/2).
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
    source_workbook: str | None = None

    def __post_init__(self) -> None:
        if (self.download_date is None) == (self.saved_date is None):
            raise ValueError(
                f"{self.path}: an entry carries a download date or a saved date, not both and "
                f"not neither"
            )
        if self.source_workbook is not None and self.saved_date is None:
            raise ValueError(
                f"{self.path}: an entry carrying a source workbook carries a saved date, "
                f"because the workbook is the thing that was saved. A series a vendor "
                f"returned did not come out of a spreadsheet."
            )

        # The writer's own functions, so a line reads back only if the recorder
        # would have written it. Running them here rather than in
        # :func:`read_manifest` puts them inside the refusal that already names
        # the line number, and holds a directly built entry too.
        field = "download date" if self.download_date is not None else "saved date"
        _validated_date(self.obtained, f"{self.path}: {field}")

        # Comparing the two triples rather than calling the validator for its
        # refusals alone. It normalises as well as refusing, so a guard reading
        # only its raises accepts a vendor spelled `Yfinance` and leaves
        # `resolve_vintage` unable to see the record. The question is what the
        # recorder would have written, not what it would have refused.
        #
        # The price basis reaches the comparison equal or not at all, since the
        # validator returns it unchanged or raises. It is compared anyway,
        # because the invariant is the whole triple rather than the two fields
        # that happen to normalise today.
        held = (self.vendor, self.symbol, self.price_basis)
        recorded = _validated_identity(*held, where=f"{self.path}: ")
        if recorded != held:
            differs = ", ".join(
                f"{name} reads {line!r} and the recorder writes {written!r}"
                for name, line, written in zip(
                    ("vendor", "symbol", "price basis"), held, recorded, strict=True
                )
                if line != written
            )
            raise ValueError(
                f"{self.path}: {differs}. The manifest is matched on the identity fields as "
                f"strings, so a spelling the recorder would not have written names a vintage "
                f"no reader can find."
            )

    @property
    def obtained(self) -> str:
        """The one date this entry carries, whichever of the two fields holds it.

        ``__post_init__`` guarantees exactly one is set and that it is an ISO
        calendar date, so a caller that wants to tell two vintages of one series
        apart asks here rather than picking a field and finding ``None`` on half
        the manifest. That guarantee is what makes the return annotation true of
        an entry read back from a manifest as well as one this module wrote.
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

    The convention is asserted rather than merely followed. Because all five
    fields are in the name, ``tests/test_vintage.py`` holds every recorded
    entry to the name its file took, which is what stands between an entry and
    a file it does not describe. Changing the join therefore moves that check,
    and a vintage already on disk keeps the name it was given.
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
    sends the reader to the wrong one. A refused line names its own number and
    the reason it was refused, since a manifest is read to find out what went
    wrong and a number says which line rather than what. The fix for a date a
    hand edit broke, for a key a hand edit dropped, and for a line that is not
    JSON are three different fixes.

    The reason takes one of three shapes and the message takes one.
    :meth:`VintageEntry.__post_init__` already writes for an operator and its
    words carry through untouched. ``json`` writes for whoever is looking at
    the text, and its column survives while its own line number does not.
    Python writes about the constructor, so :func:`_wrong_shape` says those in
    the manifest's terms before an entry is built.
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
            parsed = json.loads(line)
        except ValueError as unparsed:
            # `ValueError` rather than `json.JSONDecodeError`, which is a
            # subclass of it and is not the only thing `json.loads` raises. A
            # JSON integer literal longer than `sys.get_int_max_str_digits`
            # raises a bare `ValueError` from `int`, and catching only the
            # subclass let a long digit run in `row_count` reach an operator as
            # a CPython message naming no manifest, no line and no field.
            raise _refused_line(manifest, number, _not_json(unparsed)) from unparsed

        wrong_shape = _wrong_shape(parsed)
        if wrong_shape is not None:
            raise _refused_line(manifest, number, wrong_shape)

        try:
            entries.append(VintageEntry(**parsed))
        except (TypeError, ValueError) as refused:
            # `ValueError` is what `__post_init__` raises and is the live half.
            # Nothing reaches the `TypeError` any more, because `_wrong_shape`
            # decides all three of its cases first, and it is kept because the
            # cost of the two disagreeing is a bare constructor message reaching
            # an operator, which is the whole of what this function stopped
            # doing. The funnel catches what it always caught.
            raise _refused_line(manifest, number, str(refused)) from refused
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
    (directory / CHECKSUMS_NAME).write_bytes("".join(lines).encode("utf-8"))


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
    knows without looking at the data directory. They select exactly one
    committed vintage today, and they stop being enough the moment a second
    download of one series is recorded, which :func:`record_vintage` was built
    to allow.

    ``dated`` is what tells those two apart. It is compared against whichever
    date field the entry carries, so it names a download and it names one of
    the series lifted from Ernest Chan's workbooks, which carry a saved date and
    no download date at all. An argument named for the download date would reach
    the downloads and none of the workbook columns.

    Ambiguity refuses rather than picking. A rule that the latest date wins
    would let a new download move a pinned number with nothing in the diff to
    explain it, which is the failure ``docs/design.md``'s register cut under
    "Reading a clock for a vintage's download date", arriving through the
    manifest instead of through a clock. So a triple matching two entries stops
    the run and names both, and the caller says which one it meant.
    """
    directory = _directory(data_dir)
    try:
        entries = read_manifest(directory)
    except (OSError, ValueError) as unreadable:
        # `read_manifest` raises three classes and none of them is this one, so
        # without this a deleted or corrupt manifest reaches an operator as a
        # traceback while a deleted vintage reaches one as a line. Its message
        # is carried through rather than replaced, because it already says
        # which of the manifest's own states fired.
        raise VintageUnavailable(
            f"the vintage manifest could not be read, so no vintage can be resolved: {unreadable}"
        ) from unreadable
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
    if len(matches) > 1 and len(set(matches)) == 1:
        raise VintageUnavailable(
            f"the manifest holds {len(matches)} identical entries for {matches[0].path}. Naming a "
            f"date cannot separate them, because they are one record written more than once."
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


def _refused_line(manifest: Path, number: int, reason: str) -> ValueError:
    """The one shape every refused line takes, built in one place.

    Returned rather than raised, so the caller keeps the ``raise ... from`` that
    holds the original as the chained cause. Three literals would let a reader
    think the difference between them carried something.
    """
    return ValueError(f"{manifest} line {number} is not a vintage entry: {reason}")


def _not_json(unparsed: ValueError) -> str:
    """Why ``json.loads`` would not take the line, without a second line number.

    A :class:`json.JSONDecodeError` carries ``msg`` and ``colno`` separately,
    and its own string ends in "line 1 column 2 (char 1)". ``json`` is handed
    one line at a time, so that line number is always 1 whatever line of the
    manifest it came from, and printing it beside the manifest's would put two
    numbers meaning two different things in one message. The manifest's is the
    one an operator needs.

    Anything else ``json.loads`` raises has no position to report, so its own
    words are carried as they stand.

    Both are quoted, because several of CPython's own messages end mid-phrase.
    ``Unterminated string starting at`` is finished by the position text this
    drops, and read unquoted it would dangle into the column. Quoted, it reads
    as what it is, which is the parser's sentence rather than this module's.
    """
    if isinstance(unparsed, json.JSONDecodeError):
        return f"it is not JSON: {unparsed.msg!r} at column {unparsed.colno}"
    return f"it is not JSON: {str(unparsed)!r}"


def _wrong_shape(parsed: object) -> str | None:
    """What a parsed line got wrong before an entry is built, or ``None``.

    Decided here rather than in a handler because Python cannot be asked. A
    line that is not a mapping, a line missing a field and a line carrying a
    field that does not exist all reach ``VintageEntry(**parsed)`` as a bare
    :class:`TypeError` holding one argument, and only its message string tells
    the three apart. That message also describes the constructor rather than
    the manifest, and it names only the first key it does not recognise.

    So the price of saying this in the manifest's terms is a second statement
    of what a line must hold. It is read off :func:`dataclasses.fields` rather
    than written out, in both directions, so a field added to
    :class:`VintageEntry` is neither missed when it is required nor demanded
    when it is not.
    """
    if not isinstance(parsed, dict):
        return f"an entry's fields are a JSON object, and this line is {_json_kind(parsed)}"

    known = {field.name for field in fields(VintageEntry)}
    # A field with a default is not required on the line, which covers the two
    # date fields, since `__post_init__` takes exactly one of the two and
    # `as_json` writes only the one that is set, and `source_workbook`, which
    # only a workbook column carries. That third one is the case this comment
    # used to predict: naming the optional fields here instead would have
    # refused the module's own output the first time `VintageEntry` gained
    # another, and reading the required set off `dataclasses.fields` is why
    # adding it refused nothing.
    required = {
        field.name
        for field in fields(VintageEntry)
        if field.default is MISSING and field.default_factory is MISSING
    }
    missing = sorted(required - parsed.keys())
    unknown = sorted(parsed.keys() - known)

    reasons = []
    if missing:
        reasons.append(f"it does not carry {_names(missing)}")
    if unknown:
        # Quoted, because these come off the line rather than off the dataclass.
        # A key holding a newline would otherwise put the manifest's own text in
        # an operator's terminal as further lines reading as the module's words.
        reasons.append(f"an entry has no field named {_names(unknown)}")
    return " and ".join(reasons) or None


def _names(fields_named: list[str]) -> str:
    """Field names for a message, quoted so a line cannot forge one.

    Half of these come off the manifest line rather than off the dataclass, and
    a name holding a newline would print as further lines reading as this
    module's own words. Both halves are quoted, because they name the same kind
    of thing in one sentence.
    """
    return ", ".join(repr(name) for name in fields_named)


def _json_kind(parsed: object) -> str:
    """What ``json`` calls the thing a line parsed to, for a reader reading JSON.

    A manifest line is JSON text, so "a JSON array" sends its reader somewhere
    Python's ``list`` does not. The lookup is on the exact type, since ``bool``
    is a subclass of ``int`` and would otherwise be a number. ``json.loads``
    returns nothing else, and the fallback is there so a miss could not replace
    a refusal with a ``KeyError`` raised while reporting it.
    """
    return {
        list: "a JSON array",
        str: "a JSON string",
        int: "a JSON number",
        float: "a JSON number",
        bool: "a JSON boolean",
        type(None): "the JSON literal null",
    }.get(type(parsed), f"a {type(parsed).__name__}")


def _manifest_path(data_dir: Path | None) -> Path:
    return _directory(data_dir) / MANIFEST_NAME


def _directory(data_dir: Path | None) -> Path:
    """The data directory a call works against, read at call time.

    ``chan.paths.DATA_DIR`` is the single switch that says where the vintages
    sit, and looking it up through the module rather than binding it at import
    keeps it the only one.
    """
    return paths.DATA_DIR if data_dir is None else data_dir


def _unrecorded(directory: Path, entries: list[VintageEntry]) -> list[str] | None:
    """Every ``*.csv`` no entry names, or ``None`` when the directory cannot be listed.

    ``None`` rather than an empty list. This is the detector for an uncommitted
    download reaching a result, so "nothing is unrecorded" and "the scan could
    not run" must not be the same answer. A directory that is traversable but
    not readable reaches the second: the manifest still opens by name and the
    glob still fails.
    """
    recorded = {entry.path for entry in entries}
    try:
        present = sorted(found.name for found in directory.iterdir() if found.is_file())
    except OSError:
        return None
    return [name for name in present if name.endswith(".csv") and name not in recorded]


def _unrecorded_note(directory: Path, entries: list[VintageEntry]) -> str:
    """The other half of rule 8, said only when there is something to say."""
    unrecorded = _unrecorded(directory, entries)
    if unrecorded is None:
        return (
            f" Whether an unrecorded series sits beside it is unknown, because {directory} could "
            f"not be listed."
        )
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


def _validated_identity(
    vendor: str, symbol: str, price_basis: str, where: str = ""
) -> tuple[str, str, str]:
    """The triple the recorder would write, or a refusal naming the field that stopped it.

    ``where`` prefixes every message, because this runs both for a caller's
    arguments and for a line already in the manifest, and only the second has an
    entry to point at. :func:`record_vintage` passes nothing, since
    :func:`vintage_filename` has not run yet and there is no path to quote.

    A refusal quotes the value as it was handed over rather than as it was
    lowered, so a reader grepping the manifest for what the message said finds
    the line. Lowering first would report ``'yahoo finance'`` for a line reading
    ``Yahoo Finance``.
    """
    if not isinstance(vendor, str) or not isinstance(symbol, str):
        raise ValueError(
            f"{where}vendor and symbol are strings, not {type(vendor)} and {type(symbol)}"
        )
    lowered, uppered = vendor.lower(), symbol.upper()
    if not VENDOR_PATTERN.match(lowered):
        raise ValueError(f"{where}vendor {vendor!r} carries a character a path cannot")
    if not SYMBOL_PATTERN.match(uppered):
        raise ValueError(f"{where}symbol {symbol!r} carries a character a path cannot")
    if price_basis not in PRICE_BASES:
        raise ValueError(f"{where}price basis {price_basis!r} is not one of {PRICE_BASES}")
    return lowered, uppered, price_basis


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

    The header names the two columns and nothing else. The hand-placed
    vintages carry a three-row multi-index header instead, which is yfinance's
    shape, and writing that for every vendor would put a line reading
    ``Price,Close`` at the top of a series no vendor of that name returned.
    ``load_close`` drops every leading row whose first field is not a date, so
    it reads either.
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
    with open(manifest, "ab") as handle:
        if existing and not existing.endswith(b"\n"):
            handle.write(b"\n")
        handle.write((entry.as_json() + "\n").encode("utf-8"))


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
    payload = "".join(entry.as_json() + "\n" for entry in entries)
    temporary.write_bytes(payload.encode("utf-8"))
    temporary.replace(manifest)
