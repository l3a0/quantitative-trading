"""Earnings releases read from SEC filings, for Chan's 497 stocks in 2011 and 2012.

Example 7.2 trades a stock on the day it announced earnings, and the only
calendar Chan saved is his own flag file, which
[issue 250](https://github.com/l3a0/quantitative-trading/issues/250) commits.
It catches three of Apple's five releases inside the window, so whether the
drift survives a calendar nobody hand-collected is a separate question.
[Issue 251](https://github.com/l3a0/quantitative-trading/issues/251) asks it,
and :mod:`chan.pead_rerun` runs the comparison. A company announcing earnings
files a Form 8-K carrying Item 2.02, "Results of Operations and Financial
Condition", and EDGAR records the minute each filing was accepted. This module
reads those filings into a record under ``research/filings/earnings/``.

The record lives beside the fund holdings under ``research/filings`` rather
than in ``data/``, for the reason
[docs/design.md](../../docs/design.md)'s section "A record that reads a fund's
filings" gives: the SEC never restates a filing, so its **accession** pins what
was read, and a filing is not a vintage. It has two files.

1. ``tickers.csv``, one row per stock of Chan's flag file, mapping his 2012
   ticker to the SEC's central index key, the CIK, and to the ticker the
   owner's archive files the same company under. Each mapping names the route
   that proposed it and the check it passed or failed, in the shape of
   ``research/filings/ivv/members.csv``.
2. ``index.jsonl``, one line per stock and filing: every original Form 8-K
   carrying Item 2.02 that EDGAR accepted from :data:`FIRST_ACCEPTED` to
   :data:`LAST_ACCEPTED`, for each stock whose CIK passed its check.

**Why the acceptance time comes from the header file.** The submissions JSON
at ``data.sec.gov`` carries an ``acceptanceDateTime`` field marked as UTC. The
plan audit on issue 251 compared it with ``<ACCEPTANCE-DATETIME>`` in each
filing's ``.hdr.sgml``, which is Eastern time and matches the filing's index
page. In 175 of 248 filings from 38 filers the JSON was true UTC. In the other
73 it sat a further 4 or 5 hours later, consistently within a filer, as if
converted from Eastern twice, and Apple was one of those. So the time here is
read from the header, at the price of one request per filing.

**Why the CIK needs a check of its own.** ``company_tickers.json`` maps
today's tickers, so it sends CB to Chubb Limited, which was ACE in 2012 and
files its own Item 2.02 8-Ks in the window. Finding filings under a CIK does
not prove it is the right company. EDGAR's full-text search finds a
distinctive ticker and fails on a short one, sending COG to Concho and K to
Hovnanian. So :func:`check_cik` holds a mapping whatever route proposed it. It
passes when four things hold.

1. The CIK filed something on or before :data:`PRICE_DAY` and something on
   or after it, so it was a filer then.
2. Its EDGAR name on that day, read from the submissions JSON's ``name`` and
   dated ``formerNames``, shares a key from :func:`name_keys` with the name of exactly
   one holding in IVV's schedule at :data:`IVV_REPORT_DATE`, which
   ``research/filings/ivv/2012-03-31.csv`` records.
3. That holding's price, its value over its shares, lies within
   :data:`PRICE_TOLERANCE` of Chan's close for the ticker on
   :data:`PRICE_DAY`.
4. The CIK filed at least one original 8-K carrying Item 2.02 in the window.

The name ties the CIK to a member of the index, and the price ties that member
to Chan's ticker. ACE's CIK fails the third link: its 2012 name finds "ACE
Ltd." in the schedule, priced 5.9 percent above the old Chubb's close. The
fourth link is there because a name does not pick out one CIK. Westinghouse's
old CIK is named "CBS CORP" and filed until 2017, so on the price day it
carries the same name as CBS itself, and only the company whose stock traded
announced earnings under it. Item 2.02 is the item a registrant must file when
it releases its results, so a listed company's CIK carries several in 17
months. The price of the fourth link is that a company which furnished its
releases under another item would leave the calendar, and
``tests/test_earnings_filings.py`` counts how many did.

**The archive ticker has a check too.** Alpha Vantage files a company under
its latest ticker, so Chan's UTX is the archive's RTX, and a reused ticker
holds another company's history, as the archive's CB holds ACE's. A series
passes :func:`check_series` when it holds a close on every one of the flag
file's days on which Chan's file does, and its daily returns differ from
those of Chan's closes by more than :data:`RETURN_TOLERANCE` on at most
:data:`DAYS_ALLOWED` of them. ``tests/test_earnings_filings.py`` says why
those two numbers.

Both checks are what a reader trusts. The routes that proposed each mapping
ran in the build session, against today's EDGAR and the archive, and cannot
be rerun by code, so the table records which route answered rather than how.

The fetch needs a contact for SEC's User-Agent rule, which
:func:`chan.fund_holdings.user_agent` reads from the machine, and it keeps to
:data:`chan.fund_holdings.REQUEST_SPACING_SECONDS` between requests. The
downloaded documents are not committed. Each index line carries the sha256 of
the header file it read, so a rerun that downloads different bytes is refused.

```bash
uv run python -m chan.earnings_filings fetch
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.earnings_filings check
```
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

from chan.fund_holdings import (
    FILINGS_DIR,
    REQUEST_SPACING_SECONDS,
    FilingRefused,
    _download,
    normalised_name,
    user_agent,
)

#: Where the record lives.
RECORD_DIR = FILINGS_DIR / "earnings"

#: The ticker table's and the index's file names inside :data:`RECORD_DIR`.
TABLE_NAME = "tickers.csv"
INDEX_NAME = "index.jsonl"

#: The first and last Eastern dates of acceptance the index keeps. The first is
#: a month before the flag file's first day, 2011-01-03, so a release accepted
#: in the evening of the last trading day of 2010 reaches it. The last is the
#: flag file's last day.
FIRST_ACCEPTED = "2010-12-01"
LAST_ACCEPTED = "2012-04-24"

#: The last filing date fetched. A filing accepted after 17:30 Eastern takes the
#: next business day as its filing date, so the filing date can follow the
#: acceptance date by a weekend and a holiday. The index then keeps only what
#: was accepted by :data:`LAST_ACCEPTED`.
LAST_FILED = "2012-04-30"

#: The form and the item the index keeps. An amendment, ``8-K/A``, is left out.
FORM = "8-K"
ITEM = "2.02"

#: IVV's schedule the CIK check reads, and the day its prices are struck.
IVV_REPORT_DATE = "2012-03-31"
PRICE_DAY = "2012-03-30"

#: How far a holding's price may lie from Chan's close, as a fraction of the close.
PRICE_TOLERANCE = 0.03

#: How far one day's return may differ before the day counts against a series.
RETURN_TOLERANCE = 0.01

#: How many such days a series may carry and still pass.
DAYS_ALLOWED = 5

#: The ticker table's columns, in order.
TABLE_COLUMNS = (
    "ticker",
    "cik",
    "cik_source",
    "edgar_name",
    "ivv_row",
    "cik_check",
    "archive_ticker",
    "archive_source",
    "archive_check",
    "days_over",
)

#: The routes that can propose a CIK, and what each means.
CIK_SOURCES = {
    "tickers": "today's company_tickers.json, on Chan's ticker",
    "tickers-archive": "today's company_tickers.json, on the archive ticker",
    "name": "EDGAR's company list, on the name IVV prints for the holding",
    "search": "EDGAR's full-text search for the ticker in 8-Ks of 2011 and 2012",
    "none": "no route proposed a CIK",
}

#: What a CIK check can conclude.
CIK_CHECKS = {
    "pass": "the three links hold",
    "dates": "the CIK filed nothing before the price day, or nothing after it",
    "name": "no single IVV holding carries the CIK's name on the price day",
    "price": "the holding with that name is priced away from Chan's close",
    "silent": "the CIK filed no original Item 2.02 8-K in the window",
    "unmapped": "no CIK was proposed",
}

#: The routes that can propose an archive ticker.
ARCHIVE_SOURCES = {
    "same": "the archive holds a series under Chan's own ticker",
    "search": "the one series in the sp500 cross-section whose returns match",
    "none": "no series was proposed",
}

#: What an archive check can conclude.
ARCHIVE_CHECKS = {
    "pass": "every close is there and the returns agree",
    "returns": "the returns differ on more days than allowed",
    "missing": "the series lacks a close Chan's file holds",
    "ambiguous": "several series pass and none carries Chan's ticker",
    "none": "no series was proposed",
}

_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
_SUBMISSIONS = "https://data.sec.gov/submissions"
_ACCEPTED = re.compile(rb"<ACCEPTANCE-DATETIME>(\d{14})")
_ACCESSION = re.compile(rb"<ACCESSION-NUMBER>([0-9-]{20})")
_TYPE = re.compile(rb"<TYPE>([^\r\n<]+)")
_FORMS = {
    "inc": "inc",
    "incorporated": "inc",
    "corp": "corp",
    "corporation": "corp",
    "co": "co",
    "company": "co",
    "cos": "cos",
    "companies": "cos",
    "ltd": "ltd",
    "limited": "ltd",
    "plc": "plc",
    "lp": "lp",
    "llc": "llc",
}
_EDGAR_SUFFIX = re.compile(r"\s*[/\\]\s*[A-Za-z]+[/\\]?\s*$")
_SPELLINGS = {"bancorporation": "bancorp"}
_CLASS = re.compile(r"\b(?:class|series|cl) [a-z]\b|\bnvs\b")


@dataclass(frozen=True)
class TickerRow:
    """One row of ``tickers.csv``, written as the file holds it.

    ``cik`` and ``ivv_row`` are empty strings where nothing was found, and
    ``days_over`` is empty where no series was compared. ``ivv_row`` counts
    the IVV schedule's data rows from 1, as ``ivv/members.csv`` does.
    """

    ticker: str
    cik: str
    cik_source: str
    edgar_name: str
    ivv_row: str
    cik_check: str
    archive_ticker: str
    archive_source: str
    archive_check: str
    days_over: str

    @property
    def calendar(self) -> bool:
        """Whether the stock's CIK passed, which puts it in the universe CAL."""
        return self.cik_check == "pass"

    @property
    def priced(self) -> bool:
        """Whether its archive series passed, which puts it in the universe PX."""
        return self.archive_check == "pass"


