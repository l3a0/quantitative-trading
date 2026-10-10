"""TU momentum traded on the lagged roll return, *Algorithmic Trading*'s revision of Example 6.1.

Chapter 6 explains futures momentum by the roll return keeping its sign for
long stretches. If that is the cause, the roll return itself should be a
cleaner signal than the past total return Example 6.1 trades. Location 2690
tests it on TU, the two-year Treasury note future: go long when the lagged
roll return is above a threshold, short when it is below the negative of it,
and stay flat otherwise. With "a threshold of an annualized roll return of 3
percent" the book reports "a higher APR of 2.5 percent and Sharpe ratio of 2.1
from January 2, 2009, to August 13, 2012, with a reduced maximum drawdown of
1.1 percent". No script ships for it, so the rule below is a declaration
rather than a transcription. It landed here for
[issue 353](https://github.com/l3a0/quantitative-trading/issues/353).

**The declared rule.** Five choices, each from the issue's plan.

1. γ is :func:`chan.roll_returns.roll_returns` on the TU strip, Example 5.3's
   fit in the script's column units. :func:`chan.roll_returns.roll_returns_in_months`
   is a third of it on every row of TU, to rounding, because every contract is a quarter from the
   next, and it never reaches 0.03 in the window. So the column units are what
   the data allows rather than a preference.
2. :func:`roll_signals` reads today's γ: ``longs = γ > 0.03`` and
   ``shorts = γ < −0.03``, both strict, with a NaN comparison false.
3. The position is ``longs − shorts`` and the return is
   ``backshift(1, pos) · held_returns`` with NaN set to 0, ``TU_mom.m``'s own
   convention, so the position earns the day after its signal.
4. Every series is computed on the strip's full index of 5,565 rows, and the
   cut to 2009-01-02 to 2012-08-13, 913 rows, comes last.
5. The figures are ``TU_mom.m``'s arithmetic through
   :func:`chan.tu_momentum.figures`: the Sharpe ratio is
   ``√252 · smartmean / smartstd``, the APR is the compounded one, and the
   maximum drawdown is ``calculateMaxDD(cumprod(1 + ret) − 1)``, which is zero
   or less and is set against the book's 1.1 percent as −100 times itself.

**The declaration came after the scratch runs.** The issue said these choices
had to be declared before any figure was computed, and that did not happen.
Two scratch runs read about 90 variants first, across lags, held contracts,
units, thresholds and roll rules. The declaration therefore rests on prior
grounds the runs did not choose: Example 6.1's convention for the lag, Example
6.1's series for what the position earns, and the 2012-05-11 save for the roll
row. Rows 1 to 3 miss the book under it, and the run tries no second rule.

**The rebuild and its check.** The position earns Example 6.1's series, the
continuous front-contract close. No committed save of that series covers the
whole window, since the four OHLC saves end in May 2012, so :func:`held_returns`
rebuilds it from the strip. With L a contract's last priced row, row t earns
``close(t) / close(t−1) − 1`` of the nearest contract that was priced at t−1
and has L − t ≥ 7, where a contract still priced on the file's last row counts
as never expiring. The old contract therefore earns through row L − 7 and the
new one from row L − 6. That roll row was read from the 2012-05-11 save, which
follows the old contract through L − 8 and the new one from L − 6 and jumps by
the adjustment on L − 7. :func:`adjusted_level` adds up the same contract's
price changes, which is what Example 6.1's signal reads.
:func:`check_against_save` sets the rebuild against that save over the 1,999
changes they share, and ``tests/test_roll_momentum.py`` pins how closely they
agree and that every change differing by more than the save's rounding falls on
row L − 7.

**Example 6.1 runs on the same series for the comparison.** The book's
"higher" and "reduced" compare against Example 6.1, whose printed figures sit
on another window and another save. So Example 6.1's rule is run on the
rebuild through :func:`chan.tu_momentum.signals`,
:func:`chan.tu_momentum.positions` and
:func:`chan.tu_momentum.strategy_returns`, whose contract this module leaves as
it found it, and rows 4 to 6 compare the two rules on one series with one
arithmetic.

**The fifth-contract reading is set aside.** Holding the fifth contract priced
the day before, the farthest of the five γ is fitted on, lands nearer the
book than the declared rule does. It came out of the scratch search, and a
scratch fit of γ on the four nearest contracts, which no test here repeats,
lowered its Sharpe ratio. So the match leans on γ moving against the traded
contract's own price that day. :func:`fifth_contract_returns` computes it for
one row beside the replication, and it is never the verdict.

**Nothing is ported.** No script ships for location 2690, and the sibling
search on the issue found no roll-return signal to bring over. Everything
reused comes from this repo's own modules.

**The vintage.** ``inputdatadaily_tu_20120813/``, chan-mat, raw, saved
2012-08-14, 93 contracts and ``TU-SPOT`` over 5,565 days from 1990-06-22 to
2012-08-13, read through :func:`chan.roll_returns.load_strip`, which runs the
scale-break guard on each member's own rows. The 2012-05-11 save is read
through :func:`chan.tu_momentum.read_sources`, which guards TU over its span.
Every return here is taken within one contract, so no window-level guard call
is added.

Every result here is exploratory. The declaration was made after the scratch
runs, so this cannot count as a registered test of the roll-return signal. A
registered test would declare its rule before any reading and run it on data
this search never loaded.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray

from chan.khandani_lo_book_two import gap, matches
from chan.matlab_helpers import backshift
from chan.roll_returns import (
    NEAREST,
    SOURCE_FILES,
    Strip,
    load_strip,
    roll_returns,
    roll_returns_in_months,
)
from chan.series import WindowCrossesScaleBreak, panel_line, vintage_line
from chan.tu_momentum import BOOK_APR_PERCENT as EXAMPLE_6_1_BOOK_APR_PERCENT
from chan.tu_momentum import BOOK_MAX_DRAWDOWN_PERCENT as EXAMPLE_6_1_BOOK_MAX_DRAWDOWN_PERCENT
from chan.tu_momentum import BOOK_SHARPE as EXAMPLE_6_1_BOOK_SHARPE
from chan.tu_momentum import (
    Figures,
    figures,
    market_returns,
    positions,
    read_sources,
    signals,
    strategy_returns,
    tu_momentum,
)
from chan.vintage import VintageEntry, VintageUnavailable

ROOT = "TU"
SOURCE_FILE = SOURCE_FILES[ROOT]
#: The rows before a contract's last priced row on which the position rolls to the next.
ROLL_ROWS = 7
#: Location 2690's "annualized roll return of 3 percent".
THRESHOLD = 0.03
WINDOW_START = pd.Timestamp("2009-01-02")
WINDOW_END = pd.Timestamp("2012-08-13")
#: Both the 2012-05-11 save and the strip print four decimals, so rounding can
#: move each file's change by up to 1e-4. The two changes off the roll row stay
#: within 1e-4 of each other here, and the roll row's jumps are far larger, so a
#: difference past this is more than rounding. ``TestTheRebuildAgainstTheSave``
#: holds both sides of that gap.
SAVE_ROUNDING = 1.5e-4
#: Location 2690.
BOOK_APR_PERCENT = "2.5"
BOOK_SHARPE = "2.1"
BOOK_MAX_DRAWDOWN_PERCENT = "1.1"


def _last_priced_rows(contracts: pd.DataFrame) -> NDArray[np.float64]:
    """Each column's last priced row, infinite for a column still priced on the file's last row."""
    priced = np.isfinite(contracts.to_numpy(dtype=float))
    rows = len(priced)
    last = np.full(priced.shape[1], -np.inf)
    for column in range(priced.shape[1]):
        held = np.flatnonzero(priced[:, column])
        if held.size:
            last[column] = np.inf if held[-1] == rows - 1 else held[-1]
    return last


def _held_columns(contracts: pd.DataFrame, roll_rows: int) -> NDArray[np.int_]:
    """The column each row earns on, −1 on the first row and on any row no contract qualifies."""
    if roll_rows < 0:
        raise ValueError(f"the roll comes at least 0 rows before expiry, not {roll_rows}")
    priced = np.isfinite(contracts.to_numpy(dtype=float))
    rows = np.arange(1, len(priced))[:, None]
    qualifies = priced[:-1] & (_last_priced_rows(contracts)[None, :] - rows >= roll_rows)
    held = np.where(qualifies.any(axis=1), qualifies.argmax(axis=1), -1)
    return np.concatenate([[-1], held])


def held_contracts(contracts: pd.DataFrame, roll_rows: int = ROLL_ROWS) -> pd.Series:
    """The contract each row's return is taken on, ``None`` where there is none."""
    held = _held_columns(contracts, roll_rows)
    names = [contracts.columns[c] if c >= 0 else None for c in held]
    return pd.Series(names, index=contracts.index, name="held", dtype=object)


