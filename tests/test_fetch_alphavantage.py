"""The fetch of Alpha Vantage's daily closes into the archive, or of USD/CAD's into ``data/``.

Nothing here calls the vendor. The equity tests build a data directory and an
archive under ``tmp_path``, and hand :func:`chan.fetch_alphavantage.fetch` a
stub for the network that maps each symbol to a body or an exception and
counts its calls, and a stub for ``sleep`` that records each wait instead of
waiting.

The ``FX_DAILY`` tests cover :func:`chan.fetch_alphavantage.fetch_fx_daily`,
which records USD/CAD's closes as a vintage in a data directory under
``tmp_path``. They hand it a stub for the network that answers each request in
turn and refuses any request for a pair other than USD/CAD, and the same stub
for ``sleep``.
"""

from __future__ import annotations

import http.client
import json
import re
import urllib.parse
from datetime import date
from pathlib import Path

import pytest

from chan import archive, fetch_alphavantage
from chan.archive import (
    ARCHIVE_DIR_ENV,
    ARCHIVE_MANIFEST_NAME,
    DAILY_HEADER,
    read_archive_manifest,
)
from chan.fetch_alphavantage import (
    ATTEMPTS,
    FX_DAILY_HEADER,
    KEY_ENV,
    PAUSE_SECONDS,
    THROTTLE_WAIT_SECONDS,
    TRANSPORT_WAIT_SECONDS,
    RunStopped,
    fetch,
    fetch_fx_daily,
    fx_request_url,
    read_symbols,
    request_url,
)
from chan.vintage import MANIFEST_NAME, read_manifest, record_vintage

KEY = "SECRETKEY123"


def daily(*rows: str) -> bytes:
    return (DAILY_HEADER + "\n" + "".join(row + "\n" for row in rows)).encode("utf-8")


GOOD = daily("2009-01-02,1,1,1,10.0,5.0,100,0,1", "2008-12-31,1,1,1,9.0,4.5,100,0,1")
ERROR = json.dumps({"Error Message": "Invalid API call. Please retry or visit the docs."}).encode()
INFORMATION = json.dumps({"Information": "Thank you for using Alpha Vantage! Rate limit."}).encode()
NOTE = json.dumps({"Note": "Our standard API rate limit is 75 requests per minute."}).encode()


class Vendor:
    """A stub for the network: each symbol answers with a list of bodies or exceptions in turn."""

    def __init__(self, answers: dict[str, list[bytes | BaseException]]):
        self.answers = {symbol: list(replies) for symbol, replies in answers.items()}
        self.calls: list[str] = []

    def __call__(self, url: str) -> bytes:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        assert query["apikey"] == [KEY]
        symbol = query["symbol"][0]
        self.calls.append(symbol)
        replies = self.answers[symbol]
        reply = replies.pop(0) if len(replies) > 1 else replies[0]
        if isinstance(reply, BaseException):
            raise reply
        return reply


class Clock:
    def __init__(self):
        self.waits: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.waits.append(seconds)


@pytest.fixture
def places(tmp_path) -> tuple[Path, Path]:
    data_dir = tmp_path / "data"
    store = tmp_path / "archive"
    data_dir.mkdir()
    store.mkdir()
    (data_dir / ARCHIVE_MANIFEST_NAME).write_bytes(b"")
    return data_dir, store


def run(places, vendor, symbols, clock=None, day=date(2026, 10, 5)):
    data_dir, store = places
    return fetch(
        "sp600",
        symbols,
        key=KEY,
        get=vendor,
        sleep=clock or Clock(),
        today=lambda: day,
        data_dir=data_dir,
        directory=store,
    )


def recorded(places) -> list[str]:
    return [entry.symbol for entry in read_archive_manifest(places[0])]


