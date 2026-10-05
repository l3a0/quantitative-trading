"""The archive manifest and its reader, which hold the files a public clone cannot read.

`chan.archive` hands back an archive file's bytes only once they hash to the line
`data/archive_vintages.jsonl` records. Most of what is held here runs anywhere,
on a fixture archive built in a temporary directory. One class reads the real
archive and skips, with the reader's own reason, on a machine that has none.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path

import pandas as pd
import pytest

from chan import archive
from chan.archive import (
    ARCHIVE_DIR_ENV,
    ARCHIVE_MANIFEST_NAME,
    DAILY_HEADER,
    ArchiveRecordRefused,
    ArchiveRefused,
    ArchiveUnavailable,
    archive_dir,
    daily_path,
    minute_bars,
    read_archive_manifest,
    read_archive_vintage,
    read_cross_section,
    record_archive_file,
    resolve_archive_vintage,
)
from chan.cpo import regular_session
from chan.paths import DATA_DIR
from chan.series import load_close

#: The two committed lines, field for field. A change to either is a change to
#: which bytes issue 23's results rest on, so it fails here first.
COMMITTED = {
    "GLD": {
        "vendor": "alphavantage",
        "price_basis": "raw",
        "download_date": "2026-07-17",
        "path": "gld_intraday_1min.csv.gz",
        "row_count": 2_984_037,
        "sha256": "3611a8f755d243c142b5c14813173169dab651bb106566ef30186da39a90de7a",
        "first_date": "2004-11-18",
        "last_date": "2026-07-16",
    },
    "GDX": {
        "vendor": "alphavantage",
        "price_basis": "raw",
        "download_date": "2026-10-03",
        "path": "gdx_intraday_1min.csv.gz",
        "row_count": 2_656_028,
        "sha256": "c47f58905305ac3bdb921e99962add33ed0658ab43c0a302bd87865343df711c",
        "first_date": "2006-05-22",
        "last_date": "2026-10-02",
    },
}

#: The days from 2006 to 2020 on which GDX's last regular-session close and its
#: committed raw daily close differ by more than 2%. Seven fall in 2008 and
#: March 2020. 2009-09-17 and 2014-12-03 have no cause found.
GDX_DAYS_BEYOND_TWO_PERCENT = [
    "2008-10-15",
    "2008-10-24",
    "2008-11-06",
    "2008-11-25",
    "2008-12-01",
    "2009-09-17",
    "2014-12-03",
    "2020-03-16",
    "2020-03-18",
]

CSV = (
    b"timestamp,open,high,low,close,volume\n"
    b"2006-05-22 09:30:00,10.0,10.5,9.5,10.2,100\n"
    b"2006-05-22 09:31:00,10.2,10.4,10.1,10.3,200\n"
    b"2006-05-22 16:05:00,10.3,10.3,10.3,10.3,50\n"
)


def fixture_archive(tmp_path: Path, payload: bytes = CSV, **overrides) -> tuple[Path, Path]:
    """A data directory with a one-line archive manifest, and an archive holding its file."""
    data_dir = tmp_path / "data"
    store = tmp_path / "archive"
    data_dir.mkdir()
    store.mkdir()
    packed = gzip.compress(payload, mtime=0)
    (store / "abc_intraday_1min.csv.gz").write_bytes(packed)
    line = {
        "vendor": "alphavantage",
        "symbol": "ABC",
        "price_basis": "raw",
        "download_date": "2026-10-03",
        "path": "abc_intraday_1min.csv.gz",
        "row_count": payload.count(b"\n") - 1,
        "sha256": hashlib.sha256(packed).hexdigest(),
        "first_date": "2006-05-22",
        "last_date": "2006-05-22",
        "vendor_call": "TIME_SERIES_INTRADAY",
    }
    line.update(overrides)
    (data_dir / ARCHIVE_MANIFEST_NAME).write_text(json.dumps(line) + "\n", encoding="utf-8")
    return data_dir, store


class TestTheCommittedManifest:
    def test_it_records_exactly_the_two_archive_files_issue_23_reads(self):
        """Standalone lines only, so a cross-section's lines landing leave this standing."""
        standalone = [entry for entry in read_archive_manifest() if entry.cross_section is None]
        entries = {entry.symbol: entry for entry in standalone}
        assert set(entries) == set(COMMITTED)
        for symbol, fields in COMMITTED.items():
            for name, value in fields.items():
                assert getattr(entries[symbol], name) == value, (symbol, name)

    def test_each_standalone_line_is_written_back_byte_for_byte(self):
        """The writer omits an unset cross_section, so the minute bars' lines keep their bytes."""
        lines = (DATA_DIR / ARCHIVE_MANIFEST_NAME).read_text(encoding="utf-8").splitlines()
        entries = read_archive_manifest()
        assert len(lines) == len(entries)
        for line, entry in zip(lines, entries, strict=True):
            if entry.cross_section is None:
                assert entry.as_json() == line

    def test_no_archive_file_is_also_committed_under_data(self):
        """An archive vintage committed in `data/` would be two records of one series."""
        for entry in read_archive_manifest():
            assert not (DATA_DIR / entry.path).exists()

    def test_the_committed_manifest_is_not_the_vintage_manifest(self):
        """The suite's one-entry-per-file check reads `vintages.jsonl` and never this file."""
        assert ARCHIVE_MANIFEST_NAME != "vintages.jsonl"
        assert (DATA_DIR / ARCHIVE_MANIFEST_NAME).is_file()


