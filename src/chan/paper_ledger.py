"""A daily paper ledger on SPY and QQQ, read from ``marketlake``'s lake. A pipeline test.

Every other result in this repo is a backtest over closes already known. This
module is the first path that turns a rule into a position at a moment when
the close is not yet known, and then compares that position with what the
backtest would have held.
[Issue 775](https://github.com/l3a0/quantitative-trading/issues/775) is the
source of truth for what it must do.

**The strategy claims no edge.** It is :func:`chan.khandani_lo.reversal_weights`
on two tickers, a placeholder until
[issue 774](https://github.com/l3a0/quantitative-trading/issues/774) chooses a
real one. Its positions say whether this path and the backtest agree, and the
module computes no paper profit. ``docs/design.md``'s subsection on the paper
ledger carries the reasoning behind every choice below, and this docstring
says only what the code does.

**What one session computes.** For session t, with yesterday's official close
and today's quote at the decision minute:

1. The decision minute is ten minutes before the session's close, by the
   exchange calendar, so 12:50 on a half day.
2. The decision price is the mid of the quote at that minute.
   :func:`decision_quote` reads only rows stamped at or before it, and refuses
   a minute holding two rows, a quote that is not real-time, and a crossed or
   non-positive one.
3. The weights are ``reversal_weights`` on a two-row array, yesterday's closes
   over today's mids.
4. The position held coming in is the same computation one session earlier,
   so a session needs no state carried between runs.
5. The trade is the change in weight. A buy fills at the ask and a sell at the
   bid.
6. The replay is ``reversal_weights`` on the panel of official closes.

**Three measures per session**, which the issue calls gaps and the code does
not, because ``docs/design.md`` pins *gap* for another meaning.

1. **Position mismatch**, the number of tickers whose side differs between the
   ledger and the replay. The report prints each flipped ticker's return
   against the mean at the decision minute and at the close.
2. **The decision-price difference**, ``(mid − close) / close`` in basis points.
3. **The spread paid**, ``|fill − mid| / mid`` in basis points, beside
   :data:`chan.khandani_lo.ONE_WAY_COST`.

**What it reads.** :class:`MarketLake` reads ``marketlake``'s lake through that
repo's ``lake`` package, the optional ``lake`` extra, imported only when it is
built. It passes the root :func:`lake_root` resolves to every read, so
``marketlake``'s own config file, which holds a broker secret, is never read.
It hashes each partition against ``marketlake``'s ``manifest.jsonl`` before
reading it, and walks the exchange calendar's sessions rather than the bars
the lake happens to hold.

**How it fails.** A session that cannot be computed is one line in the report,
and the command exits 1. A lake or environment that is wrong stops the run
with one line on stderr and exit 2: the extra not installed, no lake root, a
partition that does not match its sha256, and a damaged ``marketlake`` ledger.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Protocol

import numpy as np
import pandas as pd

from chan.khandani_lo import ONE_WAY_COST, reversal_weights

#: The two tickers ``marketlake`` captures today.
TICKERS = ("SPY", "QQQ")

#: How long before the session's close the decision is made, which leaves room
#: to submit an order for the closing auction.
MINUTES_BEFORE_CLOSE = 10

#: ``marketlake``'s wall-clock zone, in which a quote minute is named.
MARKET_TZ = "America/New_York"

#: How many sessions before the first one a run reads. Session t's position
#: coming in needs the close two sessions back.
SESSIONS_BEFORE = 2

#: The lake root for one run, and the file that holds it otherwise.
LAKE_ROOT_ENV = "QT_LAKE_ROOT"
LAKE_ROOT_CONFIG = Path("~/.config/quantitative-trading/lake_root")

BASIS_POINTS = 10_000

#: The columns :func:`decision_quote` reads from a quotes table.
QUOTE_COLUMNS = ("snap_ts", "vendor_quote_ts", "bid", "ask", "last", "realtime")

#: How far back :meth:`MarketLake.sessions` looks for the sessions before the
#: first. Two sessions never sit more than this many calendar days apart.
CALENDAR_LOOKBACK_DAYS = 14

#: The words the report opens on, so no run's output can be read without them.
NO_EDGE = (
    "A pipeline test. The strategy is chan.khandani_lo.reversal_weights as a placeholder, "
    "and it claims no edge. Its positions say whether this path and the backtest agree. "
    "Nothing here is evidence that the rule pays."
)


class LedgerRefused(Exception):
    """One session cannot be computed. The run reports it and goes on."""


class LakeUnavailable(Exception):
    """The lake or this environment is wrong, so the whole run stops."""


@dataclass(frozen=True)
class Quote:
    """The one quote row a decision reads."""

    snap_ts: pd.Timestamp
    vendor_ts: pd.Timestamp
    bid: float
    ask: float
    last: float

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def lag_seconds(self) -> float:
        """How long after its minute the vendor stamped the quote, NaN when it did not."""
        if pd.isna(self.vendor_ts):
            return float("nan")
        return (self.vendor_ts - self.snap_ts).total_seconds()


def decision_quote(rows: pd.DataFrame, decision: pd.Timestamp) -> Quote:
    """The latest quote stamped at or before ``decision``, or :class:`LedgerRefused`.

    A row stamped after the decision minute is never read, whatever it holds.
    ``marketlake``'s minute read hands over only the decision minute's row
    today, and this is what keeps that true if the read ever changes.

    It refuses when no row is stamped at or before the minute, when the minute
    holds two rows, when the quote is not real-time, and when the bid is not
    positive or the ask is below the bid. ``marketlake``'s loader docstring
    records two minutes written twice on one partition, and a delayed quote is
    fifteen minutes stale.
    """
    stamps = pd.to_datetime(rows["snap_ts"], utc=True, format="ISO8601")
    known = rows[stamps <= decision]
    if known.empty:
        raise LedgerRefused(f"no quote is stamped at or before {_minute(decision)}")
    known_stamps = stamps[stamps <= decision]
    latest = known_stamps.max()
    chosen = known[known_stamps == latest]
    if len(chosen) > 1:
        raise LedgerRefused(f"{len(chosen)} quote rows share the minute {_minute(latest)}")
    row = chosen.iloc[0]
    realtime = row["realtime"]
    if pd.isna(realtime) or not bool(realtime):
        raise LedgerRefused(f"the quote at {_minute(latest)} is not real-time")
    bid, ask = float(row["bid"]), float(row["ask"])
    if not (np.isfinite(bid) and np.isfinite(ask) and bid > 0 and ask >= bid):
        raise LedgerRefused(f"the quote at {_minute(latest)} reads bid {bid} and ask {ask}")
    vendor = pd.to_datetime(row["vendor_quote_ts"], utc=True, format="ISO8601")
    return Quote(snap_ts=latest, vendor_ts=vendor, bid=bid, ask=ask, last=float(row["last"]))


def target_weights(previous_close: np.ndarray, price: np.ndarray) -> np.ndarray:
    """``reversal_weights`` on yesterday's closes over today's prices, today's row."""
    return reversal_weights(np.vstack([previous_close, price]))[1]