class TestARun:
    def test_each_symbol_is_recorded_with_its_day(self, places, capsys):
        tally = run(places, Vendor({"AAA": [GOOD], "BBB": [GOOD]}), ["AAA", "BBB"])
        assert tally.recorded == ["AAA", "BBB"] and tally.complete
        entries = read_archive_manifest(places[0])
        assert [entry.download_date for entry in entries] == ["2026-10-05", "2026-10-05"]
        assert (places[1] / "sp600" / "daily_AAA.csv").read_bytes() == GOOD
        assert "AAA: recorded 2 rows, 2008-12-31 to 2009-01-02" in capsys.readouterr().out

    def test_the_run_opens_by_naming_the_archive_and_the_manifest(self, places, capsys):
        run(places, Vendor({"AAA": [GOOD]}), ["AAA"])
        first = capsys.readouterr().out.splitlines()[0]
        assert str(places[1]) in first and ARCHIVE_MANIFEST_NAME in first

    def test_a_second_run_makes_no_request_for_a_recorded_symbol(self, places):
        run(places, Vendor({"AAA": [GOOD]}), ["AAA"])
        vendor = Vendor({"AAA": [GOOD], "BBB": [GOOD]})
        tally = run(places, vendor, ["AAA", "BBB"], day=date(2026, 10, 6))
        assert vendor.calls == ["BBB"]
        assert (tally.already, tally.recorded) == (["AAA"], ["BBB"])
        dates = {entry.symbol: entry.download_date for entry in read_archive_manifest(places[0])}
        assert dates == {"AAA": "2026-10-05", "BBB": "2026-10-06"}

    def test_a_repeated_symbol_is_fetched_once(self, places):
        vendor = Vendor({"AAA": [GOOD]})
        tally = run(places, vendor, ["AAA", "AAA"])
        assert vendor.calls == ["AAA"]
        assert tally.failed == [] and tally.complete

    def test_a_standalone_line_for_the_symbol_does_not_count_as_recorded(self, places):
        standalone = {
            "vendor": "alphavantage",
            "symbol": "AAA",
            "price_basis": "raw",
            "download_date": "2026-10-03",
            "path": "aaa_intraday_1min.csv.gz",
            "row_count": 3,
            "sha256": "0" * 64,
            "first_date": "2006-05-22",
            "last_date": "2006-05-22",
            "vendor_call": "TIME_SERIES_INTRADAY",
        }
        manifest = places[0] / ARCHIVE_MANIFEST_NAME
        manifest.write_text(json.dumps(standalone) + "\n", encoding="utf-8")
        vendor = Vendor({"AAA": [GOOD], "BBB": [KeyboardInterrupt()]})
        tally = run(places, vendor, ["AAA", "BBB"])
        assert vendor.calls == ["AAA", "BBB"]
        assert (tally.already, tally.recorded) == ([], ["AAA"])
        manifest.write_text(json.dumps(dict(standalone, symbol="CCC")) + "\n", encoding="utf-8")
        tally = run(places, Vendor({"CCC": [KeyboardInterrupt()]}), ["CCC"])
        assert (tally.recorded, tally.not_reached) == ([], ["CCC"])

    def test_an_unruled_cross_section_makes_no_request(self, places):
        vendor = Vendor({"AAA": [GOOD]})
        with pytest.raises(ValueError, match="has not ruled"):
            fetch(
                "russell2000",
                ["AAA"],
                key=KEY,
                get=vendor,
                sleep=Clock(),
                data_dir=places[0],
                directory=places[1],
            )
        assert vendor.calls == []

    def test_each_request_is_followed_by_the_pause(self, places):
        clock = Clock()
        run(places, Vendor({"AAA": [GOOD], "BBB": [GOOD]}), ["AAA", "BBB"], clock=clock)
        assert clock.waits == [PAUSE_SECONDS, PAUSE_SECONDS]

    def test_a_file_with_no_line_is_refused_with_no_request_and_left_untouched(
        self, places, capsys
    ):
        (places[1] / "sp600").mkdir()
        (places[1] / "sp600" / "daily_AAA.csv").write_bytes(b"older")
        vendor = Vendor({"AAA": [GOOD]})
        tally = run(places, vendor, ["AAA"])
        assert vendor.calls == [] and tally.failed == ["AAA"]
        assert (places[1] / "sp600" / "daily_AAA.csv").read_bytes() == b"older"
        assert "Move it aside" in capsys.readouterr().out


