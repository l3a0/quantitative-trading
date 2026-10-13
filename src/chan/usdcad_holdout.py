"""Example 2.5's linear rule on USD/CAD after 2012, with the lookback fixed from Chan's sample.

[Issue 607](https://github.com/l3a0/quantitative-trading/issues/607) registers
the test. Entry 22 of [docs/replication-log.md](../../docs/replication-log.md)
reproduces Chan's Examples 2.1 to 2.5 on his own 1,216 closes, from 2007-07-23
to 2012-03-28, and every result there is exploratory. The sample was spent
reproducing figures Chan chose, and the 115-day lookback is the half-life of
the same closes the rule trades. This run removes both. The lookback stays
115, the half-life :mod:`chan.usdcad_mean_reversion` measures on Chan's closes,
and the rule trades only closes after 2012-03-28.

**The closes.** Alpha Vantage's ``FX_DAILY`` USD/CAD, recorded on 2026-10-13
by ``python -m chan.usdcad_holdout fetch`` and committed to ``data/`` by the
owner's ruling on the issue. The vendor's daily close is a different feed from
Chan's 16:59 bar, so this is holdout B of the issue, the long one on a
different feed. Holdout A, the same 16:59 specification on Massive's minute
bars, moved to [issue 608](https://github.com/l3a0/quantitative-trading/issues/608)
with its prediction H2. The run reads the vintage through
:func:`chan.vintage.resolve_vintage` with its download date, so a later
download cannot move it, and parses the ``Date,Close`` rows itself.

**The rule** is :func:`chan.usdcad_mean_reversion.linear_mean_reversion`
exactly. The position is minus the 115-day z-score of the close, each day's
P&L is yesterday's position times today's percent change in the close, and
there is no transaction cost and no rollover interest. It runs over the 115
closes before 2012-03-29, the warm-up, and every close from 2012-03-29 on
together. The traded days are ``pnl[115:]``, from 2012-03-29 to the last close
before the download day, and the positions that earn them are
``market_value(...)[114:-1]``. The tested closes, ``y``, are the closes over
the same span, which leaves the warm-up out because it falls inside Chan's
window.

**The predictions**, registered on the issue before any holdout close was
read. Each one's statistic, comparator and slice was fixed there too.

1. H1, the claim: ``pnl[115:].sum() > 0``. It decides the verdict.
2. H3: the Newey-West t of the mean daily P&L,
   :func:`ithildincore.stats.newey_west_summary`, exceeds 1.645. The
   registered prediction is that it does not.
3. H4: jplv7's ADF at a constant and 1 lag, :func:`chan.stationarity_tests.jplv7_adf`,
   falls below its 10 percent critical value. Predicted not to.
   ``adfuller``'s statistic at the same lag is reported beside it and decides
   nothing.
4. H5: :func:`chan.stationarity_tests.vratiotest` on ``log(y)`` rejects at 5
   percent. Predicted not to.
5. H6: ``genhurst(log(y), 2)`` falls within 2 SDs of its average over 40,000
   random walks of the same length, drawn as
   :func:`chan.usdcad_hurst_noise.random_walk_hurst` draws them. Predicted to.
6. H7: the half-life of ``y``, reported beside 115 with no prediction.

H3 to H7 decide nothing. Beside them, deciding nothing too, are the deepest
drawdown and its dates, the Sharpe ratio of the raw P&L as
:func:`chan.khandani_lo.plain_sharpe` computes it, the largest absolute
position, the shares of traded days long and short, and the weekdays with no
row over the traded days.

**Refusals.** :class:`HoldoutRefused` covers a header other than
``Date,Close``, a row without two fields, a Saturday or Sunday row, since
Chan's closes hold none and the lookback counts rows, dates that do not
strictly increase, and fewer than 115 warm-up closes.
:func:`chan.series.refuse_window_crossing_a_break`, called from the first
warm-up date, refuses a zero, negative or non-finite close and a day moving by
more than a factor of 1.6. A zero close would otherwise make H1's sum infinite
and pass it. No gap threshold is set, because Chan's own closes skip 250 days.

The result is **registered**, on the owner's calling the issue a
pre-registration on 2026-10-13. :mod:`chan.aud_cad_johansen` already read
about 20 of the holdout's first days, through 2012-04-26, from Chan's own
``inputData_USDCAD_20120426.csv`` under a different rule, and the manifest
tests read the vintage in the commit that landed it.
``tests/test_usdcad_holdout.py`` is the single authority for every number any
prose surface quotes about it, and Entry 51 of the log carries the verdict. It
first ran here on 2026-10-13. The write-up, ``blog/usdcad-holdout-lessons.md``,
teaches the result, and :mod:`chan.usdcad_holdout_figures` draws its figure.

Usage::

    zsh -i -c 'uv run python -m chan.usdcad_holdout fetch'
    uv run python -m chan.usdcad_holdout run

The fetch reads ``ALPHAVANTAGE_API_KEY`` from the environment of the run, and
the owner's ``~/.zshrc`` exports it, which is why the command runs in an
interactive ``zsh``. :func:`chan.fetch_alphavantage.fetch_fx_daily` does the
work and holds every rule about the response. The run needs no key.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.stats import NeweyWestSummary, newey_west_summary
from ithildincore.timeseries import ou_half_life

from chan import fetch_alphavantage
from chan.fetch_alphavantage import FX_BASIS, FX_SYMBOL, FX_VENDOR, KEY_ENV, RunStopped
from chan.khandani_lo import plain_sharpe
from chan.series import WindowCrossesScaleBreak, refuse_window_crossing_a_break, vintage_line
from chan.stationarity_tests import Jplv7Adf, VarianceRatio, genhurst, jplv7_adf, vratiotest
from chan.usdcad_hurst_noise import PATHS, SEED, genhurst_rows, random_walks
from chan.usdcad_mean_reversion import (
    ADF_LAGS,
    ADF_ORDER,
    HURST_Q,
    Drawdown,
    adfuller_at_one_lag,
    linear_mean_reversion,
    market_value,
    pnl_drawdown,
)
from chan.vintage import (
    VintageEntry,
    VintageRefused,
    VintageUnavailable,
    read_vintage,
    resolve_vintage,
)

#: The symbol the pair is recorded under, which the fetch fixes rather than takes.
SYMBOL = FX_SYMBOL

#: The download date that picks the holdout's vintage out of the manifest.
DOWNLOAD_DATE = "2026-10-13"

#: The frozen lookback, Chan's half-life of 115.209794 days rounded, never re-estimated.
LOOKBACK = 115

#: The first traded day, the first close after Chan's last, 2012-03-28.
HOLDOUT_START = "2012-03-29"

#: H3's bar, one-sided at 5 percent.
NEWEY_WEST_CRITICAL = 1.645

#: H6's band, in random-walk standard deviations either side of their mean.
BAND_SDS = 2

#: The walks are drawn in blocks of this many, as ``random_walk_hurst`` draws them.
CHUNK = 250

#: The vintage's header, as :func:`chan.vintage.record_vintage` writes it.
HEADER = "Date,Close"


class HoldoutRefused(Exception):
    """The run stopped rather than compute on closes it cannot trust."""


@dataclass(frozen=True)
class Band:
    """``genhurst`` over seeded random walks of one length: their mean and SD, ``ddof=1``."""

    mean: float
    sd: float
    length: int
    paths: int
    seed: int

    def holds(self, hurst: float) -> bool:
        """H6: ``hurst`` within :data:`BAND_SDS` SDs of the walks' mean."""
        return abs(hurst - self.mean) <= BAND_SDS * self.sd


