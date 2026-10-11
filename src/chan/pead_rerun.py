"""Example 7.2 rerun on EDGAR's announcement calendar and the archive's prices.

[Issue 251](https://github.com/l3a0/quantitative-trading/issues/251) asks
whether the post-earnings drift Chan reports survives a calendar nobody
hand-collected and prices from another vendor. :mod:`chan.pead` reproduces his
figures on his own files, which Entry 12 of
[docs/replication-log.md](../../docs/replication-log.md) records. This module
runs the same rule, :func:`chan.pead.pead`, unchanged, on four things that can
differ from his: the stocks, the calendar, the vendor and the price basis.

**The registration.** The comparison was registered on issue 251 before any
number on these sources was seen, in the comment
https://github.com/l3a0/quantitative-trading/issues/251#issuecomment-6104973515.
Every run is **exploratory**, because the plan audit had already spent part of
the sample measuring how much of the return each vendor could serve. What the
registration fixes is followed here exactly. What it left open, and what a
reader could take for a departure from it, is named under "Deviations and
choices" below.

1. The rule is :func:`chan.pead.pead`, with a lookback of 90, an entry of 0.5,
   a denominator of 30, 252-day annualisation, book two's ``smartstd`` and no
   costs.
2. The days are the flag file's 330, from 2011-01-03 to 2012-04-24. Prices
   are cut to them before any gap is taken, as ``pead.m`` cuts them.
3. Each run prints the five figures ``pead.m`` prints, the trades taken and
   the busiest day.

**The universes.** ``ALL`` is Chan's 497 stocks. ``CAL`` is the stocks whose
CIK passed its check in ``research/filings/earnings/tickers.csv``, ``PX`` the
stocks whose archive series passed its check there, and ``U`` both.
:mod:`chan.earnings_filings` says what each check reads.

**The calendars.** Both read the Eastern acceptance time in
``research/filings/earnings/index.jsonl``, and both skip an ``8-K/A``. Several
filings on one day make one flag. A trading day is a day the committed raw SPY
vintage holds a close, which is :func:`chan.sp500_panel.calendar`.

1. **R1, the primary calendar**, uses only what EDGAR showed before the open.
   A filing accepted before 09:30 on a trading day flags that day. One
   accepted at 16:00 or later, or on a day the market was shut, flags the
   next trading day. One accepted from 09:30 to 15:59:59 flags nothing,
   because the gap from the previous close to the open came before it. A
   half-day session still closes at 16:00 here, since the registration
   words the rule by the clock.
2. **R5, the secondary calendar**, changes two things. A filing accepted on a
   later date than its ``reportDate`` flags the trading day after
   ``reportDate``, and one accepted during the session flags that same day.
   R5 reads what a trader did not have before the open. It was chosen because
   it matched Chan's flags best on a 32-stock sample, so it is the calendar
   nearest his, never a tradable one.

**The runs.**

| Run | Stocks | Prices | Flags |
| --- | --- | --- | --- |
| A | ALL | Chan's | Chan's |
| A_CAL, A_PX, A_U | CAL, PX, U | Chan's | Chan's |
| B1, B5 | CAL | Chan's | R1, R5 |
| C | PX | Alpha Vantage, adjusted | Chan's |
| D | PX | Alpha Vantage, raw | Chan's |
| E1, E5 | U | Alpha Vantage, adjusted | R1, R5 |

The adjusted open is the raw open times that day's adjusted close over its raw
close, since the vendor adjusts only the close. Chan's file is adjusted, so
the adjusted runs are the like-for-like ones.

**The attribution** is read from the arithmetic annual return and the Sharpe
ratio. The universe effect is A_U − A, and the calendar, vendor and basis
effects are B1 − A_CAL, C − A_PX and D − C. Whatever E1 − A_U leaves after
the three is printed as their interaction rather than shared out among them.
The registration's table also reads B5 against A_CAL, and E1 and E5 each
against A_U and against A, so the report prints those four comparisons too.
The interaction subtracts the basis effect as the registration words it,
although E1 and A_U both read adjusted prices and so differ in no price basis.

**The return per trade.** ``pead.m`` divides each day's summed returns by a
fixed 30 whatever the day holds. So the arithmetic annual return is the
trades taken times their mean signed return from the open to the close, times
252, over 30 and over the 330 days. A calendar can raise the figure by taking
more trades or by earning more on each, and the report prints each run's mean
return per trade, :func:`per_trade`, so a reader can tell which. The Sharpe
ratio does not depend on the 30, because dividing every day by one number
scales the mean and the deviation alike.

**The archive's prices never run in CI.** They sit in the owner's archive
under the design doc's exception for licensed bars, so C, D, E1 and E5 run
only where the archive is, and ``tests/test_pead_rerun.py`` skips their pins
elsewhere. Every other run reads only committed files.

**The scale-break guard.** Each run on Chan's prices calls
:func:`chan.pead.refuse_scale_breaks` on the stocks it reads. C, E1 and E5
call :func:`chan.series.refuse_window_crossing_a_break` on each stock's
adjusted open and close from its first price, the way
:func:`chan.pead.guarded_drift` does. D does not, because a split inside the
window is exactly what a raw series carries and what D exists to measure: the
guard would refuse the run whose question is what such a day does to the
figures. :func:`raw_breaks` counts the stocks it would refuse, and the report
prints the count.

**Deviations and choices.** No deviation from what the registration fixes.
Five choices it left open, each of which moves a figure or a count.

1. **The route to an archive series.** The audit counted 399 same-company
   series under Chan's own tickers. The check here passes 398 of them, and
   running it on every series in the ``sp500`` cross-section adds 48 renamed
   companies, such as Chan's UTX under the archive's RTX, so PX holds 446.
   The table names which route found each series.
2. **What a checked CIK is.** The registration says only "a checked CIK".
   :func:`chan.earnings_filings.check_cik` reads IVV's schedule at
   2012-03-31, and nine stocks leave CAL.

   1. Five are not in that schedule although Chan's file holds them: AK
      Steel, Compuware, Monster Worldwide, Tellabs and MEMC. Two of them
      also carry another company's proposed CIK: Compuware carries
      TetriDyn's, 827099, and Monster Worldwide carries Verisk's, 1442145.
   2. Cablevision's proposed CIK is BJ's Wholesale's, 1037461.
   3. DuPont's proposed CIK is the DuPont formed after 2015, 1666700, which
      had filed nothing by the price day and so fails on dates.
   4. NYSE Euronext fails on the name, because EDGAR files it with no legal
      form.
   5. Leucadia's CIK filed no Item 2.02 8-K in the window, so the fourth
      link drops it.
3. **The trading days.** The calendars move a filing to a trading day of the
   committed raw SPY vintage, which agrees with Chan's price file on every
   day from 2010-11-01 to 2012-04-24.
4. **D runs without the scale-break guard**, for the reason above.
5. **The calendars cover CAL rather than all 497.** The correction on issue
   251 asked for flags in the shape of Chan's file, 330 days by 497 stocks.
   The index holds no filing for the nine stocks outside CAL, so the derived
   calendars run over CAL's 488 alone. No run reads a stock outside CAL on a
   derived calendar, so only the counts of agreement with Chan's flags
   depend on this choice.

The denominator stays 30 in every run, as the rule fixes it, although the
derived calendars put more than 30 stocks on their busiest days. A day
holding more than 30 positions is a book levered past one, which the figures
carry as they stand.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import time
from pathlib import Path

import numpy as np
import pandas as pd

from chan.archive import ArchiveEntry, ArchiveUnavailable, read_cross_section
from chan.earnings_filings import FORM, Release, TickerRow, read_index, read_table
from chan.pead import DENOMINATOR, Drift, pead, read_sources, refuse_scale_breaks
from chan.series import WindowCrossesScaleBreak, refuse_window_crossing_a_break
from chan.sp500_panel import calendar as spy_calendar
from chan.vintage import VintageEntry, VintageUnavailable

#: The regular session, Eastern time.
SESSION_OPEN = time(9, 30)
SESSION_CLOSE = time(16, 0)

#: The universes, in the order the registration lists them.
UNIVERSES = ("ALL", "CAL", "PX", "U")


@dataclass(frozen=True)
class Spec:
    """One run issue 251 fixed before it ran: its stocks, its prices and its flags."""

    name: str
    universe: str
    prices: str
    flags: str


#: Every run issue 251 fixed, in the registration's order.
SPECS = (
    Spec("A", "ALL", "Chan", "Chan"),
    Spec("A_CAL", "CAL", "Chan", "Chan"),
    Spec("A_PX", "PX", "Chan", "Chan"),
    Spec("A_U", "U", "Chan", "Chan"),
    Spec("B1", "CAL", "Chan", "R1"),
    Spec("B5", "CAL", "Chan", "R5"),
    Spec("C", "PX", "adjusted", "Chan"),
    Spec("D", "PX", "raw", "Chan"),
    Spec("E1", "U", "adjusted", "R1"),
    Spec("E5", "U", "adjusted", "R5"),
)

#: The runs that read the archive.
ARCHIVE_RUNS = tuple(spec.name for spec in SPECS if spec.prices != "Chan")

#: The attribution's effects: a label, the run, and the run it is read against.
#: Beside the five the attribution names, the registration's table reads B5
#: against A_CAL, E1 against A, and E5 against A_U and against A.
EFFECTS = (
    ("universe", "A_U", "A"),
    ("calendar", "B1", "A_CAL"),
    ("calendar, R5", "B5", "A_CAL"),
    ("vendor", "C", "A_PX"),
    ("basis", "D", "C"),
    ("all of it, E1 against A_U", "E1", "A_U"),
    ("E1 against A", "E1", "A"),
    ("E5 against A_U", "E5", "A_U"),
    ("E5 against A", "E5", "A"),
)

#: The comparison the interaction is read from, and the interaction's own label.
TOTAL = "all of it, E1 against A_U"
INTERACTION = "interaction, what E1 − A_U leaves"


# --- The calendars -------------------------------------------------------------


def next_trading_day(day: pd.Timestamp, days: pd.DatetimeIndex) -> pd.Timestamp | None:
    """The first trading day strictly after ``day``'s date, or ``None`` past the calendar."""
    i = days.searchsorted(day.normalize(), side="right")
    return days[i] if i < len(days) else None