def _held_prices(contracts: pd.DataFrame, roll_rows: int) -> tuple[NDArray, NDArray]:
    """Each row's close and the close the row before, both of the contract that row holds."""
    prices = contracts.to_numpy(dtype=float)
    held = _held_columns(contracts, roll_rows)
    today = np.full(len(prices), np.nan)
    before = np.full(len(prices), np.nan)
    rows = np.flatnonzero(held >= 0)
    today[rows] = prices[rows, held[rows]]
    before[rows] = prices[rows - 1, held[rows]]
    return today, before


def held_returns(contracts: pd.DataFrame, roll_rows: int = ROLL_ROWS) -> pd.Series:
    """The rebuilt front-contract return, ``close(t) / close(t−1) − 1`` within the held contract.

    The held contract on row t is the nearest one priced at t−1 with at least
    ``roll_rows`` rows left to its last priced row, or the one still trading on
    the file's last row. The first row is NaN, and so is a row no contract
    qualifies for or a row on which the held contract, priced at t−1, has no
    price at t. TU's strip has none of the last kind.
    """
    today, before = _held_prices(contracts, roll_rows)
    with np.errstate(invalid="ignore", divide="ignore"):
        returns = today / before - 1
    return pd.Series(returns, index=contracts.index, name="held_return")