@dataclass(frozen=True)
class Release:
    """One line of ``index.jsonl``: an original 8-K carrying Item 2.02.

    ``accepted`` is the Eastern time EDGAR accepted the filing, read from its
    header file, as ``YYYY-MM-DDTHH:MM:SS``. ``report_date`` is the date of the
    event the 8-K reports, as the submissions JSON's ``reportDate`` gives it,
    and empty where that is empty. ``header_sha256`` is the sha256 of the
    ``.hdr.sgml`` bytes the time was read from.
    """

    ticker: str
    cik: int
    accession: str
    form: str
    items: str
    report_date: str
    filing_date: str
    accepted: str
    header_sha256: str


# --- The ticker table ----------------------------------------------------------


def read_table(record_dir: Path | None = None) -> list[TickerRow]:
    """Every row of ``tickers.csv``, refusing a file whose columns differ."""
    path = (RECORD_DIR if record_dir is None else record_dir) / TABLE_NAME
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != TABLE_COLUMNS:
            raise ValueError(f"{path} has columns {reader.fieldnames}, not {list(TABLE_COLUMNS)}")
        return [TickerRow(**row) for row in reader]


def serialize_table(rows: Iterable[TickerRow]) -> bytes:
    """The table's bytes, one line per row with a Unix newline."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(TABLE_COLUMNS)
    for row in rows:
        writer.writerow([getattr(row, column) for column in TABLE_COLUMNS])
    return out.getvalue().encode("utf-8")


def name_keys(name: str) -> frozenset[str]:
    """A company name reduced to what EDGAR and an iShares schedule spell alike.

    It deletes apostrophes, since EDGAR files "KOHLS CORP" for "Kohl's Corp.",
    and goes on through :func:`chan.fund_holdings.normalised_name`, which drops case,
    punctuation, a state after a slash and the word "The", and reads "&" as
    "and". Five more differences between the two sources go too.

    1. A last word after a slash, which EDGAR adds to tell filers apart, as in
       "/NEW/", "\\DE\\" and "/ Switzerland", and which the slash rule there
       reaches only for two letters.
    2. A share-class suffix, since EDGAR names the company and the schedule
       names the class.
    3. The spelling of a legal form, so "Corporation" reads "Corp", "Company"
       reads "Co" and "Limited" reads "Ltd". The form itself stays, because
       it is what tells a parent from the subsidiary that shares its name:
       "NEWS LIMITED" is not "News Corp.", and "H. J. Heinz Company, L.P." is
       not "H.J. Heinz Co.". The price of keeping it is that a name printed
       with a form on one side and none on the other does not match, which is
       why "NYSE Euronext" misses "NYSE Euronext Inc.".
    4. Initials. A run of single letters is joined, so EDGAR's "HORTON D R"
       and the schedule's "D.R. Horton" both read "dr".
    5. Two spellings. A plural "s" goes from every other word longer than
       three letters, since EDGAR files Starwood as "HOTEL" and the schedule prints
       "Hotels", and "Bancorporation" reads "Bancorp", as EDGAR files Zions
       and the schedule prints it.

    Two keys come back, the words joined in order and joined in sorted order.
    The first lets "AMAZON COM INC" meet "Amazon.com Inc.", and the second
    lets EDGAR's "LILLY ELI & CO", which puts a person's surname first, meet
    "Eli Lilly and Co.". Two names match when their keys share one.
    """
    text = _EDGAR_SUFFIX.sub(" ", name.replace("'", "").replace("’", ""))
    text = _CLASS.sub(" ", normalised_name(text))
    words: list[str] = []
    initials = False
    for word in text.split():
        if word in _FORMS:
            words.append(_FORMS[word])
            initials = False
            continue
        if len(word) == 1 and initials:
            words[-1] += word
            continue
        word = _SPELLINGS.get(word, word)
        if len(word) > 3 and word.endswith("s"):
            word = word[:-1]
        words.append(word)
        initials = len(word) == 1
    return frozenset({"".join(words), "".join(sorted(words))})


def name_on(submission: Mapping, day: str = PRICE_DAY) -> str | None:
    """The CIK's EDGAR name on ``day``, or ``None`` when it was not filing then.

    A CIK is filing on ``day`` when it filed something on or before it and
    something on or after it, by :func:`filing_span`. That rules out a CIK
    created later, such as today's Dow Inc., and a shell that stopped filing
    earlier and kept a name a later company took, such as Westinghouse's old
    CIK, which EDGAR still names "CBS CORP". A former name whose dated span
    holds the day wins, and otherwise the current ``name`` is taken.
    """
    first, last = filing_span(submission)
    if not first <= day <= last:
        return None
    for former in submission.get("formerNames", []):
        if former["from"][:10] <= day <= former["to"][:10]:
            return former["name"]
    return submission["name"]


def filing_span(submission: Mapping) -> tuple[str, str]:
    """The earliest and latest filing dates the submissions JSON knows for its CIK.

    They are read from the older pages' ``filingFrom`` and ``filingTo`` and
    the recent filings' dates. A CIK with no filing at all spans nothing.
    """
    pages = submission["filings"].get("files", [])
    recent = submission["filings"]["recent"].get("filingDate", [])
    starts = [page["filingFrom"] for page in pages] + list(recent)
    ends = [page["filingTo"] for page in pages] + list(recent)
    if not starts:
        return "9999-12-31", "0000-01-01"
    return min(starts), max(ends)


def holding_price(value: str, shares: str) -> float:
    """A holding's price on the schedule's date, its value over its shares."""
    return float(value) / float(shares)


def check_cik(
    edgar_name: str | None,
    holdings: Sequence[tuple[str, float]],
    close: float,
    releases: int,
) -> tuple[str, int | None]:
    """The CIK check's outcome and the IVV row it matched, counting from 1.

    ``edgar_name`` is :func:`name_on`'s answer, ``holdings`` the schedule's
    ``(name, price)`` rows in order, ``close`` Chan's close on the price day,
    and ``releases`` how many original Item 2.02 8-Ks :func:`candidates`
    finds for the CIK in the window. A name two holdings share fails, since
    the price would then pick between them rather than confirm one.
    """
    if edgar_name is None:
        return "dates", None
    keys = name_keys(edgar_name)
    rows = [number for number, (name, _) in enumerate(holdings, start=1) if name_keys(name) & keys]
    if len(rows) != 1:
        return "name", None
    (row,) = rows
    price = holdings[row - 1][1]
    if not np.isfinite(close) or abs(price / close - 1) > PRICE_TOLERANCE:
        return "price", row
    if releases == 0:
        return "silent", row
    return "pass", row


def check_series(chan_closes: pd.Series, archive_closes: pd.Series) -> tuple[str, int]:
    """The archive check's outcome and the days whose returns differ too much.

    Both series are read on ``chan_closes``' own index, which is the flag
    file's days. A close missing from the archive on a day Chan's file holds
    one fails the series outright, because the run would then read a price
    the check never saw. Otherwise each day's return, close over the previous
    close less 1, is compared, and a difference above
    :data:`RETURN_TOLERANCE` counts against the series.
    """
    archive = archive_closes.reindex(chan_closes.index)
    if (chan_closes.notna() & archive.isna()).any():
        return "missing", int((chan_closes.notna() & archive.isna()).sum())
    difference = (chan_closes.pct_change() - archive.pct_change()).abs()
    over = int((difference > RETURN_TOLERANCE).sum())
    return ("pass" if over <= DAYS_ALLOWED else "returns"), over


# --- The EDGAR record ----------------------------------------------------------


def submissions_url(cik: int) -> str:
    """Where EDGAR serves a CIK's submissions JSON."""
    return f"{_SUBMISSIONS}/CIK{cik:010d}.json"


