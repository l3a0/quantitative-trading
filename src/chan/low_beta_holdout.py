"""Chan's low-beta leverage rule after the book, on the S&P 500 as IVV held it from 2008.

[Issue 275](https://github.com/l3a0/quantitative-trading/issues/275) tests the
rule at Kindle location 4709 of the revised edition, that "a highly leveraged
portfolio of low-beta stocks should generate higher long-term compounded growth
than holding an unleveraged portfolio of high-beta stocks", on Chan's own S&P
500 file from 1999 to 2007. :mod:`chan.low_beta_leverage` runs it, and Entry 45
of [docs/replication-log.md](../../docs/replication-log.md) records the result.
That file holds only the stocks still in the index in 2007, and its span sits
inside the samples the low-beta literature already used.
[Issue 526](https://github.com/l3a0/quantitative-trading/issues/526) runs
issue 275's registered specification, with the changes the panel forces, on a
panel that has neither problem in the same form: IVV's members at each
month-end from 2008-12 to 2026-08, read through :mod:`chan.sp500_panel`. Its
survivor gap is smaller and measured, and every holding month comes after Chan
published.

Everything issue 275 registered carries over, its amendment of 2026-10-11
reading a ruined month as the claim contradicted included, and
:mod:`chan.low_beta_leverage` computes it. Issue 526's section "What the panel
forces", registered on 2026-10-11 before any beta or return was computed on
this panel, states what changes and why. In short:

1. **The market** is SPY's ``adjusted_close`` from Alpha Vantage, recorded
   into the archive's ``sp500`` cross-section on 2026-10-11 for this run.
2. **The calendar** is :func:`chan.sp500_panel.calendar`, the committed raw
   SPY vintage, and every series is read on its days. A day in the run's span
   with no finite SPY close stops the run as :class:`HoldoutRefused`.
3. **Membership at t** is a member of the schedule that sets month t whose
   member-month passes :func:`chan.sp500_panel.monthly_coverage` with
   Example 7.7's ``rank`` reason left out.
4. **The holding month.** Each series stops at its last row that traded and
   moved, by :func:`chan.equity_seasonals.last_traded`, and
   :func:`chan.equity_seasonals.stopped_closes` carries its last close to the
   next month-end. So a stock stopping strictly inside the holding month earns
   its return to its last close and holds cash after it, and one whose last
   row is t, or that has no close at t, or a hole at t + 1, is not eligible.
   The first and the last of those exclusions still read t + 1, which is not
   known at t, and at the 208 formations kept they leave out 12 and 4
   member-months, which :class:`NextReads` lists.
5. **The span.** Formations run from 2008-12-31 to 2026-07-31, because the
   committed TB3MS ends at 2026-08. The frame ends at 2026-08-31, so every day
   it holds has a bill rate, and it starts 252 rows before the first
   formation, so that formation has exactly the 252 returns a beta reads.

:func:`chan.low_beta_leverage.build_portfolios` takes the membership through
its ``members`` keyword, whose index also names the month-ends, since the
frame's last row closes the last holding month.

**The second amendment.** Issue 275's plan refuses a formation whose low
group's mean beta is zero or below, and says nothing of the verdict. The one
run of this specification refused at 2026-04-30, before anything the criterion
reads had been computed. The owner ruled on 2026-10-11, in issue 526's
"Amendment, 2026-10-11, after a non-positive low-group beta was seen", that
such a formation is skipped: its holding month leaves every series, the
criterion, the ruin rule and every side figure read the months that remain,
and N counts them. ``build_portfolios`` does it under ``skip_non_positive``,
and the report lists every skipped formation with both groups' mean betas.

The scale-break guard is not called, as on Chan's file. The run counts the
stock-months in either portfolio with a flagged day inside the beta window or
the holding month, and the comment above ``FLAGGED_IN_CHANS_MAT_FILES`` in
``tests/test_scale_breaks.py`` records the decision for this panel too.

**The survivor label.** This panel has a smaller survivor gap than Chan's
file, not none. The report gives the member-months the monthly rule of point
3 leaves out, and the member-months and member rows that fail the row check
against the filing, with how many carry a ticker absent from, or still in,
the last schedule. A ticker absent from the last schedule marks a company
that left the index or one that changed its ticker. Membership is each quarter-end schedule
carried forward, so a change between schedules is dated up to two months late,
or five around the missing 2013-09-30 schedule.

The result is **registered**, under issue 275's ruin amendment and issue 526's
skip amendment, both of 2026-10-11. Issue 275's plan and issue 526's panel
changes were written before any beta or return on this panel was computed.
The skip rule was chosen after one non-positive formation was visible, and N is
smaller by however many it skips. Every holding month comes after the book, so it is a
holdout for the claim.

``tests/test_low_beta_holdout.py`` is the single authority for every number
any prose surface quotes about this run. It first ran here on 2026-10-11.

The write-up, ``blog/low-beta-holdout-lessons.md``, teaches the result beside
Entry 45's, and :mod:`chan.low_beta_holdout_figures` draws its figure.

Usage:
    QT_ARCHIVE_DIR=/path/to/archive python -m chan.low_beta_holdout
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan import sp500_panel
from chan.archive import ArchiveEntry, ArchiveRefused, ArchiveUnavailable, read_cross_section
from chan.bill_rates import bill_vintage, monthly_rates
from chan.equity_seasonals import (
    MonthlyRunRefused,
    last_traded,
    members_mask,
    stopped_closes,
    traded_spans,
)
from chan.fund_panel import MemberRow, PanelRefused
from chan.low_beta_leverage import (
    BETA_DAYS,
    CAVEAT_LOCATION,
    CRITICAL,
    MIN_DAYS,
    POWER,
    PREMISE_LOCATION,
    RUIN,
    RULE_LOCATION,
    EmptyPortfolio,
    NonPositiveBeta,
    Portfolios,
    UnreadableStandardError,
    Verdict,
    build_portfolios,
    flagged_days,
    flagged_stock_months,
    formation_table,
    growth,
    kelly,
    realised_beta,
    sharpe,
    verdict,
)
from chan.series import load_vintage, vintage_line
from chan.sp500_panel import MonthCoverage
from chan.vintage import VintageEntry, VintageUnavailable

#: The market, recorded into the ``sp500`` cross-section for this run.
MARKET = "SPY"

#: The first formation's month, the first month the panel covers.
FIRST_FORMATION = sp500_panel.FIRST_MONTH

#: The last holding month the span allows, the last the committed TB3MS holds a rate for.
LAST_HELD = pd.Period("2026-08", "M")


class HoldoutRefused(Exception):
    """The run stopped rather than compute on a day or a member it cannot trust."""


@dataclass(frozen=True)
class SurvivorGap:
    """How much of the panel the monthly rule leaves out, and who.

    ``member_months`` counts every member at every month the panel covers, and
    ``left_out`` those the monthly rule of point 3 does not cover, for any
    reason. ``failed_member_months`` counts the member-months whose row failed
    the row check against the filing, and ``absent_member_months`` those of
    them whose ticker is not in the last schedule. ``failed_rows`` counts the
    member rows across every schedule that failed the row check, and
    ``still_listed`` those whose ticker is in the last schedule. A ticker
    absent from the last schedule belongs to a company that left the index or
    one that changed its ticker, and the two are not told apart here.
    """

    member_months: int
    left_out: int
    failed_member_months: int
    absent_member_months: int
    failed_rows: int
    still_listed: int
    last_schedule: str


@dataclass(frozen=True)
class NextReads:
    """The member-months point 4's two exclusions leave out at the formations kept.

    Both read the month-end after the formation, t + 1. ``last_row_at_t`` lists
    each member whose series' last row is t, and ``hole_at_t1`` each whose
    series has no row at t + 1 but rows after it, as ``(month, ticker)``
    pairs.
    """

    last_row_at_t: tuple[tuple[str, str], ...]
    hole_at_t1: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Holdout:
    """Everything the run reads and computes."""

    entries: tuple[ArchiveEntry, ...]
    spy_entry: ArchiveEntry
    calendar: VintageEntry
    bill_entry: VintageEntry
    #: Every month the panel covers, 2008-12 to 2026-08, with the rule of point 3.
    coverage: tuple[MonthCoverage, ...]
    portfolios: Portfolios
    #: Members and covered members at each formation, in formation order.
    members: tuple[int, ...]
    covered: tuple[int, ...]
    flags: dict[str, list[pd.Timestamp]]
    flagged: tuple[int, int]
    #: Series whose stop comes before their file's last row.
    moved: int
    #: Rows inside the frame's span on a day the calendar lacks, stocks and SPY.
    off_calendar: int
    survivors: SurvivorGap
    reads_next: NextReads

    @property
    def verdict(self) -> Verdict:
        return verdict(self.portfolios)


def frame_days(calendar: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """The run's days: 252 rows before the first formation to the last holding month's end."""
    first = sp500_panel.month_end(calendar, FIRST_FORMATION)
    last = sp500_panel.month_end(calendar, LAST_HELD)
    at = calendar.get_loc(first)
    if at < BETA_DAYS:
        raise HoldoutRefused(f"the calendar holds {at} rows before {first.date()}, not {BETA_DAYS}")
    return calendar[at - BETA_DAYS : calendar.get_loc(last) + 1]


def off_calendar(series: pd.DataFrame, days: pd.DatetimeIndex) -> int:
    """How many closes inside the span of ``days`` fall on a day ``days`` lacks."""
    inside = series.loc[(series.index >= days[0]) & (series.index <= days[-1])]
    return int(inside.loc[~inside.index.isin(days)].notna().to_numpy().sum())


def market_closes(spy: pd.Series, days: pd.DatetimeIndex) -> pd.Series:
    """SPY on the run's days, refused at the first day with no finite close."""
    closes = spy.reindex(days)
    bad = days[~np.isfinite(closes.to_numpy(dtype=float))]
    if len(bad):
        raise HoldoutRefused(
            f"{MARKET} has no finite close on {bad[0].date()}, a day of the calendar, and "
            f"{len(bad)} days in all"
        )
    return closes


