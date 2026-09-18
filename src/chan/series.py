"""Read a committed vintage as a date-indexed series, after checking it is the one.

A run reads a committed vintage or it does not run. Before it reads one, it
confirms the file is the file ``data/vintages.jsonl`` describes, because a
number computed from bytes nobody recorded is a number nobody can check.

This module is the reading half of :mod:`chan.vintage`. That one resolves an
entry and verifies its bytes on the standard library alone, which is what keeps
its own suite at 0.09 s. Parsing a series costs pandas, so the parse lives
here instead of there. It does not live in :mod:`chan.pair_cointegration`
either, which is a Chapter 7 replication, and every experiment that reads a
series would then import a chapter to open a file.

Two sources, told apart by what the manifest records rather than by a filename.

- The yfinance set, the default. ``adjusted`` carries Yahoo's
  dividend-adjusted close, and ``raw`` carries the as-traded close when
  ``unadjusted=True``.
- Chan's book-companion set, with ``chan=True``. Those entries carry the
  vendor ``chan-xls`` and are the adjusted-close column of Chan's own ``.xls``
  for that symbol.

The basis decides the levels. GLD pays no distributions, so its adjusted close
already equals its raw close, while GDX's dividends put today's adjusted
history about 15% below raw. Chan's 2007-vintage adjusted close was near raw,
since GDX had paid little by then, so raw is the closest modern proxy for
reproducing the book. That is why ``--ch7``, ``--ch3`` and ``--unadjusted``
read it.

The eight committed vintages are frozen on purpose. Nothing regenerates them,
and the pinned tests freeze these exact bytes against each source's drifting
vintage, so a re-download would fail the replication rather than pass it
quietly. That is a fact about the data rather than about this code, which is
why a manifest lookup does not say it and this paragraph does.
"""

from __future__ import annotations

import io
import warnings
from pathlib import Path

import pandas as pd

from chan.vintage import VintageEntry, read_vintage, resolve_vintage


def close_identity(ticker: str, *, unadjusted: bool = False, chan: bool = False) -> tuple[str, str]:
    """The vendor and price basis a ticker's flags name, as the manifest spells them.

    ``unadjusted`` is ignored when ``chan`` is set, which is the promise
    ``load_close`` has carried since before the manifest existed. Chan's
    workbooks hold one price column per symbol and it is the adjusted one, so
    ``(chan-xls, raw)`` names no entry and never will. Refusing instead would
    turn an argument the caller was told is ignored into a refusal naming a
    vintage nobody meant to ask for.
    """
    if chan:
        return "chan-xls", "adjusted"
    return "yfinance", "raw" if unadjusted else "adjusted"


def load_vintage(
    ticker: str,
    *,
    unadjusted: bool = False,
    chan: bool = False,
    dated: str | None = None,
    data_dir: Path | None = None,
) -> tuple[VintageEntry, pd.Series]:
    """The manifest entry a ticker's flags name, and the series its bytes hold.

    ``dated`` tells two downloads of one series apart. It is compared against
    whichever date field the entry carries, so it names a download and it names
    one of Chan's workbook columns, which carry a saved date instead. Left out,
    the flags must select exactly one entry or the run stops and names the
    candidates.

    ``data_dir`` defaults to :data:`chan.paths.DATA_DIR`. A test passes its own
    directory, the way :func:`chan.vintage.record_vintage` takes one, so a case
    that needs a corrupt vintage builds one somewhere that is not the committed
    ``data/``.

    The entry comes back with the series because a report that names the
    vintage it read needs both, and looking the entry up a second time would
    give a second answer to one question.
    """
    vendor, price_basis = close_identity(ticker, unadjusted=unadjusted, chan=chan)
    entry = resolve_vintage(
        vendor=vendor,
        symbol=ticker.upper(),
        price_basis=price_basis,
        dated=dated,
        data_dir=data_dir,
    )
    return entry, _parse_close(read_vintage(entry, data_dir=data_dir), ticker)


def load_close(
    ticker: str,
    *,
    unadjusted: bool = False,
    chan: bool = False,
    dated: str | None = None,
    data_dir: Path | None = None,
) -> pd.Series:
    """A ticker's daily close from a verified vintage, date-indexed.

    :func:`load_vintage` with the entry dropped, for a caller that wants the
    numbers and not the provenance. A caller that wants both calls that one, so
    the entry is not also smuggled out on ``Series.attrs``: a second way to
    reach it would be a second thing to keep true.
    """
    return load_vintage(ticker, unadjusted=unadjusted, chan=chan, dated=dated, data_dir=data_dir)[1]


def vintage_line(entry: VintageEntry) -> str:
    """One entry as a report prints it: which file, from where, and when.

    The verb matters. Four committed vintages carry a saved date because they
    are columns lifted from Ernest Chan's workbooks and nothing was fetched on
    that day, so printing one under the word "downloaded" would state a wrong
    fact about where the series came from.

    It lives beside the readers rather than in a replication, because every
    experiment that reads a vintage has to name it, and importing a chapter to
    format a line is the thing this module's docstring decided against for the
    parse. It was ``_vintage_line`` in :mod:`chan.pair_cointegration` until
    [issue 14](https://github.com/l3a0/quantitative-trading/issues/14) needed a
    second caller.
    """
    return (
        f"{entry.path}   {entry.vendor} {entry.price_basis}, {entry.obtained_verb} {entry.obtained}"
    )


def _parse_close(payload: bytes, ticker: str) -> pd.Series:
    """The series held in ``payload``, which is the buffer that was hashed.

    Parsing from the bytes rather than reopening the path is what makes one
    read answer both questions. Replacing the file between the hash and the
    parse then cannot change what comes back.

    The eight committed vintages carry yfinance's three-row header
    (Price/Close, Ticker/SYM, Date/blank) and a recorded one carries a single
    ``Date,Close``. Rather than hard-code a skip count, every leading row whose
    first field is not a parseable date is dropped, so either shape loads.
    """
    raw = pd.read_csv(io.BytesIO(payload), header=None, names=["date", "close"], usecols=[0, 1])
    with warnings.catch_warnings():
        # The header rows ("Date", "Ticker") do not parse as dates, and coerce
        # drops them to NaT. pandas warns about the mixed formats, expected here.
        warnings.simplefilter("ignore", UserWarning)
        dates = pd.to_datetime(raw["date"], errors="coerce")
    mask = dates.notna()
    series = pd.Series(
        pd.to_numeric(raw["close"][mask], errors="coerce").to_numpy(dtype=float),
        index=pd.DatetimeIndex(dates[mask]),
        name=ticker.upper(),
    )
    return series.sort_index()