def page_url(name: str) -> str:
    """Where EDGAR serves one of the older pages a submissions JSON lists."""
    return f"{_SUBMISSIONS}/{name}"


def header_url(cik: int, accession: str) -> str:
    """Where EDGAR serves a filing's header file."""
    return f"{_ARCHIVES}/{cik}/{accession.replace('-', '')}/{accession}.hdr.sgml"


def pages_to_read(submission: Mapping) -> list[str]:
    """The older pages whose filing dates overlap the window, by name."""
    return [
        page["name"]
        for page in submission["filings"].get("files", [])
        if page["filingFrom"] <= LAST_FILED and page["filingTo"] >= FIRST_ACCEPTED
    ]


def candidates(blocks: Iterable[Mapping]) -> list[dict[str, str]]:
    """Every original 8-K carrying Item 2.02 filed inside the window, by accession.

    Each block is a ``filings.recent`` object or one older page, both of which
    hold parallel arrays. An ``8-K/A`` is left out, and so is an 8-K whose
    items do not include :data:`ITEM`. A filing listed twice is kept once.
    """
    found: dict[str, dict[str, str]] = {}
    for block in blocks:
        for i, accession in enumerate(block["accessionNumber"]):
            items = block["items"][i]
            if block["form"][i] != FORM or ITEM not in items.split(","):
                continue
            if not FIRST_ACCEPTED <= block["filingDate"][i] <= LAST_FILED:
                continue
            found[accession] = {
                "accession": accession,
                "form": block["form"][i],
                "items": items,
                "report_date": block["reportDate"][i],
                "filing_date": block["filingDate"][i],
            }
    return [found[accession] for accession in sorted(found)]