def adjusted_level(contracts: pd.DataFrame, roll_rows: int = ROLL_ROWS) -> pd.Series:
    """The running sum of the held contract's price changes, 0 on the first row.

    It is an additive back-adjustment with no anchor, which is all Example
    6.1's signal and the check against the save need, since both read
    differences. A row with no change, as where no contract qualifies, adds 0.
    """
    today, before = _held_prices(contracts, roll_rows)
    change = np.nan_to_num(today - before, nan=0.0)
    return pd.Series(np.cumsum(change), index=contracts.index, name="adjusted_level")


def roll_signals(
    gamma: ArrayLike, threshold: float = THRESHOLD
) -> tuple[NDArray[np.bool_], NDArray[np.bool_]]:
    """``longs`` where γ is above ``threshold`` and ``shorts`` below its negative, both strict.

    A NaN γ compares false, so it opens neither.
    """
    g = np.asarray(gamma, dtype=float)
    with np.errstate(invalid="ignore"):
        return g > threshold, g < -threshold


def roll_position(longs: ArrayLike, shorts: ArrayLike) -> NDArray[np.float64]:
    """``longs − shorts``, one contract long, one short or flat."""
    return np.asarray(longs, dtype=float) - np.asarray(shorts, dtype=float)


def rule_returns(position: ArrayLike, market: ArrayLike) -> NDArray[np.float64]:
    """``backshift(1, pos) · market`` with NaN set to 0, so a position earns the next row."""
    held = np.asarray(position, dtype=float)
    returns = np.asarray(market, dtype=float)
    if held.shape != returns.shape:
        raise ValueError(
            f"rule_returns takes a position and a market return of one shape, not "
            f"{held.shape} and {returns.shape}"
        )
    daily = backshift(1, held) * returns
    return np.where(np.isnan(daily), 0.0, daily)


