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

Verified bytes are not the whole of a series being safe to compute across. A
committed vintage can change scale partway through, and the record says
nothing about it, so :func:`scale_breaks` reads each series against itself day
over day and :func:`refuse_window_crossing_a_break` stops a run whose window
spans one. Both live here beside the parse, because that is what they need.
Two days of ``ko_chan.csv`` are flagged today and nothing computes across
them, which is what says the guard reports a real thing rather than a
hypothetical.
"""

from __future__ import annotations

import io
import math
import warnings
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from chan.vintage import VintageEntry, read_manifest, read_vintage, resolve_vintage

#: A day-over-day price ratio further than this from 1, in log terms, is a scale break.
#:
#: Computed from 1.6 rather than typed out, because a price ratio is
#: multiplicative and a pair of endpoints is not. ``[0.6, 1.6]`` is asymmetric
#: by 0.0408 in log terms, so a move of 0.62 would pass while its reciprocal
#: 1.613 would flag, and the guard would answer differently on a series and on
#: the same series reversed.
#:
#: The number is fitted to what the manifest holds. Measured at ``e9860fb``
#: over the eight committed vintages with the two ``ko_chan.csv`` breaks
#: excluded, the widest legitimate move is 0.7521, Black Monday in that same
#: file, and the widest the other way is 1.2654, so every real move sits inside
#: ``|log r| <= 0.2849``. The two breaks sit at 0.6833 and 0.6838. Anything
#: between those two leaves the breaks caught and Black Monday alone, which is
#: why ``log(1.4)`` and ``log(1.35)`` would also serve and ``log(1.3)`` would
#: not.
#:
#: It catches a 2:1 at 0.5000, a 3:1 at 0.3333 and a 1:10 reverse at 10.0, and
#: it misses a 3:2 at 0.6667, a 5:4 at 0.8000 and a 1:1.5 reverse at 1.5. So it
#: is a floor on known contamination rather than a guarantee. A volatile
#: small-cap moves 0.75 on ordinary news, so what carries forward to a ninth
#: vintage is the derivation rather than the number: measure the envelope over
#: what the manifest holds and leave a margin.
#:
#: The sibling ``trading-strategies`` repo's ``[0.5, 2.0]`` is deliberately not
#: ported. Both KO breaks sit inside it, at 0.5050 and 0.5047, because it runs
#: on already-adjusted closes where a correct split leaves no cliff at all.
SCALE_BREAK_BOUND = math.log(1.6)


class WindowCrossesScaleBreak(Exception):
    """A run's window spans a day on which a committed series changed scale.

    Separate from :class:`chan.vintage.VintageUnavailable`, which says a run
    could not read a vintage. This one says the vintage is present, verified
    and correct, and the window read across a day where its own scale moved.
    Sharing that exception would hand the next reader a docstring describing
    something that did not happen, which is the argument
    :class:`chan.vintage.VintageRefused` already carries beside it.

    The message names the dates that were crossed and which vintage carried
    them. It does not suggest a clean window, because the dates are the fact
    and the window is advice a reader derives from them in one step.
    """


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


def scale_breaks(closes: pd.Series, *, bound: float = SCALE_BREAK_BOUND) -> list[pd.Timestamp]:
    """Every day in ``closes`` on which the series changed scale, in date order.

    A scale break is a day-over-day price ratio too far from 1 to be a price
    move, so what it says is that the series does not mean the same thing on
    both sides of the day it names. The date reported is the later of the two
    days, which is the day the move lands on, so a window starting there does
    not contain the break and a window one day wider does.

    The comparison is on the log of the ratio against :data:`SCALE_BREAK_BOUND`,
    because a ratio is multiplicative and a pair of endpoints is not.

    It sorts first. :func:`_parse_close` already does, so every series reaching
    here through :func:`load_vintage` arrives sorted, but this takes a bare
    series from any caller and a public answer that depends on how the caller
    built its index is not an answer. The recorder writes rows in the order it
    is handed them, on purpose, so a vendor answering newest-first produces a
    vintage committed backwards, and differencing that reports every ratio
    inverted.

    A ratio that is not a finite number is reported rather than skipped. "No
    break" and "could not tell" must not be the same answer, which is the rule
    :func:`chan.vintage._unrecorded` already carries. Three inputs reach it. A
    NaN close, which :func:`_parse_close` produces from an unparseable value,
    makes both ratios touching it NaN, and ``NaN > bound`` is ``False``, so a
    comparison written the other way round would report a clean series and say
    nothing. A zero close, which ``_validated_rows`` allows because a vendor
    returns one for a halted day, makes the ratios ``0.0`` and ``inf``. A
    negative close makes the log NaN out of two finite numbers.
    """
    closes = closes.sort_index()
    values = closes.to_numpy(dtype=float)
    if values.size < 2:
        return []
    with warnings.catch_warnings():
        # A zero close divides by zero and a negative one takes the log of a
        # negative, and numpy warns on both. Both are flagged on the line
        # below rather than skipped, so the warning reports something already
        # handled. `_parse_close` suppresses its own expected one the same way.
        warnings.simplefilter("ignore", RuntimeWarning)
        ratios = values[1:] / values[:-1]
        magnitudes = np.abs(np.log(ratios))
    # Written as the negation of the passing case rather than as `> bound`, so
    # a NaN magnitude flags instead of quietly passing.
    return list(closes.index[1:][~(magnitudes <= bound)])


def manifest_scale_breaks(data_dir: Path | None = None) -> dict[str, list[pd.Timestamp]]:
    """Every committed vintage that changes scale inside itself, keyed by its path.

    It iterates :func:`chan.vintage.read_manifest` rather than a list of the
    eight vintages this repo holds today, so a ninth is covered on the day it
    is recorded rather than on the day somebody remembers to extend a list.

    A vintage with nothing to report is left out, because what a caller wants
    is what was found. The key is the entry's ``path`` and not the entry, since
    an entry carries a field that is not hashable and keying by one reaches an
    operator as a traceback, which is
    [issue 93](https://github.com/l3a0/quantitative-trading/issues/93).

    It calls :func:`_parse_close` directly rather than :func:`load_close`,
    which would resolve through the manifest each entry it was just handed.
    """
    found = {}
    for entry in read_manifest(data_dir):
        closes = _parse_close(read_vintage(entry, data_dir=data_dir), entry.symbol)
        flagged = scale_breaks(closes)
        if flagged:
            found[entry.path] = flagged
    return found


def refuse_window_crossing_a_break(
    legs: Sequence[tuple[VintageEntry, pd.Series]],
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    bound: float = SCALE_BREAK_BOUND,
) -> None:
    """Stop a run whose window spans a scale break in one of the series it read.

    Each leg is its own ``(entry, closes)`` pair, clipped here to
    ``[start, end]`` on its own calendar and run through :func:`scale_breaks`.
    Running the guard per leg is what makes a flag table unnecessary: the ratio
    computation over a clipped series is already the test for whether the
    window spans the break, and running it on each leg is already the union
    across them.

    Each leg is clipped on its own trading days rather than on the joined ones.
    An inner join and a ``dropna`` drop days one leg traded and the other did
    not, which widens the gap the ratio is taken across. Measured on KO and PEP
    at ``e9860fb``, the join drops 1 of KO's 7,836 rows in the window.

    The window is the index a caller is about to return and not the ``start``
    and ``end`` it asked for. ``aligned_closes("KO", "PEP", chan=True,
    start="1962-01-01")`` hands back 1977-01-03 onward, because the
    intersection with PEP is narrower than the argument, and a check reading
    the argument would refuse a run that reads nothing wrong.

    It is all or nothing at this boundary, which is right for a single-window
    run and not for a rolling one. :func:`chan.regime_figure.make_regime_figure`
    rolls inside one :func:`chan.pair_cointegration.aligned_closes` call, so a
    flagged leg withdraws the whole figure rather than the windows that cross.
    Nothing needs the other behaviour today, since that function hard-codes GLD
    and GDX and neither is flagged, and :func:`scale_breaks` underneath returns
    the dates either way.
    """
    crossed = []
    for entry, closes in legs:
        clipped = closes.loc[(closes.index >= start) & (closes.index <= end)]
        flagged = scale_breaks(clipped, bound=bound)
        if flagged:
            crossed.append((entry, flagged))
    if not crossed:
        return
    named = "; ".join(
        f"{entry.path} on {', '.join(str(day.date()) for day in flagged)}"
        for entry, flagged in crossed
    )
    raise WindowCrossesScaleBreak(
        f"the window {start.date()} to {end.date()} crosses a scale break: {named}. "
        f"A day-over-day close ratio further from 1 than {math.exp(bound):g} is the series "
        f"changing scale rather than the price moving, and a number computed across one is "
        f"fiction. Read a window that does not span the dates named."
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
