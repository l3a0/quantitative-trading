"""The pins for the paper ledger, ``chan.paper_ledger``, from issue 775.

Almost everything here runs on a fake lake built in this file, because CI
installs no extra and so never has ``marketlake``'s package. The fake hands
over quote rows and closes the way :class:`chan.paper_ledger.MarketLake` does,
so every rule the ledger enforces is exercised with no lake at all.

``TestTheLake`` is the exception. It reads a real lake through ``marketlake``'s
package and skips, with a reason, wherever that package is not installed or no
lake root is configured. Its vintage is the 86 partitions the run checks
against ``marketlake``'s ``manifest.jsonl``, pinned as one digest of their
names and sha256s, so a lake that restated any of them fails the pin rather
than moving its numbers quietly.

The placeholder strategy claims no edge, and nothing here tests that it pays.
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chan import paper_ledger as pl
from chan.khandani_lo import reversal_weights

ET = "America/New_York"

# Five sessions, the first two before the range, so the range is three sessions.
DAYS = [date(2026, 9, d) for d in (14, 15, 16, 17, 18)]
CLOSES = {
    "SPY": [760.00, 757.40, 754.00, 762.60, 761.70],
    "QQQ": [709.20, 704.50, 704.70, 716.90, 721.40],
}
# Each session's 15:50 bid and ask.
QUOTES = {
    "SPY": [
        (761.50, 761.56),
        (756.83, 756.84),
        (753.73, 753.75),
        (762.95, 762.96),
        (761.42, 761.44),
    ],
    "QQQ": [
        (710.60, 710.66),
        (703.96, 703.98),
        (704.38, 704.41),
        (717.25, 717.26),
        (720.20, 720.22),
    ],
}


def _close(day: date, hour: int = 16) -> pd.Timestamp:
    return pd.Timestamp(year=day.year, month=day.month, day=day.day, hour=hour, tz=ET)


def _row(day: date, minute: str, bid: float, ask: float, **extra) -> dict:
    hour, mins = (int(p) for p in minute.split(":"))
    stamp = pd.Timestamp(year=day.year, month=day.month, day=day.day, hour=hour, minute=mins, tz=ET)
    row = {
        "snap_ts": stamp.tz_convert("UTC").isoformat(),
        "vendor_quote_ts": (stamp + pd.Timedelta(seconds=18)).tz_convert("UTC").isoformat(),
        "bid": bid,
        "ask": ask,
        "last": (bid + ask) / 2,
        "realtime": True,
    }
    row.update(extra)
    return row


class FakeLake:
    """A lake that answers from the tables above, with knobs for each failure."""

    def __init__(self, closes=None, quotes=None, half_days=(), extra_rows=None, absent=()):
        self.closes_by = {t: dict(zip(DAYS, v, strict=True)) for t, v in (closes or CLOSES).items()}
        self.quotes_by = {t: dict(zip(DAYS, v, strict=True)) for t, v in (quotes or QUOTES).items()}
        self.half_days = set(half_days)
        self.extra_rows = extra_rows or {}
        self.absent = set(absent)
        self.asked: list[tuple[str, date, str]] = []

    def sessions(self, first: date, last: date) -> list[date]:
        i = DAYS.index(first)
        return DAYS[i - pl.SESSIONS_BEFORE : DAYS.index(last) + 1]

    def session_close(self, day: date) -> pd.Timestamp:
        return _close(day, 13 if day in self.half_days else 16)

    def closes(self, ticker, start, end):
        return {d: c for d, c in self.closes_by[ticker].items() if start <= d <= end}

    def quote_rows(self, ticker, day, snap):
        self.asked.append((ticker, day, snap))
        if (ticker, day) in self.absent:
            raise pl.LedgerRefused(f"{ticker} quote: SnapAbsent: no cycle at {snap}")
        bid, ask = self.quotes_by[ticker][day]
        rows = [_row(day, snap, bid, ask)] + self.extra_rows.get((ticker, day), [])
        return pd.DataFrame(rows)


def _run(lake=None, first=DAYS[2], last=DAYS[4]):
    return pl.ledger(pl.read_lake(lake or FakeLake(), first, last))


class TestTheLookAheadGuard:
    """A quote stamped after the decision minute changes nothing."""

    def test_a_planted_later_row_leaves_every_session_unchanged(self) -> None:
        clean, _ = _run()
        planted = {
            (t, d): [_row(d, "15:55", 1.0, 2000.0), _row(d, "15:59", 9999.0, 9999.5)]
            for t in pl.TICKERS
            for d in DAYS
        }
        dirty, refused = _run(FakeLake(extra_rows=planted))
        assert not refused
        assert dirty == clean

    def test_the_latest_row_at_or_before_the_minute_is_the_one_read(self) -> None:
        day = DAYS[2]
        rows = pd.DataFrame(
            [_row(day, "15:48", 100.0, 100.2), _row(day, "15:50", 101.0, 101.2)]
            + [_row(day, "15:51", 500.0, 500.2)]
        )
        quote = pl.decision_quote(rows, _close(day) - timedelta(minutes=10))
        assert (quote.bid, quote.ask) == (101.0, 101.2)

    def test_a_row_only_after_the_minute_refuses(self) -> None:
        day = DAYS[2]
        rows = pd.DataFrame([_row(day, "15:51", 100.0, 100.2)])
        with pytest.raises(pl.LedgerRefused, match="at or before 15:50"):
            pl.decision_quote(rows, _close(day) - timedelta(minutes=10))


class TestTheRowGuard:
    DECISION = _close(DAYS[2]) - timedelta(minutes=10)

    def _quote(self, *rows):
        return pl.decision_quote(pd.DataFrame(list(rows)), self.DECISION)

    def test_two_rows_in_one_minute_refuse(self) -> None:
        day = DAYS[2]
        with pytest.raises(pl.LedgerRefused, match="2 quote rows share the minute 15:50"):
            self._quote(_row(day, "15:50", 1.0, 1.1), _row(day, "15:50", 1.0, 1.1))

    @pytest.mark.parametrize("realtime", [False, None])
    def test_a_quote_that_is_not_real_time_refuses(self, realtime) -> None:
        with pytest.raises(pl.LedgerRefused, match="not real-time"):
            self._quote(_row(DAYS[2], "15:50", 1.0, 1.1, realtime=realtime))

    @pytest.mark.parametrize(("bid", "ask"), [(1.2, 1.1), (0.0, 1.1), (-1.0, 1.1), (np.nan, 1.1)])
    def test_a_crossed_or_non_positive_quote_refuses(self, bid, ask) -> None:
        with pytest.raises(pl.LedgerRefused, match="reads bid"):
            self._quote(_row(DAYS[2], "15:50", bid, ask))

    def test_a_locked_quote_is_read(self) -> None:
        quote = self._quote(_row(DAYS[2], "15:50", 1.1, 1.1))
        assert quote.mid == 1.1


class TestTheWeights:
    """The ledger and the replay share the backtest's function, by construction."""

    def test_the_ledger_equals_the_replay_handed_the_mids(self) -> None:
        sessions, _ = _run()
        closes = np.array([CLOSES[t] for t in pl.TICKERS]).T
        mids = np.array([[np.mean(QUOTES[t][i]) for t in pl.TICKERS] for i in range(len(DAYS))])
        for session in sessions:
            i = DAYS.index(session.day)
            today = closes.copy()
            today[i] = mids[i]
            yesterday = closes.copy()
            yesterday[i - 1] = mids[i - 1]
            np.testing.assert_array_equal(
                [leg.weight for leg in session.legs], reversal_weights(today)[i]
            )
            np.testing.assert_array_equal(
                [leg.held for leg in session.legs], reversal_weights(yesterday)[i - 1]
            )

    def test_the_replay_is_the_backtest_on_the_closes(self) -> None:
        sessions, _ = _run()
        closes = np.array([CLOSES[t] for t in pl.TICKERS]).T
        replay = reversal_weights(closes)
        for session in sessions:
            i = DAYS.index(session.day)
            assert [leg.replay for leg in session.legs] == list(replay[i])

    def test_a_session_holds_what_the_session_before_it_set(self) -> None:
        sessions, _ = _run()
        for before, after in zip(sessions, sessions[1:], strict=False):
            assert [leg.held for leg in after.legs] == [leg.weight for leg in before.legs]


