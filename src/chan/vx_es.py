"""VX futures against E-mini S&P 500 futures, *Algorithmic Trading*'s hedge from August 2008.

Volatility rises when the stock market falls, so a VX future, which tracks the
VIX index, and an ES future, the E-mini S&P 500, should move against each
other. Chan plots the two front-month series against each other at Kindle
location 2546 and finds two regimes, 2004 to May 2008 and August 2008 to 2012.
At location 2559 he regresses one on the other over the second regime, with VX
multiplied by its $1,000 point value and ES by its $50, and reports that "a
portfolio that is long 0.3906 contracts of VX and long one contract of ES
should be stationary" and that "The standard deviation of the residues is
$2,047." He then shorts the portfolio when it deviates by one training-set
standard deviation and reports "The APR on the test set July 29, 2010, to May
8, 2012, is 12.3 percent, with a Sharpe ratio of 1.4." The text names no exit,
no training window and no save.

**What ``VX_ES.m`` holds.** The script is git blob ``ca480c4`` under
``public/img/book2/`` in the mirror
[ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) at
``e4bc46f``, 20 lines of which 14 hold code.

1. It loads ``inputDataOHLCDaily_20120517`` and takes VX's and ES's columns of
   ``cl`` and of ``tday``.
2. It intersects the two calendars, keeping the days both traded.
3. It draws Figure 5.10's scatter.
4. It fits ``regress(50*ES(post200808), [1000*VX(post200808) ones(...)])``,
   where ``post200808`` is every common day on or after 2008-08-01.

That fit runs to the file's last day, so it includes the whole test set, and
the script stops there. It prints nothing and no backtest ships. Chan's Python
port holds ``VX_ES_rollreturn.py`` and no counterpart of this script. So the
script as shipped cannot be what produced the book's figures, and
:func:`script_as_shipped` runs it as a diagnostic only.

**What the run does instead.** A sweep on
[issue 350](https://github.com/l3a0/quantitative-trading/issues/350) fitted
22,446 windows across the 2012-05-07, 2012-05-11 and 2012-05-17 saves, and
exactly one rounds to both printed figures. It sits on the 2012-05-07 save,
whose last day is the book's last test day, and ends 2010-07-28, the day
before the printed test set begins. The suite does not run the sweep, and the
issue records it. The run here takes that save and the anchor and split
Chan's own ``VX_ES_rollreturn.m`` uses, ``idx=find(tday >= 20080804)`` with
the test at ``idx(501:end)``.

1. **Read** VX and ES from :data:`SOURCE_FILE` through
   :func:`chan.series.load_panel`, drop each leg's NaN, and intersect their
   days, as the script does.
2. **Fit** ``ols(50·ES, [1000·VX, 1])`` on the first :data:`TRAINING_DAYS`
   common days on or after :data:`ANCHOR`. The hedge is minus the slope, so
   the portfolio is long that many VX contracts and one ES contract, as the
   book words it.
3. **Score** each day from the anchor as the portfolio's value less the
   training intercept, over the training residual's standard deviation with
   n − 1.
4. **Trade** with :func:`chan.bollinger.band_units`. Go long one unit below
   −1, go short one unit above +1, and otherwise hold yesterday's units. A
   position is held until the opposite band, with no exit at the mean.
5. **Earn** each day's return as :func:`chan.price_spread.daily_returns`
   gives it, on dollar positions of ``units·h·1000·VX`` and ``units·50·ES``.
   Profit on yesterday's dollar positions over yesterday's gross equals
   contract profit over gross contract value, because the multipliers cancel.
6. **Measure** the APR and Sharpe ratio on the rows after the training set,
   2010-07-29 to 2012-05-08, so the first test day earns the position held at
   the close of 2010-07-28.

That gives a hedge of 0.390594 and an APR and Sharpe ratio that print as the
book's. The residual's standard deviation is $2,044.91 against the printed
$2,047. Dropping the first training row reaches $2,046.93, and what dropped it
is not known, since the code that produced the book's figures does not ship.
``tests/test_vx_es.py`` pins each of these.

**The scale-break guard.** :func:`read_legs` calls
:func:`chan.series.refuse_window_crossing_a_break` on VX and ES over each
leg's own span, in every save it reads. Nothing in these saves flags except ZB
and ZF, so nothing is refused.

Every result here is exploratory, for two reasons. Reproducing Chan's figures
spends the 2008 to 2012 sample on a rule he chose. And the save and the exit
were chosen because they land the printed figures, so the match is partly
built in. The test set holds four holding periods, so the APR and Sharpe
ratio rest on four bets.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.timeseries import ols
from numpy.typing import NDArray

from chan.bollinger import band_units
from chan.khandani_lo import TRADING_DAYS, plain_sharpe
from chan.khandani_lo_book_two import compounded_apr, gap, matches
from chan.price_spread import daily_returns
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    panel_line,
    refuse_window_crossing_a_break,
)
from chan.vintage import VintageEntry, VintageUnavailable

#: The save the book's figures come from, saved 2012-05-09.
SOURCE_FILE = "inputDataOHLCDaily_20120507.mat"
#: The save ``VX_ES.m`` loads, saved 2012-05-18.
SCRIPT_SOURCE_FILE = "inputDataOHLCDaily_20120517.mat"
#: The save between them, saved 2012-05-12, which agrees with the later one on this window.
MIDDLE_SOURCE_FILE = "inputDataOHLCDaily_20120511.mat"

VX, ES = "VX", "ES"
#: Dollars per point, location 2559.
VX_POINT_VALUE = 1000
ES_POINT_VALUE = 50

#: ``idx=find(tday >= 20080804)`` in ``VX_ES_rollreturn.m``.
ANCHOR = pd.Timestamp("2008-08-04")
#: ``idx(501:end)`` is the test, so the first 500 rows from the anchor train.
TRAINING_DAYS = 500
#: ``post200808=find(tday>=20080801)`` in ``VX_ES.m``.
SCRIPT_ANCHOR = pd.Timestamp("2008-08-01")
#: The last day of the printed test set, "July 29, 2010, to May 8, 2012".
BOOK_TEST_END = pd.Timestamp("2012-05-08")

#: One training-set standard deviation, "deviates from one standard deviation".
BAND = 1

#: What location 2559 prints.
BOOK_HEDGE = "0.3906"
BOOK_RESIDUAL_STD = "2,047"
BOOK_APR_PERCENT = "12.3"
BOOK_SHARPE = "1.4"


@dataclass(frozen=True)
class Hedge:
    """``regress(50·ES, [1000·VX, 1])`` on ``days``.

    ``hedge`` is minus the slope, the VX contracts held long against one ES
    contract. ``residual_std`` divides by n − 1.
    """

    days: pd.DatetimeIndex
    hedge: float
    intercept: float
    residual_std: float


@dataclass(frozen=True)
class Trade:
    """The band on the portfolio, over every row from the anchor, and the test's returns.

    ``days``, ``zscore`` and ``units`` run over every row the band saw. ``daily``
    holds the test's returns only, and ``test_days`` names their rows.
    """

    days: pd.DatetimeIndex
    zscore: NDArray[np.float64]
    units: NDArray[np.float64]
    test_days: pd.DatetimeIndex
    daily: NDArray[np.float64]

    @property
    def apr(self) -> float:
        return compounded_apr(self.daily)

    @property
    def sharpe(self) -> float:
        return plain_sharpe(self.daily)


@dataclass(frozen=True)
class VxEs:
    """The specification on the 2012-05-07 save, and the diagnostics beside it.

    ``first_row_dropped`` fits on training rows 2 to 500. ``exit_at_mean``
    exits at a z-score of 0, as ``bollinger.m`` does. ``flat_at_test`` starts
    the band on the first test day, so nothing is carried into it and that
    day earns 0, though the band may enter at its close. ``book_hedge`` trades the printed
    0.3906 with the fitted intercept and deviation.
    """

    days: pd.DatetimeIndex
    hedge: Hedge
    trade: Trade
    first_row_dropped: tuple[Hedge, Trade]
    exit_at_mean: Trade
    flat_at_test: Trade
    book_hedge: Trade


def common_days(closes: pd.DataFrame) -> pd.DataFrame:
    """VX and ES on the days both traded, each leg first cut to its own rows.

    A continuous futures save prices each symbol on its own calendar, so a leg
    is its column with ``.dropna()``, as :func:`chan.series.load_panel` says,
    and ``intersect(tdayV, tdayE)`` keeps the days the two share.
    """
    vx = closes[VX].dropna()
    es = closes[ES].dropna()
    days = vx.index.intersection(es.index)
    return pd.DataFrame({VX: vx[days], ES: es[days]})


def fit_hedge(legs: pd.DataFrame) -> Hedge:
    """Regress ``50·ES`` on ``1000·VX`` and a column of ones over every row of ``legs``."""
    vx = VX_POINT_VALUE * legs[VX].to_numpy(dtype=float)
    es = ES_POINT_VALUE * legs[ES].to_numpy(dtype=float)
    design = np.column_stack([vx, np.ones(len(vx))])
    beta = ols(es, design).beta
    residual = es - design @ beta
    return Hedge(
        days=legs.index,
        hedge=-float(beta[0]),
        intercept=float(beta[1]),
        residual_std=float(np.std(residual, ddof=1)),
    )


def portfolio_value(legs: pd.DataFrame, hedge: float) -> NDArray[np.float64]:
    """Each day's dollar value of ``hedge`` VX contracts and one ES contract, both long."""
    return ES_POINT_VALUE * legs[ES].to_numpy(dtype=float) + hedge * VX_POINT_VALUE * legs[
        VX
    ].to_numpy(dtype=float)


