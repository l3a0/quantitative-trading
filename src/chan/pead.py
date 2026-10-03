"""Post-earnings announcement drift on Chan's own files, *Algorithmic Trading*'s Example 7.2.

Prices keep moving in the direction of an earnings surprise for a while after
the announcement. Chan trades the first day of that drift without knowing what
was announced. On a day a stock announced after the previous close and before
the open, the gap from that close to the open stands in for the surprise. A
gap large enough against the stock's recent gaps buys it at the open, or
shorts it if the gap was down, and the position is closed at the same day's
close. At Kindle location 3024 Chan reports an APR of 6.7 percent and a
Sharpe ratio of 1.5 on the S&P 500 from 2011-01-03 to 2012-04-24.

**The transcription.** Every step is Chan's ``pead.m`` and the helpers it
calls, read under ``archived/matlab/`` in the mirror
[ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
at ``45670240f1f3d4b5233a75f82fd18b742455b4bb``. The mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f`` holds the same ``pead.m`` under ``public/img/book2/``, identical
once line endings are stripped. The transcription landed here with
[PR #263](https://github.com/l3a0/quantitative-trading/pull/263). Where ``op``
is the open, ``cl`` the close and ``earnann`` the flags:

1. Both price arrays are cut to the days the flag file covers, before any
   return is taken, so the first day's return is NaN.
2. ``retC2O = (op − backshift(1, cl)) / backshift(1, cl)``, each stock's gap
   from the previous close to today's open.
3. ``stdC2O`` is book two's ``smartMovingStd`` of that gap over 90 days, NaN
   until the window first fills.
4. A stock is long where ``retC2O ≥ 0.5 · stdC2O`` and it announced, and short
   where ``retC2O ≤ −0.5 · stdC2O`` and it announced. Longs are set first and
   shorts second, so a stock meeting both, which needs a spread of exactly 0,
   ends short.
5. The day's return is the sum over stocks of position times
   ``(cl − op) / op``, skipping a product that is not finite, divided by 30.

Chan divides by 30 because "there is a maximum of 30 positions in one day",
location 3024. It is a constant chosen after looking at the whole window,
rather than each day's count, so the figures are those of a book that sizes
every trade at one thirtieth of its capital and leaves the rest idle.
:func:`run` measures the busiest day and the report prints it beside the 30.

``pead.m`` prints five figures, and :func:`pead` returns each.

1. ``252 · smartmean(ret)``, the arithmetic annual return. This is the book's
   "APR of 6.7 percent", printed by the script as 0.0667.
2. ``√252 · smartmean(ret) / smartstd(ret)``, the Sharpe ratio, printed as
   1.49, which the book rounds to 1.5.
3. ``prod(1 + ret)^(252 / n) − 1``, the compounded APR, printed as 0.0680. The
   book does not quote it, and a pin that set the book's 6.7 percent against
   this figure would match the wrong number.
4. and 5. The deepest drawdown of the compounded cumulative return and its
   longest duration in days, from book two's ``calculateMaxDD``, printed as
   −0.026052 and 109.

The book adds a sixth that the script does not print. Levered four times, the
strategy's "annualized average return" is "close to 27 percent", which is four
times the arithmetic figure, and :attr:`Drift.levered` carries it.

Chan names the price of his 30 himself at location 3024: it is "a certain
degree of look-ahead bias", because the most positions on one day is known
only once the window has been seen. He argues the bias is small because the
number of announcements a day is predictable. Nothing here measures that.

**The helper choice moves a printed digit.** ``smartstd`` here is book two's,
which skips a NaN and divides by n. The first edition's, which
:mod:`chan.khandani_lo` and :mod:`chan.equity_seasonals` use, zero-fills and
divides by n − 1, and with it the arithmetic return becomes 0.066833, which
prints as 0.0668 rather than Chan's 0.0667. ``tests/test_pead.py`` pins both.
:mod:`chan.matlab_helpers` says what each ``smartstd`` does and where each
came from.

**The vintages.** ``inputdataohlcdaily_stocks_20120424/``, the 497 stocks of
Chan's ``inputDataOHLCDaily_stocks_20120424.mat``, read for their opens and
closes, and ``earnannfile/``, the 497 flag series of his ``earnannFile.mat``,
read for ``Flag``. Both go through :func:`chan.series.load_panel`, which
hashes each member against its manifest entry before parsing it.
``data/README.md`` records the mirrors, the hashes and the basis. The two
sources must name the same stocks in the same order, because ``pead.m`` pairs
their columns by position, so a mismatch is refused by symbol rather than
paired wrongly.

**Every figure here is about survivors.** The price file is the S&P 500 as
Chan held it on 2012-04-24, carried backwards, so a company that left the
index before then is absent. That is Chan's own universe, so it reproduces his
figure rather than approximating it, and it says nothing about what the rule
earned on the index as it stood each day.
[Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) is where
that is measured.

**The scale-break guard runs on each stock's own rows.**
:func:`chan.series.refuse_window_crossing_a_break` reads the open and the
close of every stock over the flag file's days. On the panel's columns it
would refuse, because MPC and XYL were spun off inside the window and have no
price before 2011-06-24 and 2011-10-13, and it cannot read the day beside a
NaN. On each stock's own rows it reads every move, and neither stock has a
gap after its first price. The 30 days the guard flags in this file all fall
in 2007 to 2009, outside the window, and ``tests/test_scale_breaks.py`` pins
them.

Every result here is exploratory. Reproducing Chan's figures spends the 2011
and 2012 sample on a rule he chose, so the run says whether his numbers
reproduce on his files and nothing about whether the drift pays today.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from chan.matlab_helpers import (
    backshift,
    calculate_max_dd,
    smart_moving_std,
    smartmean,
    smartstd_book_two,
    smartsum,
)
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
)
from chan.vintage import VintageEntry, VintageUnavailable

PRICE_FILE = "inputDataOHLCDaily_stocks_20120424.mat"
FLAG_FILE = "earnannFile.mat"

#: ``lookback`` in ``pead.m``, the rows in the moving standard deviation.
LOOKBACK = 90
#: The gap a stock must clear, in moving standard deviations, to be traded.
ENTRY = 0.5
#: The divisor on each day's summed return, Chan's most positions on one day.
DENOMINATOR = 30
#: The annualisation in every figure ``pead.m`` prints.
TRADING_DAYS = 252

#: What the book prints at location 3024. The APR is the arithmetic figure.
BOOK_APR_PERCENT = 6.7
BOOK_SHARPE = 1.5
#: Location 3024 again: levered "at least four times", the strategy gives "an
#: annualized average return of close to 27 percent". That is four times the
#: arithmetic figure, since leverage multiplies every day's return.
BOOK_LEVERAGE = 4
BOOK_LEVERED_PERCENT = 27

#: What ``pead.m`` prints, in its comment lines, at the precision its
#: ``fprintf`` formats give each figure.
SCRIPT_ARITHMETIC = "0.0667"
SCRIPT_SHARPE = "1.49"
SCRIPT_APR = "0.0680"
SCRIPT_MAX_DD = "-0.026052"
SCRIPT_MAX_DDD = 109


@dataclass(frozen=True)
class Drift:
    """What one run of ``pead.m`` gives.

    ``days`` are the flag file's days, ``positions`` each stock's 1, −1 or 0 on
    each of them, and ``daily`` each day's return over :data:`DENOMINATOR`.
    The five figures are those ``pead.m`` prints. ``trades`` counts the
    positions taken across the window and ``most_held`` the most on one day,
    which is what Chan's 30 claims to be.
    """

    days: pd.DatetimeIndex
    positions: np.ndarray
    daily: np.ndarray
    arithmetic_annual: float
    sharpe: float
    compounded_apr: float
    max_drawdown: float
    max_drawdown_days: int

    @property
    def levered(self) -> float:
        """The arithmetic annual return at the book's leverage of four."""
        return BOOK_LEVERAGE * self.arithmetic_annual

    @property
    def trades(self) -> int:
        return int(np.count_nonzero(self.positions))

    @property
    def most_held(self) -> int:
        return int(np.count_nonzero(self.positions, axis=1).max())


