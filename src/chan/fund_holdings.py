"""A fund's holdings, read from its SEC filings into a committed record.

Example 7.6 ranks the S&P 600 as it stood at each December year-end, Example
7.7 ranks the S&P 500 at each month-end, and nothing Chan saved says which
companies those were. IJR and IVV, the iShares funds that track the two
indices, print their whole schedule of investments in the filings iShares
Trust makes with the SEC, so the membership can be read rather than guessed.
[Issue 361](https://github.com/l3a0/quantitative-trading/issues/361) is IJR's
scope and [issue 372](https://github.com/l3a0/quantitative-trading/issues/372)
is IVV's. [docs/design.md](../../docs/design.md)'s section "A record that
reads a fund's filings" is the reasoning.

The record lives under ``research/filings/`` rather than in ``data/``, because
a filing is pinned by its accession rather than kept as a vintage. The design
doc's section says why.

The record has two parts.

1. One CSV per filing, at ``research/filings/<fund>/<report date>.csv``,
   holding the rows under common stocks in the filing's order, with the
   columns :data:`COLUMNS`.
2. An index, ``research/filings/index.jsonl``, one line per fund and filing,
   naming the accession, the primary document's sha256 and the CSV's sha256.

The source documents are not committed, because each runs to 15 to 58 MB.
The index's sha256 says which bytes were parsed, so a fetch refuses a download
that differs from them.

Two formats, read by two parsers.

1. **HTML**: an N-Q to 2018, a shareholder report, which is an N-CSR or
   N-CSRS, to 2019, and IVV's standalone NPORT-EX for 2019-06-30. One N-Q or
   shareholder report holds every fund the trust reports at that date.
   :func:`parse_nq` reads from the fund's first schedule heading to its "Total
   Common Stocks" line, and refuses when a heading naming another fund comes
   first.
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
import http.client
import io
import json
import os
import re
import sys
import tempfile
import time
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
    directory on EDGAR. ``report_date`` is the date the schedule is as of, as
    the filing prints it. ``skipped`` is empty for a filing the reader
    records, and otherwise says why the filing holds no full schedule, so the
    date stays on the list with nothing written for it.
    """

    report_date: str
    form: str
    accession: str
    filing_date: str
    document: str
    skipped: str = ""


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
    ``linked_by`` says how, ``cusip``, ``name`` or ``name without class``, as
    :func:`link` reports it. An unlinked member carries ``None`` in all three,
    because a return needs both ends. A linked member carries ``None`` as its
    return only where a zero share count or value leaves a price undefined.
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

# IVV's quarter-ends from 2008-12-31 to 2026-06-30, surveyed on EDGAR on
# 2026-10-04 and recorded on 2026-10-05. IVV's fiscal year ends March 31, so
# its March 31 schedule is in an N-CSR, its September 30 in an N-CSRS, and its
# June 30 and December 31 in an N-Q to 2018. 2019-06-30 has only a standalone
# NPORT-EX. From 2019-09-30 an NPORT-P covers every quarter-end and is the one
# read, and where an N-CSR or N-CSRS shares its date it is not. 2025-09-30
# reads the amendment rather than the NPORT-P it corrects. One N-Q holds every
# fund in the trust, so each December N-Q here is the same accession IJR's
# list names.

_SUMMARY_ONLY = (
    'the N-CSRS prints a summary schedule of 55 holdings and "Other securities" '
    "rather than every holding, and a full-text search of the trust's filings from "
    "October 2013 to June 2014 found no amendment carrying the full list"
)