class TestTheFill:
    def _leg(self, held: float, weight: float) -> pl.Leg:
        quote = pl.Quote(pd.Timestamp("2026-09-16T19:50Z"), pd.NaT, 100.00, 100.04, 100.02)
        return pl.Leg("SPY", quote, 100.10, held, weight, weight, 0.0, 0.0)

    def test_a_buy_fills_at_the_ask(self) -> None:
        leg = self._leg(-0.001, 0.002)
        assert leg.fill == 100.04
        assert leg.spread_bp == pytest.approx(0.02 / 100.02 * 10_000)

    def test_a_sell_fills_at_the_bid(self) -> None:
        leg = self._leg(0.002, -0.001)
        assert leg.fill == 100.00
        assert leg.spread_bp == pytest.approx(0.02 / 100.02 * 10_000)

    def test_no_trade_has_no_fill(self) -> None:
        leg = self._leg(0.002, 0.002)
        assert np.isnan(leg.fill)
        assert np.isnan(pl._trade_weighted([leg]))

    def test_the_decision_price_is_set_against_the_close_in_basis_points(self) -> None:
        leg = self._leg(0.0, 0.001)
        assert leg.against_close_bp == pytest.approx((100.02 - 100.10) / 100.10 * 10_000)

    def test_the_session_spread_weights_each_ticker_by_its_trade(self) -> None:
        small = self._leg(0.0, 0.001)
        wide = pl.Leg(
            "QQQ",
            pl.Quote(pd.Timestamp("2026-09-16T19:50Z"), pd.NaT, 100.0, 100.4, 100.2),
            100.0,
            0.0,
            -0.003,
            -0.003,
            0.0,
            0.0,
        )
        expected = (0.001 * small.spread_bp + 0.003 * wide.spread_bp) / 0.004
        assert pl._trade_weighted([small, wide]) == pytest.approx(expected)