@dataclass(frozen=True)
class Leg:
    """One ticker on one session."""

    ticker: str
    quote: Quote
    close: float
    held: float
    weight: float
    replay: float
    decision_return: float
    close_return: float

    @property
    def trade(self) -> float:
        return self.weight - self.held

    @property
    def fill(self) -> float:
        """The ask for a buy, the bid for a sell, NaN when nothing trades."""
        if self.trade > 0:
            return self.quote.ask
        if self.trade < 0:
            return self.quote.bid
        return float("nan")

    @property
    def against_close_bp(self) -> float:
        return (self.quote.mid - self.close) / self.close * BASIS_POINTS

    @property
    def spread_bp(self) -> float:
        return abs(self.fill - self.quote.mid) / self.quote.mid * BASIS_POINTS

    @property
    def side_matches(self) -> bool:
        return bool(np.sign(self.weight) == np.sign(self.replay))


@dataclass(frozen=True)
class Session:
    """One session of the ledger beside its replay."""

    day: date
    decision: pd.Timestamp
    legs: tuple[Leg, ...]

    @property
    def mismatch(self) -> int:
        return sum(not leg.side_matches for leg in self.legs)

    @property
    def spread_bp(self) -> float:
        """The spread paid, each ticker weighted by the size of its trade."""
        return _trade_weighted(self.legs)


