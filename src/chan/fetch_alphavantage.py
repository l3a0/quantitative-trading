"""Fetch Alpha Vantage's daily closes into the owner's archive, one symbol at a time.

The owner extended the archive exception on 2026-10-04 to Alpha Vantage's daily
closes for the S&P 600 cross-section, and ruled the same day that the fetch
lives here, reading ``ALPHAVANTAGE_API_KEY`` from the environment of one run.
[Issue 335](https://github.com/l3a0/quantitative-trading/issues/335) records
both. A second ruling that day extended the exception to the S&P 500's members,
which [issue 373](https://github.com/l3a0/quantitative-trading/issues/373)
records, and a ruling of 2026-10-11 extended it to the S&P 400's members as
IJH held them on 2007-12-31, which
[issue 303](https://github.com/l3a0/quantitative-trading/issues/303) records.
So the fetch writes to any cross-section the archive names. Each
symbol is one ``TIME_SERIES_DAILY_ADJUSTED`` request with ``outputsize=full``
and ``datatype=csv``, and its response is written to the
archive unchanged, because one response carries the raw close beside the
adjusted close.

```bash
ALPHAVANTAGE_API_KEY=... QT_ARCHIVE_DIR=/path/to/archive \\
    uv run python -m chan.fetch_alphavantage --cross-section sp600 --symbols symbols.txt
```

The network lives here and nothing else does. :func:`chan.archive.record_archive_file`
takes the bytes and holds every rule about them, so those rules run with no
network, the way :mod:`chan.vintage` keeps the download out of its recorder.
:func:`fetch` takes its transport and its sleep as arguments, so the tests
drive every path below with a stub and never call the vendor.

**Resume is by manifest.** A symbol whose line is already in
``data/archive_vintages.jsonl`` is skipped with no request, so a rerun after a
failure asks only for what is missing. The manifest is the one in the checkout
the fetch runs in, so run it on the branch that commits the lines. A discarded
checkout keeps the files in the archive and loses the lines, and the next run
refuses every one of those files as unrecorded rather than overwriting it.

**What a body means.** Alpha Vantage answers HTTP 200 whatever it has to say,
so the body decides. Measured on 2026-10-04 with the public demo key, an
``Information`` body arrives as ``application/json`` although CSV was asked
for, and the same body answers every symbol. Six cases.

1. A CSV opening with :data:`chan.archive.DAILY_HEADER` and holding rows is
   recorded.
2. A JSON body with ``Error Message`` fails that symbol, which is how the vendor
   answers a symbol it does not hold. The run goes on.
3. A JSON body with ``Information`` or ``Note`` is retried with a growing wait.
   If it persists the run stops, because it is about the key or the rate rather
   than the symbol, and failing each symbol in turn would spend six attempts on
   each of 1,500.
4. A transport failure is retried the same way, and stops the run if it
   persists. That covers ``OSError`` and ``http.client.HTTPException``, since a
   body cut off mid-read raises ``IncompleteRead``, which is not an ``OSError``.
5. A body whose first line is comma-separated but is not the daily header
   stops the run, a byte-order mark included, because the endpoint changed and
   every symbol would fail the same way.
6. Anything else fails that symbol: an empty body, a header with no rows or
   with a date that repeats or does not exist, JSON carrying neither key, or a
   body whose first line holds no comma, such as an error page.

A failure writing to the archive or the manifest stops the run too, because it
is about the disk rather than the symbol. Every way a run ends prints the
tally.

The pacing, the test that a body opening with ``{`` is JSON, and the retry on
``Information`` and ``Note`` come from ``pipeline/download_intraday.py`` in the
sibling ``trading-strategies`` repo at ``7a26498``, which fetched GDX's minute
bars at ``477c594``. Its rewrite of ``.`` to ``-`` in a symbol is not carried
over. The symbol is sent and recorded exactly as the list writes it, because a
rewrite would record a symbol other than the one asked for.

**The key never reaches output.** The request URL holds it, so no line prints
the URL, and every line passes through :func:`_redact` before it is printed in
case a transport error quotes it.

**One currency pair takes a path of its own.** :func:`fetch_fx_daily` sends
one ``FX_DAILY`` request for a pair, USD/CAD for
[issue 607](https://github.com/l3a0/quantitative-trading/issues/607), and
records the closes through :func:`chan.vintage.record_vintage` rather than
writing the response to the archive. It shares the retry loop in
:func:`_request`, the redaction and the printing with the equity path, and
nothing else, since :func:`fetch` needs the archive and a cross-section the
owner ruled in. ``python -m chan.usdcad_holdout fetch`` runs it.
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from chan import paths
from chan.archive import (
    ARCHIVE_MANIFEST_NAME,
    CROSS_SECTIONS,
    DAILY_HEADER,
    ArchiveRecordRefused,
    ArchiveUnavailable,
    archive_dir,
    daily_path,
    read_archive_manifest,
    record_archive_file,
    require_ruled,
)
from chan.vintage import (
    MANIFEST_NAME,
    SYMBOL_PATTERN,
    VintageEntry,
    read_manifest,
    record_vintage,
)

#: The environment variable holding the owner's key, never a file.
KEY_ENV = "ALPHAVANTAGE_API_KEY"

QUERY_URL = "https://www.alphavantage.co/query"

#: The pause after every request, the sibling's single-worker cadence for a
#: premium cap of 75 requests a minute.
PAUSE_SECONDS = 0.85

#: How many times one symbol's request is tried before the run stops.
ATTEMPTS = 6

#: The wait before retrying an ``Information`` or ``Note`` body, times the attempt.
THROTTLE_WAIT_SECONDS = 15.0

#: The wait before retrying a transport failure, times the attempt.
TRANSPORT_WAIT_SECONDS = 5.0

TIMEOUT_SECONDS = 60

#: How much of a vendor's message a line quotes.
_QUOTED = 200


class RunStopped(Exception):
    """The run cannot go on, because what failed is about every symbol rather than one."""


@dataclass
class Tally:
    """What one run did, symbol by symbol, and why it ended."""

    recorded: list[str] = field(default_factory=list)
    already: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    not_reached: list[str] = field(default_factory=list)
    stopped: str | None = None
    interrupted: bool = False

    @property
    def complete(self) -> bool:
        """Whether every symbol asked for is now recorded."""
        return not (self.failed or self.not_reached or self.stopped or self.interrupted)

    def line(self) -> str:
        """The closing line: recorded, already recorded, failed with each named, not reached."""
        failed = f"failed {len(self.failed)}"
        if self.failed:
            failed += f" ({', '.join(self.failed)})"
        counts = (
            f"recorded {len(self.recorded)}, already recorded {len(self.already)}, {failed}, "
            f"not reached {len(self.not_reached)}"
        )
        if self.interrupted:
            return f"interrupted: {counts}"
        if self.stopped is not None:
            return f"stopped: {counts}"
        return counts


def urllib_get(url: str) -> bytes:
    """The response body, or an ``OSError``, which ``urllib``'s own errors all are."""
    with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def request_url(symbol: str, key: str) -> str:
    """The one request for one symbol's full daily history as CSV."""
    query = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "full",
        "datatype": "csv",
        "apikey": key,
    }
    return f"{QUERY_URL}?{urllib.parse.urlencode(query)}"


