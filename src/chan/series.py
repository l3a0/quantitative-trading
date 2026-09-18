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

:func:`aligned_closes` joins a pair on its common trading days and hands
back both manifest entries, so this module reads two series as well as one.
It sat in :mod:`chan.pair_cointegration` until
[issue 122](https://github.com/l3a0/quantitative-trading/issues/122), and it
is here for the reason the paragraph above gives for the parse.
"""

from __future__ import annotations

import io
import math
import warnings
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from chan.vintage import VintageEntry, read_vintage, resolve_vintage

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

    The two answers come back in one list, because what this function is asked
    is which days a run must not compute across and both kinds are that.
    :func:`refuse_window_crossing_a_break` tells them apart, because a refusal
    names the state it found and those two have different fixes.
    """
    days, magnitudes = _ratio_magnitudes(closes)
    # Written as the negation of the passing case rather than as `> bound`, so
    # a magnitude that is not a number flags instead of quietly passing.
    return list(days[~(magnitudes <= bound)])


def _ratio_magnitudes(closes: pd.Series) -> tuple[pd.DatetimeIndex, np.ndarray]:
    """Each day paired with how far its move from the day before is from 1, in log terms.

    The day is the later of the two, which is the day the move lands on. Both
    :func:`scale_breaks` and :func:`refuse_window_crossing_a_break` are built on
    this, so the sort, the suppression and the choice of which day to name exist
    once. Writing the arithmetic twice is how the two would come to disagree
    about one series.

    A magnitude that is not a finite number is handed back as it is, because the
    refusal needs to tell a series that changed scale apart from one whose scale
    could not be read, and those two are different facts with different fixes.
    """
    closes = closes.sort_index()
    values = closes.to_numpy(dtype=float)
    if values.size < 2:
        return closes.index[:0], np.empty(0, dtype=float)
    with warnings.catch_warnings():
        # A zero close divides by zero and a negative one takes the log of a
        # negative, and numpy warns on both. Neither is skipped, so the warning
        # reports something already handled. `_parse_close` suppresses its own
        # expected one the same way.
        warnings.simplefilter("ignore", RuntimeWarning)
        ratios = values[1:] / values[:-1]
        return closes.index[1:], np.abs(np.log(ratios))


def refuse_window_crossing_a_break(
    legs: Sequence[tuple[VintageEntry, pd.Series]],
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> None:
    """Stop a run whose window spans a scale break in one of the series it read.

    Each leg is its own ``(entry, closes)`` pair, clipped here to
    ``[start, end]`` on its own calendar and differenced. Running the guard per
    leg is what makes a flag table unnecessary: the ratio computation over a
    clipped series is already the test for whether the window spans the break,
    and running it on each leg is already the union across them.

    The message names which of two states it found, rather than calling both a
    scale break. A series that changed scale and a series whose scale could not
    be read are different facts with different fixes, which is the rule
    ``tests/test_series.py`` states for the four refusals already here. The
    second is reachable through a run whose own frame drops the row: an inner
    join and a ``dropna`` discard a NaN close, so the computed rows can be clean
    while the day beside them says nothing about whether the scale held. That
    day is refused rather than passed over, because the guard cannot rule a
    break out there and "no break" and "could not tell" must not be the same
    answer.

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
    rolls inside one :func:`aligned_closes` call, so a flagged leg withdraws
    the whole figure rather than the windows that cross. Nothing needs the
    other behaviour today, since that function hard-codes GLD and GDX and
    neither is flagged, and :func:`scale_breaks` underneath returns the dates
    either way.
    """
    moved, unreadable = [], []
    for entry, closes in legs:
        clipped = closes.loc[(closes.index >= start) & (closes.index <= end)]
        days, magnitudes = _ratio_magnitudes(clipped)
        readable = np.isfinite(magnitudes)
        # A magnitude that is not a number already fails `<= bound`, so the two
        # sets below partition the flagged days rather than overlapping.
        if (~readable).any():
            unreadable.append((entry, days[~readable]))
        changed = readable & ~(magnitudes <= SCALE_BREAK_BOUND)
        if changed.any():
            moved.append((entry, days[changed]))
    if not moved and not unreadable:
        return
    said = [f"{entry.path} changes scale on {_dates(days)}" for entry, days in moved]
    said += [
        f"{entry.path} has no readable day-over-day move on {_dates(days)}"
        for entry, days in unreadable
    ]
    why = []
    if moved:
        why.append(
            f"A day-over-day close ratio further from 1 than "
            f"{math.exp(SCALE_BREAK_BOUND):g} is the series changing scale rather than the "
            f"price moving, and a number computed across one is fiction."
        )
    if unreadable:
        why.append(
            "A close that is not a finite number leaves the scale on both sides of it unknown, "
            "and no break and could not tell are not the same answer."
        )
    raise WindowCrossesScaleBreak(
        f"the window {start.date()} to {end.date()} cannot be computed across: "
        f"{'; '.join(said)}. {' '.join(why)} Read a window that does not span the dates named."
    )


def aligned_closes(
    a: str,
    b: str,
    *,
    start: str | None = None,
    end: str | None = None,
    unadjusted: bool = False,
    chan: bool = False,
    data_dir: Path | None = None,
) -> pd.DataFrame:
    """Inner-join two tickers' closes on their common trading days.

    Optionally clipped to the inclusive window ``[start, end]``, both
    ``YYYY-MM-DD``. ``chan=True`` loads both legs from Chan's committed
    companion data. Each leg is resolved through the manifest and verified
    against the sha256 recorded there before it is read.

    The two entries come back on ``DataFrame.attrs["vintages"]``, in leg order.
    A report that names which vintage produced its numbers needs them, and the
    frame drops everything the lookup knew, so they ride along rather than
    being resolved a second time to a possibly different answer.

    There is no ``dated`` argument here on purpose. One date applied to both
    legs is wrong on the default run, whose two vintages were downloaded 72
    days apart, so a pair that needs to name its dates needs one per leg. That
    is [issue 69](https://github.com/l3a0/quantitative-trading/issues/69).
    Until it lands, an ambiguous pair stops the run and names the candidates.

    It lives beside the one-leg readers rather than in a replication, because
    every experiment that reads a pair needs this join, and importing a
    Chapter 7 replication to open two files is what this module's docstring
    decided against for the parse. It was in :mod:`chan.pair_cointegration`
    until [issue 122](https://github.com/l3a0/quantitative-trading/issues/122)
    moved it here.

    **Where this came from.** ``search/pair_cointegration.py`` in the sibling
    ``trading-strategies`` repo, at commit ``b27222b``, landed in
    ``chan.pair_cointegration`` here in ``ce3f757``. The port changed nothing
    but the formatting and the docstring. Everything that separates it from
    the sibling's version was added here afterwards, in three changes.

    1. A ``data_dir`` argument, so a test reads a copied tree rather than the
       committed ``data/``.
    2. ``load_close`` became ``load_vintage`` for each leg, which is what
       resolves the pair through the manifest and verifies its bytes, and what
       gives the two entries this function hands back on ``attrs``.
    3. The scale-break refusal after the clip.

    So diff ``b27222b:search/pair_cointegration.py`` against
    ``ce3f757:src/chan/pair_cointegration.py`` to read the port, with
    docstrings stripped from both sides because they are most of it. Neither
    side is this file, and diffing the sibling against it instead compares a
    cointegration script with a reader. The three above are the whole of what
    happened after the port.
    """
    entry_a, close_a = load_vintage(a, unadjusted=unadjusted, chan=chan, data_dir=data_dir)
    entry_b, close_b = load_vintage(b, unadjusted=unadjusted, chan=chan, data_dir=data_dir)
    joined = pd.concat([close_a, close_b], axis=1, join="inner").dropna()
    joined.columns = [a.upper(), b.upper()]
    if start is not None:
        joined = joined.loc[joined.index >= pd.Timestamp(start)]
    if end is not None:
        joined = joined.loc[joined.index <= pd.Timestamp(end)]
    if not joined.empty:
        # The clip is what decides whether a scale break is inside the window,
        # so the check runs here and not in `load_vintage`. The KO vintage
        # spans 1962 to 2008 and carries two breaks in the 1960s, and it
        # arrives here whole: refusing it at load time would stop the KO/PEP
        # replication, whose window starts in 1977 and is correct. Each leg is
        # handed over unclipped and cut to its own trading days inside the
        # check, rather than read off `joined`, whose inner join drops days one
        # leg traded and the other did not and so widens the gap a ratio is
        # taken across.
        refuse_window_crossing_a_break(
            ((entry_a, close_a), (entry_b, close_b)),
            start=joined.index[0],
            end=joined.index[-1],
        )
    joined.attrs["vintages"] = (entry_a, entry_b)
    return joined


def _dates(days: pd.DatetimeIndex) -> str:
    """Days as the ISO dates a refusal prints, which is what a reader greps for."""
    return ", ".join(str(day.date()) for day in days)


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