class TestWhereTheArchiveIs:
    def test_the_environment_variable_names_it(self, tmp_path):
        assert archive_dir({ARCHIVE_DIR_ENV: str(tmp_path)}, tmp_path / "absent") == tmp_path

    def test_the_config_file_names_it_when_the_variable_is_unset(self, tmp_path):
        config = tmp_path / "archive_dir"
        config.write_text(f"{tmp_path}\n", encoding="utf-8")
        assert archive_dir({}, config) == tmp_path

    def test_the_variable_wins_over_the_config_file(self, tmp_path):
        config = tmp_path / "archive_dir"
        config.write_text("/nowhere\n", encoding="utf-8")
        assert archive_dir({ARCHIVE_DIR_ENV: str(tmp_path)}, config) == tmp_path

    def test_neither_is_unavailable_and_names_both_ways_to_set_it(self, tmp_path):
        with pytest.raises(ArchiveUnavailable) as missing:
            archive_dir({}, tmp_path / "absent")
        assert ARCHIVE_DIR_ENV in str(missing.value)
        assert "archive_dir" in str(missing.value)

    def test_a_named_directory_that_does_not_exist_is_unavailable(self, tmp_path):
        with pytest.raises(ArchiveUnavailable, match="not a directory"):
            archive_dir({ARCHIVE_DIR_ENV: str(tmp_path / "gone")}, tmp_path / "absent")


