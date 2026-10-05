"""GLD, GDX and USO around July 2008, *Algorithmic Trading*'s Johansen tests.

Chan pairs the gold fund GLD with the gold miners' fund GDX, since a miner's
main asset is gold. At Kindle location 1922 he says the pair stopped
cointegrating on July 14, 2008, the day oil peaked, and offers a reason: dear
oil makes gold dearer to mine, so the miners lag the metal. He tests the
reason by adding the oil fund USO. Three claims, and the book prints no
statistic for any of them.

1. GLD and GDX, May 23, 2006, to July 14, 2008, "cointegrate with 99 percent
   probability" under the Johansen test.
2. GLD and GDX, July 15, 2008, to April 9, 2012, "have lost the
   cointegration".
3. GLD, GDX and USO over "the entire period from 2006 to 2012" show "a 99
   percent probability that there exists one cointegrating relationship".

No script ships for this example, so nothing is transcribed. The
specification was declared on
[issue 344](https://github.com/l3a0/quantitative-trading/issues/344) before
any statistic was computed.

1. **The test.** :func:`chan.johansen.johansen` with ``p = 0`` and ``k = 1``,
   a constant and one lagged difference. The book names neither. Every
   Johansen call in Chan's book-two scripts passes those two, and they are the
   only values his printouts vouch for in the wrapper.
2. **The columns.** GLD, GDX and then USO, the book's order. The statistics
   do not depend on it, and the eigenvector's rows follow it.
3. **The windows.** The file holds GLD and USO from 2006-04-26 and GDX from
   2006-05-23, so every window starts on GDX's first price, which is also
   where Chan's first window starts. The triplet's "entire period" is GDX's
   1,481 days, since the wrapper refuses a price that is not a number.
4. **The level.** 99 percent, the level all three claims name.

**Each claim is judged on each statistic.** The book does not say whether it
read the trace or the eigen statistic, and the two can disagree on Chan's own
file, as Entry 23 of the replication log found at location 1337. So each
claim is two rows, one per statistic, and neither was chosen after the fact.
The counts at 90 and 95 percent are reported beside each row and decide
nothing.

**Rows beside the claims.** None carries a verdict.

1. GLD and GDX alone over the triplet's 1,481 days. The book leaves this
   control out, and the triplet's result supports the oil reading only if the
   pair alone fails over the same days.
2. The triplet's first eigenvector, with the sign statsmodels gives, for the
   reason :mod:`chan.johansen` explains.
3. The CADF test of GLD on GDX in each window,
   :func:`chan.pair_cointegration.lesage_cadf` with one lag, the test and
   direction of Entry 1 of the replication log.
4. A plain ADF test with a constant and one lag on each series in each window
   it enters, which is what a Johansen rank equal to the column count would
   have to be read against.

Every result here is exploratory, twice over. Reproducing the claims spends
the 2006 to 2012 sample on a split Chan chose, and the split date and the
third ETF were both chosen after the break was seen. So the triplet's result
cannot confirm the oil hypothesis, however it comes out. It says only whether
Chan's claims hold on his file.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2, adf_tstat

from chan.johansen import LEVELS, Johansen, johansen
from chan.pair_cointegration import lesage_cadf
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
)
from chan.vintage import VintageEntry, VintageUnavailable

SOURCE_FILE = "inputData_ETF.mat"

GLD, GDX, USO = "GLD", "GDX", "USO"
#: The book's order, which every eigenvector's rows follow.
PAIR = (GLD, GDX)
TRIPLET = (GLD, GDX, USO)

#: The declared specification, a constant and one lagged difference.
JOHANSEN_P = 0
JOHANSEN_K = 1
#: The level every claim names.
LEVEL = 99
#: ``cadf(GLD, GDX, 0, 1)``, Entry 1's test.
CADF_LAGS = 1

#: Each window's first and last day, both inclusive. Location 1922 names them.
BEFORE = ("2006-05-23", "2008-07-14")
AFTER = ("2008-07-15", "2012-04-09")
WHOLE = ("2006-05-23", "2012-04-09")
WINDOWS = {"before": BEFORE, "after": AFTER, "whole": WHOLE}

#: Location 1922, quoted.
BOOK_BEFORE = "cointegrate with 99 percent probability"
BOOK_AFTER = "have lost the cointegration"
BOOK_TRIPLET = "a 99 percent probability that there exists one cointegrating relationship"


def _at_least_one(count: int) -> bool:
    # Two relations between two series is a full rank, which says each series
    # is stationary alone. The claim is about rejecting no cointegration, so
    # issue 344 decided the row holds on a count of 2 as well.
    return count >= 1


def _none(count: int) -> bool:
    return count == 0


def _exactly_one(count: int) -> bool:
    return count == 1


@dataclass(frozen=True)
class ClaimRow:
    """One claim judged on one statistic, at :data:`LEVEL`."""

    row: int
    label: str
    test: str
    statistic: str
    criterion: str
    holds_on: Callable[[int], bool]


#: The six claim rows, with the criteria issue 344 declared before any statistic.
CLAIM_ROWS = (
    ClaimRow(1, "GLD and GDX cointegrate before", "before", "trace", ">= 1", _at_least_one),
    ClaimRow(2, "GLD and GDX cointegrate before", "before", "eigen", ">= 1", _at_least_one),
    ClaimRow(3, "GLD and GDX have lost it after", "after", "trace", "== 0", _none),
    ClaimRow(4, "GLD and GDX have lost it after", "after", "eigen", "== 0", _none),
    ClaimRow(5, "GLD, GDX and USO hold one relation", "triplet", "trace", "== 1", _exactly_one),
    ClaimRow(6, "GLD, GDX and USO hold one relation", "triplet", "eigen", "== 1", _exactly_one),
)


@dataclass(frozen=True)
class Cadf:
    """``cadf(GLD, GDX, 0, lags)``'s t-statistic, AR(1) estimate and observation count."""

    t: float
    ar1: float
    nobs: int


