"""Conditional Parameter Optimization, the revised edition's Example 7.1.

A trading strategy usually has a few parameters chosen once, over a training
set, and then held. Chan's Conditional Parameter Optimization re-chooses them
every day instead. A model learns to predict the strategy's own next-day return
from the parameters and the day's market conditions, and after each close it
scores every parameter set and trades the best one the next day. What is
predicted is the strategy's return, not the asset's price.

The strategy underneath trades GLD on one-minute bars against a GLD/GDX spread,
pp. 137 to 146 of the 2021 revised edition. Chan prints two columns for the
test years 2018 to 2020: the parameters held fixed, which he calls
unconditional, and the parameters re-chosen daily, which he calls conditional.

**What reproduces and what cannot.** The unconditional column is fixed by the
bars, the grid, the rules, the endnote's recursions and the selection rule,
once each setting the book leaves open has a declared reading. The conditional
column rests on PredictNow's proprietary model, whose hyperparameters the book
does not print, so its pin is Chan's claim that conditional beats unconditional
on all four metrics rather than his digits.

**The readings.** Every setting the book leaves open was declared on
[issue 23](https://github.com/l3a0/quantitative-trading/issues/23#issuecomment-5975426355)
on 2026-10-04, before this module existed or any number was computed. The
constants and functions below implement those readings and cite them by
number. A reading changed after a result was seen would be reported beside the
declared one, never substituted for it.

**The bars.** Alpha Vantage one-minute bars, as traded, read through
:mod:`chan.archive`, because the vendor's terms grant personal, non-commercial
use and the repo does not republish them.
The archive keeps the bytes and ``data/archive_vintages.jsonl`` records their
hashes. A public clone has no archive, so :func:`run` refuses there with
:class:`chan.archive.ArchiveUnavailable`.

**The model.** scikit-learn's ``HistGradientBoostingRegressor`` with default
hyperparameters, standing in for PredictNow's "random forest with boosting".
The book's printed API call sets ``'boost': 'gbdt'``, gradient-boosted trees,
which is what that estimator fits.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.signal import lfilter

from chan import archive
from chan.archive import ArchiveEntry

# --- what the book prints, pp. 137 and 145 -----------------------------------

#: The hedge ratio's grid, ``GDX_weight``, p. 137.
GDX_WEIGHTS = (2.0, 2.5, 3.0, 3.5, 4.0)
#: The entry grid. The book prints eleven tokens for a stated ten, ending
#: "2, 2, 5", and reading 7 takes the last three as 2 and 2.5.
ENTRY_THRESHOLDS = (0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 1.25, 1.5, 2.0, 2.5)
#: The spread's lookback grid, in minutes, p. 137.
LOOKBACKS = (30, 60, 90, 120, 180, 240, 360, 720)
#: ``exit_threshold = −0.6 × entry_threshold``, fixed after Chan's own
#: optimisation, p. 140.
EXIT_FRACTION = -0.6
#: The indicators' lookbacks, in minutes, p. 140.
FEATURE_LOOKBACKS = (50, 100, 200, 400, 800, 1600, 3200)

#: The first and last regular-session bars, by the minute a bar opens.
SESSION_FIRST = "09:30"
SESSION_LAST = "15:59"
#: The last regular-session bar on a day NYSE closes at 13:00.
EARLY_CLOSE_LAST = "12:59"
#: NYSE's early closes from 2006 to 2020, every one at 13:00, from the XNYS
#: calendar of ``exchange_calendars`` 4.13.2, which encodes the exchange's
#: published schedule. On these days the bars from 13:00 to 15:59 are
#: extended-hours bars, and reading 2 drops them.
EARLY_CLOSES = frozenset(
    {
        "2006-07-03", "2006-11-24", "2007-07-03", "2007-11-23", "2007-12-24",
        "2008-07-03", "2008-11-28", "2008-12-24", "2009-11-27", "2009-12-24",
        "2010-11-26", "2011-11-25", "2012-07-03", "2012-11-23", "2012-12-24",
        "2013-07-03", "2013-11-29", "2013-12-24", "2014-07-03", "2014-11-28",
        "2014-12-24", "2015-11-27", "2015-12-24", "2016-11-25", "2017-07-03",
        "2017-11-24", "2018-07-03", "2018-11-23", "2018-12-24", "2019-07-03",
        "2019-11-29", "2019-12-24", "2020-11-27", "2020-12-24",
    }
)  # fmt: skip
#: Chan's span ends here, p. 137. It starts at GDX's first day, reading 3.
SPAN_END = "2020-12-31"
#: The share of trading days the train set takes, p. 137 and reading 9.
TRAIN_FRACTION = 0.8
TRADING_DAYS = 252
#: Reported beside the pins and deciding nothing, reading 16.
COST_PER_ROUND_TRIP = 1e-4
#: The Awesome Oscillator's slow window over its fast one, ``ta``'s default
#: 34 over 5, kept when a single lookback sets the fast window, reading 12.
AO_SLOW_RATIO = 34 / 5

#: Chan's p. 145 table, at the precision he prints it.
BOOK_UNCONDITIONAL = {"cumulative": 0.73, "annual": 0.1729, "sharpe": 1.947, "calmar": 0.984}
BOOK_CONDITIONAL = {"cumulative": 0.83, "annual": 0.1977, "sharpe": 2.325, "calmar": 1.454}
#: The decimal places Chan prints each figure to.
BOOK_DECIMALS = {"cumulative": 2, "annual": 4, "sharpe": 3, "calmar": 3}

METRICS = ("cumulative", "annual", "sharpe", "calmar")


@dataclass(frozen=True)
class Cell:
    """One of the 400 parameter sets."""

    weight: float
    entry: float
    lookback: int

    @property
    def label(self) -> str:
        """Chan's own spelling of a cell, as his p. 145 output prints it, weight_lookback_entry."""
        return f"{self.weight:g}_{self.lookback}_{self.entry:g}"


