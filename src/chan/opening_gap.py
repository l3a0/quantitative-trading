"""The opening gap strategy on STOXX Europe 50 futures, *Algorithmic Trading*'s Example 7.1.

A stop order rests until the price reaches it, so a market that opens far
from the previous day's range can trigger a crowd of them at once and carry
the move through the day. Chapter 7 of *Algorithmic Trading* calls that one
cause of short-term momentum, and Example 7.1 trades it on FSTX, the STOXX
Europe 50 index future on Eurex, which the book calls the Dow Jones STOXX 50.
Each day the rule compares the open with the previous day's high and low. An
open above the previous high by at least a tenth of the 90-day standard
deviation of daily returns is one kind of jump, an open below the previous
low by the same margin is the other, and the position is held from the open
to the same day's close. Every location below is in
``research/book-notes/algorithmic-trading.md``.

1. **Location 2965** calls the rule "the opposite momentum strategy" to
   Example 4.1's buy-on-gap reversal, "buying when the instrument gaps up,
   and shorting when it gaps down". It reports that the rule "generates an
   annual percentage rate (APR) of 13 percent and a Sharpe ratio of 1.4 from
   July 16, 2004, to May 17, 2012", and names ``gapFutures_FSTX.m``.
2. **Location 2971** is the example's caption, which says the code reads
   ``op``, ``hi``, ``lo`` and ``cl`` and calls ``smartMovingStd`` and
   ``backshift``. It also reports the rule on GBPUSD, for which no data is
   committed here.
3. **Location 3509** calls the same figures, around 13 percent and 1.4, the
   strategy's "annualized average return" and Sharpe ratio, before filtering
   it on the VIX, which Example 7.1 does not do.

**What ``gapFutures_FSTX.m`` holds.** The script is git blob ``02db940``
under ``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, and the same 35 lines sit under ``archived/matlab/`` in
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``4567024``. It loads ``inputDataOHLCDaily_20120517`` and keeps FSTX's
column of ``op``, ``hi``, ``lo`` and ``cl``. Its comment at line 27
records what line 26 printed, ``APR=    0.1327 Sharpe=1.44``. Line 34 prints
the drawdown too, and no comment records a value for it. It landed here for
[issue 358](https://github.com/l3a0/quantitative-trading/issues/358).

**The transcription.** Six steps, each mapped to the function that runs it.
The line numbers are the blob's.

1. **Line 13**, :func:`spread`.
   ``backshift(1, smartMovingStd(calculateReturns(cl, 1), 90))``, so day t
   reads the 90 close-to-close returns ending at t − 1, through book two's
   ``smartstd``, which divides by n. The first 90 rows carry no spread.
2. **Lines 15 and 16**, :func:`qualifiers`. A long qualifies when
   ``op >= backshift(1, hi) · (1 + 0.1 · spread)`` and a short when
   ``op <= backshift(1, lo) · (1 − 0.1 · spread)``. Both tests are
   non-strict, and a comparison with NaN is false, so a day with no spread
   qualifies nothing.
3. **Lines 18 to 21**, :func:`positions`. A long day holds 1 and a short day
   −1. Line 21 assigns the short after the long, so a day qualifying both
   would be short. That needs the previous high no higher than the previous
   low once the margins are added, and no day of this file does it.
4. **Line 23**, :func:`daily_returns`. The script writes
   ``ret = positions .* (op − cl) ./ op``, held from the open to the close.
5. **Line 24.** NaN set to 0, also in :func:`daily_returns`.
6. **Lines 26 to 34**, :func:`figures`. Line 26 prints
   ``prod(1 + ret)^(252 / n) − 1`` over all 2,000 rows, which is
   :func:`chan.khandani_lo_book_two.compounded_apr`, and
   ``mean(ret) · √252 / std(ret)`` with MATLAB's own ``std``. That ``std``
   divides by n − 1, so the ratio is :func:`chan.khandani_lo.plain_sharpe`.
   Neither takes a risk-free rate or a cost. Line 33 runs ``calculateMaxDD``
   on ``cumprod(1 + ret) − 1``, and line 34 prints the drawdown it gives.
   ``252 · mean(ret)`` is computed beside them, because location 3509 calls
   its figure of around 13 percent an annualized average return.

**Two readings of line 23, and the script's figure belongs to the one the
text does not describe.** Line 23 earns ``op − cl`` on a long, so a long
profits when the price falls from the open, which fades the jump rather than
following it. The text describes the opposite sign. So
:func:`daily_returns` takes a ``reading``.

1. ``"literal"`` is line 23 as written, ``positions · (op − cl) / op``. It
   gives an APR of 0.132733 and a Sharpe ratio of 1.441620, which print as
   the comment's ``0.1327`` and ``1.44``.
2. ``"momentum"`` changes that line alone, to
   ``positions · (cl − op) / op``, which is what location 2965 describes. It
   gives an APR of −0.124236 and a Sharpe ratio of −1.441620.

The two Sharpe ratios differ only in sign, because the momentum reading's
daily returns are the literal reading's negated. ``tests/test_opening_gap.py``
pins both readings and holds that the momentum reading misses the book's
13 percent and 1.4. The issue's own title calls the rule momentum, and the
module is named for Chan's caption, "Opening Gap Strategy for FSTX", rather
than for either reading.

**The vintage.** ``inputdataohlcdaily_20120517/fstx.csv``, one column of
Chan's ``inputDataOHLCDaily_20120517.mat``, read through
:func:`chan.series.load_panel` once per field as ``frame["FSTX"].dropna()``.
It is chan-mat, adjusted, saved 2012-05-18, and each of the open, high, low
and close holds 2,000 days from 2004-07-16 to 2012-05-17, exactly the book's
window. :func:`run` also reads FSTX from the 2012-05-11 and 2012-05-07 saves
for two rows beside the replication. Each save holds a different 2,000-day
window. The 2012-05-17 save also restates FSTX's prices, and it is the only
save that lands the comment. ``data/README.md`` records how the saves
differ.

**The scale-break guard runs and refuses nothing.** :func:`read_sources`
calls :func:`chan.series.refuse_window_crossing_a_break` on FSTX's closes
over the save's whole span, as :mod:`chan.tu_momentum` does for TU. FSTX
flags nothing in any of the three saves read here, so nothing is refused.

**What changed on the way over.** Four things, and none moves a figure.

1. FSTX is read as a committed vintage through :func:`chan.series.load_panel`
   rather than loaded from the ``.mat``.
2. ``plot(cumret)`` is not carried. The run draws nothing.
3. The return line takes a ``reading``, and the momentum reading is computed
   beside the script's.
4. The run calls the scale-break guard, which the script has no counterpart
   for.

**Chan's Python port** is ``PythonCodesAndData/gapFutures_FSTX.py`` in
Chan's ``PythonCodesAndData.zip``, the zip ``data/README.md`` names with
sha256 ``91e3d0d534f465feae31da3f6a19db03e32b190cf70a2470f03cde60617f8317``,
in EpchanPreview at ``e4bc46f``. The member is 996 bytes, with sha256
``8b005cee1114fd019ca761c1df7331d5f66ba9a3be8d6dcb2e614b6615a095fc``, dated
2018-12-23 in the zip's central directory. It reads
``inputDataDaily_FSTX_20120517.csv``, whose open, high, low and close equal
the committed file's. It is not committed, and :func:`python_port` carries its
arithmetic. It differs from the script in four places.

1. **The spread.** ``df['Close'].pct_change().rolling(90).std().shift()``
   divides by n − 1, and pandas wants all 90 returns in the window, so the
   first value falls one row later than line 13's, on 2004-11-22.
2. **The short test.** ``shorts=df['Open'] >= df['Low'].shift()*(1-entryZscore*stdretC2C90d)``
   flips line 16's ``<=``. Any open that clears the previous high also clears
   the previous low, so every long day passes it too, and the short is
   assigned after the long. The port is never long.
3. **The sign.** ``ret=positions*(df['Close']-df['Open'])/df['Open']`` is the
   momentum reading, where line 23 writes ``(op-cl)./op``.
4. **The Sharpe ratio.** ``np.std`` on a series divides by n, where line 26's
   ``std`` divides by n − 1.

Its comments print ``#APR=0.074864 Sharpe=0.494857`` and
``#Max DD=-0.233629 Max DDD in days=789``, which :data:`PORT_APR`,
:data:`PORT_SHARPE`, :data:`PORT_MAX_DRAWDOWN` and
:data:`PORT_MAX_DRAWDOWN_DAYS` hold. Under pandas 3 the port prints its first
line and then stops, because ``calculateMaxDD`` indexes the date-indexed
``cumret`` by position, which pandas 3 refuses. So it no longer runs as
shipped, and this is its arithmetic.

Every result here is exploratory. Reproducing Chan's figure spends his 2004
to 2012 sample on his rule, so the run says whether his numbers reproduce on
his file and nothing about whether an opening jump pays today, under either
sign.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray

from chan.buy_on_gap import SPREAD_LOOKBACK, entry_spread
from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.matlab_helpers import backshift, calculate_max_dd
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    refuse_window_crossing_a_break,
    vintage_line,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The save ``gapFutures_FSTX.m`` loads.
SOURCE_FILE = "inputDataOHLCDaily_20120517.mat"
#: The two earlier saves holding FSTX, read for one row each beside the replication.
EARLIER_SAVES = ("inputDataOHLCDaily_20120511.mat", "inputDataOHLCDaily_20120507.mat")
SYMBOL = "FSTX"
#: The four fields the script loads, ``op``, ``hi``, ``lo`` and ``cl``.
FIELDS = ("Open", "High", "Low", "Close")
#: ``entryZscore``, the fraction of the spread the open must clear.
ENTRY_ZSCORE = 0.1
#: The two signs line 23 can take. The first is the script's.
READINGS = ("literal", "momentum")

#: The script's closing comment, ``APR=    0.1327 Sharpe=1.44``.
SCRIPT_APR = "0.1327"
SCRIPT_SHARPE = "1.44"
#: Location 2965's "13 percent" and "1.4".
BOOK_APR_PERCENT = "13"
BOOK_SHARPE = "1.4"
#: Location 2965's window, "from July 16, 2004, to May 17, 2012".
BOOK_FIRST_DAY = pd.Timestamp("2004-07-16")
BOOK_LAST_DAY = pd.Timestamp("2012-05-17")
#: What ``gapFutures_FSTX.py`` prints in its comments, ``#APR=0.074864 Sharpe=0.494857``
#: and ``#Max DD=-0.233629 Max DDD in days=789``.
PORT_APR = "0.074864"
PORT_SHARPE = "0.494857"
PORT_MAX_DRAWDOWN = "-0.233629"
PORT_MAX_DRAWDOWN_DAYS = "789"


def spread(closes: ArrayLike) -> NDArray[np.float64]:
    """Line 13: the 90-row moving deviation of close-to-close returns, one row later.

    This is :func:`chan.buy_on_gap.entry_spread`, because both scripts write
    ``stdretC2C90d`` the same way, and :data:`SPREAD_LOOKBACK` is that
    module's. Day t reads the returns ending at t − 1 through book two's
    ``smartstd``, which divides by n, so the first :data:`SPREAD_LOOKBACK`
    rows are NaN.
    """
    return entry_spread(np.asarray(closes, dtype=float))


def qualifiers(
    opens: ArrayLike, highs: ArrayLike, lows: ArrayLike, spread: ArrayLike
) -> tuple[NDArray[np.bool_], NDArray[np.bool_]]:
    """Lines 15 and 16: the days a long qualifies and the days a short does.

    A long needs the open at or above the previous high times one plus a
    tenth of the spread, and a short the open at or below the previous low
    times one minus it. Both tests are non-strict, and a NaN on either side
    qualifies nothing, as in MATLAB.
    """
    op = np.asarray(opens, dtype=float)
    hi = np.asarray(highs, dtype=float)
    lo = np.asarray(lows, dtype=float)
    sd = np.asarray(spread, dtype=float)
    with np.errstate(invalid="ignore"):
        longs = op >= backshift(1, hi) * (1 + ENTRY_ZSCORE * sd)
        shorts = op <= backshift(1, lo) * (1 - ENTRY_ZSCORE * sd)
    return longs, shorts


def positions(
    opens: ArrayLike, highs: ArrayLike, lows: ArrayLike, spread: ArrayLike
) -> NDArray[np.float64]:
    """Lines 18 to 21: 1 on a long day, −1 on a short day, 0 otherwise.

    The short is assigned after the long, as line 21 assigns it, so a day
    qualifying both is short.
    """
    return _held(*qualifiers(opens, highs, lows, spread))


def _held(longs: NDArray[np.bool_], shorts: NDArray[np.bool_]) -> NDArray[np.float64]:
    held = np.zeros(len(longs))
    held[longs] = 1.0
    held[shorts] = -1.0
    return held


def daily_returns(
    positions: ArrayLike, opens: ArrayLike, closes: ArrayLike, *, reading: str = "literal"
) -> NDArray[np.float64]:
    """Lines 23 and 24: each day's open-to-close return on its position, NaN set to 0.

    ``"literal"`` is line 23 as written, ``positions · (op − cl) / op``.
    ``"momentum"`` is the sign location 2965 describes,
    ``positions · (cl − op) / op``. Any other reading is refused.
    """
    if reading not in READINGS:
        raise ValueError(f"reading is one of {READINGS}, not {reading!r}")
    held = np.asarray(positions, dtype=float)
    op = np.asarray(opens, dtype=float)
    cl = np.asarray(closes, dtype=float)
    move = op - cl if reading == "literal" else cl - op
    with np.errstate(invalid="ignore", divide="ignore"):
        ret = held * move / op
    return np.where(np.isnan(ret), 0.0, ret)


@dataclass(frozen=True)
class Figures:
    """What the script prints on one series of daily returns, and one figure beside it.

    ``apr`` and ``sharpe`` are line 26's, which line 27's comment records.
    ``max_drawdown`` and ``max_drawdown_days`` are line 34's.
    ``average_annual_return`` is ``252 · mean(ret)``, which the script does
    not print.
    """

    apr: float
    sharpe: float
    average_annual_return: float
    max_drawdown: float
    max_drawdown_days: int


def figures(daily: ArrayLike) -> Figures:
    """Line 26's APR and Sharpe ratio, which line 27's comment records, line 34's drawdown,
    and ``252 · mean(ret)``.
    """
    ret = np.asarray(daily, dtype=float)
    max_drawdown, max_drawdown_days = calculate_max_dd(np.cumprod(1 + ret) - 1)
    return Figures(
        apr=compounded_apr(ret),
        sharpe=plain_sharpe(ret),
        average_annual_return=float(TRADING_DAYS * ret.mean()),
        max_drawdown=max_drawdown,
        max_drawdown_days=max_drawdown_days,
    )


@dataclass(frozen=True)
class OpeningGap:
    """The script on one save of FSTX, row for row, under both readings of line 23."""

    days: pd.DatetimeIndex
    spread: NDArray[np.float64]
    longs: NDArray[np.bool_]
    shorts: NDArray[np.bool_]
    positions: NDArray[np.float64]
    literal: NDArray[np.float64]
    momentum: NDArray[np.float64]

    @property
    def literal_figures(self) -> Figures:
        return figures(self.literal)

    @property
    def momentum_figures(self) -> Figures:
        return figures(self.momentum)

    @property
    def first_position(self) -> pd.Timestamp:
        return self.days[int(np.argmax(self.positions != 0))]


def opening_gap(prices: pd.DataFrame) -> OpeningGap:
    """Run the script on a frame holding FSTX's :data:`FIELDS` as columns."""
    op, hi, lo, cl = (prices[field].to_numpy(dtype=float) for field in FIELDS)
    sd = spread(cl)
    longs, shorts = qualifiers(op, hi, lo, sd)
    held = _held(longs, shorts)
    return OpeningGap(
        days=prices.index,
        spread=sd,
        longs=longs,
        shorts=shorts,
        positions=held,
        literal=daily_returns(held, op, cl, reading="literal"),
        momentum=daily_returns(held, op, cl, reading="momentum"),
    )