class TestWhatABodyMeans:
    def test_an_error_message_fails_that_symbol_and_the_run_goes_on(self, places, capsys):
        tally = run(places, Vendor({"AAA": [ERROR], "BBB": [GOOD]}), ["AAA", "BBB"])
        assert (tally.failed, tally.recorded) == (["AAA"], ["BBB"])
        assert not (places[1] / "sp600" / "daily_AAA.csv").exists()
        assert recorded(places) == ["BBB"]
        assert "AAA: failed, Alpha Vantage answered 'Invalid API call." in capsys.readouterr().out

    def test_an_error_message_beside_a_note_is_an_error_and_not_retried(self, places):
        both = json.dumps({"Error Message": "Invalid API call.", "Note": "slow down"}).encode()
        vendor = Vendor({"AAA": [both]})
        tally = run(places, vendor, ["AAA"])
        assert vendor.calls == ["AAA"] and tally.failed == ["AAA"]

    @pytest.mark.parametrize("body", [INFORMATION, NOTE])
    def test_a_throttle_that_clears_is_retried_and_recorded(self, places, body):
        clock = Clock()
        tally = run(places, Vendor({"AAA": [body, GOOD]}), ["AAA"], clock=clock)
        assert tally.recorded == ["AAA"]
        assert clock.waits == [PAUSE_SECONDS, THROTTLE_WAIT_SECONDS, PAUSE_SECONDS]

    def test_a_throttle_that_persists_stops_the_run(self, places, capsys):
        clock = Clock()
        vendor = Vendor({"AAA": [GOOD], "BBB": [INFORMATION], "CCC": [GOOD]})
        tally = run(places, vendor, ["AAA", "BBB", "CCC"], clock=clock)
        assert vendor.calls == ["AAA"] + ["BBB"] * ATTEMPTS
        assert tally.recorded == ["AAA"] and tally.not_reached == ["BBB", "CCC"]
        assert tally.stopped is not None and not tally.complete
        throttles = [wait for wait in clock.waits if wait != PAUSE_SECONDS]
        assert throttles == [THROTTLE_WAIT_SECONDS * n for n in range(1, ATTEMPTS + 1)]
        assert "Thank you for using Alpha Vantage" in capsys.readouterr().out

    def test_a_transport_failure_that_clears_is_retried(self, places):
        clock = Clock()
        tally = run(places, Vendor({"AAA": [OSError("reset"), GOOD]}), ["AAA"], clock=clock)
        assert tally.recorded == ["AAA"]
        assert clock.waits == [TRANSPORT_WAIT_SECONDS, PAUSE_SECONDS]

    def test_a_transport_failure_that_persists_stops_the_run(self, places):
        clock = Clock()
        vendor = Vendor({"AAA": [TimeoutError("timed out")], "BBB": [GOOD]})
        tally = run(places, vendor, ["AAA", "BBB"], clock=clock)
        assert vendor.calls == ["AAA"] * ATTEMPTS
        assert clock.waits == [TRANSPORT_WAIT_SECONDS * n for n in range(1, ATTEMPTS + 1)]
        assert tally.line().startswith("stopped: recorded 0")
        assert tally.not_reached == ["AAA", "BBB"] and tally.stopped is not None

    def test_a_body_cut_off_mid_read_is_retried_and_stops_the_run_if_it_persists(self, places):
        cut = http.client.IncompleteRead(b"abc", 100)
        tally = run(places, Vendor({"AAA": [cut, GOOD], "BBB": [cut]}), ["AAA", "BBB"])
        assert tally.recorded == ["AAA"]
        assert tally.not_reached == ["BBB"] and "IncompleteRead" in tally.stopped

    @pytest.mark.parametrize(
        "other",
        [
            b"timestamp,open,high,low,close,volume\n2009-01-02,1,1,1,1,1\n",
            b"date,open,high,low,close,adjusted_close\n2009-01-02,1,1,1,1,1\n",
            b"\xef\xbb\xbf" + GOOD,
        ],
    )
    def test_a_csv_with_another_header_stops_the_run(self, places, other):
        vendor = Vendor({"AAA": [other], "BBB": [GOOD]})
        tally = run(places, vendor, ["AAA", "BBB"])
        assert vendor.calls == ["AAA"]
        assert tally.not_reached == ["AAA", "BBB"] and "not the daily header" in tally.stopped

    def test_a_failure_writing_the_archive_stops_the_run_with_its_tally(self, places, monkeypatch):
        append = archive._append_line
        calls = []

        def second_fails(manifest, line):
            calls.append(line)
            if len(calls) == 2:
                raise PermissionError("the manifest is read-only")
            append(manifest, line)

        monkeypatch.setattr(archive, "_append_line", second_fails)
        vendor = Vendor({"AAA": [GOOD], "BBB": [GOOD], "CCC": [GOOD]})
        tally = run(places, vendor, ["AAA", "BBB", "CCC"])
        assert tally.recorded == ["AAA"] and tally.not_reached == ["BBB", "CCC"]
        assert "writing to the archive failed" in tally.stopped
        assert not (places[1] / "sp600" / "daily_BBB.csv").exists()

    @pytest.mark.parametrize(
        ("body", "words"),
        [
            (b"", "an empty body"),
            (daily(), "no rows under it"),
            (b'{"Something": "else"}', "neither Error Message, Information nor Note"),
            (b"{not json at all", "neither Error Message, Information nor Note"),
            (b"<html>busy</html>", "neither CSV nor JSON"),
        ],
    )
    def test_anything_else_fails_that_symbol(self, places, capsys, body, words):
        tally = run(places, Vendor({"AAA": [body], "BBB": [GOOD]}), ["AAA", "BBB"])
        assert (tally.failed, tally.recorded) == (["AAA"], ["BBB"])
        assert words in capsys.readouterr().out
        assert recorded(places) == ["BBB"]