class TestThePositionMismatch:
    def test_sessions_whose_ordering_holds_read_zero(self) -> None:
        sessions, _ = _run()
        assert [s.mismatch for s in sessions] == [0, 0, 0]

    def test_an_ordering_the_close_reverses_reads_two(self) -> None:
        # On 09-17 SPY rose 1.14% and QQQ 1.73% by the close. Mids that put SPY
        # ahead at 15:50 make the ledger short SPY where the replay is long it.
        quotes = {t: list(v) for t, v in QUOTES.items()}
        quotes["SPY"][3] = (768.0, 768.02)
        quotes["QQQ"][3] = (705.0, 705.02)
        sessions, _ = _run(FakeLake(quotes=quotes))
        flipped = next(s for s in sessions if s.day == DAYS[3])
        assert flipped.mismatch == 2
        spy = flipped.legs[0]
        assert spy.decision_return > 0 > spy.close_return


class TestRefusals:
    def test_a_missing_bar_refuses_the_session_rather_than_skipping_it(self) -> None:
        closes = {t: list(v) for t, v in CLOSES.items()}
        closes["QQQ"][3] = np.nan
        sessions, refused = _run(FakeLake(closes=closes))
        assert [s.day for s in sessions] == [DAYS[2]]
        assert [d for d, _ in refused] == [DAYS[3], DAYS[4]]
        assert "no QQQ daily bar on 2026-09-17" in refused[0][1]

    def test_a_missing_quote_refuses_its_session_and_the_next(self) -> None:
        sessions, refused = _run(FakeLake(absent={("SPY", DAYS[3])}))
        assert [s.day for s in sessions] == [DAYS[2]]
        assert [d for d, _ in refused] == [DAYS[3], DAYS[4]]
        assert "SnapAbsent" in refused[0][1]

    def test_a_half_day_decides_ten_minutes_before_its_early_close(self) -> None:
        lake = FakeLake(half_days={DAYS[3]})
        pl.read_lake(lake, DAYS[2], DAYS[4])
        snaps = {(day, snap) for _, day, snap in lake.asked}
        assert (DAYS[3], "12:50") in snaps
        assert (DAYS[2], "15:50") in snaps


