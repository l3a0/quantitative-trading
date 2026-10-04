"""The archive manifest and its reader, which hold the bars a public clone cannot read.

`chan.archive` hands back an archive file's bytes only once they hash to the line
`data/archive_vintages.jsonl` records. Most of what is held here runs anywhere,
on a fixture archive built in a temporary directory. One class reads the real
archive and skips, with the reader's own reason, on a machine that has none.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

import pytest

from chan import archive
from chan.archive import (
    ARCHIVE_DIR_ENV,
    ARCHIVE_MANIFEST_NAME,
    ArchiveRefused,
    ArchiveUnavailable,
    archive_dir,
    minute_bars,
    read_archive_manifest,
    read_archive_vintage,
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
        entries = {entry.symbol: entry for entry in read_archive_manifest()}
        assert set(entries) == set(COMMITTED)
        for symbol, fields in COMMITTED.items():
            for name, value in fields.items():
                assert getattr(entries[symbol], name) == value, (symbol, name)

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

    def test_a_symbol_recorded_twice_is_refused(self, tmp_path):
        data_dir, _ = fixture_archive(tmp_path)
        manifest = data_dir / ARCHIVE_MANIFEST_NAME
        manifest.write_text(manifest.read_text(encoding="utf-8") * 2, encoding="utf-8")
        with pytest.raises(ValueError, match="names ABC more than once"):
            read_archive_manifest(data_dir)


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
