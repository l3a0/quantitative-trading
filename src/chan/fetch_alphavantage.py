"""Fetch Alpha Vantage's daily closes into the owner's archive, one symbol at a time.

The owner extended the archive exception on 2026-10-04 to Alpha Vantage's daily
closes for the S&P 600 cross-section, and ruled the same day that the fetch
lives here, reading ``ALPHAVANTAGE_API_KEY`` from the environment of one run.
[Issue 335](https://github.com/l3a0/quantitative-trading/issues/335) records
both. Each symbol is one ``TIME_SERIES_DAILY_ADJUSTED`` request with
``outputsize=full`` and ``datatype=csv``, and its response is written to the
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
from chan.vintage import SYMBOL_PATTERN

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
            body = _request(symbol, key, get, sleep)
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


def _request(symbol: str, key: str, get: Callable[[str], bytes], sleep: Callable[[float], None]):
    """One symbol's body, or :class:`RunStopped` once a throttle or transport failure persists."""
    reason = ""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            body = get(request_url(symbol, key))
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
    raise RunStopped(f"{symbol}, after {ATTEMPTS} attempts: {_redact(reason, key)}")


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