def cells() -> list[Cell]:
    """The grid in the order ties break, reading 10: weight slowest, then entry, then lookback."""
    return [Cell(w, e, n) for w in GDX_WEIGHTS for e in ENTRY_THRESHOLDS for n in LOOKBACKS]


# --- the bars ----------------------------------------------------------------


def regular_session(bars: pd.DataFrame, end: str = SPAN_END) -> pd.DataFrame:
    """The regular-session bars on or before ``end``, reading 2.

    That is the bars opening from 09:30 to 15:59, or to 12:59 on one of
    :data:`EARLY_CLOSES`. On those days the bars after 12:59 are extended-hours
    trading, so keeping them would trade, liquidate and read features on
    after-hours prints. The first run kept them, which broke reading 2, and the
    review of the pull request found it.
    """
    minutes = bars.index.strftime("%H:%M")
    early = bars.index.strftime("%Y-%m-%d").isin(EARLY_CLOSES)
    last = np.where(early, EARLY_CLOSE_LAST, SESSION_LAST)
    keep = (minutes >= SESSION_FIRST) & (minutes <= last) & (bars.index <= f"{end} 23:59")
    return bars[keep]


def minute_grid(gld: pd.Series, gdx: pd.Series) -> pd.DataFrame:
    """The two closes on one grid of minutes, reading 4.

    A day's grid is every regular-session minute at which either symbol traded,
    on a day both traded. Each close carries forward within its day and never
    across a night, and a minute before either symbol's first trade of the day
    is dropped, because the spread does not exist there.
    """
    frame = pd.concat({"gld": gld, "gdx": gdx}, axis=1, sort=True)
    # A day one symbol never traded keeps that symbol's column empty after the
    # fill, so dropping incomplete minutes drops the whole day.
    frame = frame.groupby(frame.index.normalize()).ffill()
    return frame.dropna()


def day_bounds(
    index: pd.DatetimeIndex,
) -> tuple[NDArray[np.bool_], NDArray[np.bool_], NDArray[np.intp], pd.DatetimeIndex]:
    """Each minute's day: whether it opens or closes its day, its day number, and the days."""
    days = index.normalize()
    codes, uniques = pd.factorize(days)
    codes = np.asarray(codes, dtype=np.intp)
    first = np.ones(len(codes), dtype=bool)
    first[1:] = codes[1:] != codes[:-1]
    last = np.ones(len(codes), dtype=bool)
    last[:-1] = codes[1:] != codes[:-1]
    return first, last, codes, pd.DatetimeIndex(uniques)


# --- the strategy, equations (1) and (2), the endnote and rules a to d -------