def r1_day(accepted: pd.Timestamp, days: pd.DatetimeIndex) -> pd.Timestamp | None:
    """The day R1 flags for a filing accepted at ``accepted``, Eastern, or ``None``."""
    day = accepted.normalize()
    if day in days:
        if accepted.time() < SESSION_OPEN:
            return day
        if accepted.time() < SESSION_CLOSE:
            return None
    return next_trading_day(day, days)


def r5_day(accepted: pd.Timestamp, report_date: str, days: pd.DatetimeIndex) -> pd.Timestamp | None:
    """The day R5 flags: late filings move to ``reportDate``, session filings stay."""
    day = accepted.normalize()
    if report_date and day > pd.Timestamp(report_date):
        return next_trading_day(pd.Timestamp(report_date), days)
    if day in days and SESSION_OPEN <= accepted.time() < SESSION_CLOSE:
        return day
    return r1_day(accepted, days)


#: Each calendar, as a function of one filing and the trading days.
RULES: Mapping[str, Callable[[Release, pd.DatetimeIndex], pd.Timestamp | None]] = {
    "R1": lambda release, days: r1_day(pd.Timestamp(release.accepted), days),
    "R5": lambda release, days: r5_day(pd.Timestamp(release.accepted), release.report_date, days),
}


def derived_flags(
    releases: Sequence[Release],
    stocks: Sequence[str],
    window: pd.DatetimeIndex,
    days: pd.DatetimeIndex,
    rule: str,
) -> pd.DataFrame:
    """A 0 or 1 for each day of ``window`` and each stock, in the flag file's shape.

    ``days`` is the trading calendar the rule moves a filing along, which
    runs past the window on both sides. A flag landing outside ``window`` is
    dropped, and an amendment is skipped even if one reaches here.
    """
    flags = pd.DataFrame(0.0, index=window, columns=list(stocks))
    wanted = set(stocks)
    for release in releases:
        if release.form != FORM or release.ticker not in wanted:
            continue
        day = RULES[rule](release, days)
        if day is not None and day in flags.index:
            flags.at[day, release.ticker] = 1.0
    return flags