def close_to_open(opens: np.ndarray, closes: np.ndarray) -> np.ndarray:
    """Step 2: each stock's gap from the previous close to today's open."""
    previous = backshift(1, closes)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (opens - previous) / previous


def drift_positions(gaps: np.ndarray, spread: np.ndarray, flags: np.ndarray) -> np.ndarray:
    """Step 4: 1 or −1 on an announcement day whose gap clears the threshold, else 0.

    A NaN gap or spread clears nothing, as a comparison with NaN is false in
    MATLAB too, so no stock trades before its window has filled. A flag must
    be finite, because MATLAB stops on a NaN in a logical ``&`` rather than
    reading it as either answer.
    """
    if not np.isfinite(flags).all():
        raise ValueError("the flags hold a value that is not a number, which pead.m cannot read")
    announced = flags != 0
    with np.errstate(invalid="ignore"):
        longs = (gaps >= ENTRY * spread) & announced
        shorts = (gaps <= -ENTRY * spread) & announced
    positions = np.zeros_like(gaps)
    positions[longs] = 1.0
    positions[shorts] = -1.0
    return positions


def daily_returns(positions: np.ndarray, opens: np.ndarray, closes: np.ndarray) -> np.ndarray:
    """Step 5: each day's open-to-close return on the positions, over :data:`DENOMINATOR`."""
    with np.errstate(invalid="ignore", divide="ignore"):
        return smartsum(positions * (closes - opens) / opens, axis=1) / DENOMINATOR