@dataclass(frozen=True)
class LakeRead:
    """What a run read from the lake, before anything is computed.

    ``closes`` has one row per calendar session, the first two before the
    range, and NaN where no bar was read. ``close_refusals`` says why a bar
    the lake holds could not be read. ``quotes`` maps a session and ticker to
    the quote its decision reads, or to why there is none.
    """

    closes: pd.DataFrame
    quotes: Mapping[tuple[date, str], Quote | str]
    decisions: Mapping[date, pd.Timestamp]
    close_refusals: Mapping[tuple[date, str], str] = field(default_factory=dict)


class Lake(Protocol):
    """What :func:`read_lake` asks of a lake. :class:`MarketLake` is the real one."""

    def sessions(self, first: date, last: date) -> list[date]: ...

    def session_close(self, day: date) -> pd.Timestamp: ...

    def closes(self, ticker: str, start: date, end: date) -> dict[date, float | str]: ...

    def quote_rows(self, ticker: str, day: date, snap: str) -> pd.DataFrame: ...


def decision_minute(session_close: pd.Timestamp) -> pd.Timestamp:
    return session_close - timedelta(minutes=MINUTES_BEFORE_CLOSE)


def read_lake(lake: Lake, first: date, last: date) -> LakeRead:
    """Read every close and decision quote the sessions from ``first`` to ``last`` need."""
    days = lake.sessions(first, last)
    closes = pd.DataFrame(np.nan, index=days, columns=list(TICKERS))
    close_refusals: dict[tuple[date, str], str] = {}
    for ticker in TICKERS:
        for day, close in lake.closes(ticker, days[0], days[-1]).items():
            if day not in closes.index:
                continue
            if isinstance(close, str):
                close_refusals[(day, ticker)] = close
            else:
                closes.loc[day, ticker] = close
    quotes: dict[tuple[date, str], Quote | str] = {}
    decisions: dict[date, pd.Timestamp] = {}
    for day in days[SESSIONS_BEFORE - 1 :]:
        decision = decision_minute(lake.session_close(day))
        decisions[day] = decision
        for ticker in TICKERS:
            try:
                rows = lake.quote_rows(ticker, day, _minute(decision))
                quotes[(day, ticker)] = decision_quote(rows, decision)
            except LedgerRefused as refused:
                quotes[(day, ticker)] = str(refused)
    return LakeRead(
        closes=closes, quotes=quotes, decisions=decisions, close_refusals=close_refusals
    )


def ledger(read: LakeRead) -> tuple[list[Session], list[tuple[date, str]]]:
    """Every session from the third row of ``read.closes`` on, and every one refused."""
    days = list(read.closes.index)
    tickers = list(read.closes.columns)
    closes = read.closes.to_numpy(dtype=float)
    replay = reversal_weights(closes)
    sessions: list[Session] = []
    refused: list[tuple[date, str]] = []
    for i in range(SESSIONS_BEFORE, len(days)):
        day, before = days[i], days[i - 1]
        reasons = _missing(read, days, closes, i)
        if reasons:
            refused.append((day, "; ".join(reasons)))
            continue
        held_mids = np.array([read.quotes[(before, t)].mid for t in tickers])
        mids = np.array([read.quotes[(day, t)].mid for t in tickers])
        held = target_weights(closes[i - 2], held_mids)
        weight = target_weights(closes[i - 1], mids)
        decision_returns = mids / closes[i - 1] - 1
        close_returns = closes[i] / closes[i - 1] - 1
        legs = tuple(
            Leg(
                ticker=t,
                quote=read.quotes[(day, t)],
                close=float(closes[i, j]),
                held=float(held[j]),
                weight=float(weight[j]),
                replay=float(replay[i, j]),
                decision_return=float(decision_returns[j] - decision_returns.mean()),
                close_return=float(close_returns[j] - close_returns.mean()),
            )
            for j, t in enumerate(tickers)
        )
        sessions.append(Session(day=day, decision=read.decisions[day], legs=legs))
    return sessions, refused