@dataclass(frozen=True)
class Agreement:
    """How a derived calendar's cells compare with Chan's, as counts."""

    both: int
    chan_only: int
    derived_only: int
    neither: int

    @property
    def cells(self) -> int:
        return self.both + self.chan_only + self.derived_only + self.neither


def agreement(derived: pd.DataFrame, chan: pd.DataFrame) -> Agreement:
    """Cell by cell, over ``derived``'s days and stocks."""
    mine = derived.to_numpy() != 0
    his = chan.loc[derived.index, derived.columns].to_numpy() != 0
    return Agreement(
        both=int((mine & his).sum()),
        chan_only=int((~mine & his).sum()),
        derived_only=int((mine & ~his).sum()),
        neither=int((~mine & ~his).sum()),
    )


# --- The sources ---------------------------------------------------------------


@dataclass(frozen=True)
class Sources:
    """Everything the committed runs read.

    ``opens``, ``closes`` and ``flags`` are Chan's, for all 497 stocks.
    ``days`` is the trading calendar the derived flags move along.
    """

    members: list[VintageEntry]
    announcements: list[VintageEntry]
    opens: pd.DataFrame
    closes: pd.DataFrame
    flags: pd.DataFrame
    table: list[TickerRow]
    releases: list[Release]
    days: pd.DatetimeIndex

    @property
    def window(self) -> pd.DatetimeIndex:
        return self.flags.index

    def universe(self, name: str) -> list[str]:
        """A universe's stocks, in the order of Chan's files."""
        rows = {row.ticker: row for row in self.table}
        keep = {
            "ALL": lambda row: True,
            "CAL": lambda row: row.calendar,
            "PX": lambda row: row.priced,
            "U": lambda row: row.calendar and row.priced,
        }[name]
        return [symbol for symbol in self.flags.columns if keep(rows[symbol])]

    def calendar_flags(self, rule: str) -> pd.DataFrame:
        """A derived calendar over the flag file's days, for the stocks of ``CAL``."""
        return derived_flags(self.releases, self.universe("CAL"), self.window, self.days, rule)