def fifth_contract_returns(contracts: pd.DataFrame, on_both_days: bool = False) -> pd.Series:
    """The return of the fifth nearest priced contract, the farthest of the five γ is fitted on.

    The fifth is counted among the contracts priced at t−1, so it is the
    contract the day's signal was fitted on. With ``on_both_days`` it is
    counted among the contracts priced at both t−1 and t instead, which skips
    a nearer contract that stopped trading at t−1. The first row is NaN, and
    so is a row with fewer than five to count.
    """
    prices = contracts.to_numpy(dtype=float)
    priced = np.isfinite(prices)
    returns = np.full(len(prices), np.nan)
    for t in range(1, len(prices)):
        counted = priced[t - 1] & priced[t] if on_both_days else priced[t - 1]
        columns = np.flatnonzero(counted)
        if len(columns) >= NEAREST:
            fifth = columns[NEAREST - 1]
            returns[t] = prices[t, fifth] / prices[t - 1, fifth] - 1
    return pd.Series(returns, index=contracts.index, name="fifth_return")


@dataclass(frozen=True)
class RollMomentum:
    """Both rules and the readings beside them on the strip's full index, row for row.

    The ``*_figures`` properties read the window only, which is the cut the
    declared rule makes last.
    """

    days: pd.DatetimeIndex
    gamma: NDArray[np.float64]
    gamma_in_months: NDArray[np.float64]
    market: NDArray[np.float64]
    level: NDArray[np.float64]
    position: NDArray[np.float64]
    daily: NDArray[np.float64]
    example_positions: NDArray[np.float64]
    example_daily: NDArray[np.float64]
    fifth_daily: NDArray[np.float64]
    fifth_on_both_days_daily: NDArray[np.float64]

    @property
    def window(self) -> NDArray[np.bool_]:
        return np.asarray((self.days >= WINDOW_START) & (self.days <= WINDOW_END))

    @property
    def window_days(self) -> pd.DatetimeIndex:
        return self.days[self.window]

    @property
    def figures(self) -> Figures:
        """The declared rule over the window, rows 1 to 3."""
        return figures(self.daily[self.window])

    @property
    def example_figures(self) -> Figures:
        """Example 6.1's rule on the same series and rows, what rows 4 to 6 compare against."""
        return figures(self.example_daily[self.window])

    @property
    def example_cut_first_figures(self) -> Figures:
        """Example 6.1's rule with the window cut before any series is computed."""
        level = self.level[self.window]
        held = positions(*signals(level))
        return figures(strategy_returns(held, self.market[self.window]))

    @property
    def fifth_figures(self) -> Figures:
        return figures(self.fifth_daily[self.window])

    @property
    def fifth_on_both_days_figures(self) -> Figures:
        return figures(self.fifth_on_both_days_daily[self.window])

    @property
    def held_position(self) -> NDArray[np.float64]:
        """The position each window row earns on, the one set the row before."""
        return backshift(1, self.position)[self.window]

    @property
    def month_position(self) -> NDArray[np.float64]:
        """The position the month-unit γ would take on each window row."""
        return roll_position(*roll_signals(self.gamma_in_months))[self.window]


def roll_momentum(strip: Strip, roll_rows: int = ROLL_ROWS) -> RollMomentum:
    """Run the declared rule, Example 6.1's rule and the fifth-contract reading on one strip."""
    contracts = strip.contracts
    gamma = roll_returns(contracts).to_numpy()
    market = held_returns(contracts, roll_rows).to_numpy()
    level = adjusted_level(contracts, roll_rows).to_numpy()
    position = roll_position(*roll_signals(gamma))
    example_positions = positions(*signals(level))
    return RollMomentum(
        days=contracts.index,
        gamma=gamma,
        gamma_in_months=roll_returns_in_months(contracts).to_numpy(),
        market=market,
        level=level,
        position=position,
        daily=rule_returns(position, market),
        example_positions=example_positions,
        example_daily=strategy_returns(example_positions, market),
        fifth_daily=rule_returns(position, fifth_contract_returns(contracts).to_numpy()),
        fifth_on_both_days_daily=rule_returns(
            position, fifth_contract_returns(contracts, on_both_days=True).to_numpy()
        ),
    )


@dataclass(frozen=True)
class SaveCheck:
    """The rebuild against the 2012-05-11 save, and both rules on each over the rows they share.

    ``revised_on_save`` and ``example_on_save`` run each rule on the save's own
    close with ``chan.tu_momentum.market_returns`` as the return, and the two
    ``*_on_rebuild`` fields run them on the rebuild over the same rows.
    """

    changes: int
    correlation: float
    beyond_rounding: int
    beyond_rounding_on_jump_row: int
    revised_on_save: Figures
    example_on_save: Figures
    revised_on_rebuild: Figures
    example_on_rebuild: Figures
    shared_window_rows: int