class TestTheOperatorSeesLines:
    def test_an_interrupt_returns_the_tally_with_what_was_not_reached(self, places):
        vendor = Vendor({"AAA": [GOOD], "BBB": [KeyboardInterrupt()], "CCC": [GOOD]})
        tally = run(places, vendor, ["AAA", "BBB", "CCC"])
        assert tally.interrupted and tally.recorded == ["AAA"]
        assert tally.not_reached == ["BBB", "CCC"]
        assert not tally.complete
        assert tally.line().startswith("interrupted: recorded 1")

    def test_an_interrupt_after_a_line_lands_counts_the_symbol_as_recorded(
        self, places, monkeypatch
    ):
        append = archive._append_line

        def landed_then_interrupted(manifest, line):
            append(manifest, line)
            raise KeyboardInterrupt

        monkeypatch.setattr(archive, "_append_line", landed_then_interrupted)
        tally = run(places, Vendor({"AAA": [GOOD], "BBB": [GOOD]}), ["AAA", "BBB"])
        assert tally.interrupted
        assert (tally.recorded, tally.not_reached) == (["AAA"], ["BBB"])

    def test_a_symbol_failed_before_an_interrupt_is_not_also_unreached(self, places, monkeypatch):
        say = fetch_alphavantage._say

        def interrupted_on_failure(text, key):
            say(text, key)
            if text.startswith("AAA: failed"):
                raise KeyboardInterrupt

        monkeypatch.setattr(fetch_alphavantage, "_say", interrupted_on_failure)
        tally = run(places, Vendor({"AAA": [ERROR], "BBB": [GOOD]}), ["AAA", "BBB"])
        assert (tally.failed, tally.not_reached) == (["AAA"], ["BBB"])

    def test_an_interrupt_after_every_symbol_is_recorded_still_reads_as_interrupted(
        self, places, monkeypatch
    ):
        say = fetch_alphavantage._say

        def interrupted_after_recording(text, key):
            say(text, key)
            if text.startswith("AAA: recorded"):
                raise KeyboardInterrupt

        monkeypatch.setattr(fetch_alphavantage, "_say", interrupted_after_recording)
        tally = run(places, Vendor({"AAA": [GOOD]}), ["AAA"])
        assert (tally.recorded, tally.not_reached) == (["AAA"], [])
        assert tally.interrupted and not tally.complete

    def test_an_interrupt_through_main_prints_the_tally_and_no_traceback(
        self, places, monkeypatch, tmp_path, capsys
    ):
        data_dir, store = places
        monkeypatch.setattr(fetch_alphavantage.paths, "DATA_DIR", data_dir)
        monkeypatch.setenv(KEY_ENV, KEY)
        monkeypatch.setenv(ARCHIVE_DIR_ENV, str(store))
        vendor = Vendor({"AAA": [GOOD], "BBB": [KeyboardInterrupt()]})
        monkeypatch.setattr(fetch_alphavantage, "urllib_get", vendor)
        monkeypatch.setattr(fetch_alphavantage.time, "sleep", lambda seconds: None)
        symbols = tmp_path / "symbols.txt"
        symbols.write_text("AAA\nBBB\n", encoding="utf-8")
        with pytest.raises(SystemExit) as stopped:
            fetch_alphavantage.main(["--cross-section", "sp600", "--symbols", str(symbols)])
        assert stopped.value.code == 1
        out = capsys.readouterr()
        assert out.out.splitlines()[-1] == (
            "interrupted: recorded 1, already recorded 0, failed 0, not reached 1"
        )
        assert "Traceback" not in out.out + out.err

    def test_an_interrupt_before_any_request_prints_one_line(self, tmp_path, monkeypatch):
        symbols = tmp_path / "symbols.txt"
        symbols.write_text("AAA\n", encoding="utf-8")
        monkeypatch.setenv(KEY_ENV, KEY)

        def interrupted(*args, **kwargs):
            raise KeyboardInterrupt

        monkeypatch.setattr(fetch_alphavantage, "archive_dir", interrupted)
        with pytest.raises(SystemExit) as stopped:
            fetch_alphavantage.main(["--cross-section", "sp600", "--symbols", str(symbols)])
        assert str(stopped.value) == "interrupted before any symbol was fetched"

    def test_the_tally_line_names_each_failed_symbol(self, places):
        tally = run(places, Vendor({"AAA": [ERROR], "BBB": [ERROR]}), ["AAA", "BBB"])
        assert tally.line() == (
            "recorded 0, already recorded 0, failed 2 (AAA, BBB), not reached 0"
        )

    def test_the_key_appears_in_no_output_on_any_path(self, places, capsys):
        leaky = OSError(f"could not reach {request_url('BBB', KEY)}")
        # An error page that echoes the request is quoted in the failed line.
        echoed = f"<html>apikey={KEY} refused</html>".encode()
        vendor = Vendor({"AAA": [ERROR], "ECHO": [echoed], "BBB": [leaky], "CCC": [GOOD]})
        tally = run(places, vendor, ["AAA", "ECHO", "BBB", "CCC"])
        assert tally.failed == ["AAA", "ECHO"]
        out = capsys.readouterr()
        assert KEY not in out.out + out.err
        assert KEY not in (tally.stopped or "")
        assert "<key>" in tally.stopped

    def test_no_key_prints_one_line_and_reads_no_archive(self, tmp_path, monkeypatch, capsys):
        symbols = tmp_path / "symbols.txt"
        symbols.write_text("AAA\n", encoding="utf-8")
        monkeypatch.delenv(KEY_ENV, raising=False)
        monkeypatch.setenv(ARCHIVE_DIR_ENV, str(tmp_path / "nowhere"))
        with pytest.raises(SystemExit) as stopped:
            fetch_alphavantage.main(["--cross-section", "sp600", "--symbols", str(symbols)])
        assert str(stopped.value) == f"{KEY_ENV} is not set, so no request was made"

    def test_a_missing_symbols_file_prints_one_line(self, tmp_path, monkeypatch):
        monkeypatch.setenv(KEY_ENV, KEY)
        missing = tmp_path / "absent.txt"
        with pytest.raises(SystemExit) as stopped:
            fetch_alphavantage.main(["--cross-section", "sp600", "--symbols", str(missing)])
        assert "absent.txt" in str(stopped.value)

    def test_a_refusal_through_main_carries_no_key(self, tmp_path, monkeypatch):
        symbols = tmp_path / "symbols.txt"
        symbols.write_text(f"x{KEY}\n", encoding="utf-8")
        monkeypatch.setenv(KEY_ENV, KEY)
        with pytest.raises(SystemExit) as stopped:
            fetch_alphavantage.main(["--cross-section", "sp600", "--symbols", str(symbols)])
        assert "line 1" in str(stopped.value) and KEY not in str(stopped.value)

    def test_no_archive_prints_the_reader_s_line(self, tmp_path, monkeypatch):
        symbols = tmp_path / "symbols.txt"
        symbols.write_text("AAA\n", encoding="utf-8")
        monkeypatch.setenv(KEY_ENV, KEY)
        monkeypatch.setenv(ARCHIVE_DIR_ENV, str(tmp_path / "nowhere"))
        with pytest.raises(SystemExit) as stopped:
            fetch_alphavantage.main(["--cross-section", "sp600", "--symbols", str(symbols)])
        assert "is not a directory" in str(stopped.value)

    def test_an_unruled_cross_section_is_refused_before_anything_else(self, tmp_path, monkeypatch):
        symbols = tmp_path / "symbols.txt"
        symbols.write_text("AAA\n", encoding="utf-8")
        monkeypatch.setenv(KEY_ENV, KEY)
        with pytest.raises(SystemExit) as stopped:
            fetch_alphavantage.main(["--cross-section", "russell2000", "--symbols", str(symbols)])
        assert "has not ruled" in str(stopped.value)

    def test_a_complete_run_exits_cleanly_and_an_incomplete_one_does_not(
        self, places, monkeypatch, tmp_path, capsys
    ):
        data_dir, store = places
        monkeypatch.setattr(fetch_alphavantage.paths, "DATA_DIR", data_dir)
        # A key exported with stray whitespace is stripped before it is sent.
        monkeypatch.setenv(KEY_ENV, f"  {KEY}\n")
        monkeypatch.setenv(ARCHIVE_DIR_ENV, str(store))
        vendor = Vendor({"AAA": [GOOD], "BBB": [ERROR]})
        monkeypatch.setattr(fetch_alphavantage, "urllib_get", vendor)
        monkeypatch.setattr(fetch_alphavantage.time, "sleep", lambda seconds: None)
        symbols = tmp_path / "symbols.txt"
        symbols.write_text("AAA\n", encoding="utf-8")
        argv = ["--cross-section", "sp600", "--symbols", str(symbols)]
        fetch_alphavantage.main(argv)
        assert capsys.readouterr().out.splitlines()[-1] == (
            "recorded 1, already recorded 0, failed 0, not reached 0"
        )
        symbols.write_text("AAA\nBBB\n", encoding="utf-8")
        with pytest.raises(SystemExit) as incomplete:
            fetch_alphavantage.main(argv)
        assert incomplete.value.code == 1