def lake_root(
    named: str | None = None,
    environ: Mapping[str, str] | None = None,
    config: Path | None = None,
) -> Path:
    """The lake to read, from ``--lake-root``, then ``QT_LAKE_ROOT``, then the config file.

    Never from ``marketlake``'s own config, which holds a broker secret.
    """
    environ = os.environ if environ is None else environ
    config = LAKE_ROOT_CONFIG.expanduser() if config is None else config
    text = (named or "").strip() or environ.get(LAKE_ROOT_ENV, "").strip()
    if not text and config.is_file():
        text = config.read_text(encoding="utf-8").strip()
    if not text:
        raise LakeUnavailable(
            f"no lake root is configured. Pass --lake-root, set {LAKE_ROOT_ENV}, or write the "
            f"lake's path on one line to {LAKE_ROOT_CONFIG}"
        )
    root = Path(text).expanduser()
    if not root.is_dir():
        raise LakeUnavailable(f"the lake root {root} is not a directory")
    return root


def check_partition(
    root: Path,
    path: Path,
    entries: Mapping[str, Mapping[str, object]],
    digest: Callable[[Path], str],
) -> tuple[str, str]:
    """``path``'s name under the lake and its sha256, once it matches ``manifest.jsonl``."""
    name = path.relative_to(root).as_posix()
    entry = entries.get(name)
    if entry is None:
        raise LakeUnavailable(f"{name} is not in marketlake's manifest.jsonl")
    found = digest(path)
    if found != entry["sha256"]:
        raise LakeUnavailable(
            f"{name} hashes to {found}, and marketlake's manifest.jsonl records {entry['sha256']}"
        )
    return name, found


class MarketLake:
    """A :class:`Lake` read through ``marketlake``'s own package.

    Every read passes ``lake_root``, and checks each partition against
    ``manifest.jsonl`` before reading it. ``checked`` keeps what was checked,
    for the report.
    """

    def __init__(self, root: Path) -> None:
        try:
            from lake import loader, manifest, paths
            from lake.calendar import ExchangeCalendar
        except ImportError as missing:
            raise LakeUnavailable(
                "marketlake's lake package is not installed here. "
                "Run `uv sync --extra lake` and try again"
            ) from missing
        self._root = root
        self._loader = loader
        self._manifest = manifest
        self._paths = paths.LakePaths(root)
        self._calendar = ExchangeCalendar()
        try:
            self._entries = manifest.latest_entries(root)
        except manifest.ManifestError as damaged:
            raise LakeUnavailable(f"marketlake's manifest.jsonl cannot be read: {damaged}") from (
                damaged
            )
        self.checked: dict[str, str] = {}

    def sessions(self, first: date, last: date) -> list[date]:
        before = []
        day = first
        for _ in range(CALENDAR_LOOKBACK_DAYS):
            day -= timedelta(days=1)
            if self._calendar.is_session(day):
                before.insert(0, day)
                if len(before) == SESSIONS_BEFORE:
                    break
        return before + self._sessions_between(first, last)

    def session_close(self, day: date) -> pd.Timestamp:
        return pd.Timestamp(self._calendar.session_close(day))

    def closes(self, ticker: str, start: date, end: date) -> dict[date, float | str]:
        """Each session's official close, or why it has none, one session at a time.

        One read per session rather than one over the range, because
        ``load_bars`` refuses a whole range for one quarantined day, and
        because each partition is then checked before it is read. A session
        with no partition is left out, which the ledger reports as no bar.
        """
        found: dict[date, float | str] = {}
        for day in self._sessions_between(start, end):
            path = self._paths.bars_partition_path(ticker, "1d", day)
            if not path.is_file():
                continue
            self._check(path)
            try:
                bars = self._loader.load_bars(ticker, "1d", day, day, lake_root=self._root)
            except self._loader.LoadError as refused:
                found[day] = _named(refused)
                continue
            except self._manifest.ManifestError as damaged:
                raise LakeUnavailable(f"marketlake's ledgers cannot be read: {damaged}") from (
                    damaged
                )
            except (ValueError, OSError) as unreadable:
                # pyarrow's errors for bytes it cannot decode subclass these two.
                found[day] = f"its partition cannot be decoded: {_named(unreadable)}"
                continue
            close = bars.column("close").to_pylist()
            found[day] = float(close[0]) if len(close) == 1 else f"{len(close)} daily bars"
        return found

    def quote_rows(self, ticker: str, day: date, snap: str) -> pd.DataFrame:
        path = self._paths.quotes_partition_path(ticker, day)
        if path.is_file():
            self._check(path)
        try:
            table = self._loader.load_quotes(ticker, day, snap=snap, lake_root=self._root)
        except self._loader.LoadError as refused:
            raise LedgerRefused(f"{ticker} quote: {_named(refused)}") from refused
        except self._manifest.ManifestError as damaged:
            raise LakeUnavailable(f"marketlake's ledgers cannot be read: {damaged}") from damaged
        except (ValueError, OSError) as unreadable:
            raise LedgerRefused(
                f"{ticker} quote: its partition cannot be decoded: {_named(unreadable)}"
            ) from unreadable
        return table.select(list(QUOTE_COLUMNS)).to_pandas()

    def _sessions_between(self, start: date, end: date) -> list[date]:
        days = (start + timedelta(days=n) for n in range((end - start).days + 1))
        return [day for day in days if self._calendar.is_session(day)]

    def _check(self, path: Path) -> None:
        name, found = check_partition(self._root, path, self._entries, self._manifest.sha256_file)
        self.checked[name] = found