def read_symbols(path: Path) -> list[str]:
    """One symbol per line, blank lines and ``#`` lines skipped, each kept once in order.

    A line that is not a symbol as :data:`chan.vintage.SYMBOL_PATTERN` writes
    one is refused by number before any request.
    """
    symbols: list[str] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        if not SYMBOL_PATTERN.fullmatch(text):
            raise ValueError(
                f"{path} line {number} holds {text[:40]!r}, which is not a symbol in upper case "
                f"as chan.vintage.SYMBOL_PATTERN allows"
            )
        if text not in symbols:
            symbols.append(text)
    return symbols


def fetch(
    cross_section: str,
    symbols: Iterable[str],
    *,
    key: str,
    get: Callable[[str], bytes] | None = None,
    sleep: Callable[[float], None] | None = None,
    today: Callable[[], date] | None = None,
    data_dir: Path | None = None,
    directory: Path | None = None,
) -> Tally:
    """Fetch and record each symbol the manifest does not already hold.

    Each symbol prints its own line as it is decided, and the returned
    :class:`Tally` carries the closing line. A run that stops, or that Ctrl-C
    interrupts, returns its tally with the symbols not reached rather than
    raising, so :func:`main` prints it the same way. ``download_date`` is the
    machine's local date when that symbol's response arrived, so a run spanning
    two days records both.

    ``get``, ``sleep`` and ``today`` default to :func:`urllib_get`,
    ``time.sleep`` and ``date.today``, looked up when the call is made rather
    than when the module loads, so a test that replaces one reaches
    :func:`main` too.
    """
    get = urllib_get if get is None else get
    sleep = time.sleep if sleep is None else sleep
    today = date.today if today is None else today
    require_ruled(cross_section)
    directory = archive_dir() if directory is None else directory
    manifest = (paths.DATA_DIR if data_dir is None else data_dir) / ARCHIVE_MANIFEST_NAME
    _say(f"archive {directory}, manifest {manifest}", key)
    held = {
        entry.symbol
        for entry in read_archive_manifest(data_dir)
        if entry.cross_section == cross_section
    }
    todo = list(dict.fromkeys(symbols))
    tally = Tally()
    reached = 0
    try:
        for position, symbol in enumerate(todo):
            reached = position
            if symbol in held:
                tally.already.append(symbol)
                continue
            target = directory / daily_path(cross_section, symbol)
            if target.exists():
                tally.failed.append(symbol)
                _say(
                    f"{symbol}: refused, the archive already holds {target} and no manifest "
                    f"line names it. Move it aside to fetch {symbol} again",
                    key,
                )
                continue
            body = _request(symbol, request_url(symbol, key), key, get, sleep)
            _settle(cross_section, symbol, body, key, today, data_dir, directory, tally)
    except RunStopped as stopped:
        tally.stopped = str(stopped)
        tally.not_reached = todo[reached:]
        _say(f"stopped at {stopped}", key)
    except KeyboardInterrupt:
        tally.interrupted = True
        # An interrupt can land after a line is written and before the tally
        # hears of it, so the manifest says what was recorded.
        try:
            now = {
                entry.symbol
                for entry in read_archive_manifest(data_dir)
                if entry.cross_section == cross_section
            }
        except (OSError, ValueError):
            now = held
        for symbol in todo[reached:]:
            if symbol in now and symbol not in held and symbol not in tally.recorded:
                tally.recorded.append(symbol)
        settled = set(tally.recorded) | set(tally.failed) | set(tally.already)
        tally.not_reached = [symbol for symbol in todo[reached:] if symbol not in settled]
    return tally