IVV = Fund(
    symbol="IVV",
    series_id="S000004310",
    schedule_names=("S&P 500 INDEX FUND", "CORE S&P 500 ETF"),
    filings=(
        Filing("2008-12-31", "N-Q", "0001193125-09-040696", "2009-02-27", "dnq.htm"),
        Filing("2009-03-31", "N-CSR", "0001193125-09-126206", "2009-06-05", "dncsr.htm"),
        Filing("2009-06-30", "N-Q", "0001193125-09-183934", "2009-08-28", "dnq.htm"),
        Filing("2009-09-30", "N-CSRS", "0001193125-09-248357", "2009-12-07", "dncsrs.htm"),
        Filing("2009-12-31", "N-Q", "0001193125-10-044578", "2010-03-01", "dnq.htm"),
        Filing("2010-03-31", "N-CSR", "0001193125-10-133919", "2010-06-07", "dncsr.htm"),
        Filing("2010-06-30", "N-Q", "0001193125-10-199353", "2010-08-27", "dnq.htm"),
        Filing("2010-09-30", "N-CSRS", "0001193125-10-277292", "2010-12-09", "dncsrs.htm"),
        Filing("2010-12-31", "N-Q", "0001193125-11-052046", "2011-03-01", "dnq.htm"),
        Filing("2011-03-31", "N-CSR", "0001193125-11-162711", "2011-06-10", "dncsr.htm"),
        Filing("2011-06-30", "N-Q", "0001193125-11-235651", "2011-08-29", "dnq.htm"),
        Filing("2011-09-30", "N-CSRS", "0001193125-11-336349", "2011-12-09", "d249987dncsrs.htm"),
        Filing("2011-12-31", "N-Q", "0001193125-12-088646", "2012-02-29", "d302216dnq.htm"),
        Filing("2012-03-31", "N-CSR", "0001193125-12-264907", "2012-06-08", "d336639dncsr.htm"),
        Filing("2012-06-30", "N-Q", "0001193125-12-373715", "2012-08-29", "d401274dnq.htm"),
        Filing("2012-09-30", "N-CSRS", "0001193125-12-494940", "2012-12-07", "d425526dncsrs.htm"),
        Filing("2012-12-31", "N-Q", "0001193125-13-086998", "2013-03-01", "d488313dnq.htm"),
        Filing("2013-03-31", "N-CSR", "0001193125-13-251330", "2013-06-07", "d524429dncsr.htm"),
        Filing("2013-06-30", "N-Q", "0001193125-13-351768", "2013-08-29", "d587788dnq.htm"),
        Filing(
            "2013-09-30",
            "N-CSRS",
            "0001193125-13-466531",
            "2013-12-09",
            "d609194dncsrs.htm",
            skipped=_SUMMARY_ONLY,
        ),
        Filing("2013-12-31", "N-Q", "0001193125-14-076476", "2014-02-28", "d678190dnq.htm"),
        Filing("2014-03-31", "N-CSR", "0001193125-14-230537", "2014-06-09", "d714017dncsr.htm"),
        Filing("2014-06-30", "N-Q", "0001193125-14-327134", "2014-08-29", "d778190dnq.htm"),
        Filing("2014-09-30", "N-CSRS", "0001193125-14-434445", "2014-12-05", "d804519dncsrs.htm"),
        Filing("2014-12-31", "N-Q", "0001193125-15-065725", "2015-02-26", "d875299dnq.htm"),
        Filing("2015-03-31", "N-CSR", "0001193125-15-216083", "2015-06-08", "d914945dncsr.htm"),
        Filing("2015-06-30", "N-Q", "0001193125-15-306363", "2015-08-28", "d59070dnq.htm"),
        Filing("2015-09-30", "N-CSRS", "0001193125-15-396474", "2015-12-07", "d93555dncsrs.htm"),
        Filing("2015-12-31", "N-Q", "0001193125-16-480933", "2016-02-26", "d146052dnq.htm"),
        Filing("2016-03-31", "N-CSR", "0001193125-16-613829", "2016-06-06", "d184535dncsr.htm"),
        Filing("2016-06-30", "N-Q", "0001193125-16-695276", "2016-08-29", "d231174dnq.htm"),
        Filing("2016-09-30", "N-CSRS", "0001193125-16-788378", "2016-12-08", "d270106dncsrs.htm"),
        Filing("2016-12-31", "N-Q", "0001193125-17-065125", "2017-03-01", "d346678dnq.htm"),
        Filing("2017-03-31", "N-CSR", "0001193125-17-194722", "2017-06-05", "d335700dncsr.htm"),
        Filing("2017-06-30", "N-Q", "0001193125-17-271743", "2017-08-29", "d438168dnq.htm"),
        Filing("2017-09-30", "N-CSRS", "0001193125-17-359934", "2017-12-04", "d462369dncsrs.htm"),
        Filing("2017-12-31", "N-Q", "0001193125-18-063612", "2018-02-28", "d539192dnq.htm"),
        Filing("2018-03-31", "N-CSR", "0001193125-18-186572", "2018-06-07", "d544791dncsr.htm"),
        Filing("2018-06-30", "N-Q", "0001193125-18-261300", "2018-08-29", "d577177dnq.htm"),
        Filing("2018-09-30", "N-CSRS", "0001193125-18-344229", "2018-12-07", "d586605dncsrs.htm"),
        Filing("2018-12-31", "N-Q", "0001193125-19-059323", "2019-03-01", "d655820dnq.htm"),
        Filing("2019-03-31", "N-CSR", "0001193125-19-167652", "2019-06-07", "d738391dncsr.htm"),
        Filing(
            "2019-06-30",
            "NPORT-EX",
            "0001752724-19-108752",
            "2019-08-26",
            "NPORT_8256597219292071.htm",
        ),
        Filing("2019-09-30", "NPORT-P", "0001752724-19-177847", "2019-11-25", _NPORT_DOCUMENT),
        Filing("2019-12-31", "NPORT-P", "0001752724-20-038725", "2020-02-27", _NPORT_DOCUMENT),
        Filing("2020-03-31", "NPORT-P", "0001752724-20-112027", "2020-06-01", _NPORT_DOCUMENT),
        Filing("2020-06-30", "NPORT-P", "0001752724-20-176909", "2020-08-27", _NPORT_DOCUMENT),
        Filing("2020-09-30", "NPORT-P", "0001752724-20-247818", "2020-11-25", _NPORT_DOCUMENT),
        Filing("2020-12-31", "NPORT-P", "0001752724-21-040719", "2021-02-25", _NPORT_DOCUMENT),
        Filing("2021-03-31", "NPORT-P", "0001752724-21-116363", "2021-05-27", _NPORT_DOCUMENT),
        Filing("2021-06-30", "NPORT-P", "0001752724-21-186201", "2021-08-26", _NPORT_DOCUMENT),
        Filing("2021-09-30", "NPORT-P", "0001752724-21-255857", "2021-11-24", _NPORT_DOCUMENT),
        Filing("2021-12-31", "NPORT-P", "0001752724-22-046281", "2022-02-25", _NPORT_DOCUMENT),
        Filing("2022-03-31", "NPORT-P", "0001752724-22-122805", "2022-05-26", _NPORT_DOCUMENT),
        Filing("2022-06-30", "NPORT-P", "0001752724-22-193652", "2022-08-25", _NPORT_DOCUMENT),
        Filing("2022-09-30", "NPORT-P", "0001752724-22-268673", "2022-11-28", _NPORT_DOCUMENT),
        Filing("2022-12-31", "NPORT-P", "0001752724-23-039243", "2023-02-24", _NPORT_DOCUMENT),
        Filing("2023-03-31", "NPORT-P", "0001752724-23-123220", "2023-05-26", _NPORT_DOCUMENT),
        Filing("2023-06-30", "NPORT-P", "0001752724-23-191503", "2023-08-25", _NPORT_DOCUMENT),
        Filing("2023-09-30", "NPORT-P", "0001752724-23-264277", "2023-11-22", _NPORT_DOCUMENT),
        Filing("2023-12-31", "NPORT-P", "0001752724-24-043113", "2024-02-27", _NPORT_DOCUMENT),
        Filing("2024-03-31", "NPORT-P", "0001752724-24-123331", "2024-05-28", _NPORT_DOCUMENT),
        Filing("2024-06-30", "NPORT-P", "0001752724-24-194289", "2024-08-27", _NPORT_DOCUMENT),
        Filing("2024-09-30", "NPORT-P", "0001752724-24-269943", "2024-11-26", _NPORT_DOCUMENT),
        Filing("2024-12-31", "NPORT-P", "0001752724-25-043800", "2025-02-27", _NPORT_DOCUMENT),
        Filing("2025-03-31", "NPORT-P", "0001752724-25-119791", "2025-05-27", _NPORT_DOCUMENT),
        Filing("2025-06-30", "NPORT-P", "0001752724-25-210389", "2025-08-28", _NPORT_DOCUMENT),
        Filing("2025-09-30", "NPORT-P/A", "0002071691-26-015790", "2026-07-13", _NPORT_DOCUMENT),
        Filing("2025-12-31", "NPORT-P", "0002071691-26-004238", "2026-02-25", _NPORT_DOCUMENT),
        Filing("2026-03-31", "NPORT-P", "0002071691-26-012459", "2026-05-28", _NPORT_DOCUMENT),
        Filing("2026-06-30", "NPORT-P", "0002071691-26-019760", "2026-08-25", _NPORT_DOCUMENT),
    ),
    not_stocks=(
        NotStock(
            "2022-06-30",
            "Under Armour Inc",
            "904311206",
            "a line for Under Armour's Class C shares holding zero shares at zero value, "
            "so the fund held none of them that day",
        ),
    ),
)