def read_sources(
    data_dir: Path | None = None, *, source_file: str = SOURCE_FILE
) -> tuple[VintageEntry, pd.DataFrame]:
    """FSTX's entry and its four fields from one save, after the scale-break guard.

    Each field is FSTX's own column without its NaN, and the four must share
    one calendar, which is refused otherwise rather than aligned. The guard
    reads the closes over the save's whole span.
    """
    columns = {}
    for field in FIELDS:
        members, frame = load_panel(source_file, field=field, data_dir=data_dir)
        columns[field] = frame[SYMBOL].dropna()
    (entry,) = [member for member in members if member.symbol == SYMBOL]
    days = columns["Close"].index
    if not all(column.index.equals(days) for column in columns.values()):
        raise ValueError(f"{entry.path} prices its {', '.join(FIELDS)} on different days")
    prices = pd.DataFrame(columns)
    refuse_window_crossing_a_break(
        [(entry, prices["Close"])], start=prices.index[0], end=prices.index[-1]
    )
    return entry, prices


def _verdict(value: float, printed: str) -> str:
    return "reproduced" if matches(value, printed) else f"gap {gap(value, printed):+g}"


def report(
    entry: VintageEntry,
    result: OpeningGap,
    earlier: list[tuple[VintageEntry, OpeningGap]],
) -> None:
    """Print the vintage, both readings beside the script's and the book's, and the rest."""
    literal = result.literal_figures
    momentum = result.momentum_figures
    print("The opening gap strategy on STOXX Europe 50 futures, Algorithmic Trading's Example 7.1")
    print(f"  vintage   {vintage_line(entry)}")
    print(
        f"  window    {result.days[0].date()} to {result.days[-1].date()}, "
        f"{len(result.days)} trading days"
    )
    print(
        f"  rule      long when the open clears the previous high by {ENTRY_ZSCORE} of the "
        f"{SPREAD_LOOKBACK}-day std,"
    )
    print("            short when it clears the previous low, held from the open to the close")
    print()
    print(f"  {'Figure':<28} {'Computed':>10}  {'Script':>7}  {'Verdict':<12} {'Book':>5}  Verdict")
    for label, value, script, book in (
        ("APR, literal", literal.apr, SCRIPT_APR, (100 * literal.apr, BOOK_APR_PERCENT)),
        ("Sharpe ratio, literal", literal.sharpe, SCRIPT_SHARPE, (literal.sharpe, BOOK_SHARPE)),
        ("APR, momentum", momentum.apr, None, (100 * momentum.apr, BOOK_APR_PERCENT)),
        ("Sharpe ratio, momentum", momentum.sharpe, None, (momentum.sharpe, BOOK_SHARPE)),
    ):
        verdict = _verdict(value, script) if script is not None else "none"
        print(
            f"  {label:<28} {value:>10.6f}  {script or 'none':>7}  {verdict:<12} "
            f"{book[1]:>5}  {_verdict(*book)}"
        )
    print()
    print("Beside the replication. No source prints these, so none carries a verdict.")
    print(f"  252 x mean, literal          {literal.average_annual_return:.6f}")
    print(
        f"  maximum drawdown, literal    {literal.max_drawdown:.6f} over "
        f"{literal.max_drawdown_days} days"
    )
    print(
        f"  maximum drawdown, momentum   {momentum.max_drawdown:.6f} over "
        f"{momentum.max_drawdown_days} days"
    )
    print(
        f"  long on {int(result.longs.sum())} days, short on {int(result.shorts.sum())}, "
        f"both on {int((result.longs & result.shorts).sum())}, "
        f"first position {result.first_position.date()}"
    )
    for earlier_entry, run_on in earlier:
        f = run_on.literal_figures
        print(f"  {vintage_line(earlier_entry)}")
        print(
            f"    {run_on.days[0].date()} to {run_on.days[-1].date()}, literal APR {f.apr:.6f}, "
            f"Sharpe ratio {f.sharpe:.6f}"
        )
    print()
    print(
        f"  Annualised over {TRADING_DAYS} days with no risk-free rate and no cost, on "
        "back-adjusted prices."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def python_port_spread(closes: ArrayLike) -> NDArray[np.float64]:
    """``gapFutures_FSTX.py``'s ``stdretC2C90d``, pandas' rolling deviation one row later.

    ``Close.pct_change().rolling(90).std().shift()`` divides by n − 1 where
    :func:`spread` divides by n. Pandas also wants all 90 returns in the
    window, and the first return is NaN, so the first 91 rows are NaN rather
    than 90.
    """
    returns = pd.Series(np.asarray(closes, dtype=float)).pct_change()
    return returns.rolling(SPREAD_LOOKBACK).std().shift().to_numpy()


def python_port_qualifiers(
    opens: ArrayLike, highs: ArrayLike, lows: ArrayLike, spread: ArrayLike
) -> tuple[NDArray[np.bool_], NDArray[np.bool_]]:
    """The port's two tests: line 15's long, and line 16's short with its inequality flipped.

    The port writes ``Open >= Low.shift() · (1 − 0.1 · spread)``, so a short
    qualifies on every day the open does not jump below the previous low by the margin.
    """
    longs, _ = qualifiers(opens, highs, lows, spread)
    op = np.asarray(opens, dtype=float)
    lo = np.asarray(lows, dtype=float)
    sd = np.asarray(spread, dtype=float)
    with np.errstate(invalid="ignore"):
        shorts = op >= backshift(1, lo) * (1 - ENTRY_ZSCORE * sd)
    return longs, shorts


def python_port_sharpe(daily: ArrayLike) -> float:
    """``np.sqrt(252) * np.mean(ret) / np.std(ret)``, where ``np.std`` divides by n."""
    ret = np.asarray(daily, dtype=float)
    return float(np.sqrt(TRADING_DAYS) * ret.mean() / ret.std(ddof=0))


@dataclass(frozen=True)
class PythonPort:
    """``gapFutures_FSTX.py`` on one save of FSTX, row for row."""

    days: pd.DatetimeIndex
    spread: NDArray[np.float64]
    longs: NDArray[np.bool_]
    shorts: NDArray[np.bool_]
    positions: NDArray[np.float64]
    returns: NDArray[np.float64]

    @property
    def figures(self) -> Figures:
        """The script's figures on the port's returns, so this Sharpe ratio divides by n − 1."""
        return figures(self.returns)

    @property
    def sharpe(self) -> float:
        """The Sharpe ratio the port prints, dividing by n."""
        return python_port_sharpe(self.returns)


def python_port(prices: pd.DataFrame) -> PythonPort:
    """Run the port's arithmetic on a frame holding FSTX's :data:`FIELDS` as columns.

    The short is assigned after the long, as the port assigns it, and the
    return is :func:`daily_returns`' momentum reading, which is the port's
    ``positions * (Close - Open) / Open``.
    """
    op, hi, lo, cl = (prices[field].to_numpy(dtype=float) for field in FIELDS)
    sd = python_port_spread(cl)
    longs, shorts = python_port_qualifiers(op, hi, lo, sd)
    held = _held(longs, shorts)
    return PythonPort(
        days=prices.index,
        spread=sd,
        longs=longs,
        shorts=shorts,
        positions=held,
        returns=daily_returns(held, op, cl, reading="momentum"),
    )


def report_python_port(port: PythonPort) -> None:
    """Print the port's four figures beside its comments, and the days it holds."""
    f = port.figures
    print()
    print("Chan's Python port, gapFutures_FSTX.py, on the same save")
    print(f"  {'Figure':<28} {'Computed':>10}  {'Port':>9}  Verdict")
    for label, value, printed in (
        ("APR", f.apr, PORT_APR),
        ("Sharpe ratio, over n", port.sharpe, PORT_SHARPE),
        ("maximum drawdown", f.max_drawdown, PORT_MAX_DRAWDOWN),
        ("maximum drawdown days", f.max_drawdown_days, PORT_MAX_DRAWDOWN_DAYS),
    ):
        shown = f"{value:>10d}" if isinstance(value, int) else f"{value:>10.6f}"
        print(f"  {label:<28} {shown}  {printed:>9}  {_verdict(value, printed)}")
    held = port.positions
    print(
        f"  long on {int((held == 1).sum())} days, short on {int((held == -1).sum())}, "
        f"flat on {int((held == 0).sum())}, both tests passed on "
        f"{int((port.longs & port.shorts).sum())}"
    )


def run(data_dir: Path | None = None) -> OpeningGap:
    """Read the script's save and the two earlier ones, run each, and print the report."""
    entry, prices = read_sources(data_dir)
    result = opening_gap(prices)
    earlier = []
    for source_file in EARLIER_SAVES:
        earlier_entry, earlier_prices = read_sources(data_dir, source_file=source_file)
        earlier.append((earlier_entry, opening_gap(earlier_prices)))
    report(entry, result, earlier)
    report_python_port(python_port(prices))
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="The opening gap strategy on STOXX Europe 50 futures, Example 7.1 of "
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