#: The header ``FX_DAILY`` writes under ``datatype=csv``, measured on 2026-10-13.
FX_DAILY_HEADER = "timestamp,open,high,low,close"

#: The fields of one ``FX_DAILY`` row: a date and four prices.
FX_DAILY_FIELDS = len(FX_DAILY_HEADER.split(","))

#: The vendor and basis a pair's daily closes are recorded under.
FX_VENDOR = "alphavantage"
FX_BASIS = "raw"


def fx_request_url(from_symbol: str, to_symbol: str, key: str) -> str:
    """The one request for a currency pair's full daily history as CSV."""
    query = {
        "function": "FX_DAILY",
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "outputsize": "full",
        "datatype": "csv",
        "apikey": key,
    }
    return f"{QUERY_URL}?{urllib.parse.urlencode(query)}"


def fx_vendor_column(from_symbol: str, to_symbol: str) -> str:
    """The column and the call a pair's recorded closes came from, for the manifest line."""
    return f"close, FX_DAILY from_symbol={from_symbol} to_symbol={to_symbol} outputsize=full"


@dataclass(frozen=True)
class FxCloses:
    """One ``FX_DAILY`` response read down to its dates and closes.

    ``rows`` pairs each date with the close as the vendor wrote it, oldest
    first, and leaves out every row dated on or after the download day.
    ``dropped`` names those, and ``received`` counts every row the body held.
    """

    rows: list[tuple[str, str]]
    dropped: list[str]
    received: int