class TestReadingAnArchiveFile:
    def test_bytes_matching_the_record_are_returned(self, tmp_path):
        data_dir, store = fixture_archive(tmp_path)
        entry = resolve_archive_vintage("abc", data_dir)
        assert read_archive_vintage(entry, store) == (store / entry.path).read_bytes()

    def test_bytes_that_differ_are_refused_naming_both_hashes(self, tmp_path):
        data_dir, store = fixture_archive(tmp_path)
        entry = resolve_archive_vintage("ABC", data_dir)
        (store / entry.path).write_bytes(gzip.compress(CSV.replace(b"10.3", b"10.4"), mtime=0))
        with pytest.raises(ArchiveRefused) as refused:
            read_archive_vintage(entry, store)
        assert entry.sha256 in str(refused.value)
        assert str(store / entry.path) in str(refused.value)

    def test_a_hash_differing_only_in_its_last_digit_is_refused(self, tmp_path):
        """The refusal compares the whole digest, not a prefix of it."""
        data_dir, store = fixture_archive(tmp_path)
        real = resolve_archive_vintage("ABC", data_dir).sha256
        flipped = real[:-1] + ("0" if real[-1] != "0" else "1")
        (tmp_path / "flipped").mkdir()
        data_dir, store = fixture_archive(tmp_path / "flipped", sha256=flipped)
        with pytest.raises(ArchiveRefused):
            read_archive_vintage(resolve_archive_vintage("ABC", data_dir), store)

    def test_columns_other_than_open_to_volume_are_refused(self, tmp_path):
        payload = b"timestamp,open,high,low,close,adjusted_close\n2006-05-22 09:30:00,1,1,1,1,1\n"
        data_dir, store = fixture_archive(tmp_path, payload=payload)
        with pytest.raises(ValueError, match="not open to volume"):
            minute_bars("ABC", data_dir=data_dir, directory=store)

    def test_a_file_the_archive_lacks_is_unavailable_not_refused(self, tmp_path):
        data_dir, store = fixture_archive(tmp_path)
        entry = resolve_archive_vintage("ABC", data_dir)
        (store / entry.path).unlink()
        with pytest.raises(ArchiveUnavailable, match="holds no abc_intraday_1min.csv.gz"):
            read_archive_vintage(entry, store)

    def test_minute_bars_parse_every_row_with_the_entry_attached(self, tmp_path):
        data_dir, store = fixture_archive(tmp_path)
        bars = minute_bars("ABC", data_dir=data_dir, directory=store)
        assert list(bars.columns) == ["open", "high", "low", "close", "volume"]
        assert len(bars) == 3
        assert bars.index[0].strftime("%Y-%m-%d %H:%M") == "2006-05-22 09:30"
        assert bars.attrs["vintage"].symbol == "ABC"

    def test_a_row_count_the_file_does_not_hold_is_refused(self, tmp_path):
        data_dir, store = fixture_archive(tmp_path, row_count=4)
        with pytest.raises(ArchiveRefused, match="parses to 3 rows, not the 4"):
            minute_bars("ABC", data_dir=data_dir, directory=store)

    def test_an_unrecorded_symbol_is_a_lookup_error(self, tmp_path):
        data_dir, _ = fixture_archive(tmp_path)
        with pytest.raises(LookupError, match="no archive vintage for XYZ"):
            resolve_archive_vintage("xyz", data_dir)


class TestAMalformedLineIsRefusedByNumber:
    @pytest.mark.parametrize(
        ("override", "words"),
        [
            ({"path": "../escape.csv.gz"}, "bare file name"),
            ({"path": "sub/abc.csv.gz"}, "bare file name"),
            ({"sha256": "ABC"}, "64 lowercase hex"),
            ({"row_count": 0}, "positive whole number"),
            ({"price_basis": "adjusted"}, "other than raw"),
            ({"symbol": "abc"}, "upper case"),
            ({"first_date": "May 2006"}, "first_date that is not an ISO"),
            ({"path": ".."}, "bare file name"),
            ({"first_date": "2006-05-22T09:30"}, "first_date that is not an ISO"),
            ({"sha256": "a" * 65}, "64 lowercase hex"),
            ({"row_count": 3.0}, "positive whole number"),
        ],
    )
    def test_each_bad_field_is_named(self, tmp_path, override, words):
        data_dir, _ = fixture_archive(tmp_path, **override)
        with pytest.raises(ValueError, match=words):
            read_archive_manifest(data_dir)

    def test_a_missing_field_is_refused(self, tmp_path):
        data_dir, _ = fixture_archive(tmp_path)
        manifest = data_dir / ARCHIVE_MANIFEST_NAME
        line = json.loads(manifest.read_text(encoding="utf-8"))
        del line["vendor_call"]
        manifest.write_text(json.dumps(line) + "\n", encoding="utf-8")
        with pytest.raises(ValueError, match="line 1 does not carry exactly"):
            read_archive_manifest(data_dir)

    def test_an_extra_field_is_refused(self, tmp_path):
        data_dir, _ = fixture_archive(tmp_path, extra="x")
        with pytest.raises(ValueError, match="does not carry exactly"):
            read_archive_manifest(data_dir)

    def test_a_symbol_recorded_twice_is_refused(self, tmp_path):
        data_dir, _ = fixture_archive(tmp_path)
        manifest = data_dir / ARCHIVE_MANIFEST_NAME
        manifest.write_text(manifest.read_text(encoding="utf-8") * 2, encoding="utf-8")
        with pytest.raises(ValueError, match="names ABC more than once"):
            read_archive_manifest(data_dir)


def daily(*rows: str) -> bytes:
    """A daily file as Alpha Vantage writes one, the newest row first."""
    return (DAILY_HEADER + "\n" + "".join(row + "\n" for row in rows)).encode("utf-8")