class TestTheLakeRoot:
    def test_the_argument_wins(self, tmp_path: Path) -> None:
        other = tmp_path / "other"
        other.mkdir()
        environ = {pl.LAKE_ROOT_ENV: str(other)}
        assert pl.lake_root(str(tmp_path), environ, tmp_path / "none") == tmp_path

    def test_the_environment_comes_before_the_file(self, tmp_path: Path) -> None:
        config = tmp_path / "lake_root"
        config.write_text("/nowhere\n")
        assert pl.lake_root(None, {pl.LAKE_ROOT_ENV: str(tmp_path)}, config) == tmp_path

    def test_the_file_is_read_last(self, tmp_path: Path) -> None:
        config = tmp_path / "lake_root"
        config.write_text(f"{tmp_path}\n")
        assert pl.lake_root(None, {}, config) == tmp_path

    def test_none_of_the_three_names_all_three(self, tmp_path: Path) -> None:
        with pytest.raises(pl.LakeUnavailable) as stopped:
            pl.lake_root(None, {}, tmp_path / "none")
        message = str(stopped.value)
        assert "--lake-root" in message and pl.LAKE_ROOT_ENV in message
        assert "lake_root" in message.split(pl.LAKE_ROOT_ENV)[1]

    def test_a_root_that_is_not_a_directory_stops(self, tmp_path: Path) -> None:
        with pytest.raises(pl.LakeUnavailable, match="not a directory"):
            pl.lake_root(str(tmp_path / "missing"), {}, tmp_path / "none")


class TestThePartitionCheck:
    def _digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_a_matching_partition_returns_its_name_and_sha(self, tmp_path: Path) -> None:
        path = tmp_path / "quotes" / "ticker=SPY" / "date=2026-09-15.parquet"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"sealed")
        sha = self._digest(path)
        entries = {"quotes/ticker=SPY/date=2026-09-15.parquet": {"sha256": sha}}
        assert pl.check_partition(tmp_path, path, entries, self._digest) == (
            "quotes/ticker=SPY/date=2026-09-15.parquet",
            sha,
        )

    def test_a_changed_partition_stops_the_run(self, tmp_path: Path) -> None:
        path = tmp_path / "p.parquet"
        path.write_bytes(b"restated")
        with pytest.raises(pl.LakeUnavailable, match="hashes to"):
            pl.check_partition(tmp_path, path, {"p.parquet": {"sha256": "0" * 64}}, self._digest)

    def test_an_unrecorded_partition_stops_the_run(self, tmp_path: Path) -> None:
        path = tmp_path / "p.parquet"
        path.write_bytes(b"x")
        with pytest.raises(pl.LakeUnavailable, match="not in marketlake's manifest.jsonl"):
            pl.check_partition(tmp_path, path, {}, self._digest)


