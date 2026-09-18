"""What the vintage recorder must do, and what it must refuse.

Every case here is driven by a synthetic series, because the recorder takes
rows rather than fetching them. Nothing in this file touches a network or the
committed ``data/`` directory, except the last class, which reads the eight
vintages this repo ships and checks the manifest still describes them.

The order the cases appear in is the order the rules appear on
[issue 1](https://github.com/l3a0/quantitative-trading/issues/1).
"""

import hashlib
import json

import pytest

from chan import vintage
from chan.paths import DATA_DIR
from chan.vintage import (
    CHECKSUMS_NAME,
    MANIFEST_NAME,
    VintageEntry,
    VintageRefused,
    read_manifest,
    record_vintage,
)

ROWS = [("2026-08-25", 50.0), ("2026-08-26", 51.25), ("2026-08-27", 52.0)]
SOURCE = dict(vendor="yfinance", symbol="GDX", price_basis="raw", download_date="2026-08-27")
RECORDED_NAME = "yfinance_gdx_raw_2026-08-25_2026-08-27_dl2026-08-27.csv"


@pytest.fixture
def data_dir(tmp_path):
    """A directory holding an empty manifest, which is what a recorder needs.

    The manifest is committed rather than created on demand, so a run against a
    real tree always finds one. A test has to supply the same starting state.
    """
    (tmp_path / MANIFEST_NAME).write_text("", encoding="utf-8")
    return tmp_path


def manifest_lines(data_dir):
    return (data_dir / MANIFEST_NAME).read_text(encoding="utf-8").splitlines()


class TestRecordingAVintage:
    def test_every_manifest_field_reads_back(self, data_dir):
        """Rule 2. Nine values, and the sha256 is the hash of the file on disk."""
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert read_manifest(data_dir) == [entry]
        recorded = json.loads(manifest_lines(data_dir)[0])
        assert recorded == {
            "vendor": "yfinance",
            "symbol": "GDX",
            "price_basis": "raw",
            "first_date": "2026-08-25",
            "last_date": "2026-08-27",
            "download_date": "2026-08-27",
            "path": RECORDED_NAME,
            "row_count": 3,
            "sha256": entry.sha256,
        }
        written = (data_dir / RECORDED_NAME).read_bytes()
        assert hashlib.sha256(written).hexdigest() == entry.sha256

    def test_a_known_input_produces_known_bytes(self, data_dir):
        """The sha256 is a claim about bytes, and the bytes come from the serializer.

        Every other case here reads fields back out of the manifest, and all of
        them stay green when the float formatting, the date format or the line
        terminator moves. Each of those silently re-hashes every vintage
        recorded afterwards, so the byte shape is pinned rather than inferred.
        """
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert (data_dir / entry.path).read_bytes() == (
            b"Price,Close\nTicker,GDX\nDate,\n2026-08-25,50.0\n2026-08-26,51.25\n2026-08-27,52.0\n"
        )

    def test_the_header_matches_the_shape_every_committed_vintage_carries(self, data_dir):
        """A second header shape would make data/README.md describe one of two.

        `load_close` drops every leading row whose first field is not a date,
        so a plainer header would read fine. Writing the shape already in the
        ground costs nothing and keeps one description true for every file.
        """
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        written = (data_dir / entry.path).read_text(encoding="utf-8").splitlines()[:3]
        committed = (DATA_DIR / "gdx_20yr_prices.csv").read_text(encoding="utf-8").splitlines()[:3]
        assert written == committed

    def test_unsorted_rows_record_the_span_of_their_dates(self, data_dir):
        """Rule 2. Taking the first and last row records a span the series does not have."""
        entry = record_vintage([ROWS[2], ROWS[0], ROWS[1]], data_dir=data_dir, **SOURCE)

        assert (entry.first_date, entry.last_date) == ("2026-08-25", "2026-08-27")

    def test_two_downloads_of_one_span_both_record(self, data_dir):
        """Rule 1, and the reason the download date is in the path.

        Two downloads with no new bar between them, over a weekend or a holiday
        or after a delisting, agree on vendor, symbol, span and price basis. A
        four-field path gives them one name and the refusal blocks the second,
        which is the pair a test of the premise needs.
        """
        first = record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        second = record_vintage(
            ROWS, data_dir=data_dir, **{**SOURCE, "download_date": "2026-08-29"}
        )

        assert first.path != second.path
        assert first.sha256 == second.sha256
        assert len(manifest_lines(data_dir)) == 2