#: Two symbols' files, each newest first, with ABC missing the first day.
ABC = daily("2009-01-05,1,1,1,12.0,6.0,100,0,1", "2009-01-02,1,1,1,10.0,5.0,100,0,1")
XYZ = daily(
    "2009-01-05,1,1,1,22.0,22.0,100,0,1",
    "2009-01-02,1,1,1,21.0,21.0,100,0,1",
    "2008-12-31,1,1,1,20.0,20.0,100,0,1",
)


#: A CSV opening on another header, as a changed endpoint would answer.
MINUTE_SHAPED = b"timestamp,open,high,low,close,volume\n2009-01-02,1,1,1,1,1\n"


def empty_store(tmp_path: Path) -> tuple[Path, Path]:
    """A data directory holding an empty archive manifest, and an empty archive."""
    data_dir = tmp_path / "data"
    store = tmp_path / "archive"
    data_dir.mkdir()
    store.mkdir()
    (data_dir / ARCHIVE_MANIFEST_NAME).write_bytes(b"")
    return data_dir, store


def cross_line(**overrides) -> dict:
    """One valid cross-section line for ABC, before any override."""
    line = {
        "cross_section": "sp600",
        "vendor": "alphavantage",
        "symbol": "ABC",
        "price_basis": "adjusted",
        "download_date": "2026-10-05",
        "path": "sp600/daily_ABC.csv",
        "row_count": 2,
        "sha256": hashlib.sha256(ABC).hexdigest(),
        "first_date": "2009-01-02",
        "last_date": "2009-01-05",
        "vendor_call": "TIME_SERIES_DAILY_ADJUSTED, outputsize=full, datatype=csv",
    }
    line.update(overrides)
    return line