#: Every fund the reader knows, by the symbol ``fetch`` takes.
FUNDS: Mapping[str, Fund] = {IJR.symbol: IJR, IVV.symbol: IVV}


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

    2018 splits two holdings' values with a space, "83,6 15,992" and
    "40,72 8,908", and one industry subtotal. Closing the space leaves a
    correctly grouped number, so each is read as one. Without that, the year's
    sum falls short of its printed total by $124,344,900, which is the two
    holdings together.
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


_DATE_LINE = re.compile(r"[A-Z][a-z]+ \d{1,2}, \d{4}")


def _headings(items: Sequence[tuple[str, str | tuple[str, ...]]]) -> Iterable[tuple[int, str]]:
    """Every schedule heading in an N-Q, as its position and the fund it names.

    Three shapes. Mostly a heading is the text line after one opening
    "Schedule of Investments". The 2018-06-30 N-Q prints the fund on the line
    before it and the date on the line after, so where the line after is a
    date the line before is the heading. From late 2018 it is one table row
    whose first cell opens that way and whose second names the fund.
    """
    for position, (kind, content) in enumerate(items):
        if kind == "row":
            assert isinstance(content, tuple)
            if len(content) >= 2 and content[0].lower().startswith("schedule of investments"):
                yield position, _schedule_name(content[1])
        elif position > 0:
            before_kind, before = items[position - 1]
            if before_kind != "text" or not str(before).lower().startswith(
                "schedule of investments"
            ):
                continue
            if not _DATE_LINE.fullmatch(str(content)):
                yield position, _schedule_name(str(content))
            elif position > 1 and items[position - 2][0] == "text":
                yield position - 2, _schedule_name(str(items[position - 2][1]))