@dataclass(frozen=True)
class Gap:
    """The most weekdays with no row between two consecutive closes, and those two closes."""

    weekdays: int
    after: pd.Timestamp
    before: pd.Timestamp


@dataclass(frozen=True)
class Holdout:
    """Everything the run computes on the warm-up and the holdout together."""

    entry: VintageEntry
    #: The warm-up's closes and then the holdout's, in date order.
    closes: pd.Series
    lookback: int
    #: Every row's P&L, zero through the warm-up.
    pnl: pd.Series
    #: Every row's position, ``market_value(closes, lookback)``.
    positions: np.ndarray
    newey_west: NeweyWestSummary
    adf: Jplv7Adf
    adfuller_statistic: float
    vratio: VarianceRatio
    hurst: float
    half_life: float
    drawdown: Drawdown
    sharpe: float

    @property
    def warm_up(self) -> pd.Series:
        """The ``lookback`` closes before the first traded day."""
        return self.closes.iloc[: self.lookback]

    @property
    def tested(self) -> pd.Series:
        """``y``, the closes H4 to H7 read, from the first traded day on."""
        return self.closes.iloc[self.lookback :]

    @property
    def traded(self) -> pd.Series:
        """``pnl[lookback:]``, the traded days' P&L."""
        return self.pnl.iloc[self.lookback :]

    @property
    def held(self) -> np.ndarray:
        """``market_value(...)[lookback - 1:-1]``, the positions that earn the traded days."""
        return self.positions[self.lookback - 1 : -1]

    @property
    def total_pnl(self) -> float:
        """H1's statistic, the traded days' P&L summed."""
        return float(self.traded.sum())

    @property
    def largest_position(self) -> float:
        return float(np.max(np.abs(self.held)))

    @property
    def long_share(self) -> float:
        """The share of traded days held long, with every traded day in the denominator."""
        return float(np.mean(self.held > 0))

    @property
    def short_share(self) -> float:
        """The share held short. A zero position counts as neither."""
        return float(np.mean(self.held < 0))

    @property
    def weekdays(self) -> int:
        """The weekdays from the first traded day to the last, both included."""
        return len(pd.bdate_range(self.tested.index[0], self.tested.index[-1]))

    @property
    def missing_weekdays(self) -> int:
        """Those weekdays with no row."""
        return self.weekdays - len(self.tested)

    @property
    def longest_gap(self) -> Gap:
        """The most weekdays with no row between two consecutive traded closes."""
        days = self.tested.index
        missing = [len(pd.bdate_range(a, b)) - 2 for a, b in zip(days[:-1], days[1:], strict=True)]
        at = int(np.argmax(missing))
        return Gap(weekdays=missing[at], after=days[at], before=days[at + 1])

    @property
    def h1(self) -> bool:
        return self.total_pnl > 0

    @property
    def h3(self) -> bool:
        return self.newey_west.t_newey_west > NEWEY_WEST_CRITICAL

    @property
    def h4(self) -> bool:
        return self.adf.statistic < self.adf.critical[2]

    @property
    def h5(self) -> bool:
        return bool(self.vratio.rejects)

    @property
    def log_verdict(self) -> str:
        """The verdict the issue mapped from H1 before the run."""
        return "reproduced" if self.h1 else "did not reproduce"