def manifest_of(tmp_path: Path, *lines: dict) -> Path:
    """A data directory whose archive manifest holds exactly these lines."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    payload = "".join(json.dumps(line, sort_keys=True) + "\n" for line in lines)
    (data_dir / ARCHIVE_MANIFEST_NAME).write_text(payload, encoding="utf-8")
    return data_dir


def standalone(symbol: str = "ABC") -> dict:
    """A standalone minute-bar line, as GLD's and GDX's are."""
    return {
        "vendor": "alphavantage",
        "symbol": symbol,
        "price_basis": "raw",
        "download_date": "2026-10-03",
        "path": f"{symbol.lower()}_intraday_1min.csv.gz",
        "row_count": 3,
        "sha256": "0" * 64,
        "first_date": "2006-05-22",
        "last_date": "2006-05-22",
        "vendor_call": "TIME_SERIES_INTRADAY",
    }


class TestACrossSectionLine:
    def test_a_valid_line_is_read_with_its_cross_section(self, tmp_path):
        (entry,) = read_archive_manifest(manifest_of(tmp_path, cross_line()))
        assert entry.cross_section == "sp600"
        assert entry.path == daily_path("sp600", "ABC") == "sp600/daily_ABC.csv"

    def test_the_line_is_written_back_byte_for_byte(self, tmp_path):
        (entry,) = read_archive_manifest(manifest_of(tmp_path, cross_line()))
        assert entry.as_json() == json.dumps(cross_line(), sort_keys=True)

    @pytest.mark.parametrize(
        ("override", "words"),
        [
            ({"path": "sp600/ABC.csv"}, "other than <cross_section>/daily_<symbol>.csv"),
            ({"path": "../daily_ABC.csv"}, "other than <cross_section>/daily_<symbol>.csv"),
            ({"price_basis": "raw"}, "cross-section price_basis other than adjusted"),
            ({"cross_section": "sp500"}, "has not ruled into the archive"),
            ({"symbol": "AB/C", "path": "sp600/daily_AB/C.csv"}, "SYMBOL_PATTERN"),
        ],
    )
    def test_each_cross_section_rule_is_refused_by_name(self, tmp_path, override, words):
        with pytest.raises(ValueError, match=re.escape(words)):
            read_archive_manifest(manifest_of(tmp_path, cross_line(**override)))

    def test_an_adjusted_basis_without_a_cross_section_is_refused(self, tmp_path):
        line = standalone()
        line["price_basis"] = "adjusted"
        with pytest.raises(ValueError, match="other than raw"):
            read_archive_manifest(manifest_of(tmp_path, line))

    def test_a_null_cross_section_is_refused(self, tmp_path):
        line = standalone()
        line["cross_section"] = None
        with pytest.raises(ValueError, match="not a name"):
            read_archive_manifest(manifest_of(tmp_path, line))

    def test_a_pair_recorded_twice_is_refused_naming_it(self, tmp_path):
        with pytest.raises(ValueError, match="names sp600/ABC more than once"):
            read_archive_manifest(manifest_of(tmp_path, cross_line(), cross_line()))

    def test_one_symbol_in_two_cross_sections_is_accepted(self, tmp_path, monkeypatch):
        monkeypatch.setattr(archive, "CROSS_SECTIONS", ("sp600", "sp400"))
        later = cross_line(cross_section="sp400", path="sp400/daily_ABC.csv")
        entries = read_archive_manifest(manifest_of(tmp_path, cross_line(), later))
        assert [entry.cross_section for entry in entries] == ["sp600", "sp400"]

    def test_one_symbol_alone_and_in_a_cross_section_is_accepted(self, tmp_path):
        entries = read_archive_manifest(manifest_of(tmp_path, standalone(), cross_line()))
        assert [entry.cross_section for entry in entries] == [None, "sp600"]

    def test_a_lookup_by_symbol_reads_only_the_standalone_line(self, tmp_path):
        data_dir = manifest_of(tmp_path, cross_line(), standalone())
        assert resolve_archive_vintage("ABC", data_dir).cross_section is None

    def test_a_symbol_only_in_a_cross_section_is_no_standalone_vintage(self, tmp_path):
        with pytest.raises(LookupError, match="no archive vintage for ABC"):
            resolve_archive_vintage("ABC", manifest_of(tmp_path, cross_line()))


class TestRecordingADailyFile:
    def test_the_file_and_the_line_agree_on_hash_rows_and_span(self, tmp_path):
        data_dir, store = empty_store(tmp_path)
        entry = record_archive_file(
            "sp600", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
        )
        assert (store / "sp600" / "daily_XYZ.csv").read_bytes() == XYZ
        assert read_archive_manifest(data_dir) == [entry]
        span = (entry.row_count, entry.first_date, entry.last_date)
        assert span == (3, "2008-12-31", "2009-01-05")
        assert entry.sha256 == hashlib.sha256(XYZ).hexdigest()
        assert (entry.price_basis, entry.cross_section) == ("adjusted", "sp600")

    def test_rows_in_any_order_give_the_earliest_and_latest_date(self, tmp_path):
        data_dir, store = empty_store(tmp_path)
        ascending = daily(
            "2008-12-31,1,1,1,20.0,20.0,100,0,1",
            "",
            "2009-01-05,1,1,1,22.0,22.0,100,0,1",
            "2009-01-02,1,1,1,21.0,21.0,100,0,1",
        )
        entry = record_archive_file(
            "sp600",
            "XYZ",
            ascending,
            download_date="2026-10-05",
            data_dir=data_dir,
            directory=store,
        )
        assert (entry.row_count, entry.first_date, entry.last_date) == (
            3,
            "2008-12-31",
            "2009-01-05",
        )
        _, panel = read_cross_section("sp600", data_dir=data_dir, directory=store)
        assert panel["XYZ"].tolist() == [20.0, 21.0, 22.0]

    @pytest.mark.parametrize(
        ("symbol", "day", "words"),
        [("xyz", "2026-10-05", "SYMBOL_PATTERN"), ("XYZ", "5 Oct 2026", "ISO calendar date")],
    )
    def test_a_bad_symbol_or_day_is_refused_before_anything_is_written(
        self, tmp_path, symbol, day, words
    ):
        data_dir, store = empty_store(tmp_path)
        with pytest.raises(ValueError, match=words):
            record_archive_file(
                "sp600", symbol, XYZ, download_date=day, data_dir=data_dir, directory=store
            )
        assert list(store.iterdir()) == [] and read_archive_manifest(data_dir) == []

    def test_bytes_on_disk_that_differ_from_the_payload_leave_no_file_and_no_line(
        self, tmp_path, monkeypatch
    ):
        data_dir, store = empty_store(tmp_path)
        real = Path.read_bytes

        def tampered(path):
            return b"other bytes" if path.name.startswith("daily_") else real(path)

        monkeypatch.setattr(Path, "read_bytes", tampered)
        with pytest.raises(OSError, match="does not match the bytes that were hashed"):
            record_archive_file(
                "sp600", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
            )
        monkeypatch.undo()
        assert not (store / "sp600" / "daily_XYZ.csv").exists()
        assert read_archive_manifest(data_dir) == []

    def test_a_line_is_appended_after_one_missing_its_newline(self, tmp_path):
        data_dir, store = empty_store(tmp_path)
        (data_dir / ARCHIVE_MANIFEST_NAME).write_text(json.dumps(standalone()), encoding="utf-8")
        record_archive_file(
            "sp600", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
        )
        assert [entry.symbol for entry in read_archive_manifest(data_dir)] == ["ABC", "XYZ"]

    def test_a_file_already_in_the_archive_is_refused_and_left_untouched(self, tmp_path):
        data_dir, store = empty_store(tmp_path)
        (store / "sp600").mkdir()
        (store / "sp600" / "daily_XYZ.csv").write_bytes(b"older bytes")
        with pytest.raises(ArchiveRecordRefused, match="Move it aside"):
            record_archive_file(
                "sp600", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
            )
        assert (store / "sp600" / "daily_XYZ.csv").read_bytes() == b"older bytes"
        assert read_archive_manifest(data_dir) == []

    def test_a_symbol_already_recorded_is_refused(self, tmp_path):
        data_dir, store = empty_store(tmp_path)
        record_archive_file(
            "sp600", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
        )
        (store / "sp600" / "daily_XYZ.csv").unlink()
        with pytest.raises(ArchiveRecordRefused, match="already records sp600/XYZ"):
            record_archive_file(
                "sp600", "XYZ", XYZ, download_date="2026-10-06", data_dir=data_dir, directory=store
            )

    @pytest.mark.parametrize(
        ("payload", "words"),
        [
            (MINUTE_SHAPED, "not the daily header"),
            (daily(), "no rows under it"),
            (daily("Jan 2,1,1,1,1,1,1,0,1"), "ISO date"),
            (daily("2026-02-30,1,1,1,1,1,1,0,1"), "ISO date"),
            (
                daily("2009-01-02,1,1,1,1,1,1,0,1", "2009-01-02,1,1,1,1,1,1,0,1"),
                "1 dates appear twice, the first 2009-01-02",
            ),
            (b"", "not the daily header"),
        ],
    )
    def test_bytes_that_are_not_a_daily_file_leave_no_file_and_no_line(
        self, tmp_path, payload, words
    ):
        data_dir, store = empty_store(tmp_path)
        with pytest.raises(ValueError, match=words):
            record_archive_file(
                "sp600",
                "XYZ",
                payload,
                download_date="2026-10-05",
                data_dir=data_dir,
                directory=store,
            )
        assert not (store / "sp600" / "daily_XYZ.csv").exists()
        assert read_archive_manifest(data_dir) == []

    def test_an_unruled_cross_section_is_refused_before_anything_is_written(self, tmp_path):
        data_dir, store = empty_store(tmp_path)
        with pytest.raises(ValueError, match="has not ruled"):
            record_archive_file(
                "sp500", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
            )
        assert list(store.iterdir()) == []

    def test_an_interrupt_before_the_line_lands_takes_the_file_back(self, tmp_path, monkeypatch):
        data_dir, store = empty_store(tmp_path)

        def interrupted(manifest, line):
            raise KeyboardInterrupt

        monkeypatch.setattr(archive, "_append_line", interrupted)
        with pytest.raises(KeyboardInterrupt):
            record_archive_file(
                "sp600", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
            )
        assert not (store / "sp600" / "daily_XYZ.csv").exists()
        assert read_archive_manifest(data_dir) == []

    @pytest.mark.parametrize("failure", [OSError("disk full"), KeyboardInterrupt()])
    def test_a_failure_part_way_through_the_write_takes_the_file_back(
        self, tmp_path, monkeypatch, failure
    ):
        data_dir, store = empty_store(tmp_path)

        class Partial:
            def __init__(self, path, mode):
                self.handle = open(path, mode)

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                self.handle.close()

            def write(self, payload):
                self.handle.write(payload[:10])
                raise failure

        monkeypatch.setattr(archive, "open", Partial, raising=False)
        with pytest.raises(type(failure)):
            record_archive_file(
                "sp600", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
            )
        assert not (store / "sp600" / "daily_XYZ.csv").exists()
        assert read_archive_manifest(data_dir) == []

    def test_an_interrupt_after_the_line_lands_keeps_the_file(self, tmp_path, monkeypatch):
        data_dir, store = empty_store(tmp_path)
        append = archive._append_line

        def landed_then_interrupted(manifest, line):
            append(manifest, line)
            raise KeyboardInterrupt

        monkeypatch.setattr(archive, "_append_line", landed_then_interrupted)
        with pytest.raises(KeyboardInterrupt):
            record_archive_file(
                "sp600", "XYZ", XYZ, download_date="2026-10-05", data_dir=data_dir, directory=store
            )
        (entry,) = read_archive_manifest(data_dir)
        assert read_archive_vintage(entry, store) == XYZ


def recorded_store(tmp_path: Path) -> tuple[Path, Path]:
    """An archive holding ABC and XYZ under sp600, both recorded."""
    data_dir, store = empty_store(tmp_path)
    for symbol, payload in (("XYZ", XYZ), ("ABC", ABC)):
        record_archive_file(
            "sp600",
            symbol,
            payload,
            download_date="2026-10-05",
            data_dir=data_dir,
            directory=store,
        )
    return data_dir, store


class TestReadingACrossSection:
    def test_the_frame_is_date_by_symbol_on_the_union_of_dates(self, tmp_path):
        data_dir, store = recorded_store(tmp_path)
        entries, panel = read_cross_section("sp600", data_dir=data_dir, directory=store)
        assert [entry.symbol for entry in entries] == ["ABC", "XYZ"]
        assert list(panel.columns) == ["ABC", "XYZ"]
        days = panel.index.strftime("%Y-%m-%d").tolist()
        assert days == ["2008-12-31", "2009-01-02", "2009-01-05"]
        assert panel["ABC"].tolist()[1:] == [5.0, 6.0]
        assert pd.isna(panel["ABC"].iloc[0])
        assert panel["XYZ"].tolist() == [20.0, 21.0, 22.0]

    def test_the_raw_close_is_the_other_column(self, tmp_path):
        data_dir, store = recorded_store(tmp_path)
        _, panel = read_cross_section("sp600", column="close", data_dir=data_dir, directory=store)
        assert panel["ABC"].dropna().tolist() == [10.0, 12.0]

    def test_any_other_column_is_refused(self, tmp_path):
        data_dir, store = recorded_store(tmp_path)
        with pytest.raises(ValueError, match="column must be one of"):
            read_cross_section("sp600", column="volume", data_dir=data_dir, directory=store)

    def test_symbols_narrow_the_read_and_an_unrecorded_one_is_left_out(self, tmp_path):
        data_dir, store = recorded_store(tmp_path)
        entries, panel = read_cross_section(
            "sp600", symbols=["xyz", "QQQ"], data_dir=data_dir, directory=store
        )
        assert [entry.symbol for entry in entries] == ["XYZ"]
        assert list(panel.columns) == ["XYZ"]

    def test_symbols_are_matched_after_stripping_and_narrowing_to_none_is_empty(self, tmp_path):
        data_dir, store = recorded_store(tmp_path)
        entries, _ = read_cross_section(
            "sp600", symbols=[" xyz "], data_dir=data_dir, directory=store
        )
        assert [entry.symbol for entry in entries] == ["XYZ"]
        entries, panel = read_cross_section(
            "sp600", symbols=["QQQ"], data_dir=data_dir, directory=store
        )
        assert entries == [] and panel.empty

    def test_an_unrecorded_name_is_a_lookup_error(self, tmp_path):
        data_dir, store = recorded_store(tmp_path)
        with pytest.raises(LookupError, match="no cross-section named sp400"):
            read_cross_section("sp400", data_dir=data_dir, directory=store)

    def test_an_altered_file_is_refused(self, tmp_path):
        data_dir, store = recorded_store(tmp_path)
        (store / "sp600" / "daily_ABC.csv").write_bytes(ABC.replace(b"12.0", b"12.5"))
        with pytest.raises(ArchiveRefused):
            read_cross_section("sp600", data_dir=data_dir, directory=store)

    def test_a_missing_file_refuses_the_whole_read(self, tmp_path):
        data_dir, store = recorded_store(tmp_path)
        (store / "sp600" / "daily_ABC.csv").unlink()
        with pytest.raises(ArchiveUnavailable, match="holds no sp600/daily_ABC.csv"):
            read_cross_section("sp600", data_dir=data_dir, directory=store)

    def test_a_row_count_the_file_does_not_hold_is_refused(self, tmp_path):
        data_dir = manifest_of(tmp_path, cross_line(row_count=3))
        store = tmp_path / "archive"
        (store / "sp600").mkdir(parents=True)
        (store / "sp600" / "daily_ABC.csv").write_bytes(ABC)
        with pytest.raises(ArchiveRefused, match="parses to 2 rows, not the 3"):
            read_cross_section("sp600", data_dir=data_dir, directory=store)

    def test_a_file_with_another_header_is_refused(self, tmp_path):
        other = MINUTE_SHAPED
        data_dir = manifest_of(
            tmp_path, cross_line(sha256=hashlib.sha256(other).hexdigest(), row_count=1)
        )
        store = tmp_path / "archive"
        (store / "sp600").mkdir(parents=True)
        (store / "sp600" / "daily_ABC.csv").write_bytes(other)
        with pytest.raises(ValueError, match="not the daily header"):
            read_cross_section("sp600", data_dir=data_dir, directory=store)

    def test_no_archive_is_unavailable(self, tmp_path, monkeypatch):
        data_dir, _ = recorded_store(tmp_path)
        monkeypatch.delenv(ARCHIVE_DIR_ENV, raising=False)
        monkeypatch.setattr(archive, "ARCHIVE_DIR_CONFIG", tmp_path / "absent")
        with pytest.raises(ArchiveUnavailable, match="no data archive is configured"):
            read_cross_section("sp600", data_dir=data_dir)


@pytest.fixture(scope="module")
def store() -> Path:
    """The configured archive, or a skip carrying the reader's own reason."""
    try:
        return archive.archive_dir()
    except ArchiveUnavailable as absent:
        pytest.skip(str(absent))