def _page_footer(row: tuple[str, ...]) -> bool:
    """Whether a row is a shareholder report's running footer and page number.

    Nine of IVV's shareholder reports from 2010-09-30 to 2019-03-31 end each
    odd page inside a schedule with a row reading "SCHEDULES OF INVESTMENTS"
    and the page number, letter-spaced in 2019. It has a number in its last
    cell, so it would otherwise be refused as a row no year printed. The even
    page's footer leads with its number and is passed already, as a row whose
    last cell is not one.
    """
    return len(row) == 2 and "".join(row[0].split()).upper() == "SCHEDULESOFINVESTMENTS"


def _name_start(cell: str) -> bool:
    """Whether a row of one cell is the start of a name the next row finishes.

    The 2010-09-30 N-CSRS wraps two names across two table rows, "E.I. du Pont
    de Nemours" above "and Co." and "Discovery" above "Communications Inc.
    Series A", and the first row carries no numbers. Every other row of one
    cell under common stocks, in all of IVV's HTML schedules and IJR's N-Q
    years, is an industry heading printing its percentage of net assets, an
    industry heading carried onto a new page with "(continued)", or a subtotal.
    One subtotal in IVV's 2011-12-31 N-Q prints as "7585,592,127" and passes
    this test, and an industry heading follows it, so no name takes it.
    """
    return "%" not in cell and not cell.endswith("(continued)") and _number(cell) is None