def read_fx_daily(body: bytes, download_date: str) -> FxCloses:
    """The dates and closes of one ``FX_DAILY`` body, or a ``ValueError`` saying why not.

    Seven refusals, each before anything is written.

    1. A JSON body. ``Error Message`` is quoted, and anything else is named as
       a body carrying none of the vendor's three keys. A throttle never gets
       here, because :func:`_request` retries it.
    2. An empty body.
    3. A first line other than :data:`FX_DAILY_HEADER`, a byte-order mark
       included, because the endpoint changed.
    4. A body that does not end in a newline. The vendor writes the newest row
       first, so a body cut off mid-read ends on an old row that still parses.
    5. A row with other than five fields, or a date that is not a calendar
       day, for the same reason.
    6. A body with no row dated before the download day.
    7. A row dated on a Saturday or a Sunday. Chan's closes hold none, and the
       run counts rows to set its lookback, so a weekend row would shift every
       window after it.

    A row dated on or after the download day is a session still trading rather
    than a close, so it is dropped and named rather than refused. The rest are
    sorted oldest first, because the vendor writes them newest first.
    """
    stripped = body.lstrip()
    if stripped.startswith(b"{"):
        try:
            parsed = json.loads(stripped)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict) and "Error Message" in parsed:
            raise ValueError(
                f"Alpha Vantage answered {str(parsed['Error Message'])[:_QUOTED]!r}, so nothing "
                f"was recorded"
            )
        raise ValueError(
            "a JSON body carrying neither Error Message, Information nor Note, so nothing was "
            "recorded"
        )
    if not body:
        raise ValueError("an empty body, so nothing was recorded")
    text = body.decode("utf-8", "replace")
    first = text.split("\n", 1)[0].rstrip("\r")
    if first != FX_DAILY_HEADER:
        raise ValueError(
            f"the body opens with {first[:80]!r}, not the FX_DAILY header "
            f"{FX_DAILY_HEADER!r}, so nothing was recorded"
        )
    if not body.endswith(b"\n"):
        raise ValueError(
            "the body does not end in a newline, so it was cut off and its last row may be "
            "partial. Nothing was recorded"
        )
    lines = [line.rstrip("\r") for line in text.split("\n")[1:-1]]
    rows, dropped = [], []
    for number, line in enumerate(lines, start=2):
        fields = line.split(",")
        if len(fields) != FX_DAILY_FIELDS:
            raise ValueError(
                f"line {number} holds {len(fields)} fields rather than {FX_DAILY_FIELDS}, so the "
                f"body was cut off or the endpoint changed. Nothing was recorded"
            )
        day, close = fields[0], fields[-1]
        try:
            calendar_day = date.fromisoformat(day)
        except ValueError:
            calendar_day = None
        if calendar_day is None or calendar_day.isoformat() != day:
            raise ValueError(
                f"line {number} is dated {day[:40]!r}, which is not an ISO calendar date. Nothing "
                f"was recorded"
            )
        if day >= download_date:
            dropped.append(day)
        else:
            rows.append((day, close))
    if not rows:
        raise ValueError(
            f"the body holds no row dated before {download_date}, so nothing was recorded"
        )
    rows.sort()
    weekend = [day for day, _ in rows if date.fromisoformat(day).weekday() >= 5]
    if weekend:
        raise ValueError(
            f"{len(weekend)} rows fall on a Saturday or a Sunday, the first {weekend[0]}. Chan's "
            f"closes hold no weekend day and the lookback counts rows, so nothing was recorded"
        )
    return FxCloses(rows=rows, dropped=sorted(dropped), received=len(lines))