def month_end_mask(
    rows: tuple[MemberRow, ...],
    coverage: tuple[MonthCoverage, ...],
    symbols: list[str],
    calendar: pd.DatetimeIndex,
) -> pd.DataFrame:
    """The covered members at each month the panel covers, indexed by that month's last day."""
    mask = members_mask(rows, coverage, symbols)
    days = [sp500_panel.month_end(calendar, month) for month in mask.index]
    return mask.set_axis(pd.DatetimeIndex(days), axis=0)


def refuse_uncovered(closes: pd.DataFrame, mask: pd.DataFrame) -> None:
    """Refuse a covered member with no close at its formation or the month-end after.

    The coverage reads the committed holes file and the manifest's spans, and
    the frame reads the bytes, so a disagreement between the two would drop a
    member the coverage reports as eligible.
    """
    for formed, held_to in zip(mask.index[:-1], mask.index[1:], strict=True):
        covered = mask.columns[mask.loc[formed].to_numpy()]
        for day in (formed, held_to):
            row = closes.loc[day, covered]
            if row.isna().any():
                raise HoldoutRefused(
                    f"formed {formed.date()}: covered member {row.index[row.isna()][0]} has no "
                    f"close on {day.date()}"
                )


def survivor_gap(rows: tuple[MemberRow, ...], coverage: tuple[MonthCoverage, ...]) -> SurvivorGap:
    """What the monthly rule leaves out, and the member-months and rows failing the row check."""
    by_key = {row.key: row for row in rows}
    last = sp500_panel.schedule_months()[-1][0]
    listed = {row.ticker for row in rows if row.report_date == last and row.ticker}
    failed = [
        by_key[key].ticker
        for month in coverage
        for key, reason in zip(month.missing, month.reasons, strict=True)
        if reason not in sp500_panel.MISSES
    ]
    failing = [row for row in rows if row.check != "pass"]
    return SurvivorGap(
        member_months=sum(month.members for month in coverage),
        left_out=sum(month.members - month.covered for month in coverage),
        failed_member_months=len(failed),
        absent_member_months=sum(1 for ticker in failed if ticker not in listed),
        failed_rows=len(failing),
        still_listed=sum(1 for row in failing if row.ticker in listed),
        last_schedule=last,
    )


