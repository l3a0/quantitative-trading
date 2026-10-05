"""Spot and roll returns of five futures, *Algorithmic Trading*'s Example 5.3.

A future's total return splits into the move of the spot price under it and
the return it earns by converging on that spot as it nears expiry, which is
the roll return. Chan's Example 5.3, at Kindle location 2399, assumes both are
constant and estimates each by linear regression for five futures: the
Brazilian real (BR), corn (C), WTI crude (CL), copper (HG) and the two-year
Treasury note (TU). The book uses the result, Table 5.1, to explain why some
futures trend and others do not, and Chapter 6 leans on it twice.

1. **The spot return α** comes from regressing the log spot price on time.
2. **The roll return γ** comes from regressing, on one day, the log prices of
   the contracts then trading against their time to maturity, "measured in
   months", so it varies slowly from day to day.

**The transcription.** Every step is Chan's ``estimateFuturesReturns.m``, read
under ``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, git blob ``1a70a28``. It reads one strip at a time, and its column named ``0000$`` is
the spot, which here is the member ``<root>-SPOT``.

1. :func:`spot_return` is 252 times the slope of ``log(spot)`` on
   ``T = 1, 2, ..., N``, the row number over the strip's every day. The script
   drops the rows where the spot is not finite and keeps each surviving row's
   original number, so a gap in the spot still counts as elapsed days.
2. :func:`roll_returns` lists, on each row, the contract columns with a finite
   price, in column order. It fits only when there are at least five and the
   first five are adjacent columns, regressing their log prices on
   ``1, 2, 3, 4, 5`` and setting ``gamma(t) = -12 * slope``. Every other row
   is NaN.
3. The script prints ``Average annualized spot return=%f`` and ``Average
   annualized roll return=%f``, the second being the mean of γ over the rows
   where it is defined, which is :func:`chan.matlab_helpers.smartmean`.

Each slope is one :func:`numpy.linalg.lstsq` call on the variable and a column
of ones, the fit ``ols(y, [T ones])`` makes, as :mod:`chan.pca_factor` does.
The script's ``fwdshift`` on the list of priced columns tests adjacency, which
:func:`numpy.diff` on those indices does directly.

**The script measures maturity in columns, not months.** The ``-12``
annualizes on the assumption that adjacent columns are one month apart. That
holds for BR and CL, whose contracts are monthly. It does not hold for C,
whose contracts run two or three months apart, for HG, whose strip mixes
monthly and wider gaps, or for TU, whose contracts are quarterly. The book's
text says months and the script's arithmetic says columns. The reproduction
runs the script's arithmetic, because that is what printed Table 5.1.
:func:`roll_returns_in_months` runs the same fit on the same five prices with
each contract's month offset from the nearest one as the regressor, and the
report prints it beside the replication with no verdict, because Chan printed
no figure for it.

**Chan's 2018 Python port agrees on C.** ``estimateFuturesReturns.py``, in the
``PythonCodesAndData.zip`` that ``data/README.md`` records, reads the C2 strip
and prints both figures in full in its comments, which :data:`PORT_C2` holds.
Its rule is the MATLAB script's, row number for row number.

**Two of Table 5.1's ten cells do not reproduce.** HG's α and TU's α miss on
Chan's own saved file, and ``TestTheFigures`` in ``tests/test_roll_returns.py``
says by how much. Three readings were tried after the miss, and
``TestTheReadingsTriedAfterTheMiss`` pins each. Regressing on calendar days
lands HG's cell and still misses TU's, and it moves C's α off the figure the
Python port printed, so the specification stays the script's row number.

**The vintage.** The five strips :data:`SOURCE_FILES` names, vendor
``chan-mat``, basis ``raw``, saved 2012-08-14, one vintage per contract and one
for the spot, read through :func:`chan.series.load_panel`. Its index is the
union of the members' days, which is the file's own ``tday``, so the panel's
row number is the script's. Table 5.1's C is the C2 strip.

**The scale-break guard runs on each member's own rows.** :func:`load_strip`
calls :func:`chan.series.refuse_window_crossing_a_break` on the spot and on
every contract, reading each as ``closes[symbol].dropna()`` over its own first
and last day. A contract's panel column is NaN on every day before it listed
and after it expired, so passing the columns over the strip's span would have
the guard report a day with no readable move on every strip. Over a restart
gap the guard compares the settlements on either side, which is the move a
holder would see, and it flags none.
[Issue 347](https://github.com/l3a0/quantitative-trading/issues/347) decided
this, and ``TestTheScaleBreakDecision`` in ``tests/test_roll_returns.py`` holds
both halves.

**What two later experiments import.** :data:`ROOTS`, :func:`load_strip`,
:func:`spot_return`, :func:`roll_returns` and :func:`roll_returns_in_months`
are the contract that
[issue 348](https://github.com/l3a0/quantitative-trading/issues/348) and
[issue 353](https://github.com/l3a0/quantitative-trading/issues/353) build
against. :func:`roll_returns` keeps its NaN rows in place, because Example 5.4
fills the full-length series and dropping them would lose the alignment.

**What changed on the way over.** Three things, and none moves a figure.

1. The strips are read as committed vintages through :func:`load_strip`
   rather than loaded from the ``.mat``.
2. The script reads one strip per run, chosen by editing its load line. This
   runs all five in Table 5.1's order.
3. The plots are not carried. Figures 5.4 and 5.5 belong to the write-up.

Every result here is exploratory. Reproducing Table 5.1 spends Chan's 1986 to
2012 strips on a model he chose, so the run says whether his numbers reproduce
on his file and nothing about whether a roll return persists out of sample.
The month-spaced γ is a reading of the book's text, declared on issue 347
before the build, and is exploratory too.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.matlab_helpers import smartmean
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The five roots in Table 5.1's order. Table 5.1's C is the C2 strip.
ROOTS = ("BR", "C2", "CL", "HG", "TU")
#: Each root's strip, the file the script's load line names.
SOURCE_FILES = {root: f"inputDataDaily_{root}_20120813.mat" for root in ROOTS}
#: Table 5.1 at location 2399, α and γ in percent at one decimal. TU's α is
#: printed as −0.0, a negative number that rounds to zero, so it is kept as
#: ``-0.0`` with its sign.
BOOK_TABLE_5_1 = {
    "BR": (-2.7, 10.8),
    "C2": (2.8, -12.8),
    "CL": (7.3, -7.1),
    "HG": (5.0, 7.7),
    "TU": (-0.0, 3.2),
}
#: What ``estimateFuturesReturns.py`` prints in its comments for the C2 strip,
#: the spot return and then the roll return.
PORT_C2 = ("0.02805562210100287", "-0.12775650227459556")
#: The trading days a year the spot return is annualized by.
DAYS_PER_YEAR = 252
#: The months a year the roll return is annualized by.
MONTHS_PER_YEAR = 12
#: How many of the nearest priced contracts each day's fit reads.
NEAREST = 5
#: CME's month letters, January first. They run alphabetically in calendar
#: order, which is why a sorted strip is Chan's contract order.
MONTH_LETTERS = "FGHJKMNQUVXZ"


@dataclass(frozen=True)
class Strip:
    """One strip's members, its spot and its contracts, all on the file's ``tday``.

    ``spot`` and ``contracts`` hold every day of the strip, with NaN where a
    column was not priced. ``contracts`` holds the contract columns in Chan's
    order with the spot removed.
    """

    root: str
    members: list[VintageEntry]
    spot: pd.Series
    contracts: pd.DataFrame


@dataclass(frozen=True)
class StripReturns:
    """One strip's spot return and its two roll-return series, row for row."""

    strip: Strip
    alpha: float
    gamma: pd.Series
    gamma_in_months: pd.Series

    @property
    def mean_gamma(self) -> float:
        """The script's second printed figure, the mean of γ where it is defined."""
        return float(smartmean(self.gamma.to_numpy()))

    @property
    def mean_gamma_in_months(self) -> float:
        return float(smartmean(self.gamma_in_months.to_numpy()))