def zscore(legs: pd.DataFrame, fitted: Hedge) -> NDArray[np.float64]:
    """The portfolio's distance from the training intercept, in training residual deviations."""
    return (portfolio_value(legs, fitted.hedge) - fitted.intercept) / fitted.residual_std


def opposite_band_units(z: NDArray[np.float64]) -> NDArray[np.float64]:
    """Long below −1 until above +1, short above +1 until below −1."""
    return band_units(z < -BAND, z > BAND, z > BAND, z < -BAND)


def mean_exit_units(z: NDArray[np.float64]) -> NDArray[np.float64]:
    """``bollinger.m``'s rule with this band: exit a long above 0 and a short below 0."""
    return band_units(z < -BAND, z > 0, z > BAND, z < 0)


def trade(
    legs: pd.DataFrame,
    fitted: Hedge,
    *,
    test_from: int = TRAINING_DAYS,
    units_rule=opposite_band_units,
) -> Trade:
    """Run the band over every row of ``legs`` and keep the returns from row ``test_from`` on.

    The band starts on ``legs``' first row, so the test's first day earns
    whatever position the band held the day before.
    """
    z = zscore(legs, fitted)
    units = units_rule(z)
    vx = legs[VX].to_numpy(dtype=float)
    es = legs[ES].to_numpy(dtype=float)
    positions = np.column_stack(
        [units * fitted.hedge * VX_POINT_VALUE * vx, units * ES_POINT_VALUE * es]
    )
    daily = daily_returns(positions, np.column_stack([vx, es]))
    return Trade(
        days=legs.index,
        zscore=z,
        units=units,
        test_days=legs.index[test_from:],
        daily=daily[test_from:],
    )