def report(
    sessions: Sequence[Session],
    refused: Sequence[tuple[date, str]],
    checked: Mapping[str, str],
    first: date,
    last: date,
    out=None,
) -> None:
    """Print the ledger, its replay, the three measures and what was read."""
    out = sys.stdout if out is None else out

    def say(line: str = "") -> None:
        print(line, file=out)

    say(f"Paper ledger on {' and '.join(TICKERS)}, sessions {first} to {last}.")
    say(NO_EDGE)
    say()
    say(
        f"Each session decides {MINUTES_BEFORE_CLOSE} minutes before its close, on the mid of "
        "that minute's quote. A buy fills at the ask and a sell at the bid. The replay is "
        "reversal_weights on the official closes."
    )
    say()
    if sessions:
        say(_legs_table(sessions).to_string(index=False))
        say()
        say(_sessions_table(sessions).to_string(index=False))
        say()
        _summary(sessions, say)
    total = len(sessions) + len(refused)
    say(f"Sessions computed: {len(sessions)} of {total}.")
    for day, reason in refused:
        say(f"Refused {day}: {reason}")
    say()
    say(f"Partitions read, each matching marketlake's manifest.jsonl: {len(checked)}")
    for name in sorted(checked):
        say(f"  {checked[name]}  {name}")


def run(first: date, last: date, root: Path, out=None) -> int:
    """Read, compute and report. 0 when every session computed, 1 when any was refused."""
    lake = MarketLake(root)
    sessions, refused = ledger(read_lake(lake, first, last))
    report(sessions, refused, lake.checked, first, last, out=out)
    return 1 if refused else 0


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="A daily paper ledger on SPY and QQQ from marketlake's quotes, replayed "
        "against the backtest. A pipeline test that claims no edge."
    )
    parser.add_argument("--from", dest="first", required=True, type=date.fromisoformat)
    parser.add_argument("--to", dest="last", required=True, type=date.fromisoformat)
    parser.add_argument(
        "--lake-root", help=f"the lake to read, else {LAKE_ROOT_ENV}, else {LAKE_ROOT_CONFIG}"
    )
    args = parser.parse_args(argv)
    if args.last < args.first:
        parser.error("--to is before --from")
    try:
        code = run(args.first, args.last, lake_root(args.lake_root))
    except LakeUnavailable as stopped:
        # A refusal is worth nothing at the bottom of a traceback, so it reaches
        # the reader as one line, the way chan.khandani_lo.main does it.
        print(f"Stopped: {stopped}", file=sys.stderr)
        raise SystemExit(2) from stopped
    raise SystemExit(code)