def check_against_save(
    strip: Strip, result: RollMomentum, save: pd.Series, roll_rows: int = ROLL_ROWS
) -> SaveCheck:
    """Set the rebuild against the save's close on every day the save holds."""
    span = np.asarray(result.days.isin(save.index))
    if not result.days[span].equals(save.index):
        raise ValueError("the save holds a day the strip does not, so the rows cannot be paired")
    rows = np.flatnonzero(span)[1:]
    closes = save.to_numpy(dtype=float)
    save_change = np.diff(closes)
    rebuild_change = np.diff(result.level[span])
    beyond = np.abs(save_change - rebuild_change) > SAVE_ROUNDING
    held = _held_columns(strip.contracts, roll_rows)
    last = _last_priced_rows(strip.contracts)
    on_jump_row = int(sum(last[held[t]] - t == roll_rows for t in rows[beyond]))
    save_market = market_returns(closes)
    correlation = float(np.corrcoef(save_market[1:], result.market[rows])[0, 1])
    shared = save.index >= WINDOW_START
    revised_on_save = rule_returns(result.position[span], save_market)
    window = span & result.window
    return SaveCheck(
        changes=len(save_change),
        correlation=correlation,
        beyond_rounding=int(beyond.sum()),
        beyond_rounding_on_jump_row=on_jump_row,
        revised_on_save=figures(revised_on_save[shared]),
        example_on_save=tu_momentum(save).active_line_figures,
        revised_on_rebuild=figures(result.daily[window]),
        example_on_rebuild=figures(result.example_daily[window]),
        shared_window_rows=int(shared.sum()),
    )


def _verdict(value: float, printed: str) -> str:
    return (
        "reproduced"
        if matches(value, printed)
        else f"did not reproduce, gap {gap(value, printed):+g}"
    )


def margins(result: RollMomentum) -> tuple[float, float, float]:
    """Rows 4 to 6: how far the declared rule beats Example 6.1 on the APR, Sharpe and drawdown.

    Each is positive when the claim holds. The drawdown's is Example 6.1's
    magnitude less the declared rule's, so a smaller drawdown is a positive
    margin.
    """
    revised, example = result.figures, result.example_figures
    return (
        revised.apr - example.apr,
        revised.sharpe - example.sharpe,
        abs(example.max_drawdown) - abs(revised.max_drawdown),
    )


def _claim(margin: float) -> str:
    return "reproduced" if margin > 0 else "did not reproduce"


def _three(found: Figures) -> str:
    return (
        f"APR {100 * found.apr:.6f} percent, Sharpe ratio {found.sharpe:.6f}, maximum "
        f"drawdown {100 * found.max_drawdown:.4f} percent"
    )