def anchored(legs: pd.DataFrame, end: pd.Timestamp = BOOK_TEST_END) -> pd.DataFrame:
    """The rows from :data:`ANCHOR` to ``end``, both included.

    The 2012-05-07 save ends on :data:`BOOK_TEST_END`, so the cut moves
    nothing there. It matters for the later saves, which run past the book's
    last test day and would otherwise be measured over a longer test.
    """
    return legs.loc[(legs.index >= ANCHOR) & (legs.index <= end)]


def specification(legs: pd.DataFrame) -> tuple[Hedge, Trade]:
    """Fit on the first 500 anchored rows and trade every anchored row, the test measured."""
    rows = anchored(legs)
    fitted = fit_hedge(rows.iloc[:TRAINING_DAYS])
    return fitted, trade(rows, fitted)


def vx_es(legs: pd.DataFrame) -> VxEs:
    """The specification and its diagnostics on VX and ES's common days."""
    rows = anchored(legs)
    fitted, traded = specification(legs)
    dropped = fit_hedge(rows.iloc[1:TRAINING_DAYS])
    test = rows.iloc[TRAINING_DAYS:]
    return VxEs(
        days=legs.index,
        hedge=fitted,
        trade=traded,
        first_row_dropped=(dropped, trade(rows, dropped)),
        exit_at_mean=trade(rows, fitted, units_rule=mean_exit_units),
        flat_at_test=trade(test, fitted, test_from=0),
        book_hedge=trade(rows, replace(fitted, hedge=float(BOOK_HEDGE))),
    )


def script_as_shipped(legs: pd.DataFrame) -> Hedge:
    """``VX_ES.m``'s own fit, every common day from 2008-08-01 to the file's last."""
    return fit_hedge(legs.loc[legs.index >= SCRIPT_ANCHOR])


def position_changes(traded: Trade) -> list[tuple[pd.Timestamp, float]]:
    """The test days on which the band's units differ from the day before."""
    start = len(traded.days) - len(traded.test_days)
    return [
        (traded.days[i], float(traded.units[i]))
        for i in range(max(start, 1), len(traded.days))
        if traded.units[i] != traded.units[i - 1]
    ]


