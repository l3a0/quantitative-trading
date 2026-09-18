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
from pathlib import Path

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
    write_checksums,
)

ROWS = [("2026-08-25", 50.0), ("2026-08-26", 51.25), ("2026-08-27", 52.0)]
SOURCE = dict(vendor="yfinance", symbol="GDX", price_basis="raw", download_date="2026-08-27")
RECORDED_NAME = "yfinance_gdx_raw_2026-08-25_2026-08-27_dl2026-08-27.csv"
RECORDED_ON_29 = "yfinance_gdx_raw_2026-08-25_2026-08-27_dl2026-08-29.csv"


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
            b"Date,Close\n2026-08-25,50.0\n2026-08-26,51.25\n2026-08-27,52.0\n"
        )

    def test_an_integer_close_is_written_as_a_float(self, data_dir):
        """One series handed in twice must hash the same, whatever the caller's types.

        `repr(50)` is `50` and `repr(50.0)` is `50.0`, so without the coercion a
        caller passing ints and a caller passing floats record the same series
        under two different digests.
        """
        entry = record_vintage([("2026-08-25", 50)], data_dir=data_dir, **SOURCE)

        assert (data_dir / entry.path).read_bytes() == b"Date,Close\n2026-08-25,50.0\n"

    def test_the_header_does_not_borrow_one_vendor_s_shape(self, data_dir):
        """The eight committed vintages carry yfinance's three-row header.

        Writing that shape for every vendor would put `Price,Close` and a
        `Ticker` row at the top of a series no vendor of that name returned,
        which is a claim the file has no business making. `load_close` drops
        every leading row whose first field is not a date, so it reads either
        shape, and `data/README.md` describes both.
        """
        entry = record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        written = (data_dir / entry.path).read_text(encoding="utf-8").splitlines()
        committed = (DATA_DIR / "gdx_20yr_prices.csv").read_text(encoding="utf-8").splitlines()
        assert written[0] == "Date,Close"
        assert committed[:3] == ["Price,Close", "Ticker,GDX", "Date,"]

    def test_the_manifest_keeps_the_order_entries_were_written_in(self, data_dir):
        """`read_manifest` promises write order, and the rollback rewrites the file."""
        first = record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        second = record_vintage(
            [("2026-01-05", 9.0)], data_dir=data_dir, **{**SOURCE, "download_date": "2026-01-06"}
        )

        assert [entry.path for entry in read_manifest(data_dir)] == [first.path, second.path]

    def test_a_line_that_will_not_parse_names_itself(self, data_dir):
        """A manifest is read to find out what went wrong, so it says which line."""
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        manifest.write_text(manifest.read_text() + "{not json}\n", encoding="utf-8")

        with pytest.raises(ValueError, match="line 2"):
            read_manifest(data_dir)

    def test_an_appended_entry_cannot_be_glued_to_the_line_above(self, data_dir):
        """A manifest whose last line lost its newline would otherwise lose two entries.

        The append would run the new object onto the end of the old one, and
        nothing could read the file afterwards, including the rollback that
        would have undone it.
        """
        first = record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        manifest.write_text(manifest.read_text().rstrip("\n"), encoding="utf-8")

        second = record_vintage(
            [("2026-01-05", 9.0)], data_dir=data_dir, **{**SOURCE, "download_date": "2026-01-06"}
        )

        assert [entry.path for entry in read_manifest(data_dir)] == [first.path, second.path]

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

    def test_a_symbol_is_normalised_and_a_path_separator_is_refused(self, data_dir):
        """The name joins five fields with underscores, so no field may hold one.

        Beyond that the rule is deliberately wide. A leading caret is how every
        index is written and an equals sign is how futures and currency pairs
        are, and refusing those would refuse vintages this repo will want.
        """
        entry = record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "symbol": "gdx"})
        assert entry.symbol == "GDX"

        for refused in ["A_B", "A/B", "-X", ""]:
            with pytest.raises(ValueError, match="symbol"):
                record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "symbol": refused})

        for accepted in ["^GSPC", "ES=F", "BRK.B", "BTC-USD"]:
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "symbol": accepted})

    def test_a_vendor_is_lowered_and_an_underscore_is_refused(self, data_dir):
        """Refusing `FRED` outright would be a spelling rule pretending to be a path rule."""
        entry = record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "vendor": "FRED"})
        assert entry.vendor == "fred"

        with pytest.raises(ValueError, match="vendor"):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "vendor": "alpha_vantage"})

    def test_a_date_that_no_calendar_carries_is_refused(self, data_dir):
        """The shape of a date is not the same question as whether the day exists.

        A regex passes `2026-02-31` and `2026-99-99`, and both would reach the
        manifest as a span and a filename nothing could ever match.
        """
        with pytest.raises(ValueError, match="row date"):
            record_vintage([("2026-02-31", 1.0)], data_dir=data_dir, **SOURCE)

        with pytest.raises(ValueError, match="download date"):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "download_date": "2026-99-99"})

        assert manifest_lines(data_dir) == []

    def test_the_writer_checks_its_date_before_it_builds_anything(self, data_dir):
        """The reader's guard catches the same date later and in worse words.

        `record_vintage` validates its download date first, then builds a
        filename, then reads the manifest. `VintageEntry` now refuses the same
        value, which makes the writer's own call look redundant to whoever
        reads the two together. Deleting it costs two messages.

        1. The refusal names `..._dlbanana.csv`, a path that never existed.
        2. Against a directory with no manifest, the read runs first and the
           refusal reports a missing manifest rather than a bad date, which is
           the conflation `read_manifest`'s own docstring exists to stop.

        Both assertions anchor at the start of the message, because the
        reader's guard prefixes the entry's path and the writer's does not.
        """
        with pytest.raises(ValueError, match=r"^download date 'banana' is not"):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "download_date": "banana"})

        unrecorded = data_dir / "no-manifest-here"
        unrecorded.mkdir()

        with pytest.raises(ValueError, match=r"^download date 'banana' is not"):
            record_vintage(ROWS, data_dir=unrecorded, **{**SOURCE, "download_date": "banana"})

        assert manifest_lines(data_dir) == []

    def test_a_date_the_writer_would_refuse_is_refused_on_the_way_back(self, data_dir):
        """The manifest is the record, so a line's date is not taken on trust.

        `record_vintage` ran its date through the same check and `read_manifest`
        ran nothing, so a hand-edited or badly-merged line carried a date the
        writer would have refused. Every value below is one the writer refuses.
        Two of them, `2026-02-31` and `2026-13-01`, clear the shape check and
        are caught by the calendar behind it, which is why `_validated_date`
        has two halves.

        The bad line is written rather than placed through a helper, because a
        helper builds the entry first and the guard would refuse it there,
        which tests nothing about reading. It is the second line, so the refusal
        is shown naming the line it came from rather than the only one there is.
        """
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        good = manifest_lines(data_dir)[0]
        recorded = json.loads(good)
        refused = ["", " 2026-08-27 ", "banana", "2026-1-3", "2026-02-31", "2026-13-01", 20260827]

        for field in ["download_date", "saved_date"]:
            for value in refused:
                line = {key: held for key, held in recorded.items() if key != "download_date"}
                line[field] = value
                manifest.write_text(f"{good}\n{json.dumps(line)}\n", encoding="utf-8")

                with pytest.raises(ValueError, match="line 2"):
                    read_manifest(data_dir)

        # The same second line with a date the writer would have written, so the
        # refusals above are the date's doing rather than the line's shape.
        readable = {key: held for key, held in recorded.items() if key != "download_date"}
        readable["saved_date"] = "2026-08-27"
        manifest.write_text(f"{good}\n{json.dumps(readable)}\n", encoding="utf-8")

        assert [entry.obtained for entry in read_manifest(data_dir)] == ["2026-08-27"] * 2

    def test_a_close_that_is_not_a_finite_number_is_refused(self, data_dir):
        """A vendor value too large to parse arrives as an infinity, not as an error.

        `float("1e400")` is `inf`, and freezing that into a vintage records an
        artifact of parsing as a price, with a checksum that will verify it
        happily for the rest of its life.
        """
        for close in [float("nan"), float("inf"), "1e400", None, "n/a"]:
            with pytest.raises(ValueError, match="close on"):
                record_vintage([("2026-08-25", close)], data_dir=data_dir, **SOURCE)

        assert manifest_lines(data_dir) == []

    def test_a_manifest_that_cannot_be_read_is_not_reported_as_absent(self, tmp_path):
        """Absent and unreadable are different problems with different fixes.

        `Path.is_file` is False for both, so the obvious check sends a reader
        looking for a missing file when the path is occupied by something else.
        """
        (tmp_path / MANIFEST_NAME).mkdir()

        with pytest.raises(OSError) as unreadable:
            read_manifest(tmp_path)
        assert not isinstance(unreadable.value, FileNotFoundError)
        assert "not a readable file" in str(unreadable.value)

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
        because nothing resolves it and nothing therefore verifies it. An entry
        with no file is the state `chan.vintage.read_vintage` reports, naming
        the vintage whose record outlived its series. The seam below is the
        moment between the two, and it is checked from inside the write.
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

    def test_an_interrupt_rolls_back_like_any_other_failure(self, data_dir):
        """The catch is `BaseException` because the danger is not only an `OSError`.

        A keyboard interrupt between the entry and the file leaves exactly the
        orphan the write order exists to prevent, and it is the one failure a
        person is most likely to cause by hand.
        """

        def interrupted(path, payload):
            raise KeyboardInterrupt

        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(vintage, "_write_new_file", interrupted)
        with pytest.raises(KeyboardInterrupt):
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        monkeypatch.undo()

        assert manifest_lines(data_dir) == []

    def test_a_rollback_leaves_earlier_entries_alone(self, data_dir, monkeypatch):
        """The rollback replaces the whole manifest, so it can take the wrong line.

        Two downloads of one span share a sha256 and differ only in their
        download date and path, which the suite asserts elsewhere. A rollback
        comparing on any single field would drop the earlier vintage and leave
        its file on disk with no entry, which is the state this module exists
        to prevent.
        """
        kept = record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        monkeypatch.setattr(
            vintage, "_write_new_file", lambda path, payload: (_ for _ in ()).throw(OSError("disk"))
        )
        with pytest.raises(OSError):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "download_date": "2026-08-29"})

        assert [entry.path for entry in read_manifest(data_dir)] == [kept.path]
        assert (data_dir / kept.path).exists()

    def test_a_rollback_leaves_the_projection_describing_what_is_there(self, data_dir):
        """A projection written before the file survives a rollback and names a ghost.

        `shasum -a 256 -c` then fails forever on a line for a vintage that was
        never recorded, which reads as corruption rather than as a failed run.
        """
        kept = record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            vintage, "_write_new_file", lambda path, payload: (_ for _ in ()).throw(OSError("disk"))
        )
        with pytest.raises(OSError):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "download_date": "2026-08-29"})
        monkeypatch.undo()

        assert (data_dir / CHECKSUMS_NAME).read_text(encoding="utf-8") == (
            f"{kept.sha256}  {kept.path}\n"
        )

    def test_losing_the_path_to_another_writer_destroys_nothing(self, data_dir, monkeypatch):
        """The refusal asks `Path.exists` and the write asks the filesystem.

        Those disagree on a dangling symlink, and they disagree whenever
        anything lands in between. The exclusive create is what decides, and
        losing to it must not delete whatever won, because that file is not
        something this repo can recapture.
        """
        real_write = vintage._write_new_file

        def someone_else_gets_there_first(path, payload):
            path.write_bytes(b"not ours\n")
            return real_write(path, payload)

        monkeypatch.setattr(vintage, "_write_new_file", someone_else_gets_there_first)
        with pytest.raises(VintageRefused, match="taken before the write"):
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert (data_dir / RECORDED_NAME).read_bytes() == b"not ours\n"
        assert manifest_lines(data_dir) == []

    def test_the_rollback_swaps_a_new_manifest_in_rather_than_truncating_the_old(
        self, data_dir, monkeypatch
    ):
        """The rollback is the only write that replaces the manifest instead of appending.

        Writing it in place would truncate the record first and refill it
        second, so a failure between those two loses every entry rather than
        the one being undone. The temporary file and the rename are what make
        the manifest go from its old contents to its new ones with nothing in
        between, and this is the case that says so.
        """
        kept = record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        seen = {}
        swap = Path.replace

        def watched(source, target):
            seen["manifest_before_the_swap"] = Path(target).read_bytes()
            return swap(source, target)

        monkeypatch.setattr(Path, "replace", watched)
        monkeypatch.setattr(
            vintage, "_write_new_file", lambda path, payload: (_ for _ in ()).throw(OSError("disk"))
        )
        with pytest.raises(OSError):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "download_date": "2026-08-29"})

        # Read at the instant of the rename, the old manifest is whole: both
        # entries, every line parsing. A rewrite in place would be empty here,
        # and a rewrite with no rename would never reach this at all.
        standing = seen["manifest_before_the_swap"].decode("utf-8").splitlines()
        assert [json.loads(line)["path"] for line in standing] == [kept.path, RECORDED_ON_29]
        assert [entry.path for entry in read_manifest(data_dir)] == [kept.path]

    def test_a_projection_that_cannot_be_written_does_not_undo_the_vintage(self, data_dir):
        """Once the file verifies the record is true, and nothing undoes a true record.

        The projection is regenerable and the vintage is not. A caller told the
        record failed would rerun and meet a refusal that reads as a duplicate
        download rather than as stale checksums.
        """
        (data_dir / CHECKSUMS_NAME).mkdir()

        with pytest.raises(OSError, match="is recorded and verified"):
            record_vintage(ROWS, data_dir=data_dir, **SOURCE)

        assert len(read_manifest(data_dir)) == 1
        assert (data_dir / RECORDED_NAME).exists()


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

    def test_every_entry_names_the_series_its_file_actually_holds(self):
        """The hash, the row count and the span say nothing about which series it is.

        All three would pass with the vendor, the symbol and the price basis
        swapped, and those are the three fields that say what a reader is
        looking at. The symbol is recoverable from the file, because every
        committed vintage carries yfinance's `Ticker,` header row, so it is
        derived rather than restated.
        """
        for entry in read_manifest():
            header = (DATA_DIR / entry.path).read_text(encoding="utf-8").splitlines()[1]
            assert header == f"Ticker,{entry.symbol}", entry.path

    def test_the_identity_of_all_eight_is_pinned(self):
        """Nothing in the bytes says which vendor sent a file or on what day.

        The backfill is committed data with no generator, so a hand edit to any
        of these is a hand edit to the record. This is the assertion that makes
        one fail.
        """
        assert {
            (e.path, e.vendor, e.symbol, e.price_basis, e.download_date, e.saved_date)
            for e in read_manifest()
        } == {
            ("gld_20yr_prices.csv", "yfinance", "GLD", "adjusted", "2026-06-16", None),
            ("gld_20yr_prices_unadjusted.csv", "yfinance", "GLD", "raw", "2026-08-27", None),
            ("gdx_20yr_prices.csv", "yfinance", "GDX", "adjusted", "2026-08-27", None),
            ("gdx_20yr_prices_unadjusted.csv", "yfinance", "GDX", "raw", "2026-08-27", None),
            ("gld_chan.csv", "chan-xls", "GLD", "adjusted", None, "2007-12-02"),
            ("gdx_chan.csv", "chan-xls", "GDX", "adjusted", None, "2007-12-02"),
            ("ko_chan.csv", "chan-xls", "KO", "adjusted", None, "2008-01-23"),
            ("pep_chan.csv", "chan-xls", "PEP", "adjusted", None, "2008-01-23"),
        }

    def test_every_committed_line_is_the_one_its_entry_would_write(self):
        """A line's text is decided by the entry, not by how it was typed.

        Without sorted keys a hand-written line and a recorded one differ in
        field order while carrying the same nine values, and the manifest stops
        being a file a diff can be read against.
        """
        lines = (DATA_DIR / MANIFEST_NAME).read_text(encoding="utf-8").splitlines()

        assert [json.loads(line) for line in lines]
        for line in lines:
            assert VintageEntry(**json.loads(line)).as_json() == line

    def test_the_projection_regenerates_over_the_committed_manifest(self, tmp_path):
        """Running it over the eight reproduces the file that was kept by hand.

        That is what says the projection took the record over rather than
        replaced it, and it is the only case that exercises the ordering, since
        every other one writes a single entry.
        """
        (tmp_path / MANIFEST_NAME).write_bytes((DATA_DIR / MANIFEST_NAME).read_bytes())

        write_checksums(tmp_path)

        assert (tmp_path / CHECKSUMS_NAME).read_bytes() == (DATA_DIR / CHECKSUMS_NAME).read_bytes()

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

        shared = dict(
            vendor="yfinance",
            symbol="GDX",
            price_basis="raw",
            first_date="2026-08-25",
            last_date="2026-08-27",
            path="x.csv",
            row_count=3,
            sha256="0" * 64,
        )
        with pytest.raises(ValueError, match="not both and not neither"):
            VintageEntry(**shared)
        with pytest.raises(ValueError, match="not both and not neither"):
            VintageEntry(**shared, download_date="2026-08-27", saved_date="2026-08-27")