@dataclass(frozen=True)
class GoldMinersOil:
    """The three claim tests, the control, and the rows beside them.

    ``before`` and ``after`` test GLD and GDX either side of the break.
    ``triplet`` tests all three over the whole span and ``control`` tests GLD
    and GDX alone over the same days. ``cadf`` and ``adf`` are keyed by the
    window names in :data:`WINDOWS`, and ``adf`` holds each series that enters
    that window's Johansen test.
    """

    days: dict[str, pd.DatetimeIndex]
    before: Johansen
    after: Johansen
    triplet: Johansen
    control: Johansen
    cadf: dict[str, Cadf]
    adf: dict[str, dict[str, float]]

    def found(self, row: ClaimRow, level: int = LEVEL) -> int:
        """How many relations the row's test finds on its statistic at ``level``."""
        return getattr(self, row.test).relations(row.statistic, level)

    def holds(self, row: ClaimRow) -> bool:
        """Whether the row's declared criterion holds at :data:`LEVEL`."""
        return row.holds_on(self.found(row))


def gold_miners_oil(closes: pd.DataFrame) -> GoldMinersOil:
    """Run the four Johansen tests and the rows beside them on GLD, GDX and USO."""
    window = {name: closes.loc[start:end] for name, (start, end) in WINDOWS.items()}

    def test(name: str, symbols: tuple[str, ...]) -> Johansen:
        return johansen(window[name][list(symbols)].to_numpy(dtype=float), JOHANSEN_P, JOHANSEN_K)

    entering = {"before": PAIR, "after": PAIR, "whole": TRIPLET}
    return GoldMinersOil(
        days={name: frame.index for name, frame in window.items()},
        before=test("before", PAIR),
        after=test("after", PAIR),
        triplet=test("whole", TRIPLET),
        control=test("whole", PAIR),
        cadf={
            name: Cadf(
                *lesage_cadf(
                    frame[GLD].to_numpy(dtype=float), frame[GDX].to_numpy(dtype=float), CADF_LAGS
                )
            )
            for name, frame in window.items()
        },
        adf={
            name: {
                s: adf_tstat(window[name][s].to_numpy(dtype=float), lags=1, constant=True)[0]
                for s in symbols
            }
            for name, symbols in entering.items()
        },
    )