def _missing(read: LakeRead, days: list[date], closes: np.ndarray, i: int) -> list[str]:
    """Why session ``i`` cannot be computed, empty when it can."""
    reasons = []
    for k in (i - 2, i - 1, i):
        for j, ticker in enumerate(read.closes.columns):
            if not np.isfinite(closes[k, j]):
                why = read.close_refusals.get((days[k], ticker))
                reasons.append(
                    f"{ticker} daily bar on {days[k]}: {why}"
                    if why
                    else f"no {ticker} daily bar on {days[k]}"
                )
    for k in (i - 1, i):
        for ticker in read.closes.columns:
            quote = read.quotes.get((days[k], ticker), "no quote was read")
            if not isinstance(quote, Quote):
                reasons.append(f"{ticker} on {days[k]}: {quote}")
    return reasons


def _trade_weighted(legs: Sequence[Leg]) -> float:
    traded = [leg for leg in legs if leg.trade != 0]
    size = sum(abs(leg.trade) for leg in traded)
    if size == 0:
        return float("nan")
    return sum(abs(leg.trade) * leg.spread_bp for leg in traded) / size


def _legs_table(sessions: Sequence[Session]) -> pd.DataFrame:
    rows = []
    for session in sessions:
        for leg in session.legs:
            rows.append(
                {
                    "session": session.day.isoformat(),
                    "decision": session.decision.tz_convert(MARKET_TZ).strftime("%H:%M"),
                    "ticker": leg.ticker,
                    "bid": f"{leg.quote.bid:.2f}",
                    "ask": f"{leg.quote.ask:.2f}",
                    "last": f"{leg.quote.last:.3f}",
                    "lag s": f"{leg.quote.lag_seconds:.1f}",
                    "close": f"{leg.close:.2f}",
                    "held": f"{leg.held:+.6f}",
                    "weight": f"{leg.weight:+.6f}",
                    "replay": f"{leg.replay:+.6f}",
                    "side": "same" if leg.side_matches else "DIFFERS",
                    "fill": f"{leg.fill:.2f}",
                    "vs close bp": f"{leg.against_close_bp:+.2f}",
                    "spread bp": f"{leg.spread_bp:.2f}",
                }
            )
    return pd.DataFrame(rows)


def _sessions_table(sessions: Sequence[Session]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "session": session.day.isoformat(),
                "position mismatch": session.mismatch,
                "spread paid bp": f"{session.spread_bp:.2f}",
            }
            for session in sessions
        ]
    )


def _summary(sessions: Sequence[Session], say: Callable[[str], None]) -> None:
    flipped = [s for s in sessions if s.mismatch]
    say(f"Position mismatch: {len(flipped)} of {len(sessions)} sessions.")
    for session in flipped:
        for leg in session.legs:
            if not leg.side_matches:
                say(
                    f"  {session.day} {leg.ticker}: its return against the mean was "
                    f"{leg.decision_return * BASIS_POINTS:+.2f} bp at the decision and "
                    f"{leg.close_return * BASIS_POINTS:+.2f} bp at the close."
                )
    say("Decision price against the close, bp, mean signed and mean absolute:")
    for ticker in TICKERS:
        legs = [leg for s in sessions for leg in s.legs if leg.ticker == ticker]
        signed = np.mean([leg.against_close_bp for leg in legs])
        absolute = np.mean([abs(leg.against_close_bp) for leg in legs])
        say(f"  {ticker} {signed:+.2f} and {absolute:.2f}")
    say("Spread paid at the assumed fill, bp, weighted by the size of each trade:")
    for ticker in TICKERS:
        legs = [leg for s in sessions for leg in s.legs if leg.ticker == ticker]
        say(f"  {ticker} {_trade_weighted(legs):.2f}")
    every = [leg for s in sessions for leg in s.legs]
    say(
        f"  both {_trade_weighted(every):.2f}, against the "
        f"{ONE_WAY_COST * BASIS_POINTS:.2f} a side the backtest charges"
    )


def _minute(instant: datetime | pd.Timestamp) -> str:
    """An instant as the ET wall-clock minute ``marketlake`` names it by."""
    return pd.Timestamp(instant).tz_convert(MARKET_TZ).strftime("%H:%M")


def _named(error: Exception) -> str:
    return f"{type(error).__name__}: {error}"


if __name__ == "__main__":
    main()