def read_legs(
    source_file: str = SOURCE_FILE, data_dir: Path | None = None
) -> tuple[list[VintageEntry], pd.DataFrame]:
    """VX and ES from one save on their common days, each leg guarded over its own span."""
    members, closes = load_panel(source_file, data_dir=data_dir)
    read = [m for m in members if m.symbol in (VX, ES)]
    for member in read:
        leg = closes[member.symbol].dropna()
        refuse_window_crossing_a_break([(member, leg)], start=leg.index[0], end=leg.index[-1])
    return read, common_days(closes)


def _verdict(value: float, printed: str) -> str:
    plain = printed.replace(",", "")
    return (
        "reproduced" if matches(value, plain) else f"did not reproduce, gap {gap(value, plain):+g}"
    )


def _span(days: pd.DatetimeIndex) -> str:
    return f"{days[0].date()} to {days[-1].date()}, {len(days)} days"


def report(
    members: list[VintageEntry],
    result: VxEs,
    later: tuple[Hedge, Trade],
    shipped: Hedge,
) -> None:
    """Print the vintage, each printed figure beside the computed one, and the diagnostics."""
    h, t = result.hedge, result.trade
    print("VX against ES, Algorithmic Trading's hedge from August 2008")
    print(f"  vintage   {panel_line(members)}: {', '.join(m.symbol for m in members)}")
    print(f"  calendar  {_span(result.days)} that both legs traded")
    print(f"  training  {_span(h.days)}")
    print(f"  test      {_span(t.test_days)}")
    print()
    rows = [
        ("Hedge, VX contracts per ES", h.hedge, BOOK_HEDGE),
        ("Residual standard deviation, $", h.residual_std, BOOK_RESIDUAL_STD),
        ("APR, percent", 100 * t.apr, BOOK_APR_PERCENT),
        ("Sharpe ratio", t.sharpe, BOOK_SHARPE),
    ]
    print(f"  {'Figure':<32} {'Computed':>12}  {'Book':>8}  Verdict")
    for label, value, printed in rows:
        print(f"  {label:<32} {value:>12.6f}  {printed:>8}  {_verdict(value, printed)}")
    print()
    print("Diagnostics. Each row changes one thing, and none carries a verdict.")
    print(f"  {'Row':<52} {'Hedge':>9} {'Resid std':>10} {'APR':>9} {'Sharpe':>9}")
    dropped_hedge, dropped_trade = result.first_row_dropped
    later_hedge, later_trade = later
    for label, fitted, traded in (
        ("Training rows 2 to 500", dropped_hedge, dropped_trade),
        ("Exit at the mean", h, result.exit_at_mean),
        ("Flat on the first test day", h, result.flat_at_test),
        (
            f"Trading the printed {BOOK_HEDGE}",
            replace(h, hedge=float(BOOK_HEDGE)),
            result.book_hedge,
        ),
        ("The 2012-05-17 save, test cut at 2012-05-08", later_hedge, later_trade),
    ):
        print(
            f"  {label:<52} {fitted.hedge:>9.6f} {fitted.residual_std:>10.2f} "
            f"{traded.apr:>9.6f} {traded.sharpe:>9.6f}"
        )
    print(
        f"  {'VX_ES.m as shipped, 2012-05-17 save from 2008-08-01':<52} "
        f"{shipped.hedge:>9.6f} {shipped.residual_std:>10.2f} {'none':>9} {'none':>9}"
    )
    print()
    held = t.units[len(t.days) - len(t.test_days) - 1]
    changes = ", ".join(
        f"{'long' if units > 0 else 'short'} {day.date()}" for day, units in position_changes(t)
    )
    print(f"  held at the close of {h.days[-1].date()}: {held:+.0f}, then {changes}")
    print(
        f"  Annualised over {TRADING_DAYS} days with no cost. The training window was "
        "chosen against the printed figures."
    )
    print("  Exploratory. docs/replication-log.md carries the verdicts.")


def run(data_dir: Path | None = None) -> VxEs:
    """Read the 2012-05-07 and 2012-05-17 saves, run the specification, and print the report."""
    members, legs = read_legs(SOURCE_FILE, data_dir)
    result = vx_es(legs)
    _, later_legs = read_legs(SCRIPT_SOURCE_FILE, data_dir)
    report(members, result, specification(later_legs), script_as_shipped(later_legs))
    return result


def main() -> None:
    argparse.ArgumentParser(
        description="VX against ES, Algorithmic Trading's hedge from August 2008"
    ).parse_args()
    try:
        run()
    except (VintageUnavailable, WindowCrossesScaleBreak) as refused:
        # A refusal that names the source or the flagged day reaches the reader
        # as one line, the way chan.price_spread.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