class TestTheRefusal:
    def test_a_second_write_leaves_the_original_file_alone(self, data_dir):
        """Rule 3. An overwrite that succeeds looks like a successful run.

        Asserting that something raised is not enough. The second call carries
        different closes, so a refusal that raised after writing would leave
        different bytes behind and still pass that weaker check.
        """
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        before = (data_dir / entry.path).read_bytes()

        with pytest.raises(VintageRefused):
            record_vintage(
                [("2026-08-25", 999.0), ("2026-08-27", 1.0), ("2026-08-26", 2.0)],
                data_dir=data_dir,
                **SOURCE,
            )

        assert (data_dir / entry.path).read_bytes() == before
        assert len(manifest_lines(data_dir)) == 1

    def test_a_deleted_file_with_a_live_entry_still_refuses(self, data_dir):
        """Rule 3. Checking only the file on disk re-records and leaves two entries."""
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        (data_dir / entry.path).unlink()

        with pytest.raises(VintageRefused):
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert len(manifest_lines(data_dir)) == 1

    def test_the_message_names_the_path_and_which_condition_fired(self, data_dir):
        """Rule 3. The recorder raises and whoever ran it is the only reader.

        "The file exists" sends that reader to the wrong fix when the real
        state is a manifest entry whose file was deleted, so the two conditions
        do not share a message.
        """
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        with pytest.raises(VintageRefused) as both_hold:
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        assert entry.path in str(both_hold.value)
        assert "manifest already holds an entry" in str(both_hold.value)

        (data_dir / MANIFEST_NAME).write_text("", encoding="utf-8")
        with pytest.raises(VintageRefused) as file_only:
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        assert entry.path in str(file_only.value)
        assert "already on disk" in str(file_only.value)

    def test_an_absent_manifest_raises_rather_than_being_created(self, tmp_path):
        """Rule 7. A manifest that is moved or lost turns every path new again.

        Creating one on demand is the refusal switching itself off, and it
        arrives looking like a clean first run.
        """
        with pytest.raises(FileNotFoundError):
            record_vintage(ROWS, data_dir=tmp_path, **SOURCE)

        assert not (tmp_path / MANIFEST_NAME).exists()
        assert list(tmp_path.iterdir()) == []

    def test_an_empty_series_and_a_repeated_date_are_refused(self, data_dir):
        """Rule 9. Neither is a series, and both reach the manifest as a wrong span."""
        with pytest.raises(ValueError, match="empty series"):
            record_vintage([], data_dir=data_dir, **SOURCE)

        with pytest.raises(ValueError, match="more than one close"):
            record_vintage(
                [("2026-08-25", 50.0), ("2026-08-25", 51.0)], data_dir=data_dir, **SOURCE
            )

        assert manifest_lines(data_dir) == []
        assert list(data_dir.iterdir()) == [data_dir / MANIFEST_NAME]

    def test_an_unknown_price_basis_is_refused(self, data_dir):
        """Rule 10. Every refusal compares strings, and so does the path.

        `raw` and `unadjusted` name one thing, and a free-form field lets them
        be two vintages of one download that the name no longer keeps apart.
        """
        with pytest.raises(ValueError, match="price basis"):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "price_basis": "unadjusted"})

        with pytest.raises(ValueError, match="vendor"):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "vendor": "Yahoo Finance"})

        assert manifest_lines(data_dir) == []