def parse_closes(payload: bytes, path: str = "the vintage") -> pd.Series:
    """The ``Date,Close`` rows of a recorded vintage, refused on a row the run cannot trust.

    A close is parsed as it is written, so a NaN or a zero reaches the
    scale-break guard rather than being refused here.
    """
    lines = payload.decode("utf-8").splitlines()
    if not lines or lines[0] != HEADER:
        opening = lines[0][:80] if lines else ""
        raise HoldoutRefused(f"{path} opens with {opening!r}, not {HEADER!r}")
    days, values = [], []
    for number, line in enumerate(lines[1:], start=2):
        fields = line.split(",")
        if len(fields) != 2:
            raise HoldoutRefused(f"{path} line {number} holds {len(fields)} fields, not 2")
        try:
            day = date.fromisoformat(fields[0])
            value = float(fields[1])
        except ValueError as unreadable:
            raise HoldoutRefused(f"{path} line {number} cannot be read: {unreadable}") from None
        if day.weekday() >= 5:
            raise HoldoutRefused(
                f"{path} line {number} is dated {day}, a {day.strftime('%A')}. Chan's closes hold "
                f"no weekend day and the lookback counts rows"
            )
        if days and day <= days[-1]:
            raise HoldoutRefused(
                f"{path} line {number} is dated {day}, which does not come after {days[-1]}, so "
                f"the dates do not strictly increase"
            )
        days.append(day)
        values.append(value)
    index = pd.to_datetime([day.isoformat() for day in days])
    return pd.Series(values, index=index, name=SYMBOL, dtype=float)


def read_closes(
    *, dated: str = DOWNLOAD_DATE, data_dir: Path | None = None
) -> tuple[VintageEntry, pd.Series]:
    """The holdout vintage's manifest entry and its closes."""
    entry = resolve_vintage(
        vendor=FX_VENDOR, symbol=SYMBOL, price_basis=FX_BASIS, dated=dated, data_dir=data_dir
    )
    return entry, parse_closes(read_vintage(entry, data_dir), entry.path)