class TestTheSymbolList:
    def test_blank_lines_and_comments_are_skipped_and_repeats_kept_once(self, tmp_path):
        path = tmp_path / "symbols.txt"
        path.write_text("# today's members\nAAA\n\nBRK.B\nAAA\n  CCC  \n", encoding="utf-8")
        assert read_symbols(path) == ["AAA", "BRK.B", "CCC"]

    @pytest.mark.parametrize("bad", ["aaa", "AB/C", "A B"])
    def test_a_line_that_is_not_a_symbol_is_refused_by_number(self, tmp_path, bad):
        path = tmp_path / "symbols.txt"
        path.write_text(f"AAA\n{bad}\n", encoding="utf-8")
        with pytest.raises(ValueError, match="line 2"):
            read_symbols(path)

    def test_a_symbol_is_sent_exactly_as_written(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(request_url("BRK.B", KEY)).query)
        assert query["symbol"] == ["BRK.B"]
        assert query["function"] == ["TIME_SERIES_DAILY_ADJUSTED"]
        assert (query["outputsize"], query["datatype"]) == (["full"], ["csv"])


# --- the FX_DAILY path --------------------------------------------------------------------


def fx_body(*rows: str, header: str = FX_DAILY_HEADER, end: str = "\r\n") -> bytes:
    """An ``FX_DAILY`` body as the vendor writes it: newest row first, CRLF line ends."""
    return (end.join([header, *rows]) + end).encode("utf-8")