def read_sources(data_dir: Path | None = None) -> tuple[list[VintageEntry], pd.DataFrame]:
    """GLD, GDX and USO from the first day all three are priced, refused across a scale break.

    GDX's first price is the file's 2006-05-23, four weeks after GLD's and
    USO's. Cutting there is what keeps a missing price from reaching the
    Johansen test, which refuses one by name.
    """
    members, closes = load_panel(SOURCE_FILE, data_dir=data_dir)
    read = [m for m in members if m.symbol in TRIPLET]
    frame = closes[list(TRIPLET)]
    frame = frame.loc[frame.dropna().index[0] :]
    refuse_window_crossing_a_break(
        [(m, frame[m.symbol]) for m in read], start=frame.index[0], end=frame.index[-1]
    )
    return read, frame


def _counts(test: Johansen, statistic: str) -> str:
    return ", ".join(f"{test.relations(statistic, level)} at {level}%" for level in LEVELS)


def _table(name: str, test: Johansen, symbols: tuple[str, ...]) -> list[str]:
    lines = [f"  {name}, columns {', '.join(symbols)}"]
    for i in range(len(symbols)):
        trace_bars = ", ".join(f"{v:.3f}" for v in test.trace_critical[i])
        eigen_bars = ", ".join(f"{v:.3f}" for v in test.eigen_critical[i])
        lines.append(
            f"    r <= {i}  trace {test.trace[i]:>9.6f} against {trace_bars}"
            f"   eigen {test.eigen[i]:>9.6f} against {eigen_bars}"
        )
    lines.append("    eigenvalues  " + ", ".join(f"{v:.8f}" for v in test.eigenvalues))
    return lines


def report(members: list[VintageEntry], result: GoldMinersOil) -> None:
    """Print the vintage, each claim's verdict, every test's table and the rows beside them."""
    print("GLD, GDX and USO around July 2008, Algorithmic Trading's location 1922")
    print(f"  vintage  {panel_line(members)}: {', '.join(m.symbol for m in members)}")
    for name, days in result.days.items():
        print(f"  {name:<7}  {days[0].date()} to {days[-1].date()}, {len(days)} trading days")
    print(f"  test     johansen(., {JOHANSEN_P}, {JOHANSEN_K}), judged at {LEVEL}%")
    print()
    print(f"  {'#':>2}  {'Claim':<36} {'Statistic':<9} {'Holds when':<10} Found      Verdict")
    for row in CLAIM_ROWS:
        verdict = "reproduced" if result.holds(row) else "did not reproduce"
        print(
            f"  {row.row:>2}  {row.label:<36} {row.statistic:<9} {row.criterion:<10} "
            f"{result.found(row):<10} {verdict}"
        )
    print()
    print("  Relations found, counting rejected nulls up to the first that is not")
    for name in ("before", "after", "triplet", "control"):
        test = getattr(result, name)
        print(f"    {name:<8} trace  {_counts(test, 'trace')}")
        print(f"    {name:<8} eigen  {_counts(test, 'eigen')}")
    print()
    print("  Each test, critical values at 90, 95 and 99 percent")
    for line in (
        _table("before", result.before, PAIR)
        + _table("after", result.after, PAIR)
        + _table("triplet", result.triplet, TRIPLET)
        + _table("control", result.control, PAIR)
    ):
        print(line)
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    print(
        "  triplet's first eigenvector, rows GLD, GDX, USO  "
        + ", ".join(f"{v:.6f}" for v in result.triplet.eigenvectors[:, 0])
    )
    print(
        f"  CADF t-statistic of GLD on GDX, against {EG_CRIT_N2['5%']} at 95% and "
        f"{EG_CRIT_N2['1%']} at 99%"
    )
    for name, cadf in result.cadf.items():
        print(f"    {name:<7}  {cadf.t:.6f} on {cadf.nobs} observations")
    print(f"  ADF with a constant and one lag, each alone, against {ADF_CRIT_CONST['10%']} at 90%")
    for name, stats in result.adf.items():
        print(f"    {name:<7}  " + ", ".join(f"{s} {t:.6f}" for s, t in stats.items()))
    print()
    print(
        "  Exploratory. The split and the third ETF were chosen after the break was "
        "seen. docs/replication-log.md carries the verdicts."
    )


def run(data_dir: Path | None = None) -> GoldMinersOil:
    """Read the three ETFs, guard them, run the tests, and print the report."""
    members, closes = read_sources(data_dir)
    result = gold_miners_oil(closes)
    report(members, result)
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="GLD, GDX and USO around July 2008, Algorithmic Trading's Johansen tests"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.pead.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
