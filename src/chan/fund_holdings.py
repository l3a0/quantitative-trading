"""A fund's year-end holdings, read from its SEC filings into a committed record.

Example 7.6 ranks the S&P 600 as it stood at each December year-end, and
nothing Chan saved says which companies those were. IJR, the iShares S&P 600
fund, prints its whole schedule of investments for every December 31 in a
filing iShares Trust makes with the SEC, so the membership can be read rather
than guessed.
[Issue 361](https://github.com/l3a0/quantitative-trading/issues/361) is the
scope, and [docs/design.md](../../docs/design.md)'s section "A record that
reads a fund's filings" is the reasoning.

**A filing is not a vintage.** A vendor restates a price series, so a vintage
keeps the bytes. The SEC never restates a filing. An accession number names
fixed bytes, and a correction arrives as a new accession. So the accession pins
what was read, the way the edition pins a table printed in a book, and the
record lives under ``research/filings/`` rather than in ``data/``.

The record has two parts.

1. One CSV per filing, at ``research/filings/<fund>/<report date>.csv``,
   holding the rows under common stocks in the filing's order, with the
   columns :data:`COLUMNS`.
2. An index, ``research/filings/index.jsonl``, one line per filing, naming the
   accession, the primary document's sha256 and the CSV's sha256.

The source documents are not committed, because each N-Q runs to 15 to 38 MB.
The index's sha256 says which bytes were parsed, so a fetch refuses a download
that differs from them.

Two formats, read by two parsers.

1. **N-Q**, 2007 to 2018. One HTML file holds every fund the trust reports at
   that quarter-end. :func:`parse_nq` reads from the fund's first schedule
   heading to its "Total Common Stocks" line, and refuses when a heading naming
   another fund comes first.
2. **N-PORT**, from 2019. One XML file per series. :func:`parse_nport` reads
   the ``invstOrSec`` rows whose ``assetCat`` is ``EC``.

The N-PORT ``balance`` is not the share count the filing's own HTML exhibit
prints, by a median 1.13% in 2019 and 0.046% in 2024 on the survey the issue
records. The prices agree, so value over shares is the holding's price in
either format, which is all :func:`place` reads. Share counts are never
compared across the two formats.

The fetch needs a contact for SEC's User-Agent rule. A contact identifies a
person, so it comes from ``QT_SEC_USER_AGENT`` or
``~/.config/quantitative-trading/sec_user_agent`` and never from a tracked
file, per the design doc's Configuration section.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

from chan import paths

#: iShares Trust's central index key at the SEC. Every fund here files under it.
TRUST_CIK = 1100663

#: Where the record lives, outside ``data/`` because a filing is not a vintage.
FILINGS_DIR = paths.REPO_ROOT / "research" / "filings"

#: The index's file name inside :data:`FILINGS_DIR`.
INDEX_NAME = "index.jsonl"

#: The columns of every holdings file, in order.
COLUMNS = ("name", "shares", "value", "cusip", "isin", "ticker")

#: The environment variable naming SEC's User-Agent contact for one run.
USER_AGENT_ENV = "QT_SEC_USER_AGENT"

#: The machine-local file holding that contact on one line.
USER_AGENT_CONFIG = Path("~/.config/quantitative-trading/sec_user_agent")

#: SEC asks for no more than 10 requests a second. This spacing stays under it.
REQUEST_SPACING_SECONDS = 0.15

_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
_NPORT = "{http://www.sec.gov/edgar/nport}"


class FilingRefused(Exception):
    """A fetch or a write stopped rather than produce a record nobody can check.

    The message is one line, because ``main`` prints it as the whole report.
    """


@dataclass(frozen=True)
class Filing:
    """One filing in a fund's committed list.

    ``document`` is the primary document's path inside the accession's
    directory on EDGAR. ``report_date`` is the date the schedule is as of,
    which is the last business day when December 31 is not one.
    """

    report_date: str
    form: str
    accession: str
    filing_date: str
    document: str


@dataclass(frozen=True)
class NotStock:
    """A row under common stocks that is not a company's stock.

    ``report_date``, ``name`` and ``cusip`` together name exactly one row of one
    holdings file, and ``reason`` says what the row is instead. The CUSIP is
    there because N-PORT gives OmniAb's two earnout rows one title, and it is
    empty for an N-Q, which prints none.
    """

    report_date: str
    name: str
    cusip: str
    reason: str


@dataclass(frozen=True)
class Fund:
    """A fund the reader can record, and everything that differs between funds.

    ``schedule_names`` are the names an N-Q's schedule heading gives the fund,
    upper-cased with "iShares" and the registered-trademark sign removed, since
    a fund is renamed over the years. ``series_id`` is the N-PORT series.
    """

    symbol: str
    series_id: str
    schedule_names: tuple[str, ...]
    filings: tuple[Filing, ...]
    not_stocks: tuple[NotStock, ...]


@dataclass(frozen=True)
class Holding:
    """One row under common stocks, written as the filing prints it.

    An N-Q prints no identifiers, so its rows leave ``cusip``, ``isin`` and
    ``ticker`` empty. An N-Q's numbers lose their thousands separators and
    nothing else. An N-PORT's are the XML's own strings.
    """

    name: str
    shares: str
    value: str
    cusip: str = ""
    isin: str = ""
    ticker: str = ""


@dataclass(frozen=True)
class Schedule:
    """What one filing holds under common stocks, and the total it prints for them.

    ``printed_total`` is the N-Q's "Total Common Stocks" figure. N-PORT prints
    no such line, so it is ``None`` there.
    """

    holdings: tuple[Holding, ...]
    printed_total: int | None


@dataclass(frozen=True)
class IndexEntry:
    """One line of ``research/filings/index.jsonl``."""

    fund: str
    series_id: str
    form: str
    accession: str
    filing_date: str
    report_date: str
    document: str
    document_sha256: str
    path: str
    sha256: str
    row_count: int
    printed_total: int | None


@dataclass(frozen=True)
class Placement:
    """One member of a filing, and where its calendar year left it.

    ``previous`` is the row it was linked to in the filing before, and
    ``linked_by`` says how, ``cusip`` or ``name``. An unlinked member carries
    ``None`` in all three, because a return needs both ends.
    """

    holding: Holding
    previous: Holding | None
    linked_by: str | None
    calendar_return: Decimal | None


# --- The committed lists -----------------------------------------------------
# Every IJR year-end from 2007 to 2025 has exactly one filing, surveyed on
# EDGAR on 2026-10-04. IJR's fiscal year ends March 31, so December 31 is
# always its third fiscal quarter and never an N-CSR period.

_NPORT_DOCUMENT = "primary_doc.xml"

IJR = Fund(
    symbol="IJR",
    series_id="S000004313",
    schedule_names=("S&P SMALLCAP 600 INDEX FUND", "CORE S&P SMALL-CAP ETF"),
    filings=(
        Filing("2007-12-31", "N-Q", "0001193125-08-043324", "2008-02-29", "dnq.htm"),
        Filing("2008-12-31", "N-Q", "0001193125-09-040696", "2009-02-27", "dnq.htm"),
        Filing("2009-12-31", "N-Q", "0001193125-10-044578", "2010-03-01", "dnq.htm"),
        Filing("2010-12-31", "N-Q", "0001193125-11-052046", "2011-03-01", "dnq.htm"),
        Filing("2011-12-31", "N-Q", "0001193125-12-088646", "2012-02-29", "d302216dnq.htm"),
        Filing("2012-12-31", "N-Q", "0001193125-13-086998", "2013-03-01", "d488313dnq.htm"),
        Filing("2013-12-31", "N-Q", "0001193125-14-076476", "2014-02-28", "d678190dnq.htm"),
        Filing("2014-12-31", "N-Q", "0001193125-15-065725", "2015-02-26", "d875299dnq.htm"),
        Filing("2015-12-31", "N-Q", "0001193125-16-480933", "2016-02-26", "d146052dnq.htm"),
        Filing("2016-12-31", "N-Q", "0001193125-17-065125", "2017-03-01", "d346678dnq.htm"),
        Filing("2017-12-31", "N-Q", "0001193125-18-063612", "2018-02-28", "d539192dnq.htm"),
        Filing("2018-12-31", "N-Q", "0001193125-19-059323", "2019-03-01", "d655820dnq.htm"),
        Filing("2019-12-31", "NPORT-P", "0001752724-20-038667", "2020-02-27", _NPORT_DOCUMENT),
        Filing("2020-12-31", "NPORT-P", "0001752724-21-040685", "2021-02-25", _NPORT_DOCUMENT),
        Filing("2021-12-31", "NPORT-P", "0001752724-22-046380", "2022-02-25", _NPORT_DOCUMENT),
        # December 31 fell on a Saturday, so the schedule is as of the Friday.
        Filing("2022-12-30", "NPORT-P", "0001752724-23-037514", "2023-02-24", _NPORT_DOCUMENT),
        Filing("2023-12-31", "NPORT-P", "0001752724-24-038606", "2024-02-26", _NPORT_DOCUMENT),
        Filing("2024-12-31", "NPORT-P", "0001752724-25-041377", "2025-02-26", _NPORT_DOCUMENT),
        Filing("2025-12-31", "NPORT-P", "0000940400-26-007526", "2026-02-25", _NPORT_DOCUMENT),
    ),
    not_stocks=(
        *(
            NotStock(
                date,
                "Gerber Scientific Inc. Escrow",
                "",
                "an escrow interest valued at a cent a unit, held after Gerber Scientific's "
                "own stock left the schedule in 2011",
            )
            for date in (
                "2011-12-31",
                "2012-12-31",
                "2013-12-31",
                "2014-12-31",
                "2015-12-31",
                "2016-12-31",
                "2017-12-31",
            )
        ),
        NotStock(
            "2018-12-31",
            "A Schulman Inc.",
            "",
            "the A Schulman CVR under the company's name: footnoted as valued on "
            "unobservable inputs, at $1.91 a unit, and the same 1,640,554 units the "
            "2019 filing names a CVR",
        ),
        NotStock(
            "2019-12-31",
            "SCHULMAN A INC CVR COM NPV",
            "808CVR104",
            "the A Schulman contingent value right",
        ),
        *(
            NotStock(date, name, cusip, f"one of OmniAb's two earnout share classes, {note}")
            for date, name in (
                ("2022-12-30", "Omniab Inc/old"),
                ("2023-12-31", "Omniab Inc/old"),
                ("2024-12-31", "Omniab Inc/old"),
                ("2025-12-31", "OmniAb, Inc."),
            )
            for cusip, note in (
                ("68218J202", "450,637 units valued at $4.51 in all"),
                ("68218J301", "450,637 units valued at $4.51 in all"),
            )
        ),
    ),
)

#: Every fund the reader knows, by the symbol ``fetch`` takes.
FUNDS: Mapping[str, Fund] = {IJR.symbol: IJR}


# --- Reading an N-Q's HTML ---------------------------------------------------


class _Rows(HTMLParser):
    """Flattens an N-Q into its text lines and its table rows, in document order.

    A ``<sup>`` is dropped with everything inside it. From 2012 to 2017 that is
    where the footnote markers sit, and in some years the registered-trademark
    sign in a fund's heading. Every run of whitespace, a non-breaking space
    included, becomes one space.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[tuple[str, str | tuple[str, ...]]] = []
        self._text: list[str] = []
        self._cells: list[str] | None = None
        self._cell: list[str] | None = None
        self._sup = 0

    def _flush(self) -> None:
        text = _squash("".join(self._text))
        if text:
            self.items.append(("text", text))
        self._text = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "sup":
            self._sup += 1
        elif tag == "tr":
            self._flush()
            self._cells = []
        elif tag in ("td", "th") and self._cells is not None:
            self._cell = []
        elif tag in ("p", "div", "br") and self._cell is not None:
            # 2014 breaks "Pep Boys - Manny, Moe & Jack (The)" across two lines
            # of one cell, and the break is the only space before "Jack".
            self._cell.append(" ")
        elif tag in ("p", "div", "br", "table", "hr") and self._cells is None:
            self._flush()

    def handle_endtag(self, tag: str) -> None:
        if tag == "sup":
            self._sup = max(0, self._sup - 1)
        elif tag in ("td", "th") and self._cell is not None and self._cells is not None:
            self._cells.append(_squash("".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._cells is not None:
            cells = tuple(cell for cell in self._cells if cell not in ("", "$"))
            if cells:
                self.items.append(("row", cells))
            self._cells = None
            self._cell = None
        elif tag in ("p", "div", "table") and self._cells is None:
            self._flush()

    def handle_data(self, data: str) -> None:
        if self._sup:
            return
        if self._cell is not None:
            self._cell.append(data)
        elif self._cells is None:
            self._text.append(data)


def _squash(text: str) -> str:
    """Every run of whitespace as one space, a non-breaking space included."""
    return " ".join(text.split())


def _decode(document: bytes) -> str:
    """The document as text. The N-Q files are ASCII with character references."""
    try:
        return document.decode("utf-8")
    except UnicodeDecodeError:
        return document.decode("cp1252")


_GROUPED = re.compile(r"\d{1,3}(?:,\d{3})*")
_FOOTNOTES = re.compile(r"(?:\s*\([a-z]\))+$")


def _number(cell: str) -> str | None:
    """A printed whole number without its separators, or ``None`` for anything else.

    2018 splits one value with a space, as "83,6 15,992". Closing the space
    leaves a correctly grouped number, so it is read as one. Without that,
    the year's sum falls short of its printed total by $124,344,900.
    """
    candidate = cell.removeprefix("$").strip().replace(" ", "")
    if not _GROUPED.fullmatch(candidate):
        return None
    return candidate.replace(",", "")


def _schedule_name(heading: str) -> str:
    """A schedule heading's fund name, upper-cased, without "iShares" or a suffix."""
    name = heading.replace("®", " ")
    name = re.sub(r"\(Percentages shown.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"^\s*iSHARES\b", "", name, flags=re.IGNORECASE)
    return _squash(name).upper()


def _headings(items: Sequence[tuple[str, str | tuple[str, ...]]]) -> Iterable[tuple[int, str]]:
    """Every schedule heading in an N-Q, as its position and the fund it names.

    Two shapes. To 2017 a heading is the text line after one opening
    "Schedule of Investments". In 2018 it is one table row whose first cell
    opens that way and whose second names the fund.
    """
    for position, (kind, content) in enumerate(items):
        if kind == "row":
            assert isinstance(content, tuple)
            if len(content) >= 2 and content[0].lower().startswith("schedule of investments"):
                yield position, _schedule_name(content[1])
        elif position > 0:
            before_kind, before = items[position - 1]
            if before_kind == "text" and str(before).lower().startswith("schedule of investments"):
                yield position, _schedule_name(str(content))


def parse_nq(document: bytes, schedule_names: Sequence[str]) -> Schedule:
    """The fund's rows under common stocks in one N-Q, with the total it prints.

    The fund's section opens at its first schedule heading. Rows are read from
    its "COMMON STOCKS" line to its "Total Common Stocks" line, and every row
    holding a name, a share count and a value is a holding. A row of one number
    is an industry subtotal and a row of text is a heading, so both are passed.
    Footnote markers are dropped: a ``<sup>`` by :class:`_Rows`, and a trailing
    run such as "(a)(b)" here.

    It refuses when the section never opens, when a heading naming another fund
    comes before the total, and when a row under common stocks has a shape no
    year was seen to print.
    """
    parser = _Rows()
    parser.feed(_decode(document))
    parser.close()
    parser._flush()
    items = parser.items
    wanted = {name.upper() for name in schedule_names}
    headings = list(_headings(items))
    opening = next((at for at, name in headings if name in wanted), None)
    if opening is None:
        raise ValueError(f"no schedule heading names {sorted(wanted)}")
    others = [at for at, name in headings if at > opening and name not in wanted]
    boundary = others[0] if others else len(items)

    holdings: list[Holding] = []
    started = False
    for position in range(opening, boundary):
        kind, content = items[position]
        if kind != "row":
            continue
        assert isinstance(content, tuple)
        first = content[0]
        upper = first.upper()
        if upper.startswith("TOTAL COMMON STOCKS"):
            total = _number(content[-1]) if len(content) > 1 else None
            if total is None:
                following = items[position + 1] if position + 1 < boundary else None
                if following and following[0] == "row":
                    total = _number(following[1][-1])
            if total is None:
                raise ValueError(f"the Total Common Stocks line prints no total: {content}")
            return Schedule(tuple(holdings), int(total))
        if not started:
            started = upper.startswith("COMMON STOCKS")
            continue
        numbers = [_number(cell) for cell in content]
        if len(content) == 1:
            continue
        if numbers[-1] is None:
            continue
        if len(content) == 3 and numbers[0] is None and numbers[1] is not None:
            name = _FOOTNOTES.sub("", first).strip()
            holdings.append(Holding(name=name, shares=str(numbers[1]), value=str(numbers[2])))
            continue
        raise ValueError(f"a row under common stocks has a shape no year printed: {content}")
    raise ValueError(
        "no Total Common Stocks line before "
        + ("the next fund's heading" if others else "the end of the document")
    )


# --- Reading an N-PORT's XML -------------------------------------------------


def parse_nport(document: bytes, series_id: str) -> Schedule:
    """The rows under common stocks in one N-PORT, as the XML gives them.

    A row is an ``invstOrSec`` whose ``assetCat`` is ``EC``. Its name is the
    ``title``, because from 2022 the ``name`` is cut at 30 characters and the
    title stays whole. A CUSIP of nine zeros is the filer saying there is none,
    so it is written empty. It refuses a document filed for another series.
    """
    root = ET.fromstring(document)
    filed_for = root.findtext(f".//{_NPORT}genInfo/{_NPORT}seriesId")
    if filed_for != series_id:
        raise ValueError(f"the document is series {filed_for}, not {series_id}")
    holdings: list[Holding] = []
    for row in root.iter(f"{_NPORT}invstOrSec"):
        if row.findtext(f"{_NPORT}assetCat") != "EC":
            continue
        cusip = (row.findtext(f"{_NPORT}cusip") or "").strip()
        identifiers = row.find(f"{_NPORT}identifiers")
        isin = ticker = ""
        if identifiers is not None:
            isin_element = identifiers.find(f"{_NPORT}isin")
            ticker_element = identifiers.find(f"{_NPORT}ticker")
            isin = "" if isin_element is None else isin_element.get("value", "")
            ticker = "" if ticker_element is None else ticker_element.get("value", "")
        holdings.append(
            Holding(
                name=_squash(row.findtext(f"{_NPORT}title") or ""),
                shares=(row.findtext(f"{_NPORT}balance") or "").strip(),
                value=(row.findtext(f"{_NPORT}valUSD") or "").strip(),
                cusip="" if cusip == "000000000" else cusip,
                isin=isin,
                ticker=ticker,
            )
        )
    return Schedule(tuple(holdings), None)


def parse(document: bytes, fund: Fund, filing: Filing) -> Schedule:
    """The schedule one filing holds, read by the parser its form needs."""
    if filing.form == "N-Q":
        return parse_nq(document, fund.schedule_names)
    if filing.form.startswith("NPORT"):
        return parse_nport(document, fund.series_id)
    raise ValueError(f"no parser reads form {filing.form}")


# --- The record --------------------------------------------------------------


def serialize(holdings: Iterable[Holding]) -> bytes:
    """A holdings file's bytes: a header, then one line per row, LF endings."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(COLUMNS)
    for holding in holdings:
        writer.writerow([getattr(holding, column) for column in COLUMNS])
    return buffer.getvalue().encode("utf-8")


def read_holdings(path: Path) -> tuple[Holding, ...]:
    """A holdings file's rows, in the filing's order."""
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise ValueError(f"{path} has columns {reader.fieldnames}, not {list(COLUMNS)}")
        return tuple(Holding(**row) for row in reader)


def holdings_path(fund: Fund, filing: Filing, filings_dir: Path | None = None) -> Path:
    """Where one filing's holdings file sits."""
    directory = FILINGS_DIR if filings_dir is None else filings_dir
    return directory / fund.symbol.lower() / f"{filing.report_date}.csv"


def read_index(filings_dir: Path | None = None) -> list[IndexEntry]:
    """Every line of ``research/filings/index.jsonl``, or none when it is absent."""
    directory = FILINGS_DIR if filings_dir is None else filings_dir
    index = directory / INDEX_NAME
    if not index.exists():
        return []
    entries = []
    for line in index.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(IndexEntry(**json.loads(line)))
    return entries


def _index_line(entry: IndexEntry) -> str:
    return json.dumps(entry.__dict__, ensure_ascii=False)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def record(
    fund: Fund, filing: Filing, document: bytes, filings_dir: Path | None = None
) -> IndexEntry:
    """Write one filing's holdings file and its index line, or refuse.

    A rerun that would write the same bytes changes nothing. One that would
    write different bytes to an existing file, or a different line for an
    accession the index already holds, refuses and names both hashes. An N-Q
    whose rows do not sum to the total it prints is refused too, because that
    is a parse that read the wrong rows.
    """
    directory = FILINGS_DIR if filings_dir is None else filings_dir
    document_sha256 = _sha256(document)
    schedule = parse(document, fund, filing)
    if schedule.printed_total is not None:
        parsed = sum(int(holding.value) for holding in schedule.holdings)
        if parsed != schedule.printed_total:
            raise FilingRefused(
                f"{fund.symbol} {filing.report_date}: the rows sum to {parsed:,}, "
                f"and the filing prints {schedule.printed_total:,}"
            )
    content = serialize(schedule.holdings)
    target = holdings_path(fund, filing, directory)
    relative = target.relative_to(directory).as_posix()
    entry = IndexEntry(
        fund=fund.symbol,
        series_id=fund.series_id,
        form=filing.form,
        accession=filing.accession,
        filing_date=filing.filing_date,
        report_date=filing.report_date,
        document=filing.document,
        document_sha256=document_sha256,
        path=relative,
        sha256=_sha256(content),
        row_count=len(schedule.holdings),
        printed_total=schedule.printed_total,
    )
    if target.exists():
        existing = _sha256(target.read_bytes())
        if existing != entry.sha256:
            raise FilingRefused(
                f"{relative} holds sha256 {existing} and this parse would write "
                f"{entry.sha256}, so it was left alone"
            )
    entries = read_index(directory)
    held = next((line for line in entries if line.accession == filing.accession), None)
    if held is not None and held != entry:
        raise FilingRefused(
            f"the index already records {filing.accession} with file sha256 {held.sha256} "
            f"and document sha256 {held.document_sha256}, and this parse gives "
            f"{entry.sha256} from {entry.document_sha256}"
        )
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    if held is None:
        entries.append(entry)
        entries.sort(key=lambda line: (line.fund, line.report_date))
        text = "".join(_index_line(line) + "\n" for line in entries)
        (directory / INDEX_NAME).write_bytes(text.encode("utf-8"))
    return entry


# --- Fetching ----------------------------------------------------------------


def user_agent(environ: Mapping[str, str] | None = None, config: Path | None = None) -> str:
    """SEC's User-Agent contact on this machine, or :class:`FilingRefused` naming both places."""
    environ = os.environ if environ is None else environ
    config = USER_AGENT_CONFIG.expanduser() if config is None else config
    named = environ.get(USER_AGENT_ENV, "").strip()
    if not named and config.is_file():
        named = config.read_text(encoding="utf-8").strip()
    if not named:
        raise FilingRefused(
            f"SEC asks every request to name a contact. Set {USER_AGENT_ENV}, or write "
            f"one line to {USER_AGENT_CONFIG}, such as 'Your Name you@example.com'"
        )
    return named


def document_url(filing: Filing, cik: int = TRUST_CIK) -> str:
    """Where EDGAR serves a filing's primary document."""
    return f"{_ARCHIVES}/{cik}/{filing.accession.replace('-', '')}/{filing.document}"


def _download(url: str, contact: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": contact})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError) as failure:
        raise FilingRefused(f"{url} could not be read: {failure}") from failure


def fetch(
    fund: Fund,
    *,
    filings_dir: Path | None = None,
    contact: str | None = None,
    download: Callable[[str, str], bytes] = _download,
    pause: Callable[[float], None] = time.sleep,
) -> list[IndexEntry]:
    """Download each filing in the fund's list, record it, and delete the download.

    Each document lands in a temporary directory the run removes once it is
    parsed. Where the index already names a document, a download whose sha256
    differs is refused before anything is parsed.
    """
    contact = user_agent() if contact is None else contact
    held = {entry.accession: entry for entry in read_index(filings_dir)}
    written = []
    with tempfile.TemporaryDirectory(prefix="fund_holdings_") as scratch:
        for number, filing in enumerate(fund.filings):
            if number:
                pause(REQUEST_SPACING_SECONDS)
            content = download(document_url(filing), contact)
            known = held.get(filing.accession)
            if known is not None and _sha256(content) != known.document_sha256:
                raise FilingRefused(
                    f"{filing.accession} downloaded with sha256 {_sha256(content)}, "
                    f"and the index records {known.document_sha256}"
                )
            saved = Path(scratch) / f"{filing.report_date}_{Path(filing.document).name}"
            saved.write_bytes(content)
            written.append(record(fund, filing, saved.read_bytes(), filings_dir))
            saved.unlink()
    return written


# --- Members, links and placement --------------------------------------------


def members(fund: Fund, filing: Filing, filings_dir: Path | None = None) -> tuple[Holding, ...]:
    """The rows of one holdings file that are not on the fund's list of non-stock rows.

    A second share class is a separate member, because the fund holds it as a
    separate line.
    """
    rows = read_holdings(holdings_path(fund, filing, filings_dir))
    excluded = {
        (entry.name, entry.cusip)
        for entry in fund.not_stocks
        if entry.report_date == filing.report_date
    }
    return tuple(row for row in rows if (row.name, row.cusip) not in excluded)


_PUNCTUATION = re.compile(r"[^\w\s]")
_SHARE_CLASS = re.compile(r"\b(?:class [a-z]|series [a-z]|nvs)\b")


def normalised_name(name: str) -> str:
    """A name reduced to what two filings spell the same way.

    Case, punctuation, the registered-trademark sign and a curly apostrophe
    against a straight one all go. A full stop is deleted rather than spaced,
    so "U.S." and "US" agree. Words stay, a share-class suffix such as
    "Class A" among them, because that is what tells a fund's two lines in one
    company apart.
    """
    text = name.replace("’", "'").replace("®", " ").replace(".", "").casefold()
    return _squash(_PUNCTUATION.sub(" ", text))


def _without_share_class(name: str) -> str:
    """A normalised name with "Class A", "Series A" and "NVS" taken out."""
    return _squash(_SHARE_CLASS.sub(" ", normalised_name(name)))


def _pair(
    current: Sequence[Holding],
    previous: Sequence[Holding],
    key: Callable[[str], str],
    how: str,
    pairs: list[tuple[Holding | None, str | None]],
    *,
    by_cusip: bool,
) -> list[tuple[Holding | None, str | None]]:
    """One pass of :func:`link` over the members ``pairs`` leaves unpaired.

    A pairing is kept only when it is one to one. A key two previous rows
    share, or a previous row two current members both reach, leaves every
    member involved unpaired rather than guessed. A previous row an earlier
    pass already took is not offered again.
    """
    taken = {id(row) for row, _ in pairs if row is not None}
    open_rows = [number for number, row in enumerate(previous) if id(row) not in taken]
    cusips: dict[str, list[int]] = {}
    keys: dict[str, list[int]] = {}
    for number in open_rows:
        row = previous[number]
        if row.cusip:
            cusips.setdefault(row.cusip, []).append(number)
        keys.setdefault(key(row.name), []).append(number)

    proposed: list[tuple[int | None, str | None]] = []
    for row, (paired, _) in zip(current, pairs, strict=True):
        if paired is not None:
            proposed.append((None, None))
            continue
        if by_cusip and row.cusip and row.cusip in cusips:
            candidates, found_by = cusips[row.cusip], "cusip"
        else:
            # Two rows that each carry a CUSIP and disagree are two securities,
            # whatever their names say.
            candidates = [
                number
                for number in keys.get(key(row.name), [])
                if not (row.cusip and previous[number].cusip)
            ]
            found_by = how
        proposed.append((candidates[0], found_by) if len(candidates) == 1 else (None, None))

    reached: dict[int, int] = {}
    for target, _ in proposed:
        if target is not None:
            reached[target] = reached.get(target, 0) + 1
    return [
        (previous[target], found_by)
        if target is not None and reached[target] == 1
        else (paired, paired_by)
        for (target, found_by), (paired, paired_by) in zip(proposed, pairs, strict=True)
    ]


def link(
    current: Sequence[Holding], previous: Sequence[Holding]
) -> list[tuple[Holding | None, str | None]]:
    """Pair each current member with the same holding in the previous filing.

    Each pair comes with how it was found. Two passes, and the second only
    reaches what the first left.

    1. The CUSIP decides where both rows carry one. Otherwise the normalised
       names decide, share-class suffix included, which is what keeps Central
       Garden's two N-Q lines apart. That pairs as ``cusip`` or ``name``.
    2. The names again with the share-class suffix taken out, as
       ``name without class``. The 2018 N-Q prints "Lithia Motors Inc., Class A"
       where the 2019 N-PORT prints "Lithia Motors Inc", for a company IJR holds
       one line of. The one-to-one rule is what keeps this pass from guessing:
       Central Garden's two lines share one name once the suffix goes, so
       neither is paired.

    A member neither pass pairs is left unpaired.
    """
    pairs: list[tuple[Holding | None, str | None]] = [(None, None)] * len(current)
    pairs = _pair(current, previous, normalised_name, "name", pairs, by_cusip=True)
    return _pair(
        current, previous, _without_share_class, "name without class", pairs, by_cusip=False
    )


def _price(holding: Holding) -> Decimal:
    return Decimal(holding.value) / Decimal(holding.shares)


def place(fund: Fund, report_date: str, filings_dir: Path | None = None) -> list[Placement]:
    """Each member of one filing, with its rough calendar-year return where it can be had.

    The return is value over shares in this filing, divided by the same in the
    filing linked to it, less one. A member the link leaves unpaired cannot be
    placed. The first filing in the list has nothing before it, so it is
    refused rather than reported as wholly unplaced.

    The return is rough on purpose. Value over shares moves with a split as
    well as with the price, so a member whose share count fell twentyfold
    between two filings reads as a gain of more than fifty times, which
    ``tests/test_fund_holdings.py`` pins on Steak n Shake in 2009. Dividends
    are not in it either.
    """
    order = [filing.report_date for filing in fund.filings]
    at = order.index(report_date)
    if at == 0:
        raise ValueError(f"{report_date} is {fund.symbol}'s first filing, so nothing precedes it")
    current = members(fund, fund.filings[at], filings_dir)
    previous = members(fund, fund.filings[at - 1], filings_dir)
    placements = []
    for holding, (linked, how) in zip(current, link(current, previous), strict=True):
        if linked is None:
            placements.append(Placement(holding, None, None, None))
        else:
            change = _price(holding) / _price(linked) - 1
            placements.append(Placement(holding, linked, how, change))
    return placements


# --- The command -------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> None:
    """``python -m chan.fund_holdings fetch IJR`` downloads and records every filing."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 2 or arguments[0] != "fetch" or arguments[1] not in FUNDS:
        raise SystemExit(f"usage: python -m chan.fund_holdings fetch {{{','.join(FUNDS)}}}")
    try:
        entries = fetch(FUNDS[arguments[1]])
    except FilingRefused as refusal:
        # One line rather than a traceback, the way chan.equity_seasonals
        # reports a vintage it could not read.
        raise SystemExit(str(refusal)) from refusal
    for entry in entries:
        print(f"{entry.report_date}  {entry.form:8}{entry.accession}  {entry.row_count} rows")


if __name__ == "__main__":
    main()