#: Three weekdays, newest first, as measured on 2026-10-13.
FX_GOOD = fx_body(
    "2026-10-12,1.4,1.5,1.3,1.4012",
    "2026-10-09,1.4,1.5,1.3,1.3998",
    "2026-10-08,1.4,1.5,1.3,1.4005",
)


class FxVendor:
    """A stub for the network that answers every ``FX_DAILY`` request in turn."""

    def __init__(self, *replies: bytes | BaseException):
        self.replies = list(replies)
        self.calls = 0

    def __call__(self, url: str) -> bytes:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        assert query["apikey"] == [KEY]
        assert query["function"] == ["FX_DAILY"]
        assert (query["from_symbol"], query["to_symbol"]) == (["USD"], ["CAD"])
        assert (query["outputsize"], query["datatype"]) == (["full"], ["csv"])
        self.calls += 1
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        if isinstance(reply, BaseException):
            raise reply
        return reply


@pytest.fixture
def data_dir(tmp_path) -> Path:
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / MANIFEST_NAME).write_bytes(b"")
    return directory


def fx_run(data_dir, vendor, day=date(2026, 10, 13), clock=None):
    return fetch_fx_daily(
        key=KEY,
        get=vendor,
        sleep=clock or Clock(),
        today=lambda: day,
        data_dir=data_dir,
    )