class TestTheRealArchive:
    """Runs only where an archive is configured: one hash check, and one parse of both files."""

    def test_every_recorded_file_hashes_to_its_line(self, store):
        for entry in read_archive_manifest():
            try:
                read_archive_vintage(entry, store)
            except ArchiveUnavailable as absent:
                pytest.skip(str(absent))

    @pytest.mark.parametrize(
        ("symbol", "days", "median", "largest", "days_beyond_two_percent"),
        [
            ("GLD", 3776, 0.00012187512739675332, 0.006385656816790597, []),
            ("GDX", 3680, 0.0004560102615875916, 0.06961038961038957, GDX_DAYS_BEYOND_TWO_PERCENT),
        ],
    )
    def test_each_day_s_last_close_agrees_with_the_daily_vintage(
        self, store, symbol, days, median, largest, days_beyond_two_percent
    ):
        """The last regular-session bar of each day from 2006 to 2020 against the raw daily close.

        The session is the one Example 7.1 reads, `chan.cpo.regular_session`,
        which ends at 12:59 on an early close. A bar's timestamp is the minute it
        opens, so the 15:59 bar closes at 16:00. The official close comes from the
        closing auction, so small differences are expected and a large one is a
        day worth naming. The span stops where `chan.cpo.EARLY_CLOSES` stops.
        """
        bars = minute_bars(symbol, directory=store)
        session = regular_session(bars)
        session = session[session.index >= "2006-01-01"]
        last = session.groupby(session.index.normalize())["close"].last()
        daily = load_close(symbol, unadjusted=True)
        shared = last.index.intersection(daily.index)
        gap = (last[shared] / daily[shared] - 1).abs()
        assert len(shared) == days
        assert gap.median() == pytest.approx(median, abs=1e-12)
        assert gap.max() == pytest.approx(largest, abs=1e-12)
        assert gap[gap > 0.02].index.strftime("%Y-%m-%d").tolist() == days_beyond_two_percent