def window(closes: pd.Series, *, start: str, end: str | None, lookback: int) -> pd.Series:
    """The ``lookback`` closes before ``start`` and every close from ``start`` to ``end``."""
    first = pd.Timestamp(start)
    before = closes.loc[closes.index < first]
    if len(before) < lookback:
        raise HoldoutRefused(
            f"the vintage holds {len(before)} closes before {first.date()}, and the warm-up needs "
            f"{lookback}"
        )
    after = closes.loc[closes.index >= first]
    if end is not None:
        after = after.loc[after.index <= pd.Timestamp(end)]
    if len(after) < 2:
        raise HoldoutRefused(f"the vintage holds {len(after)} closes from {first.date()} on")
    return pd.concat([before.iloc[-lookback:], after])


def compute(
    entry: VintageEntry,
    closes: pd.Series,
    *,
    start: str = HOLDOUT_START,
    end: str | None = None,
    lookback: int = LOOKBACK,
) -> Holdout:
    """Run the rule over the warm-up and the holdout, and every test on the holdout's closes."""
    kept = window(closes, start=start, end=end, lookback=lookback)
    refuse_window_crossing_a_break([(entry, closes)], start=kept.index[0], end=kept.index[-1])
    x = kept.to_numpy(dtype=float)
    y = x[lookback:]
    pnl = pd.Series(linear_mean_reversion(x, lookback), index=kept.index)
    traded = pnl.iloc[lookback:]
    return Holdout(
        entry=entry,
        closes=kept,
        lookback=lookback,
        pnl=pnl,
        positions=market_value(x, lookback),
        newey_west=newey_west_summary(traded.to_numpy()),
        adf=jplv7_adf(y, ADF_ORDER, ADF_LAGS),
        adfuller_statistic=adfuller_at_one_lag(y)[0],
        vratio=vratiotest(np.log(y)),
        hurst=genhurst(np.log(y), HURST_Q),
        half_life=ou_half_life(y),
        drawdown=pnl_drawdown(traded),
        sharpe=plain_sharpe(traded.to_numpy()),
    )


def random_walk_genhurst(
    length: int, paths: int = PATHS, seed: int = SEED, chunk: int = CHUNK
) -> Band:
    """H6's band: ``genhurst`` on ``paths`` seeded random walks of ``length`` log prices.

    The walks are :func:`chan.usdcad_hurst_noise.random_walk_hurst`'s, the same
    generator, seed and blocks, and only ``genhurst`` is computed on them. That
    costs about 6 s where the port's estimator, which this band does not need,
    adds a minute or more.
    """
    rng = np.random.default_rng(seed)
    values = np.concatenate(
        [
            genhurst_rows(random_walks(min(chunk, paths - start), length, rng), HURST_Q)
            for start in range(0, paths, chunk)
        ]
    )
    return Band(
        mean=float(values.mean()),
        sd=float(values.std(ddof=1)),
        length=length,
        paths=paths,
        seed=seed,
    )


def read_holdout(
    *,
    dated: str = DOWNLOAD_DATE,
    start: str = HOLDOUT_START,
    end: str | None = None,
    lookback: int = LOOKBACK,
    data_dir: Path | None = None,
) -> Holdout:
    """Read the vintage and compute the holdout on it."""
    entry, closes = read_closes(dated=dated, data_dir=data_dir)
    return compute(entry, closes, start=start, end=end, lookback=lookback)


def _outcome(holds: bool, registered: bool | None) -> str:
    said = "holds" if holds else "does not hold"
    if registered is None:
        return said
    return f"{said}, as registered" if holds == registered else f"{said}, against the registration"