def read_committed(data_dir: Path | None = None, record_dir: Path | None = None) -> Sources:
    """Chan's files, the ticker table and the index, refusing a table that disagrees.

    The table must name exactly the stocks of Chan's flag file in its order,
    since every universe is a selection from it.
    """
    members, announcements, opens, closes, flags = read_sources(data_dir)
    table = read_table(record_dir)
    if [row.ticker for row in table] != list(flags.columns):
        raise VintageUnavailable(
            "research/filings/earnings/tickers.csv does not list the flag file's stocks in "
            "its order"
        )
    days = spy_calendar(data_dir)
    return Sources(
        members, announcements, opens, closes, flags, table, read_index(record_dir), days
    )


@dataclass(frozen=True)
class ArchivePrices:
    """The archive's prices for PX, on the flag file's days, under Chan's tickers."""

    entries: dict[str, ArchiveEntry]
    adjusted_open: pd.DataFrame
    adjusted_close: pd.DataFrame
    raw_open: pd.DataFrame
    raw_close: pd.DataFrame


def read_archive(sources: Sources, directory: Path | None = None) -> ArchivePrices:
    """Each PX stock's archive series, renamed from its archive ticker to Chan's.

    Every file is hashed against its manifest line by
    :func:`chan.archive.read_cross_section` before it is parsed.
    """
    rows = {row.ticker: row for row in sources.table}
    stocks = sources.universe("PX")
    rename = {rows[stock].archive_ticker: stock for stock in stocks}
    read = {}
    for column in ("open", "close", "adjusted_close"):
        entries, frame = read_cross_section(
            "sp500", column=column, symbols=list(rename), directory=directory
        )
        read[column] = frame.rename(columns=rename).reindex(index=sources.window, columns=stocks)
    found = {rename[entry.symbol]: entry for entry in entries}
    missing = [stock for stock in stocks if stock not in found]
    if missing:
        raise ArchiveUnavailable(f"the archive's sp500 lines hold no series for {missing}")
    ratio = read["adjusted_close"] / read["close"]
    return ArchivePrices(
        entries=found,
        adjusted_open=read["open"] * ratio,
        adjusted_close=read["adjusted_close"],
        raw_open=read["open"],
        raw_close=read["close"],
    )


def _from_first_price(prices: pd.Series) -> pd.Series:
    first = prices.first_valid_index()
    return prices.iloc[:0] if first is None else prices.loc[first:]