def pead(opens: pd.DataFrame, closes: pd.DataFrame, flags: pd.DataFrame) -> Drift:
    """Run ``pead.m`` on three date-by-stock frames and return its five figures.

    The frames are cut to the days all three share, which for Chan's files is
    the flag file's 330. ``opens`` and ``closes`` must hold the same stocks in
    the same order as ``flags``.
    """
    if not (opens.columns.equals(flags.columns) and closes.columns.equals(flags.columns)):
        raise ValueError("the price frames and the flags must hold the same stocks in one order")
    days = opens.index.intersection(closes.index).intersection(flags.index)
    op = opens.loc[days].to_numpy(dtype=float)
    cl = closes.loc[days].to_numpy(dtype=float)
    gaps = close_to_open(op, cl)
    positions = drift_positions(
        gaps, smart_moving_std(gaps, LOOKBACK), flags.loc[days].to_numpy(dtype=float)
    )
    daily = daily_returns(positions, op, cl)
    mean = float(smartmean(daily))
    max_dd, max_ddd = calculate_max_dd(np.cumprod(1 + daily) - 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        # A window with no trade has a spread of 0, and MATLAB's 0/0 is NaN too.
        sharpe = float(np.sqrt(TRADING_DAYS) * mean / smartstd_book_two(daily))
    return Drift(
        days=days,
        positions=positions,
        daily=daily,
        arithmetic_annual=TRADING_DAYS * mean,
        sharpe=sharpe,
        compounded_apr=float(np.prod(1 + daily) ** (TRADING_DAYS / len(daily)) - 1),
        max_drawdown=max_dd,
        max_drawdown_days=max_ddd,
    )


def read_sources(
    data_dir: Path | None = None,
) -> tuple[list[VintageEntry], list[VintageEntry], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Both committed sources: the price members, the flag members, and the three frames.

    A stock in one source and not the other is refused by symbol, because
    ``pead.m`` pairs the two files' columns by position and would pair the
    wrong stocks rather than stop.
    """
    prices, opens = load_panel(PRICE_FILE, field="Open", data_dir=data_dir)
    _, closes = load_panel(PRICE_FILE, field="Close", data_dir=data_dir)
    announcements, flags = load_panel(FLAG_FILE, field="Flag", data_dir=data_dir)
    priced = [entry.symbol for entry in prices]
    flagged = [entry.symbol for entry in announcements]
    if priced != flagged:
        only_priced = sorted(set(priced) - set(flagged))
        only_flagged = sorted(set(flagged) - set(priced))
        raise VintageUnavailable(
            f"{PRICE_FILE} and {FLAG_FILE} do not hold the same stocks: "
            f"{', '.join(only_priced) or 'none'} priced and not flagged, "
            f"{', '.join(only_flagged) or 'none'} flagged and not priced. pead.m pairs the "
            f"two files' columns by position, so it cannot run on them."
        )
    return prices, announcements, opens, closes, flags


def refuse_scale_breaks(
    members: list[VintageEntry], opens: pd.DataFrame, closes: pd.DataFrame, days: pd.DatetimeIndex
) -> None:
    """Run the scale-break guard on each stock's own opens and closes over ``days``."""
    for frame in (opens, closes):
        refuse_window_crossing_a_break(
            [(entry, frame[entry.symbol].dropna()) for entry in members],
            start=days[0],
            end=days[-1],
        )


def report(prices: list[VintageEntry], announcements: list[VintageEntry], drift: Drift) -> None:
    """Print the sources, the rule, and each figure beside what Chan printed."""
    print("Post-earnings announcement drift, Chan's Example 7.2 in Algorithmic Trading")
    print(f"  prices   {panel_line(prices)}, the Open and Close columns")
    print(f"  flags    {panel_line(announcements)}, the Flag column")
    print(
        f"  window   {drift.days[0].date()} to {drift.days[-1].date()}, "
        f"{len(drift.days)} trading days, {drift.positions.shape[1]} stocks"
    )
    print(
        f"  rule     on an announcement day, long if the close-to-open gap is at least {ENTRY} "
        f"of its {LOOKBACK}-day moving std, short if at most -{ENTRY}, out at the close"
    )
    print(
        f"  sizing   each day's summed return over {DENOMINATOR}. The busiest day held "
        f"{drift.most_held} positions, and {drift.trades} were taken in all."
    )
    print()
    rows = [
        (
            "Arithmetic annual return, 252 x mean",
            f"{drift.arithmetic_annual:.6f}",
            f"{drift.arithmetic_annual:7.4f}".strip(),
            SCRIPT_ARITHMETIC,
            f"{BOOK_APR_PERCENT} percent",
        ),
        (
            "Sharpe ratio, sqrt(252) x mean / std",
            f"{drift.sharpe:.4f}",
            f"{drift.sharpe:4.2f}",
            SCRIPT_SHARPE,
            f"{BOOK_SHARPE}",
        ),
        (
            f"Levered {BOOK_LEVERAGE} times, {TRADING_DAYS} x mean",
            f"{drift.levered:.6f}",
            "none",
            "none",
            f"{BOOK_LEVERED_PERCENT} percent",
        ),
        (
            "Compounded APR",
            f"{drift.compounded_apr:.6f}",
            f"{drift.compounded_apr:10.4f}".strip(),
            SCRIPT_APR,
            "none",
        ),
        (
            "Maximum drawdown",
            f"{drift.max_drawdown:.6f}",
            f"{drift.max_drawdown:f}",
            SCRIPT_MAX_DD,
            "none",
        ),
        (
            "Maximum drawdown duration, days",
            f"{drift.max_drawdown_days}",
            f"{drift.max_drawdown_days}",
            f"{SCRIPT_MAX_DDD}",
            "none",
        ),
    ]
    print(f"  {'Figure':<38} {'Computed':>10} {'Prints as':>10} {'pead.m':>10} {'Book':>12}")
    for label, computed, printed, script, book in rows:
        print(f"  {label:<38} {computed:>10} {printed:>10} {script:>10} {book:>12}")
    print()
    print(
        "  The price file holds only the stocks in the index on 2012-04-24, "
        "so every figure above is about survivors."
    )
    print(
        "  Exploratory. Reproducing Chan's figures spends the 2011 and 2012 sample on a rule he "
        "chose, so this says whether"
    )
    print(
        "  his numbers reproduce on his files and nothing about whether the drift pays today. "
        "docs/replication-log.md Entry 12 carries the verdicts."
    )


def run(data_dir: Path | None = None) -> Drift:
    """Read both sources, guard the window, run ``pead.m`` and print the report."""
    prices, announcements, opens, closes, flags = read_sources(data_dir)
    drift = pead(opens, closes, flags)
    refuse_scale_breaks(prices, opens, closes, drift.days)
    report(prices, announcements, drift)
    return drift


def main() -> None:
    argparse.ArgumentParser(
        description="Post-earnings announcement drift on Chan's own files, Example 7.2 of "
        "Algorithmic Trading"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source is worth nothing at the bottom of a
        # traceback, so it reaches the reader as one line, the way
        # chan.khandani_lo.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