def _slope(y: np.ndarray, x: np.ndarray) -> float:
    """The slope of ``ols(y, [x ones])``."""
    design = np.column_stack([x, np.ones(len(x))])
    return float(np.linalg.lstsq(design, y, rcond=None)[0][0])


def contract_month(symbol: str) -> int:
    """A contract's delivery month counted from year 0, read off ``<root>-<year><letter>``."""
    contract = symbol.rsplit("-", 1)[-1]
    if len(contract) != 5 or not contract[:4].isdigit() or contract[4] not in MONTH_LETTERS:
        raise ValueError(f"{symbol} does not name a contract as <root>-<year><month letter>")
    return int(contract[:4]) * 12 + MONTH_LETTERS.index(contract[4])


def spot_return(spot: pd.Series) -> float:
    """252 times the slope of the log spot on its row number, Chan's α.

    The rows are numbered 1 to N over the full index before the ones whose
    spot is not finite are dropped, so a gap still counts as elapsed days.
    """
    values = np.asarray(spot, dtype=float)
    rows = np.arange(1, len(values) + 1, dtype=float)
    priced = np.isfinite(values)
    if priced.sum() < 2:
        raise ValueError("spot_return needs at least two priced days to fit a slope")
    return DAYS_PER_YEAR * _slope(np.log(values[priced]), rows[priced])