class TestTheFailurePath:
    def test_a_failed_write_rolls_the_entry_back_out(self, data_dir, monkeypatch):
        """Rule 6. Removing only the file would retire the path for good.

        The entry goes in before the file, so a write that fails leaves an
        entry the refusal honours forever. One transient error would then cost
        this vintage its name, and the repair is a hand edit to a manifest
        nothing else edits.
        """
        monkeypatch.setattr(
            vintage, "_write_new_file", lambda path, payload: (_ for _ in ()).throw(OSError("disk"))
        )
        with pytest.raises(OSError):
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert manifest_lines(data_dir) == []
        assert not (data_dir / RECORDED_NAME).exists()

        monkeypatch.undo()
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        assert entry.path == RECORDED_NAME

    def test_the_entry_is_written_before_the_file(self, data_dir, monkeypatch):
        """Rule 5. The order decides which state a crash leaves behind.

        A file with no entry is how an uncommitted download reaches a result,
        because `load_close` reads by filename and consults no manifest. An
        entry with no file is the state a verifier reports. The seam below is
        the moment between the two, and it is checked from inside the write.
        """
        seen = {}

        def fail_after_the_entry_landed(path, payload):
            seen["entries"] = manifest_lines(data_dir)
            seen["file_exists"] = path.exists()
            raise OSError("disk")

        monkeypatch.setattr(vintage, "_write_new_file", fail_after_the_entry_landed)
        with pytest.raises(OSError):
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert len(seen["entries"]) == 1
        assert json.loads(seen["entries"][0])["path"] == RECORDED_NAME
        assert seen["file_exists"] is False

    def test_a_file_that_does_not_match_its_entry_is_removed(self, data_dir, monkeypatch):
        """Rule 6. A short write ships a hash describing bytes never on disk."""
        monkeypatch.setattr(
            vintage, "_write_new_file", lambda path, payload: path.write_bytes(payload[:-5])
        )
        with pytest.raises(OSError, match="does not match"):
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert manifest_lines(data_dir) == []
        assert not (data_dir / RECORDED_NAME).exists()

    def test_the_write_itself_refuses_an_occupied_path(self, data_dir):
        """Rule 4. The refusal above returns before this, which is the point.

        Those checks are a look followed by a write, and `Path.exists` reports
        a file that cannot be opened as absent. This is the write refusing on
        its own, so the guard does not rest on the look being right.
        """
        occupied = data_dir / "already-here.csv"
        occupied.write_bytes(b"first\n")

        with pytest.raises(FileExistsError):
            vintage._write_new_file(occupied, b"second\n")

        assert occupied.read_bytes() == b"first\n"


class TestTheChecksumProjection:
    def test_the_projection_follows_the_manifest(self, data_dir):
        """One surface owns the hash, and `shasum -a 256 -c` keeps working."""
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert (data_dir / CHECKSUMS_NAME).read_text(encoding="utf-8") == (
            f"{entry.sha256}  {entry.path}\n"
        )

    def test_a_refused_record_leaves_the_projection_alone(self, data_dir):
        """It is regenerated after a vintage verifies, so a failure never touches it."""
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        before = (data_dir / CHECKSUMS_NAME).read_bytes()

        with pytest.raises(VintageRefused):
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert (data_dir / CHECKSUMS_NAME).read_bytes() == before


class TestTheCommittedManifest:
    """The eight vintages this repo ships, and the record that describes them.

    Nothing in this repo checked the committed bytes against a recorded hash
    before now. `data/README.md` documents `shasum -a 256 -c` for a person to
    run and no step or test ran it, so a file could change and every pinned
    number could go on reading as though it had not.
    """

    def test_every_entry_describes_the_file_it_names(self):
        for entry in read_manifest():
            raw = (DATA_DIR / entry.path).read_bytes()
            days = [
                line.split(",")[0]
                for line in raw.decode("utf-8").splitlines()
                if line[:4].isdigit()
            ]
            assert hashlib.sha256(raw).hexdigest() == entry.sha256, entry.path
            assert entry.row_count == len(days), entry.path
            assert (entry.first_date, entry.last_date) == (min(days), max(days)), entry.path

    def test_every_committed_series_has_exactly_one_entry(self):
        """A file with no entry is how an uncommitted download reaches a result."""
        recorded = [entry.path for entry in read_manifest()]
        on_disk = sorted(path.name for path in DATA_DIR.glob("*.csv"))

        assert sorted(recorded) == on_disk
        assert len(set(recorded)) == len(recorded)

    def test_the_committed_projection_is_the_one_the_manifest_produces(self):
        """Regenerating it is a no-op diff, which is what says it reproduces the record."""
        entries = sorted(read_manifest(), key=lambda entry: entry.path)
        expected = "".join(f"{entry.sha256}  {entry.path}\n" for entry in entries)

        assert (DATA_DIR / CHECKSUMS_NAME).read_text(encoding="utf-8") == expected

    def test_an_entry_carries_one_kind_of_date(self):
        """The four `*_chan.csv` files were saved, not downloaded.

        Their date is when Ernest Chan last saved the workbook a column was
        lifted from. A save date in a field named for a download is a wrong
        fact in the field that identifies the vintage, so those four carry
        their own field and the rest carry a download date.
        """
        by_path = {entry.path: entry for entry in read_manifest()}

        for name, entry in by_path.items():
            assert (entry.download_date is None) != (entry.saved_date is None), name
            assert (entry.saved_date is not None) == name.endswith("_chan.csv"), name

        with pytest.raises(ValueError, match="not both and not neither"):
            VintageEntry(
                vendor="yfinance",
                symbol="GDX",
                price_basis="raw",
                first_date="2026-08-25",
                last_date="2026-08-27",
                path="x.csv",
                row_count=3,
                sha256="0" * 64,
            )