def nothing_written(data_dir: Path) -> bool:
    return read_manifest(data_dir) == [] and sorted(p.name for p in data_dir.iterdir()) == [
        MANIFEST_NAME
    ]


class TestTheFxDaily:
    def test_the_fetch_takes_no_pair_because_the_ruling_reaches_only_usd_cad(self, data_dir):
        vendor = FxVendor(FX_GOOD)
        with pytest.raises(TypeError):
            fetch_fx_daily("EUR", "USD", key=KEY, get=vendor, sleep=Clock(), data_dir=data_dir)
        assert vendor.calls == 0
        assert nothing_written(data_dir)

    def test_the_closes_are_recorded_oldest_first_under_the_pair(self, data_dir, capsys):
        entry = fx_run(data_dir, FxVendor(FX_GOOD))
        assert (entry.vendor, entry.symbol, entry.price_basis) == ("alphavantage", "USDCAD", "raw")
        assert entry.path == "alphavantage_usdcad_raw_2026-10-08_2026-10-12_dl2026-10-13.csv"
        assert entry.vendor_column == (
            "close, FX_DAILY from_symbol=USD to_symbol=CAD outputsize=full"
        )
        assert (data_dir / entry.path).read_bytes() == (
            b"Date,Close\n2026-10-08,1.4005\n2026-10-09,1.3998\n2026-10-12,1.4012\n"
        )
        assert entry.path in (data_dir / "checksums.sha256").read_text(encoding="utf-8")
        out = capsys.readouterr().out
        assert "USDCAD: 3 rows received, 0 dated on or after 2026-10-13 dropped" in out
        assert "recorded alphavantage_usdcad_raw_2026-10-08_2026-10-12_dl2026-10-13.csv" in out

    def test_a_body_with_lf_line_ends_reads_the_same(self, data_dir):
        body = FX_GOOD.replace(b"\r\n", b"\n")
        assert fx_run(data_dir, FxVendor(body)).row_count == 3

    def test_rows_dated_on_or_after_the_download_day_are_dropped_and_named(self, data_dir, capsys):
        body = fx_body(
            "2026-10-14,1.4,1.5,1.3,1.5",
            "2026-10-13,1.4,1.5,1.3,1.5",
            "2026-10-12,1.4,1.5,1.3,1.4012",
        )
        entry = fx_run(data_dir, FxVendor(body))
        assert (entry.row_count, entry.last_date) == (1, "2026-10-12")
        out = capsys.readouterr().out
        assert "2 dated on or after 2026-10-13 dropped (2026-10-13, 2026-10-14)" in out
        assert "USDCAD: 3 rows received, 2 dated" in out

    def test_the_manifest_holding_the_pair_refuses_before_any_request(self, data_dir):
        fx_run(data_dir, FxVendor(FX_GOOD))
        vendor = FxVendor(FX_GOOD)
        with pytest.raises(ValueError, match="already holds alphavantage_usdcad_raw_"):
            fx_run(data_dir, vendor, day=date(2026, 10, 14))
        assert vendor.calls == 0
        assert len(read_manifest(data_dir)) == 1

    @pytest.mark.parametrize(
        ("vendor", "basis"), [("yfinance", "raw"), ("alphavantage", "adjusted")]
    )
    def test_a_usdcad_vintage_from_another_vendor_or_basis_does_not_refuse(
        self, data_dir, vendor, basis
    ):
        record_vintage(
            [("2026-10-08", 1.4)],
            vendor=vendor,
            symbol="USDCAD",
            price_basis=basis,
            download_date="2026-10-10",
            data_dir=data_dir,
        )
        assert fx_run(data_dir, FxVendor(FX_GOOD)).row_count == 3
        assert len(read_manifest(data_dir)) == 2

    @pytest.mark.parametrize(
        ("body", "words"),
        [
            (fx_body("2026-10-12,1,1,1,1", header="timestamp,open,high,low"), "not the FX_DAILY"),
            (b"\xef\xbb\xbf" + FX_GOOD, "not the FX_DAILY header"),
            (FX_GOOD.rstrip(b"\r\n"), "does not end in a newline"),
            (FX_GOOD[:-12], "does not end in a newline"),
            (fx_body("2026-10-12,1,1,1,1", "2026-10-09,1,1,1"), "line 3 holds 4 fields"),
            (fx_body("2026-10-12,1,1,1,1,1"), "line 2 holds 6 fields"),
            (fx_body("2026-10-12,1,1,1,1", ""), "line 3 holds 1 fields"),
            (fx_body("2026-13-12,1,1,1,1"), "not an ISO calendar date"),
            (fx_body("20261009,1,1,1,1"), "not an ISO calendar date"),
            (fx_body("2026-W41-5,1,1,1,1"), "not an ISO calendar date"),
            (fx_body("2026-10-11,1,1,1,1", "2026-10-09,1,1,1,1"), "Saturday or a Sunday"),
            (fx_body("2026-10-10,1,1,1,1"), "the first 2026-10-10"),
            (fx_body("2026-10-13,1,1,1,1"), "no row dated before 2026-10-13"),
            (fx_body(), "no row dated before"),
            (b"", "an empty body"),
            (fx_body("2026-10-12,1,1,1,"), "is not a number"),
            (fx_body("2026-10-12,1,1,1,nan"), "not a finite number"),
            (fx_body("2026-10-12,1,1,1,1", "2026-10-12,1,1,1,1"), "more than one close"),
            (ERROR, "Alpha Vantage answered 'Invalid API call."),
            (b'{"Something": "else"}', "neither Error Message, Information nor Note"),
        ],
    )
    def test_a_body_the_run_cannot_trust_is_refused_and_nothing_is_written(
        self, data_dir, body, words
    ):
        with pytest.raises(ValueError, match=re.escape(words)):
            fx_run(data_dir, FxVendor(body))
        assert nothing_written(data_dir)

    def test_a_throttle_that_persists_stops_the_fetch(self, data_dir):
        vendor = FxVendor(INFORMATION)
        with pytest.raises(RunStopped, match="Thank you for using Alpha Vantage") as stopped:
            fx_run(data_dir, vendor)
        assert str(stopped.value).startswith(f"USDCAD, after {ATTEMPTS} attempts: ")
        assert vendor.calls == ATTEMPTS
        assert nothing_written(data_dir)

    def test_a_transport_failure_that_clears_is_retried(self, data_dir):
        clock = Clock()
        entry = fx_run(data_dir, FxVendor(OSError("reset"), FX_GOOD), clock=clock)
        assert entry.row_count == 3
        assert clock.waits == [TRANSPORT_WAIT_SECONDS, PAUSE_SECONDS]

    def test_a_body_cut_off_mid_read_stops_the_fetch_if_it_persists(self, data_dir):
        with pytest.raises(RunStopped, match="IncompleteRead"):
            fx_run(data_dir, FxVendor(http.client.IncompleteRead(b"abc", 100)))
        assert nothing_written(data_dir)

    def test_the_key_appears_in_no_output_when_a_transport_error_quotes_the_request(
        self, data_dir, capsys
    ):
        leaky = OSError(f"could not reach {fx_request_url(KEY)}")
        with pytest.raises(RunStopped) as stopped:
            fx_run(data_dir, FxVendor(leaky))
        out = capsys.readouterr()
        assert KEY not in str(stopped.value) and "<key>" in str(stopped.value)
        assert KEY not in out.out + out.err