def _nearest_adjacent(prices: np.ndarray) -> np.ndarray | None:
    """The column positions of the five nearest priced contracts, when they are adjacent.

    ``None`` when fewer than five are priced or the first five skip a column,
    which is when the script leaves γ NaN.
    """
    priced = np.flatnonzero(np.isfinite(prices))
    if len(priced) < NEAREST:
        return None
    nearest = priced[:NEAREST]
    if not (np.diff(nearest) == 1).all():
        return None
    return nearest


def _fit_each_row(contracts: pd.DataFrame, maturities: np.ndarray | None) -> pd.Series:
    """γ on every row: −12 times the slope of the log prices on their maturities.

    ``maturities`` holds each column's month, and ``None`` reads the column
    positions 1 to 5 instead, which is what the script does.
    """
    prices = contracts.to_numpy(dtype=float)
    gamma = np.full(len(prices), np.nan)
    positions = np.arange(1, NEAREST + 1, dtype=float)
    for t, row in enumerate(prices):
        nearest = _nearest_adjacent(row)
        if nearest is None:
            continue
        x = positions if maturities is None else maturities[nearest] - maturities[nearest[0]]
        gamma[t] = -MONTHS_PER_YEAR * _slope(np.log(row[nearest]), x)
    return pd.Series(gamma, index=contracts.index, name="gamma")


def roll_returns(contracts: pd.DataFrame) -> pd.Series:
    """Chan's γ on every row of ``contracts``, NaN where the rule does not fit.

    Each row reads its five nearest priced contracts when they are adjacent
    columns and regresses their log prices on ``1, 2, 3, 4, 5``, so maturity is
    measured in columns. The NaN rows stay in place.
    """
    return _fit_each_row(contracts, None)


def roll_returns_in_months(contracts: pd.DataFrame) -> pd.Series:
    """γ on the same rows as :func:`roll_returns`, with maturity measured in months.

    The regressor is each contract's month offset from the nearest of the five,
    read off its symbol, so the NaN pattern is the same and a strip of monthly
    contracts gives the same series.
    """
    months = np.array([contract_month(symbol) for symbol in contracts.columns], dtype=float)
    return _fit_each_row(contracts, months).rename("gamma_in_months")


def maturity_spacings(contracts: pd.DataFrame) -> Counter[tuple[int, ...]]:
    """How many rows each pattern of month gaps across the five fitted contracts covers."""
    months = np.array([contract_month(symbol) for symbol in contracts.columns])
    found: Counter[tuple[int, ...]] = Counter()
    for row in contracts.to_numpy(dtype=float):
        nearest = _nearest_adjacent(row)
        if nearest is not None:
            found[tuple(int(gap) for gap in np.diff(months[nearest]))] += 1
    return found