def guard_archive(
    entries: Mapping[str, ArchiveEntry], frames: Sequence[pd.DataFrame], window: pd.DatetimeIndex
) -> None:
    """The scale-break guard on each stock's archive prices, from its first price."""
    for frame in frames:
        refuse_window_crossing_a_break(
            [(entries[stock], _from_first_price(frame[stock])) for stock in frame.columns],
            start=window[0],
            end=window[-1],
        )


def raw_breaks(prices: ArchivePrices, window: pd.DatetimeIndex) -> list[str]:
    """The PX stocks whose raw open or close the guard would refuse inside the window."""
    refused = []
    for stock in prices.raw_close.columns:
        try:
            guard_archive(
                prices.entries,
                [prices.raw_open[[stock]], prices.raw_close[[stock]]],
                window,
            )
        except WindowCrossesScaleBreak:
            refused.append(stock)
    return refused


# --- The runs ------------------------------------------------------------------


def committed_runs(sources: Sources) -> dict[str, Drift]:
    """A, A_CAL, A_PX, A_U, B1 and B5, which read only committed files."""
    derived = {rule: sources.calendar_flags(rule) for rule in RULES}
    members = {entry.symbol: entry for entry in sources.members}
    runs = {}
    for spec in SPECS:
        if spec.prices != "Chan":
            continue
        stocks = sources.universe(spec.universe)
        flags = sources.flags if spec.flags == "Chan" else derived[spec.flags]
        drift = pead(sources.opens[stocks], sources.closes[stocks], flags[stocks])
        refuse_scale_breaks(
            [members[stock] for stock in stocks],
            sources.opens[stocks],
            sources.closes[stocks],
            drift.days,
        )
        runs[spec.name] = drift
    return runs


def archive_runs(sources: Sources, prices: ArchivePrices) -> dict[str, Drift]:
    """C, D, E1 and E5, which read the archive's prices."""
    derived = {rule: sources.calendar_flags(rule) for rule in RULES}
    guard_archive(prices.entries, (prices.adjusted_open, prices.adjusted_close), sources.window)
    runs = {}
    for spec in SPECS:
        if spec.prices == "Chan":
            continue
        stocks = sources.universe(spec.universe)
        flags = sources.flags if spec.flags == "Chan" else derived[spec.flags]
        if spec.prices == "adjusted":
            opens, closes = prices.adjusted_open, prices.adjusted_close
        else:
            opens, closes = prices.raw_open, prices.raw_close
        runs[spec.name] = pead(opens[stocks], closes[stocks], flags[stocks])
    return runs


@dataclass(frozen=True)
class Effect:
    """One row of the attribution, in arithmetic annual return and Sharpe ratio."""

    label: str
    arithmetic: float
    sharpe: float


def attribution(runs: Mapping[str, Drift]) -> list[Effect]:
    """The comparisons issue 251 fixed, with the interaction right after E1 − A_U.

    The interaction is what E1 − A_U leaves after the calendar, vendor and
    basis effects. An effect whose runs are not in ``runs`` is left out, and
    so is the interaction unless all four of its effects are there.
    """
    effects = []
    for label, run, reference in EFFECTS:
        if run in runs and reference in runs:
            effects.append(
                Effect(
                    label,
                    runs[run].arithmetic_annual - runs[reference].arithmetic_annual,
                    runs[run].sharpe - runs[reference].sharpe,
                )
            )
    by = {effect.label: effect for effect in effects}
    parts = ("calendar", "vendor", "basis")
    if TOTAL in by and all(part in by for part in parts):
        interaction = Effect(
            INTERACTION,
            by[TOTAL].arithmetic - sum(by[part].arithmetic for part in parts),
            by[TOTAL].sharpe - sum(by[part].sharpe for part in parts),
        )
        effects.insert(effects.index(by[TOTAL]) + 1, interaction)
    return effects


def per_trade(drift: Drift) -> float:
    """The mean signed return from the open to the close of one trade.

    ``pead.m`` sums each day's signed returns and divides by 30, so 30 times
    the days' summed returns is the trades' summed returns. A trade whose
    return is missing counts as 0 there, as ``smartsum`` reads it.
    """
    return float(DENOMINATOR * np.sum(drift.daily) / drift.trades)