def next_reads(
    rows: tuple[MemberRow, ...],
    coverage: tuple[MonthCoverage, ...],
    spans: dict[str, tuple[str, str]],
    holes: frozenset[tuple[str, str]],
    calendar: pd.DatetimeIndex,
    formed: pd.DatetimeIndex,
) -> NextReads:
    """Split the ``next`` misses at the formations into a last row at t and a hole at t + 1.

    ``spans`` are the ones the coverage was computed on. The coverage rule
    gives ``next`` only to a member covered at t whose series ends at t or has
    a hole at t + 1, so any other ``next`` is refused as a rule this split does
    not know.
    """
    by_key = {row.key: row for row in rows}
    kept = {day.to_period("M") for day in formed}
    last_row, hole = [], []
    for month in coverage:
        period = pd.Period(month.month, "M")
        if period not in kept:
            continue
        day = sp500_panel.month_end(calendar, period)
        for key, reason in zip(month.missing, month.reasons, strict=True):
            if reason != "next":
                continue
            ticker = by_key[key].ticker
            if pd.Timestamp(spans[ticker][1]) == day:
                last_row.append((month.month, ticker))
            elif (ticker, str(period + 1)) in holes:
                hole.append((month.month, ticker))
            else:
                raise HoldoutRefused(f"{ticker} misses {month.month} for next with neither cause")
    return NextReads(tuple(last_row), tuple(hole))