class TestTheCommand:
    def test_the_report_opens_by_saying_it_claims_no_edge(self) -> None:
        sessions, refused = _run()
        out = io.StringIO()
        pl.report(sessions, refused, {}, DAYS[2], DAYS[4], out=out)
        text = out.getvalue()
        assert "claims no edge" in text.splitlines()[1]
        assert "Position mismatch: 0 of 3 sessions." in text
        assert "Sessions computed: 3 of 3." in text
        assert "position mismatch spread paid bp" in text
        assert "5.00 a side the backtest charges" in text

    def test_a_refused_session_is_one_line(self) -> None:
        sessions, refused = _run(FakeLake(absent={("SPY", DAYS[4])}))
        out = io.StringIO()
        pl.report(sessions, refused, {}, DAYS[2], DAYS[4], out=out)
        lines = [line for line in out.getvalue().splitlines() if line.startswith("Refused")]
        assert lines == [
            "Refused 2026-09-18: SPY on 2026-09-18: SPY quote: SnapAbsent: no cycle at 15:50"
        ]

    def test_no_lake_package_stops_with_one_line(self, monkeypatch, tmp_path, capsys) -> None:
        monkeypatch.setitem(sys.modules, "lake", None)
        with pytest.raises(SystemExit) as stopped:
            pl.main(["--from", "2026-09-15", "--to", "2026-09-16", "--lake-root", str(tmp_path)])
        assert stopped.value.code == 2
        err = capsys.readouterr().err.strip().splitlines()
        assert err == [
            "Stopped: marketlake's lake package is not installed here. "
            "Run `uv sync --extra lake` and try again"
        ]

    def test_a_refused_session_exits_one(self, monkeypatch, tmp_path) -> None:
        lake = FakeLake(absent={("SPY", DAYS[4])})
        lake.checked = {}
        monkeypatch.setattr(pl, "MarketLake", lambda root: lake)
        assert pl.run(DAYS[2], DAYS[4], tmp_path, out=io.StringIO()) == 1
        assert pl.run(DAYS[2], DAYS[3], tmp_path, out=io.StringIO()) == 0


def _configured_lake() -> Path | None:
    if importlib.util.find_spec("lake") is None:
        return None
    try:
        return pl.lake_root()
    except pl.LakeUnavailable:
        return None


LAKE = _configured_lake()


@pytest.mark.skipif(
    LAKE is None,
    reason="needs marketlake's package, `uv sync --extra lake`, and a lake root in "
    f"{pl.LAKE_ROOT_ENV} or {pl.LAKE_ROOT_CONFIG}",
)
class TestTheLake:
    """The twenty sessions issue 775 records, 2026-09-15 to 2026-10-12, on a real lake.

    The pins hold on any lake whose 86 partitions in that range hash to what
    the laptop's shadow lake held on 2026-10-28, which the digest checks first.
    """

    FIRST = date(2026, 9, 15)
    LAST = date(2026, 10, 12)
    DIGEST = "6c3c139fa9aea7b28501955311cc27b2af6ad541215975651b1928092c900957"

    @pytest.fixture(scope="class")
    @classmethod
    def run(cls):
        lake = pl.MarketLake(LAKE)
        sessions, refused = pl.ledger(pl.read_lake(lake, cls.FIRST, cls.LAST))
        return sessions, refused, lake.checked

    def test_the_partitions_are_the_ones_recorded(self, run) -> None:
        _, _, checked = run
        lines = "".join(f"{checked[name]}  {name}\n" for name in sorted(checked))
        assert len(checked) == 86
        assert hashlib.sha256(lines.encode()).hexdigest() == self.DIGEST

    def test_every_session_computes_and_none_mismatches(self, run) -> None:
        sessions, refused, _ = run
        assert refused == []
        assert len(sessions) == 20
        assert [s.mismatch for s in sessions] == [0] * 20

    def test_the_means_the_report_prints(self, run) -> None:
        sessions, _, _ = run
        legs = {t: [leg for s in sessions for leg in s.legs if leg.ticker == t] for t in pl.TICKERS}
        signed = {t: np.mean([leg.against_close_bp for leg in legs[t]]) for t in pl.TICKERS}
        spread = pl._trade_weighted([leg for s in sessions for leg in s.legs])
        assert round(signed["SPY"], 2) == 3.33
        assert round(signed["QQQ"], 2) == 1.96
        assert round(spread, 2) == 0.17