def parse_nq(document: bytes, schedule_names: Sequence[str]) -> Schedule:
    """The fund's rows under common stocks in one HTML schedule, with the total it prints.

    The fund's section opens at its first schedule heading. Rows are read from
    its "COMMON STOCKS" line to its "Total Common Stocks" line, and every row
    holding a name, a share count and a value is a holding. A row of one number
    is an industry subtotal and a row of text is a heading, so both are passed,
    except where :func:`_name_start` says the text is a name the row below
    finishes. Footnote markers are dropped: a ``<sup>`` by :class:`_Rows`, and a
    trailing run such as "(a)(b)" here.

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
    name_start = ""
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
        held_over, name_start = name_start, ""
        if len(content) == 1:
            name_start = first if _name_start(first) else ""
            continue
        if _page_footer(content) or numbers[-1] is None:
            continue
        if len(content) == 3 and numbers[0] is None and numbers[1] is not None:
            name = _FOOTNOTES.sub("", f"{held_over} {first}".strip()).strip()
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


#: The forms whose schedule is HTML, read by :func:`parse_nq`. An NPORT-EX is
#: the exhibit an N-PORT files in HTML, which for IVV's 2019-06-30 stands alone.
_HTML_FORMS = ("N-Q", "N-CSR", "N-CSRS", "NPORT-EX")


def parse(document: bytes, fund: Fund, filing: Filing) -> Schedule:
    """The schedule one filing holds, read by the parser its form needs."""
    if filing.form in _HTML_FORMS:
        return parse_nq(document, fund.schedule_names)
    if filing.form in ("NPORT-P", "NPORT-P/A"):
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
    write different bytes to an existing file, or a different line for a
    fund's accession the index already holds, refuses and names both hashes.
    The fund is part of that key because one N-Q holds every fund in the
    trust, so IJR's and IVV's December N-Q share an accession. A schedule
    whose rows do not sum to the total it prints is refused too, because that
    is a parse that read the wrong rows, and so is a filing the list skips.
    """
    if filing.skipped:
        raise FilingRefused(f"{fund.symbol} {filing.report_date} is skipped: {filing.skipped}")
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
    held = next(
        (
            line
            for line in entries
            if (line.fund, line.accession) == (fund.symbol, filing.accession)
        ),
        None,
    )
    if held is not None and held != entry:
        raise FilingRefused(
            f"the index already records {fund.symbol} {filing.accession} "
            f"with file sha256 {held.sha256} "
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
    except (OSError, http.client.HTTPException) as failure:
        # URLError and a timeout are both OSErrors, and so is a connection reset
        # while the body is read. A body cut short is an HTTPException.
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
    differs is refused before anything is parsed. A filing the list skips is
    not downloaded.
    """
    contact = user_agent() if contact is None else contact
    held = {(entry.fund, entry.accession): entry for entry in read_index(filings_dir)}
    written = []
    with tempfile.TemporaryDirectory(prefix="fund_holdings_") as scratch:
        for number, filing in enumerate(f for f in fund.filings if not f.skipped):
            if number:
                pause(REQUEST_SPACING_SECONDS)
            content = download(document_url(filing), contact)
            known = held.get((fund.symbol, filing.accession))
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
    separate line. A filing the list skips has no holdings file, so it is
    refused with the reason rather than read as a missing file.
    """
    if filing.skipped:
        raise ValueError(
            f"{fund.symbol} {filing.report_date} has no holdings file: {filing.skipped}"
        )
    rows = read_holdings(holdings_path(fund, filing, filings_dir))
    excluded = {
        (entry.name, entry.cusip)
        for entry in fund.not_stocks
        if entry.report_date == filing.report_date
    }
    return tuple(row for row in rows if (row.name, row.cusip) not in excluded)


_PUNCTUATION = re.compile(r"[^\w\s]")
# A state appended after a slash, as 2015 prints "UniFirst Corp./MA". Exactly
# two letters and then the end of a word, so "RE/MAX" keeps its name.
_STATE_SUFFIX = re.compile(r"/[a-z]{2}(?![a-z])", re.IGNORECASE)
_SHARE_CLASS = re.compile(r"\b(?:class|series) ([a-z])\b|\bnvs\b")
_SPELLINGS = {"cos": "companies"}


def normalised_name(name: str) -> str:
    """A name reduced to what two filings spell the same way.

    Case, punctuation, the registered-trademark sign and a curly apostrophe
    against a straight one all go. A full stop is deleted rather than spaced,
    so "U.S." and "US" agree. Four restylings the filings make between years go
    too: a state after a slash such as "/IL", the word "The", "&" against
    "and", and "Cos" against "Companies". Words stay otherwise, a share-class
    suffix such as "Class A" among them, because that is what tells a fund's
    two lines in one company apart.
    """
    text = name.replace("’", "'").replace("®", " ").replace(".", "")
    text = _STATE_SUFFIX.sub(" ", text).replace("&", " and ").casefold()
    words = _PUNCTUATION.sub(" ", text).split()
    return " ".join(_SPELLINGS.get(word, word) for word in words if word != "the")


def _without_share_class(name: str) -> str:
    """A normalised name with "Class A", "Series A" and "NVS" taken out."""
    return _squash(_SHARE_CLASS.sub(" ", normalised_name(name)))


def _share_classes(name: str) -> set[str]:
    """The class letters a name prints, so "Class A" and "Series A" agree."""
    return {letter for letter in _SHARE_CLASS.findall(normalised_name(name)) if letter}


def _two_securities(current: Holding, previous: Holding) -> bool:
    """Whether the two rows' identifiers say they are different securities.

    Two CUSIPs that disagree do. Where neither row carries a CUSIP, two ISINs
    that disagree do too: Nabors's Bermuda shares carry no CUSIP, and their
    ISIN changed with the 1-for-50 reverse split between 2019 and 2020.
    """
    if current.cusip and previous.cusip:
        return current.cusip != previous.cusip
    if not current.cusip and not previous.cusip and current.isin and previous.isin:
        return current.isin != previous.isin
    return False


def _classes_disagree(current: Holding, previous: Holding) -> bool:
    """Whether both names print a class letter and the letters differ."""
    mine, theirs = _share_classes(current.name), _share_classes(previous.name)
    return bool(mine and theirs and mine != theirs)


Pairs = list[tuple[Holding | None, str | None]]


def _pair(
    current: Sequence[Holding],
    previous: Sequence[Holding],
    key: Callable[[Holding], str],
    allowed: Callable[[Holding, Holding], bool],
    how: str,
    pairs: Pairs,
) -> Pairs:
    """One pass of :func:`link` over the members ``pairs`` leaves unpaired.

    A pairing is kept only when it is one to one. A key two previous rows
    share, or a previous row two current members both reach, leaves every
    member involved unpaired rather than guessed. A previous row an earlier
    pass already took is not offered again.
    """
    taken = {id(row) for row, _ in pairs if row is not None}
    keys: dict[str, list[int]] = {}
    for number, row in enumerate(previous):
        if id(row) not in taken and key(row):
            keys.setdefault(key(row), []).append(number)

    proposed: list[int | None] = []
    for row, (paired, _) in zip(current, pairs, strict=True):
        found = keys.get(key(row), []) if paired is None and key(row) else []
        candidates = [number for number in found if allowed(row, previous[number])]
        proposed.append(candidates[0] if len(candidates) == 1 else None)

    reached: dict[int, int] = {}
    for target in proposed:
        if target is not None:
            reached[target] = reached.get(target, 0) + 1
    return [
        (previous[target], how) if target is not None and reached[target] == 1 else pair
        for target, pair in zip(proposed, pairs, strict=True)
    ]


def link(current: Sequence[Holding], previous: Sequence[Holding]) -> Pairs:
    """Pair each current member with the same holding in the previous filing.

    Each pair comes with how it was found. Three passes, each reaching only
    what the ones before it left.

    1. ``cusip``, where both rows carry the same one. It runs first so that a
       row with no CUSIP cannot take a previous row by name from the row whose
       CUSIP matches it.
    2. ``name``, on the normalised names with the share-class suffix kept,
       which is what keeps Central Garden's two N-Q lines apart.
    3. ``name without class``, on the names with the suffix taken out. The 2018
       N-Q prints "Lithia Motors Inc., Class A" where the 2019 N-PORT prints
       "Lithia Motors Inc", for a company IJR holds one line of. A pair whose
       names print two different class letters is refused, and the one-to-one
       rule keeps Central Garden's two lines unpaired once their suffixes go.

    Neither name pass pairs two rows whose identifiers say they are different
    securities. A member no pass pairs is left unpaired.
    """
    pairs: Pairs = [(None, None)] * len(current)
    pairs = _pair(current, previous, lambda row: row.cusip, lambda a, b: True, "cusip", pairs)
    pairs = _pair(
        current,
        previous,
        lambda row: normalised_name(row.name),
        lambda a, b: not _two_securities(a, b),
        "name",
        pairs,
    )
    return _pair(
        current,
        previous,
        lambda row: _without_share_class(row.name),
        lambda a, b: not _two_securities(a, b) and not _classes_disagree(a, b),
        "name without class",
        pairs,
    )


def _price(holding: Holding) -> Decimal | None:
    """Value over shares, or ``None`` where a zero share count leaves it undefined."""
    shares = Decimal(holding.shares)
    return Decimal(holding.value) / shares if shares else None


def place(fund: Fund, report_date: str, filings_dir: Path | None = None) -> list[Placement]:
    """Each member of one filing, with its rough calendar-year return where it can be had.

    The return is value over shares in this filing, divided by the same in the
    filing linked to it, less one. A member the link leaves unpaired cannot be
    placed. Nor can a linked one whose price is undefined, which is a zero share
    count in either filing or a zero value in the earlier one, so it keeps its
    link and carries no return. The first filing in the list has nothing before
    it, so it is refused rather than reported as wholly unplaced. The filing
    before is the one before in the list, a year for IJR and a quarter for IVV,
    and one the list skips refuses with its reason.

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
            continue
        now, then = _price(holding), _price(linked)
        change = now / then - 1 if now is not None and then else None
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