def ema_var(
    spread: NDArray[np.float64], lookback: int
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """The endnote's ``Spread_EMA`` and ``Spread_VAR``, reading 5.

    ``EMA(0) = Spread(0)`` and ``EMA(t+1) = α·Spread(t+1) + (1−α)·EMA(t)``.
    ``VAR(1) = (Spread(1) − Spread(0))²`` and
    ``VAR(t+1) = α·(Spread(t+1) − EMA(t+1))² + (1−α)·VAR(t)``, with
    ``α = 2 / lookback``. ``VAR(0)`` is undefined and comes back NaN.
    """
    alpha = 2.0 / lookback
    decay = 1.0 - alpha
    ema = lfilter([alpha], [1.0, -decay], spread, zi=[decay * spread[0]])[0]
    var = np.full(len(spread), np.nan)
    if len(spread) > 1:
        var[1] = (spread[1] - spread[0]) ** 2
    if len(spread) > 2:
        squared = (spread[2:] - ema[2:]) ** 2
        var[2:] = lfilter([alpha], [1.0, -decay], squared, zi=[decay * var[1]])[0]
    return ema, var


def zscore(spread: NDArray[np.float64], lookback: int) -> NDArray[np.float64]:
    """Equation (2), NaN wherever the variance is undefined or zero, reading 5."""
    ema, var = ema_var(spread, lookback)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (spread - ema) / np.sqrt(var)
    z[~(var > 0)] = np.nan
    return z


def positions(z: NDArray[np.float64], entry: float, first: NDArray[np.bool_]) -> NDArray[np.int8]:
    """The position held after each minute's close under rules a to d, reading 6.

    Exits apply before entries, so a long whose z-score rises above the entry
    threshold exits and goes short on the same close. Every day starts flat,
    and a minute whose z-score is NaN fires no rule.

    The rules collapse to events. Below −entry is long and above +entry is
    short. Between −0.6·entry and +0.6·entry both exits fire, so it is flat.
    The two bands left over exit one side only: from 0.6·entry to entry a long
    goes flat and anything else holds, and from −entry to −0.6·entry a short
    goes flat. Those two need the position before them, which is the last of
    the other events, so one forward fill finds it and a second applies them.
    ``tests/test_cpo.py`` holds this against a literal loop over the rules.
    """
    inner = -EXIT_FRACTION * entry
    valid = ~np.isnan(z)
    zz = np.where(valid, z, 0.0)
    decisive = np.full(len(z), np.int8(0))
    decisive_at = np.zeros(len(z), dtype=bool)
    long_entry = valid & (zz < -entry)
    short_entry = valid & (zz > entry)
    both_exit = valid & (zz > -inner) & (zz < inner)
    decisive[long_entry] = 1
    decisive[short_entry] = -1
    decisive_at |= long_entry | short_entry | both_exit
    decisive_at |= first
    before = _forward_fill(decisive, decisive_at)
    long_exit_only = valid & (zz >= inner) & (zz <= entry) & (before == 1)
    short_exit_only = valid & (zz >= -entry) & (zz <= -inner) & (before == -1)
    events = decisive.copy()
    events[long_exit_only | short_exit_only] = 0
    return _forward_fill(events, decisive_at | long_exit_only | short_exit_only)


def _forward_fill(values: NDArray[np.int8], at: NDArray[np.bool_]) -> NDArray[np.int8]:
    """Carry each marked value forward until the next mark. The first minute must be marked."""
    index = np.where(at, np.arange(len(values)), 0)
    np.maximum.accumulate(index, out=index)
    return values[index]


def round_trips(
    held: NDArray[np.int8],
    price: NDArray[np.float64],
    first: NDArray[np.bool_],
    last: NDArray[np.bool_],
    codes: NDArray[np.intp],
    n_days: int,
) -> tuple[NDArray[np.float64], NDArray[np.int64]]:
    """Each day's summed round-trip return and its count of trips, readings 6 and 8.

    A trip is a run of one non-zero position within a day. It is entered at the
    close of the run's first minute and exited at the close of the minute after
    its last, or at the day's last close where the run reaches it. A position
    taken at the day's last close is liquidated at that same close, so it earns
    nothing and is not counted. A trip returns ``side × (exit / entry − 1)``.
    """
    n = len(held)
    nonzero = held != 0
    start = nonzero.copy()
    start[1:] &= first[1:] | (held[1:] != held[:-1])
    end = nonzero.copy()
    end[:-1] &= last[:-1] | (held[1:] != held[:-1])
    starts = np.flatnonzero(start)
    ends = np.flatnonzero(end)
    exits = np.where(last[ends], ends, np.minimum(ends + 1, n - 1))
    earning = exits > starts
    starts, exits = starts[earning], exits[earning]
    side = held[starts].astype(np.float64)
    returns = side * (price[exits] / price[starts] - 1.0)
    day = codes[starts]
    return (
        np.bincount(day, weights=returns, minlength=n_days),
        np.bincount(day, minlength=n_days).astype(np.int64),
    )


@dataclass(frozen=True)
class Labels:
    """The daily return of every cell on every day, and its round trips."""

    days: pd.DatetimeIndex
    returns: NDArray[np.float64]
    trips: NDArray[np.int64]


def strategy_labels(grid: pd.DataFrame) -> Labels:
    """Run all 400 cells over the minute grid, reading 8."""
    first, last, codes, days = day_bounds(grid.index)
    gld = grid["gld"].to_numpy(dtype=np.float64)
    gdx = grid["gdx"].to_numpy(dtype=np.float64)
    grid_cells = cells()
    returns = np.empty((len(days), len(grid_cells)))
    trips = np.empty((len(days), len(grid_cells)), dtype=np.int64)
    column = {cell: i for i, cell in enumerate(grid_cells)}
    for weight in GDX_WEIGHTS:
        spread = gld - weight * gdx
        for lookback in LOOKBACKS:
            z = zscore(spread, lookback)
            for entry in ENTRY_THRESHOLDS:
                held = positions(z, entry, first)
                i = column[Cell(weight, entry, lookback)]
                returns[:, i], trips[:, i] = round_trips(held, gld, first, last, codes, len(days))
    return Labels(days, returns, trips)


# --- selection, split and metrics -------------------------------------------


def train_days(n_days: int) -> int:
    """How many of the first days the train set takes, reading 9."""
    return int(TRAIN_FRACTION * n_days)


def unconditional_cell(train_returns: NDArray[np.float64]) -> int:
    """The column with the highest compounded train return, the first on a tie, reading 10."""
    compounded = np.prod(1.0 + train_returns, axis=0) - 1.0
    return int(np.argmax(compounded))


def metrics(returns: NDArray[np.float64]) -> dict[str, float]:
    """pyfolio's four, reading 11, plus the arithmetic annual return reported beside them."""
    wealth = np.cumprod(1.0 + returns)
    cumulative = float(wealth[-1] - 1.0)
    annual = float((1.0 + cumulative) ** (TRADING_DAYS / len(returns)) - 1.0)
    peak = np.maximum.accumulate(np.concatenate([[1.0], wealth]))[1:]
    drawdown = float(np.min(wealth / peak - 1.0))
    return {
        "cumulative": cumulative,
        "annual": annual,
        "sharpe": float(np.sqrt(TRADING_DAYS) * returns.mean() / returns.std(ddof=1)),
        "calmar": annual / abs(drawdown) if drawdown < 0 else float("inf"),
        "arithmetic_annual": float(TRADING_DAYS * returns.mean()),
        "max_drawdown": drawdown,
    }


# --- the features and the model ---------------------------------------------


def indicators(bars: pd.DataFrame, lookback: int) -> pd.DataFrame:
    """The seven named indicators at one lookback, reading 12.

    Six come from ``ta`` 0.11.0. The Bollinger z-score is computed here, with the
    population standard deviation ``ta``'s Bollinger bands use, because ``ta``
    gives the bands and their width rather than the z-score. ``ta``'s ATR and ADX
    return 0 rather than NaN before their window fills, so the earliest rows
    carry zeros the model cannot tell from readings. Reading 12 takes ``ta`` as
    it is, so that is left alone and stated.
    """
    from ta.momentum import AwesomeOscillatorIndicator
    from ta.trend import ADXIndicator
    from ta.volatility import AverageTrueRange, DonchianChannel
    from ta.volume import ForceIndexIndicator, MFIIndicator

    high, low, close = bars["high"], bars["low"], bars["close"]
    volume = bars["volume"].astype(np.float64)
    mean = close.rolling(lookback, min_periods=lookback).mean()
    spread = close.rolling(lookback, min_periods=lookback).std(ddof=0)
    return pd.DataFrame(
        {
            "bbz": (close - mean) / spread,
            "mfi": MFIIndicator(high, low, close, volume, lookback).money_flow_index(),
            "force": ForceIndexIndicator(close, volume, lookback).force_index(),
            "donchian": DonchianChannel(high, low, close, lookback).donchian_channel_pband(),
            "atr": AverageTrueRange(high, low, close, lookback).average_true_range(),
            "ao": AwesomeOscillatorIndicator(
                high, low, lookback, int(round(AO_SLOW_RATIO * lookback))
            ).awesome_oscillator(),
            "adx": ADXIndicator(high, low, close, lookback).adx(),
        },
        index=bars.index,
    )


def daily_features(bars: pd.DataFrame, prefix: str, days: pd.DatetimeIndex) -> pd.DataFrame:
    """Each indicator's value at the symbol's last regular-session bar of each day, reading 13."""
    session = regular_session(bars)
    final = ~session.index.normalize().duplicated(keep="last")
    columns = []
    for lookback in FEATURE_LOOKBACKS:
        values = indicators(session, lookback)[final]
        values.index = values.index.normalize()
        values.columns = [f"{prefix}_{name}_{lookback}" for name in values.columns]
        columns.append(values)
    return pd.concat(columns, axis=1).reindex(days)


def design_rows(features: NDArray[np.float32], day_rows: NDArray[np.intp]) -> NDArray[np.float32]:
    """One row per cell for each listed day: the three parameters, then the day's features."""
    grid = np.array([[c.weight, c.entry, c.lookback] for c in cells()], dtype=np.float32)
    per_day = features[day_rows]
    n_cells = len(grid)
    out = np.empty((len(day_rows) * n_cells, 3 + features.shape[1]), dtype=np.float32)
    out[:, :3] = np.tile(grid, (len(day_rows), 1))
    out[:, 3:] = np.repeat(per_day, n_cells, axis=0)
    return out


def fit_model(features: NDArray[np.float32], returns: NDArray[np.float64], n_train: int):
    """Fit on train rows only, reading 14: features at close d, labels of day d+1, both in train."""
    from sklearn.ensemble import HistGradientBoostingRegressor

    decided = np.arange(n_train - 1)
    x = design_rows(features, decided)
    y = returns[decided + 1].reshape(-1).astype(np.float64)
    return HistGradientBoostingRegressor(random_state=0).fit(x, y)


def conditional_choices(
    model, features: NDArray[np.float32], n_train: int, n_days: int
) -> NDArray[np.intp]:
    """For each test day, the cell the model scores highest from the previous close, reading 15."""
    decided = np.arange(n_train - 1, n_days - 1)
    scores = model.predict(design_rows(features, decided)).reshape(len(decided), len(cells()))
    return np.argmax(scores, axis=1)


# --- the run ----------------------------------------------------------------


@dataclass(frozen=True)
class Result:
    """Everything the report prints, and every figure the tests pin."""

    vintages: tuple[ArchiveEntry, ArchiveEntry]
    days: pd.DatetimeIndex
    n_train: int
    unconditional: Cell
    unconditional_returns: NDArray[np.float64]
    unconditional_trips: NDArray[np.int64]
    conditional_cells: NDArray[np.intp]
    conditional_returns: NDArray[np.float64]
    conditional_trips: NDArray[np.int64]
    #: Every cell's test-window Sharpe ratio and round trips a day, in grid
    #: order. Added after the result was seen, to say where Chan's 1.947 sits
    #: among them. It decides nothing.
    cell_sharpes: NDArray[np.float64]
    cell_trips: NDArray[np.float64]

    @property
    def test_days(self) -> pd.DatetimeIndex:
        return self.days[self.n_train :]


def run(data_dir: Path | None = None, directory: Path | None = None) -> Result:
    """Read both archive vintages, run all 400 cells, choose both arms and return the test days."""
    gld_bars = archive.minute_bars("GLD", data_dir=data_dir, directory=directory)
    gdx_bars = archive.minute_bars("GDX", data_dir=data_dir, directory=directory)
    grid = minute_grid(regular_session(gld_bars)["close"], regular_session(gdx_bars)["close"])
    labels = strategy_labels(grid)
    n_days = len(labels.days)
    n_train = train_days(n_days)

    best = unconditional_cell(labels.returns[:n_train])
    test = slice(n_train, n_days)

    features = pd.concat(
        [
            daily_features(gld_bars, "gld", labels.days),
            daily_features(gdx_bars, "gdx", labels.days),
        ],
        axis=1,
    ).to_numpy(dtype=np.float32)
    model = fit_model(features, labels.returns, n_train)
    chosen = conditional_choices(model, features, n_train, n_days)
    rows = np.arange(n_train, n_days)

    return Result(
        vintages=(gld_bars.attrs["vintage"], gdx_bars.attrs["vintage"]),
        days=labels.days,
        n_train=n_train,
        unconditional=cells()[best],
        unconditional_returns=labels.returns[test, best],
        unconditional_trips=labels.trips[test, best],
        conditional_cells=chosen,
        conditional_returns=labels.returns[rows, chosen],
        conditional_trips=labels.trips[rows, chosen],
        cell_sharpes=np.array(
            [metrics(labels.returns[test, i])["sharpe"] for i in range(len(cells()))]
        ),
        cell_trips=labels.trips[test].mean(axis=0),
    )


def costed(returns: NDArray[np.float64], trips: NDArray[np.int64]) -> NDArray[np.float64]:
    """Daily returns net of :data:`COST_PER_ROUND_TRIP` on every trip, reading 16."""
    return returns - COST_PER_ROUND_TRIP * trips


def claim_holds(unconditional: dict[str, float], conditional: dict[str, float]) -> bool:
    """Chan's claim, reading 18: conditional beats unconditional on all four metrics."""
    return all(conditional[name] > unconditional[name] for name in METRICS)


def report(result: Result) -> None:
    for entry in result.vintages:
        print(
            f"vintage  {entry.symbol}  {entry.vendor}  {entry.price_basis}  "
            f"downloaded {entry.download_date}  {entry.path}  sha256 {entry.sha256[:12]}"
        )
    days = result.days
    print(
        f"span     {days[0]:%Y-%m-%d} to {days[-1]:%Y-%m-%d}, {len(days)} days, "
        f"test from {result.test_days[0]:%Y-%m-%d} ({len(result.test_days)} days)"
    )
    print(f"unconditional cell  {result.unconditional.label}  (weight_lookback_entry)")
    arms = {
        "unconditional": (
            result.unconditional_returns,
            result.unconditional_trips,
            BOOK_UNCONDITIONAL,
        ),
        "conditional": (result.conditional_returns, result.conditional_trips, BOOK_CONDITIONAL),
    }
    figures = {}
    for name, (returns, trips, book) in arms.items():
        gross = metrics(returns)
        net = metrics(costed(returns, trips))
        figures[name] = gross
        print(f"\n{name}, test days, zero cost")
        for metric in METRICS:
            places = BOOK_DECIMALS[metric]
            print(
                f"  {metric:<10}  {gross[metric]:.{places}f}  book {book[metric]:.{places}f}  "
                f"gap {gross[metric] - book[metric]:+.{places}f}"
            )
        print(f"  arithmetic annual {gross['arithmetic_annual']:.4f}, deciding nothing")
        print(f"  round trips a day {trips.mean():.1f}")
        print(
            "  net of 1 bp a round trip, deciding nothing: "
            + ", ".join(f"{m} {net[m]:.4f}" for m in METRICS)
        )
    held = claim_holds(figures["unconditional"], figures["conditional"])
    verdict = "holds" if held else "does not hold"
    print(f"\nChan's claim, conditional beats unconditional on all four: {verdict}")
    sharpes = result.cell_sharpes
    nearest = int(np.argmin(np.abs(sharpes - BOOK_UNCONDITIONAL["sharpe"])))
    print(
        "\nadded after the result was seen, deciding nothing: the 400 cells' test Sharpe "
        f"ratios run from {sharpes.min():.3f} to {sharpes.max():.3f}, "
        f"median {np.median(sharpes):.3f}. "
        f"{int((sharpes < BOOK_UNCONDITIONAL['sharpe']).sum())} sit below Chan's 1.947, and the "
        f"nearest is {cells()[nearest].label} at {sharpes[nearest]:.3f}, "
        f"{result.cell_trips[nearest]:.1f} round trips a day"
    )


def main() -> None:
    report(run())


if __name__ == "__main__":
    main()