def acceptance(header: bytes, accession: str) -> str:
    """The Eastern acceptance time a header file prints, as ``YYYY-MM-DDTHH:MM:SS``.

    The header must name the accession it was fetched for and the form
    :data:`FORM`, so a mislabelled filing in the submissions JSON is refused
    rather than read.
    """
    named = _ACCESSION.search(header)
    if named is None or named.group(1).decode() != accession:
        raise FilingRefused(f"the header fetched for {accession} names another accession")
    form = _TYPE.search(header)
    if form is None or form.group(1).decode().strip() != FORM:
        raise FilingRefused(f"the header of {accession} is not a {FORM}")
    stamp = _ACCEPTED.search(header)
    if stamp is None:
        raise FilingRefused(f"the header of {accession} prints no acceptance time")
    t = stamp.group(1).decode()
    return f"{t[:4]}-{t[4:6]}-{t[6:8]}T{t[8:10]}:{t[10:12]}:{t[12:]}"


def read_index(record_dir: Path | None = None) -> list[Release]:
    """Every line of ``index.jsonl``, or none when it is absent."""
    path = (RECORD_DIR if record_dir is None else record_dir) / INDEX_NAME
    if not path.exists():
        return []
    return [
        Release(**json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def serialize_index(releases: Iterable[Release]) -> bytes:
    """The index's bytes, sorted by ticker and acceptance time."""
    ordered = sorted(releases, key=lambda r: (r.ticker, r.accepted, r.accession))
    return "".join(json.dumps(asdict(r)) + "\n" for r in ordered).encode("utf-8")


def fetch(
    rows: Sequence[TickerRow] | None = None,
    *,
    record_dir: Path | None = None,
    contact: str | None = None,
    download: Callable[[str, str], bytes] = _download,
    pause: Callable[[float], None] = time.sleep,
) -> list[Release]:
    """Read every checked CIK's Item 2.02 8-Ks from EDGAR, write the index, return it.

    For each row whose CIK passed, it reads the submissions JSON, refuses when
    the name on :data:`PRICE_DAY` is not the table's ``edgar_name``, reads the
    older pages the window spills into, and reads each candidate's header for
    its acceptance time. A filing accepted outside the window is dropped. A
    header whose sha256 differs from the one the index already records for
    the same ticker and accession is refused before anything is written. One
    request goes out per :data:`REQUEST_SPACING_SECONDS` at most.
    """
    rows = read_table(record_dir) if rows is None else rows
    directory = RECORD_DIR if record_dir is None else record_dir
    contact = user_agent() if contact is None else contact
    held = {(r.ticker, r.accession): r for r in read_index(directory)}
    sent = [0]

    def get(url: str) -> bytes:
        if sent[0]:
            pause(REQUEST_SPACING_SECONDS)
        sent[0] += 1
        return download(url, contact)

    releases: list[Release] = []
    for row in rows:
        if not row.calendar:
            continue
        cik = int(row.cik)
        submission = json.loads(get(submissions_url(cik)))
        if name_on(submission) != row.edgar_name:
            raise FilingRefused(
                f"{row.ticker}: CIK {cik} was named {name_on(submission)!r} on {PRICE_DAY}, "
                f"and the table records {row.edgar_name!r}"
            )
        blocks = [submission["filings"]["recent"]]
        blocks += [json.loads(get(page_url(name))) for name in pages_to_read(submission)]
        for filing in candidates(blocks):
            header = get(header_url(cik, filing["accession"]))
            accepted = acceptance(header, filing["accession"])
            if not FIRST_ACCEPTED <= accepted[:10] <= LAST_ACCEPTED:
                continue
            release = Release(
                ticker=row.ticker,
                cik=cik,
                header_sha256=hashlib.sha256(header).hexdigest(),
                accepted=accepted,
                **filing,
            )
            kept = held.get((release.ticker, release.accession))
            if kept is not None and kept != release:
                raise FilingRefused(
                    f"{release.ticker} {release.accession}: the index records "
                    f"{kept.accepted} from header sha256 {kept.header_sha256}, and this "
                    f"fetch read {release.accepted} from {release.header_sha256}"
                )
            releases.append(release)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / INDEX_NAME).write_bytes(serialize_index(releases))
    return releases


# --- The archive check ---------------------------------------------------------


def checked_archive(row: TickerRow, chan_closes: pd.Series, archive: pd.DataFrame) -> TickerRow:
    """The row with its archive check recomputed on ``archive``'s adjusted closes.

    ``archive`` is the ``sp500`` cross-section's adjusted closes, one column
    per archive ticker. A row with no archive ticker is left as it is.
    """
    if not row.archive_ticker or row.archive_ticker not in archive.columns:
        return row
    outcome, over = check_series(chan_closes, archive[row.archive_ticker])
    return replace(row, archive_check=outcome, days_over=str(over))


def check(directory: Path | None = None, record_dir: Path | None = None) -> list[str]:
    """Recompute every archive check and return the tickers whose outcome moved.

    It reads Chan's closes through :func:`chan.pead.read_sources` and the
    archive through :func:`chan.archive.read_cross_section`, and writes
    nothing, so a moved outcome is something to explain rather than a file
    silently rewritten.
    """
    from chan.archive import read_cross_section
    from chan.pead import read_sources

    rows = read_table(record_dir)
    _, _, _, closes, flags = read_sources()
    wanted = sorted({row.archive_ticker for row in rows if row.archive_ticker})
    _, archive = read_cross_section("sp500", symbols=wanted, directory=directory)
    moved = []
    for row in rows:
        again = checked_archive(row, closes[row.ticker].loc[flags.index], archive)
        if (again.archive_check, again.days_over) != (row.archive_check, row.days_over):
            moved.append(row.ticker)
    return moved


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="The Item 2.02 8-K record for Chan's 497 stocks, issue 251"
    )
    parser.add_argument("command", choices=("fetch", "check"))
    args = parser.parse_args(argv)
    try:
        if args.command == "fetch":
            releases = fetch()
            print(f"{len(releases)} filings written to {RECORD_DIR / INDEX_NAME}")
        else:
            moved = check()
            print(
                "every archive check reproduces"
                if not moved
                else f"{len(moved)} archive checks moved: {', '.join(moved)}"
            )
            if moved:
                raise SystemExit(1)
    except FilingRefused as refused:
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