def skipped_line(portfolios: Portfolios) -> str:
    """How many formations the skip amendment left out, and the first, as every surface says it."""
    skipped = portfolios.skipped
    if not skipped:
        return "  No formation had a low group's mean beta of zero or below, so none is skipped."
    return (
        f"  {len(skipped)} formation{'s' if len(skipped) > 1 else ''} skipped under issue 526's "
        f"amendment of 2026-10-11, the first formed {skipped[0].formed.date()}: a low group's "
        "mean beta of zero or below has no beta-matched leverage."
    )


def read_holdout(*, data_dir: Path | None = None, directory: Path | None = None) -> Holdout:
    """Read the members, the closes, SPY, the calendar and the bills, and build the portfolios."""
    rows = sp500_panel.load()
    symbols = sp500_panel.tickers(rows)
    if MARKET in symbols:
        raise HoldoutRefused(f"{MARKET} is a member ticker, so it cannot also be the market")
    entries, adjusted = read_cross_section(
        sp500_panel.CROSS_SECTION,
        column="adjusted_close",
        symbols=symbols,
        data_dir=data_dir,
        directory=directory,
    )
    _, volume = read_cross_section(
        sp500_panel.CROSS_SECTION,
        column="volume",
        symbols=symbols,
        data_dir=data_dir,
        directory=directory,
    )
    market_entries, market = read_cross_section(
        sp500_panel.CROSS_SECTION,
        column="adjusted_close",
        symbols=[MARKET],
        data_dir=data_dir,
        directory=directory,
    )
    if len(market_entries) != 1:
        raise ArchiveUnavailable(
            f"data/archive_vintages.jsonl records no {sp500_panel.CROSS_SECTION} line for {MARKET}"
        )
    calendar_entry, raw_spy = load_vintage("SPY", unadjusted=True, data_dir=data_dir)
    calendar = pd.DatetimeIndex(raw_spy.index)
    bill_entry = bill_vintage(data_dir=data_dir)
    bills = dict(monthly_rates(data_dir=data_dir))
    if str(LAST_HELD) not in bills:
        raise HoldoutRefused(f"the bill series holds no rate for {LAST_HELD}")

    days = frame_days(calendar)
    stops = last_traded(adjusted, volume)
    manifest = sp500_panel.spans(data_dir)
    moved = sum(1 for symbol, stop in stops.items() if str(stop.date()) != manifest[symbol][1])
    spans = traded_spans(manifest, stops)
    # With the rank reason left out, no member is linked to an earlier
    # schedule's row, so the links, which read every holdings file, are not
    # computed.
    holes = sp500_panel.read_holes()
    coverage = tuple(
        sp500_panel.monthly_coverage(rows, spans, holes, calendar, previous={}, rank=False)
    )
    closes = stopped_closes(adjusted.reindex(days), stops, calendar).reindex(columns=symbols)
    spy = market_closes(market[MARKET], days)
    mask = month_end_mask(rows, coverage, symbols, calendar)
    refuse_uncovered(closes, mask)

    portfolios = build_portfolios(closes, spy, bills, members=mask, skip_non_positive=True)
    formed = pd.DatetimeIndex(portfolios.formed)
    by_day = dict(zip(mask.index, coverage, strict=True))
    flags = flagged_days(closes)
    return Holdout(
        entries=tuple(entries),
        spy_entry=market_entries[0],
        calendar=calendar_entry,
        bill_entry=bill_entry,
        coverage=coverage,
        portfolios=portfolios,
        members=tuple(by_day[day].members for day in formed),
        covered=tuple(int(mask.loc[day].sum()) for day in formed),
        flags=flags,
        flagged=flagged_stock_months(portfolios, flags),
        moved=moved,
        off_calendar=off_calendar(adjusted, days) + off_calendar(market, days),
        survivors=survivor_gap(rows, coverage),
        reads_next=next_reads(rows, coverage, spans, holes, calendar, formed),
    )