def report(holdout: Holdout, band: Band) -> None:
    """Print the vintage, the window, each prediction with its outcome, then the side figures."""
    h = holdout
    warm, tested, traded = h.warm_up, h.tested, h.traded
    print("Example 2.5's linear rule on USD/CAD after 2012, lookback fixed at Chan's half-life")
    print(f"  closes   {vintage_line(h.entry)}, FX_DAILY's daily close")
    print(
        f"  warm-up  {len(warm)} closes, {warm.index[0].date()} to {warm.index[-1].date()}, "
        "inside Chan's window"
    )
    print(
        f"  traded   {len(traded)} days, {tested.index[0].date()} to {tested.index[-1].date()}, "
        f"lookback {h.lookback} days, frozen"
    )
    gap = h.longest_gap
    print(
        f"  gaps     {h.missing_weekdays} of {h.weekdays} weekdays have no row, the longest run "
        f"{gap.weekdays} weekday{'' if gap.weekdays == 1 else 's'}, between {gap.after.date()} "
        f"and {gap.before.date()}"
    )
    print()
    print(
        f"  H1 cumulative P&L {h.total_pnl:.4f}, against > 0: {_outcome(h.h1, None)}. "
        f"Verdict: {h.log_verdict}."
    )
    print("  H2 not run, holdout A moved to issue 608, so H1 is a single-feed result.")
    nw = h.newey_west
    print(
        f"  H3 Newey-West t {nw.t_newey_west:.4f} at lag {nw.lag} over {nw.n} days, against "
        f"> {NEWEY_WEST_CRITICAL}: {_outcome(h.h3, False)}."
    )
    print(
        f"  H4 jplv7 ADF {h.adf.statistic:.4f}, against the 10% value {h.adf.critical[2]:.4f}: "
        f"{_outcome(h.h4, False)}. adfuller beside it {h.adfuller_statistic:.4f}."
    )
    print(
        f"  H5 variance ratio p-value {h.vratio.p_value:.4f}, rejects at 5%: "
        f"{_outcome(h.h5, False)}."
    )
    print(
        f"  H6 genhurst {h.hurst:.4f}, against {band.mean:.4f} +/- {BAND_SDS} x {band.sd:.4f} "
        f"over {band.paths:,} walks of {band.length}: {_outcome(band.holds(h.hurst), True)}."
    )
    half_life = "infinite" if math.isinf(h.half_life) else f"{h.half_life:.4f}"
    print(f"  H7 half-life {half_life} days, beside the frozen {h.lookback}, no prediction.")
    print()
    print("  Beside the predictions, deciding nothing")
    d = h.drawdown
    print(
        f"  deepest drawdown {d.depth:.4f}, from {d.peak.date()} to {d.trough.date()}. "
        f"Sharpe {h.sharpe:.4f}, the raw P&L's."
    )
    print(
        f"  largest absolute position {h.largest_position:.4f}, long on {h.long_share:.4f} and "
        f"short on {h.short_share:.4f} of the traded days."
    )
    print()
    print(
        "  Registered on issue 607 before any holdout close was read. chan.aud_cad_johansen "
        "already read about 20 of the"
    )
    print(
        "  holdout's first days, through 2012-04-26, on Chan's feed under a different rule. "
        "docs/replication-log.md Entry 51 carries the verdict."
    )


def run(
    *,
    dated: str = DOWNLOAD_DATE,
    start: str = HOLDOUT_START,
    end: str | None = None,
    lookback: int = LOOKBACK,
    data_dir: Path | None = None,
) -> tuple[Holdout, Band]:
    """Read the vintage, compute the holdout and H6's band, and print the report."""
    holdout = read_holdout(dated=dated, start=start, end=end, lookback=lookback, data_dir=data_dir)
    band = random_walk_genhurst(len(holdout.tested))
    report(holdout, band)
    return holdout, band


def fetch(key: str) -> None:
    """Fetch USD/CAD's ``FX_DAILY`` closes and record them, or refuse with one line."""
    if not key:
        raise ValueError(f"{KEY_ENV} is not set, so no request was made")
    fetch_alphavantage.fetch_fx_daily(key=key)


def main(argv: Sequence[str] | None = None) -> None:
    """``python -m chan.usdcad_holdout {fetch,run}``."""
    parser = argparse.ArgumentParser(
        prog="python -m chan.usdcad_holdout",
        description=(
            "Example 2.5's linear rule on USD/CAD after 2012, issue 607. fetch records "
            f"Alpha Vantage's FX_DAILY closes, reading {KEY_ENV} from the environment, and "
            "run computes the registered predictions on them."
        ),
    )
    parser.add_argument("command", choices=("fetch", "run"))
    args = parser.parse_args(sys.argv[1:] if argv is None else list(argv))
    key = os.environ.get(KEY_ENV, "").strip() if args.command == "fetch" else ""
    try:
        if args.command == "fetch":
            fetch(key)
        else:
            run()
    except (
        HoldoutRefused,
        WindowCrossesScaleBreak,
        VintageUnavailable,
        VintageRefused,
        ValueError,
        RunStopped,
        OSError,
    ) as refusal:
        # A refusal is worth nothing at the bottom of a traceback, so it
        # reaches the reader as one line, the way chan.sp500_panel prints one.
        # The line passes through the key's redaction, in case a transport
        # error or a vendor body ever quotes the request.
        said = str(refusal).replace(key, "<key>") if key else str(refusal)
        raise SystemExit(said) from refusal


if __name__ == "__main__":
    main()