def fetch_fx_daily(
    from_symbol: str = "USD",
    to_symbol: str = "CAD",
    *,
    key: str,
    get: Callable[[str], bytes] | None = None,
    sleep: Callable[[float], None] | None = None,
    today: Callable[[], date] | None = None,
    data_dir: Path | None = None,
) -> VintageEntry:
    """Fetch a pair's ``FX_DAILY`` closes and record them as a vintage in ``data/``.

    The owner ruled on 2026-10-13, on
    [issue 607](https://github.com/l3a0/quantitative-trading/issues/607), that
    USD/CAD's closes from this call are committed, so they go through
    :func:`chan.vintage.record_vintage` rather than into the archive. The
    vintage's symbol joins the two currencies, its basis is ``raw`` and its
    ``vendor_column`` names the call.

    A second download would record a second vintage under a new name, because
    the name carries the download date. So the fetch refuses before any request
    when the manifest already holds a vintage of the pair from this vendor.
    :func:`read_fx_daily` holds every rule about the body. ``get``, ``sleep``
    and ``today`` default as :func:`fetch`'s do, and ``download_date`` is the
    machine's local date when the response arrived.
    """
    get = urllib_get if get is None else get
    sleep = time.sleep if sleep is None else sleep
    today = date.today if today is None else today
    symbol = f"{from_symbol}{to_symbol}"
    held = [
        entry
        for entry in read_manifest(data_dir)
        if (entry.vendor, entry.symbol, entry.price_basis) == (FX_VENDOR, symbol, FX_BASIS)
    ]
    if held:
        raise ValueError(
            f"the manifest already holds {held[0].path}, a vintage of {symbol} from "
            f"{FX_VENDOR}, so no request was made. A second download would record a second "
            f"vintage beside it"
        )
    manifest = (paths.DATA_DIR if data_dir is None else data_dir) / MANIFEST_NAME
    _say(f"FX_DAILY {from_symbol}/{to_symbol}, manifest {manifest}", key)
    body = _request(symbol, fx_request_url(from_symbol, to_symbol, key), key, get, sleep)
    download_date = today().isoformat()
    closes = read_fx_daily(body, download_date)
    dropped = f" ({', '.join(closes.dropped)})" if closes.dropped else ""
    _say(
        f"{symbol}: {closes.received} rows received, {len(closes.dropped)} dated on or after "
        f"{download_date} dropped{dropped}",
        key,
    )
    entry = record_vintage(
        closes.rows,
        vendor=FX_VENDOR,
        symbol=symbol,
        price_basis=FX_BASIS,
        download_date=download_date,
        vendor_column=fx_vendor_column(from_symbol, to_symbol),
        data_dir=data_dir,
    )
    _say(
        f"{symbol}: recorded {entry.path}, {entry.row_count} rows, {entry.first_date} to "
        f"{entry.last_date}",
        key,
    )
    return entry


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m chan.fetch_alphavantage",
        description=(
            "Fetch Alpha Vantage's daily closes into the owner's archive and record each "
            f"symbol in data/{ARCHIVE_MANIFEST_NAME}. Reads {KEY_ENV} from the environment."
        ),
    )
    parser.add_argument(
        "--cross-section",
        required=True,
        help=f"the cross-section to record under, one of {', '.join(CROSS_SECTIONS)}",
    )
    parser.add_argument(
        "--symbols", required=True, type=Path, help="a file holding one symbol per line"
    )
    args = parser.parse_args(argv)
    key = os.environ.get(KEY_ENV, "").strip()
    try:
        require_ruled(args.cross_section)
        symbols = read_symbols(args.symbols)
        if not key:
            raise ValueError(f"{KEY_ENV} is not set, so no request was made")
        tally = fetch(args.cross_section, symbols, key=key)
    except KeyboardInterrupt:
        raise SystemExit("interrupted before any symbol was fetched") from None
    except (ArchiveUnavailable, ValueError, OSError) as refusal:
        # A refusal is worth nothing at the bottom of a traceback, which is the
        # reason `chan.equity_seasonals.main` gives for the same line.
        raise SystemExit(_redact(str(refusal), key)) from refusal
    _say(tally.line(), key)
    if not tally.complete:
        raise SystemExit(1)