# --- The report ----------------------------------------------------------------


def report(
    sources: Sources,
    runs: Mapping[str, Drift],
    refused_raw: Sequence[str] | None,
    archive_absent: str | None,
) -> None:
    """Print every run, the attribution, the calendars' agreement and who was dropped."""
    print("Example 7.2 rerun on EDGAR's calendar and the archive's prices, issue 251")
    print(
        f"  window   {sources.window[0].date()} to {sources.window[-1].date()}, "
        f"{len(sources.window)} trading days"
    )
    sizes = ", ".join(f"{name} {len(sources.universe(name))}" for name in UNIVERSES)
    print(f"  stocks   {sizes}")
    print(f"  filings  {len(sources.releases)} original Item 2.02 8-Ks in the index")
    print()
    header = (
        f"  {'Run':<6} {'Stocks':<6} {'Prices':<9} {'Flags':<6} {'Arith':>9} {'Sharpe':>7} "
        f"{'APR':>9} {'MaxDD':>10} {'DDdays':>6} {'Trades':>6} {'Busiest':>7} "
        f"{'PerTrade':>9}"
    )
    print(header)
    for spec in SPECS:
        if spec.name not in runs:
            print(f"  {spec.name:<6} {spec.universe:<6} {spec.prices:<9} {spec.flags:<6} not run")
            continue
        drift = runs[spec.name]
        print(
            f"  {spec.name:<6} {spec.universe:<6} {spec.prices:<9} {spec.flags:<6} "
            f"{drift.arithmetic_annual:9.6f} {drift.sharpe:7.4f} {drift.compounded_apr:9.6f} "
            f"{drift.max_drawdown:10.6f} {drift.max_drawdown_days:6d} {drift.trades:6d} "
            f"{drift.most_held:7d} {per_trade(drift):9.6f}"
        )
    print()
    print(f"  {'Effect':<36} {'Arith':>10} {'Sharpe':>8}")
    for effect in attribution(runs):
        print(f"  {effect.label:<36} {effect.arithmetic:10.6f} {effect.sharpe:8.4f}")
    print()
    for rule in RULES:
        counts = agreement(sources.calendar_flags(rule), sources.flags)
        print(
            f"  {rule} against Chan's flags over {counts.cells:,} cells of CAL: both "
            f"{counts.both}, Chan's only {counts.chan_only}, {rule}'s only "
            f"{counts.derived_only}, neither {counts.neither:,}"
        )
    print()
    for label, keep in (("CAL", lambda row: row.calendar), ("PX", lambda row: row.priced)):
        out = [row for row in sources.table if not keep(row)]
        print(f"  Not in {label}, {len(out)}:")
        for row in out:
            why = row.cik_check if label == "CAL" else row.archive_check
            print(f"    {row.ticker:<6} {why}")
    if refused_raw is not None:
        print()
        print(
            f"  D reads raw prices without the scale-break guard. It would refuse "
            f"{len(refused_raw)} of PX's {len(sources.universe('PX'))} stocks: "
            f"{', '.join(refused_raw) or 'none'}."
        )
    if archive_absent is not None:
        print()
        print(f"  C, D, E1 and E5 did not run: {archive_absent}")
    print()
    print(
        "  Exploratory. The audit on issue 251 spent part of the sample before the registration, "
        "and R5 reads"
    )
    print(
        "  what a trader did not have before the open. docs/replication-log.md carries the entry."
    )


def run(
    data_dir: Path | None = None,
    record_dir: Path | None = None,
    directory: Path | None = None,
) -> dict[str, Drift]:
    """Every run this machine can make, printed, and returned by name."""
    sources = read_committed(data_dir, record_dir)
    runs = committed_runs(sources)
    refused_raw, absent = None, None
    try:
        prices = read_archive(sources, directory)
    except ArchiveUnavailable as missing:
        absent = str(missing)
    else:
        runs.update(archive_runs(sources, prices))
        refused_raw = raw_breaks(prices, sources.window)
    report(sources, runs, refused_raw, absent)
    return runs


def main() -> None:
    argparse.ArgumentParser(
        description="Example 7.2 rerun on EDGAR's announcement calendar and the archive's "
        "prices, issue 251"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