def report(
    strip: Strip,
    result: RollMomentum,
    save_entry: VintageEntry,
    check: SaveCheck,
) -> None:
    """Print the vintage, the six rows with their verdicts, and the rows beside them."""
    found = result.figures
    days = result.window_days
    print("TU momentum traded on the lagged roll return, Algorithmic Trading's location 2690")
    print(f"  vintage  {panel_line(strip.members)}")
    print(
        f"  window   {days[0].date()} to {days[-1].date()}, {len(days)} trading days, cut from "
        f"{len(result.days)} rows after every series is computed"
    )
    print(
        f"  rule     long when the column-unit roll return is above {THRESHOLD}, short below "
        f"-{THRESHOLD}, held the next day, on the front contract rolled {ROLL_ROWS} rows "
        "before its last price"
    )
    print()
    rows = [
        ("APR percent", 100 * found.apr, BOOK_APR_PERCENT),
        ("Sharpe ratio", found.sharpe, BOOK_SHARPE),
        ("Maximum drawdown percent", -100 * found.max_drawdown, BOOK_MAX_DRAWDOWN_PERCENT),
    ]
    print(f"  {'Figure':<32} {'Computed':>12}  {'Chan':>6}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<32} {value:>12.6f}  {printed:>6}  {_verdict(value, printed)}")
    example = result.example_figures
    apr, sharpe, drawdown = margins(result)
    print()
    print("  The claims against Example 6.1's rule on the same series and rows")
    print(f"  {'Claim':<32} {'Revised':>12} {'Example 6.1':>12} {'Margin':>10}  Verdict")
    for label, revised, against, margin in (
        ("Higher APR", found.apr, example.apr, apr),
        ("Higher Sharpe ratio", found.sharpe, example.sharpe, sharpe),
        ("Reduced maximum drawdown", found.max_drawdown, example.max_drawdown, drawdown),
    ):
        print(f"  {label:<32} {revised:>12.6f} {against:>12.6f} {margin:>+10.6f}  {_claim(margin)}")
    print()
    print("Beside the replication. No book prints these, so none carries a verdict.")
    print(
        f"  the book's own comparison, Example 6.1's printed figures on 2004-06-01 to 2012-05-11: "
        f"APR {EXAMPLE_6_1_BOOK_APR_PERCENT} percent, Sharpe ratio {EXAMPLE_6_1_BOOK_SHARPE}, "
        f"maximum drawdown {EXAMPLE_6_1_BOOK_MAX_DRAWDOWN_PERCENT} percent"
    )
    print(
        f"  Example 6.1 with the window cut first, APR {result.example_cut_first_figures.apr:.6f}"
    )
    print(f"  the 2012-05-11 save, {vintage_line(save_entry)}")
    print(
        f"    the rebuild against it over {check.changes} changes: return correlation "
        f"{check.correlation:.6f}, {check.beyond_rounding} changes differ by more than "
        f"{SAVE_ROUNDING:g}, {check.beyond_rounding_on_jump_row} of them on row L - {ROLL_ROWS}"
    )
    print(f"    over the {check.shared_window_rows} window rows the save covers")
    print(f"      revised rule on the save     {_three(check.revised_on_save)}")
    print(f"      revised rule on the rebuild  {_three(check.revised_on_rebuild)}")
    print(f"      Example 6.1 on the save      {_three(check.example_on_save)}")
    print(f"      Example 6.1 on the rebuild   {_three(check.example_on_rebuild)}")
    held = result.held_position
    print(
        f"  long on {int((held > 0).sum())} of {len(held)} rows, "
        f"{100 * (held > 0).mean():.2f} percent, short on {int((held < 0).sum())}, "
        f"{int((np.diff(held) != 0).sum())} changes of position"
    )
    gamma = pd.Series(result.gamma, index=result.days)
    print(
        "  gamma on 2008-12-31 "
        f"{gamma.loc['2008-12-31']:.7f}, and on 2009-01-02, 01-05 and 01-06 "
        + ", ".join(f"{gamma.loc[day]:.1e}" for day in ("2009-01-02", "2009-01-05", "2009-01-06"))
    )
    print(
        f"  gamma's window mean {np.nanmean(result.gamma[result.window]):.6f}, the month-unit "
        f"gamma's window peak {np.nanmax(result.gamma_in_months[result.window]):.5f}, "
        f"month-unit position flat on {int((result.month_position == 0).sum())} of "
        f"{len(held)} rows"
    )
    print(f"  the fifth contract priced the day before, {_three(result.fifth_figures)}")
    print(
        "  the fifth of those priced on both days, Sharpe ratio "
        f"{result.fifth_on_both_days_figures.sharpe:.6f}"
    )
    print()
    print("  Annualised over 252 days with no risk-free rate and no cost, on raw contract prices.")
    print("  Exploratory. docs/replication-log.md Entry 35 carries the verdicts.")


def run(data_dir: Path | None = None) -> tuple[RollMomentum, SaveCheck]:
    """Read the strip and the save, guard both, run both rules, and print the report."""
    strip = load_strip(ROOT, data_dir)
    save_entry, save = read_sources(data_dir)
    result = roll_momentum(strip)
    check = check_against_save(strip, result, save)
    report(strip, result, save_entry, check)
    return result, check


def main() -> None:
    argparse.ArgumentParser(
        description="TU momentum traded on the lagged roll return, location 2690 of "
        "Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.price_spread.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