def _request(
    label: str,
    url: str,
    key: str,
    get: Callable[[str], bytes],
    sleep: Callable[[float], None],
) -> bytes:
    """One request's body, or :class:`RunStopped` once a throttle or transport failure persists.

    ``label`` names the request in the refusal, a symbol for the equity path
    and the pair for :func:`fetch_fx_daily`, and ``url`` is what is sent. Both
    paths share this loop so neither can miss an exception the other handles.
    """
    reason = ""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            body = get(url)
        except (OSError, http.client.HTTPException) as failure:
            reason = f"the request failed with {type(failure).__name__}: {failure}"
            sleep(TRANSPORT_WAIT_SECONDS * attempt)
            continue
        sleep(PAUSE_SECONDS)
        throttle = _throttle_message(body)
        if throttle is None:
            return body
        reason = f"Alpha Vantage answered {throttle[:_QUOTED]!r}"
        sleep(THROTTLE_WAIT_SECONDS * attempt)
    raise RunStopped(f"{label}, after {ATTEMPTS} attempts: {_redact(reason, key)}")


def _settle(
    cross_section: str,
    symbol: str,
    body: bytes,
    key: str,
    today: Callable[[], date],
    data_dir: Path | None,
    directory: Path,
    tally: Tally,
) -> None:
    """Record one body, fail its symbol, or stop the run, by what the body holds."""
    stripped = body.lstrip()
    first = stripped.split(b"\n", 1)[0].decode("utf-8", "replace").strip()
    if stripped.startswith(b"{"):
        try:
            parsed = json.loads(stripped)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict) and "Error Message" in parsed:
            reason = f"Alpha Vantage answered {str(parsed['Error Message'])[:_QUOTED]!r}"
        else:
            reason = "a JSON body carrying neither Error Message, Information nor Note"
    elif first == DAILY_HEADER:
        try:
            entry = record_archive_file(
                cross_section,
                symbol,
                body,
                download_date=today().isoformat(),
                data_dir=data_dir,
                directory=directory,
            )
        except (ValueError, ArchiveRecordRefused) as refused:
            reason = str(refused)
        except OSError as failure:
            raise RunStopped(f"{symbol}: writing to the archive failed, {failure}") from failure
        else:
            tally.recorded.append(symbol)
            _say(
                f"{symbol}: recorded {entry.row_count} rows, {entry.first_date} to "
                f"{entry.last_date}",
                key,
            )
            return
    elif "," in first:
        raise RunStopped(f"{symbol}: the CSV opens with {first[:80]!r}, not the daily header")
    elif not stripped:
        reason = "an empty body"
    else:
        reason = f"a body that is neither CSV nor JSON, opening {first[:80]!r}"
    tally.failed.append(symbol)
    _say(f"{symbol}: failed, {reason}", key)


def _throttle_message(body: bytes) -> str | None:
    """The vendor's ``Information`` or ``Note`` text, when that is all the body says."""
    stripped = body.lstrip()
    if not stripped.startswith(b"{"):
        return None
    try:
        parsed = json.loads(stripped)
    except ValueError:
        return None
    if not isinstance(parsed, dict) or "Error Message" in parsed:
        return None
    for name in ("Information", "Note"):
        if name in parsed:
            return str(parsed[name])
    return None


def _redact(text: str, key: str) -> str:
    return text.replace(key, "<key>") if key else text


def _say(text: str, key: str) -> None:
    print(_redact(text, key), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