def report(holdout: Holdout) -> None:
    """Print the vintages, the window, the verdict, every side figure and every label."""
    h = holdout
    p = h.portfolios
    result = h.verdict
    downloads = sorted({entry.download_date for entry in h.entries})
    print("A levered low-beta portfolio against an unlevered high-beta one, on IVV's S&P 500")
    print(
        f"  stocks   {len(h.entries)} {sp500_panel.CROSS_SECTION} series, Alpha Vantage "
        f"adjusted, downloaded {', '.join(downloads)}, members from "
        f"{sp500_panel.MEMBERS_PATH.name} and {sp500_panel.HOLES_PATH.name}"
    )
    print(
        f"  market   {h.spy_entry.path}, Alpha Vantage adjusted, downloaded "
        f"{h.spy_entry.download_date}"
    )
    print(f"  calendar {vintage_line(h.calendar)}")
    print(f"  bills    {vintage_line(h.bill_entry)}")
    print(
        f"  window   formed {p.formed[0].date()} to {p.formed[-1].date()}, held to "
        f"{p.held_to[0].date()} to {p.held_to[-1].date()}, {len(p.low)} months"
    )
    print(
        f"  beta     OLS slope with an intercept on {MARKET}'s daily excess return, "
        f"{BETA_DAYS} days ending at formation, at least {MIN_DAYS} finite"
    )
    print(
        "  groups   lowest and highest fifth by beta, ties by symbol, equal-weighted, "
        f"held one month, location {PREMISE_LOCATION}"
    )
    sizes = [len(held) for held in p.low_members]
    print(
        f"  members  {sum(h.members)} member-months at the formations, {sum(h.covered)} covered, "
        f"{sum(p.eligible)} eligible with a beta"
    )
    print(
        f"  eligible {min(p.eligible)} to {max(p.eligible)} stocks per formation, each "
        f"portfolio {min(sizes)} to {max(sizes)}"
    )
    print(
        f"  leverage k = high group's mean beta / low group's, mean {p.leverage.mean():.4f}, "
        f"min {p.leverage.min():.4f}, max {p.leverage.max():.4f}"
    )
    print()
    print(
        f'  Claim, location {RULE_LOCATION}, "Holding a highly leveraged portfolio of low-beta '
        "stocks should generate higher"
    )
    print(
        "  long-term compounded growth than holding an unleveraged portfolio of high-beta "
        f'stocks": {result.outcome.upper()}.'
    )
    print(f"  {result.line()}")
    print(skipped_line(p))
    for skip in p.skipped:
        print(
            f"    formed {skip.formed.date()}, held to {skip.held_to.date()}, low group's mean "
            f"beta {skip.low_beta:.4f}, high group's {skip.high_beta:.4f}"
        )
    if result.by_ruin:
        print(f"  {'Ruined month':<14} {'Formed':<12} {'k':>8} {'Levered':>9}")
        for ruin in result.ruined:
            print(
                f"  {str(ruin.held_to.date()):<14} {str(ruin.formed.date()):<12} "
                f"{ruin.leverage:>8.4f} {ruin.levered:>9.4f}"
            )
        print(
            f"  A levered return of {RUIN:.0f} or below leaves d undefined, so the Newey-West t "
            "and Y are not computed."
        )
    else:
        print(
            f"  d = ln(1 + levered low) - ln(1 + high), {result.months} months, mean x 12 "
            f"{result.gap:.4f}, Newey-West t {result.t:.4f} at lag {result.lag}, "
            f"Y {result.detectable:.4f}"
        )
        print(
            f"  One-sided at 5 percent against {CRITICAL}, Y = ({CRITICAL} + {POWER}) x the "
            "standard error x 12, registered before any number."
        )
    print()
    print("  Beside the verdict, deciding nothing")
    print(f"  {'Series':<14} {'Growth':>8} {'Sharpe':>8} {'Beta':>8}")
    levered_growth = "ruin" if result.by_ruin else f"{growth(p.levered):.4f}"
    for name, series, grew in (
        ("levered low", p.levered, levered_growth),
        ("low", p.low, f"{growth(p.low):.4f}"),
        ("high", p.high, f"{growth(p.high):.4f}"),
    ):
        print(
            f"  {name:<14} {grew:>8} {sharpe(series, p.rf):>8.4f} {realised_beta(series, p):>8.4f}"
        )
    print(f"  {MARKET:<14} {growth(p.spy):>8.4f} {'':>8} {realised_beta(p.spy, p):>8.4f}")
    print(
        "  Growth is 12 x the mean monthly log return. Sharpe is the monthly excess return's, "
        "x sqrt(12). Beta is on SPY's monthly excess return."
    )
    if result.by_ruin:
        print(
            f"  The levered low's Sharpe and beta read all {len(p.levered)} months of "
            "rf + k x (r_low - rf), each month as if freshly funded."
        )
    reading = kelly(p)
    print(
        f"  Kelly, location {RULE_LOCATION}, look-ahead: the low portfolio's full-sample m / s^2 "
        f"{reading.leverage:.4f}, Gaussian growth there r + S^2/2 = {reading.bill:.4f} + "
        f"{reading.moments.levered_growth:.4f} = {reading.growth:.4f}, against the high "
        f"portfolio's realised {growth(p.high):.4f}."
    )
    low_flags, high_flags = h.flagged
    print(
        f"  Scale-break flags inside the beta window or the holding month: {low_flags} low and "
        f"{high_flags} high stock-months of {2 * sum(sizes)}. None is refused."
    )
    print()
    print("  Every formation, deciding nothing")
    print(
        f"  {'Formed':<12} {'Members':>7} {'Covered':>7} {'Eligible':>8} {'Each':>5} "
        f"{'Low beta':>9} {'High beta':>10} {'k':>8}"
    )
    table = formation_table(p)
    for (formed, row), members, covered in zip(table.iterrows(), h.members, h.covered, strict=True):
        print(
            f"  {str(formed.date()):<12} {members:>7} {covered:>7} {row['eligible']:>8.0f} "
            f"{row['per group']:>5.0f} {row['low beta']:>9.4f} {row['high beta']:>10.4f} "
            f"{row['k']:>8.4f}"
        )
    print()
    print(
        f'  Location {CAVEAT_LOCATION}: "one should be quite wary of using too much leverage on '
        'normally low-beta stocks", because returns have fat tails.'
    )
    s = h.survivors
    print(
        f"  Survivors: the monthly rule leaves out {s.left_out} of {s.member_months} "
        f"member-months. {s.failed_member_months} of them fail the row check against the "
        f"filing, {s.absent_member_months} of those with a ticker absent from the "
        f"{s.last_schedule} schedule, and of the {s.failed_rows} member rows that fail it, "
        f"{s.still_listed} carry a ticker still in that schedule."
    )
    n = h.reads_next
    print(
        f"  Read at t + 1: {len(n.last_row_at_t)} member-months whose last row is t and "
        f"{len(n.hole_at_t1)} with a hole at t + 1 are left out at the formations kept."
    )
    print(
        "  Membership is each quarter-end schedule carried forward, so a change between "
        "schedules is dated up to two months late, or five around the missing 2013-09-30."
    )
    print(
        "  Registered on issue 526 before any beta or return was computed on this panel, with "
        "issue 275's plan, its ruin amendment and issue 526's skip amendment, both of 2026-10-11."
    )
    print(
        "  Every holding month comes after the book, so this is a holdout. "
        "docs/replication-log.md Entry 49 carries the verdict."
    )


def run(*, data_dir: Path | None = None, directory: Path | None = None) -> Holdout:
    """Read the archive, build the portfolios, and print the report."""
    holdout = read_holdout(data_dir=data_dir, directory=directory)
    report(holdout)
    return holdout


def main() -> None:
    argparse.ArgumentParser(
        description="Whether a levered low-beta portfolio out-compounds an unlevered high-beta "
        "one on IVV's S&P 500 from 2008, issue 526"
    ).parse_args()
    try:
        run()
    except (
        ArchiveUnavailable,
        ArchiveRefused,
        PanelRefused,
        MonthlyRunRefused,
        VintageUnavailable,
        HoldoutRefused,
        NonPositiveBeta,
        EmptyPortfolio,
        UnreadableStandardError,
    ) as refused:
        # A refusal reaches the reader as one line, the way
        # chan.low_beta_leverage.main prints one.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