def load_strip(root: str, data_dir: Path | None = None) -> Strip:
    """One of the five strips, after the scale-break guard has read every member.

    This is the one read path. It reads the strip through
    :func:`chan.series.load_panel` and runs the guard on each member's own
    rows, from its first settlement to its last, for the reason the module
    docstring gives.
    """
    if root not in SOURCE_FILES:
        raise ValueError(
            f"load_strip reads the five strips of Table 5.1, {', '.join(ROOTS)}, and not {root}"
        )
    members, closes = load_panel(SOURCE_FILES[root], data_dir=data_dir)
    for entry in members:
        own = closes[entry.symbol].dropna()
        if own.empty:
            continue
        refuse_window_crossing_a_break([(entry, own)], start=own.index[0], end=own.index[-1])
    spot_symbol = f"{root}-SPOT"
    if spot_symbol not in closes.columns:
        raise VintageUnavailable(f"{SOURCE_FILES[root]} holds no {spot_symbol} column")
    return Strip(
        root=root,
        members=members,
        spot=closes[spot_symbol],
        contracts=closes.drop(columns=spot_symbol),
    )


def strip_returns(strip: Strip) -> StripReturns:
    """α and both γ series for one strip."""
    return StripReturns(
        strip=strip,
        alpha=spot_return(strip.spot),
        gamma=roll_returns(strip.contracts),
        gamma_in_months=roll_returns_in_months(strip.contracts),
    )


def _book_label(root: str) -> str:
    return "C" if root == "C2" else root


def _percent(figure: float) -> str:
    """A Table 5.1 cell as the book prints it. Python keeps the sign of ``-0.0``."""
    return f"{figure:.1f}%"


def report(results: dict[str, StripReturns]) -> None:
    """Print each strip's figures beside Table 5.1, then the rows beside the replication."""
    print("Spot and roll returns under the constant-returns model, Chan's Example 5.3 in")
    print("Algorithmic Trading")
    for root, result in results.items():
        print(f"  {root:<4} {panel_line(result.strip.members)}")
    print(
        "  rule  alpha is 252 times the slope of log spot on row number. gamma is -12 times "
        "the slope of the five"
    )
    print(
        "        nearest contracts' log prices on columns 1 to 5, where they are adjacent, "
        "averaged where defined."
    )
    print()
    print(f"  {'Symbol':<8} {'alpha':>10} {'Book':>7} {'gamma':>10} {'Book':>7}")
    for root, result in results.items():
        book_alpha, book_gamma = BOOK_TABLE_5_1[root]
        print(
            f"  {_book_label(root):<8} {result.alpha:>10.6f} {_percent(book_alpha):>7} "
            f"{result.mean_gamma:>10.6f} {_percent(book_gamma):>7}"
        )
    print()
    print("  Beside the replication, with no published figure: gamma with maturity in months")
    print(f"  {'Symbol':<8} {'gamma':>10} {'months':>10} {'Days':>6}  {'Span':<24}  Month gaps")
    for root, result in results.items():
        defined = result.gamma.dropna().index
        spacings = maturity_spacings(result.strip.contracts)
        gaps = ", ".join(
            f"{'-'.join(map(str, gap))} on {count}" for gap, count in spacings.most_common()
        )
        print(
            f"  {_book_label(root):<8} {result.mean_gamma:>10.6f} "
            f"{result.mean_gamma_in_months:>10.6f} {len(defined):>6}  "
            f"{defined[0].date()} to {defined[-1].date()}  {gaps}"
        )
    print()
    print(
        "  Exploratory. Reproducing Table 5.1 spends Chan's 1986 to 2012 strips on a model he "
        "chose, so this says"
    )
    print(
        "  whether his numbers reproduce on his file and nothing about whether a roll return "
        "persists."
    )


def run(data_dir: Path | None = None) -> dict[str, StripReturns]:
    """Read the five strips, estimate each one's returns, and print the report."""
    results = {root: strip_returns(load_strip(root, data_dir)) for root in ROOTS}
    report(results)
    return results


def main() -> None:
    argparse.ArgumentParser(
        description="Spot and roll returns of five futures, Example 5.3 of Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the reader as one line, as chan.price_spread
        # does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
