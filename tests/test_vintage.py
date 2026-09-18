"""What the vintage recorder must do, and what it must refuse.

Every case here is driven by a synthetic series, because the recorder takes
rows rather than fetching them. Nothing in this file touches a network, and
nothing writes into the committed ``data/`` directory. The last two classes
read it. ``TestTheCommittedManifest`` checks the manifest still describes the
eight vintages this repo ships, and ``TestARecordedVintageIsHeldToo`` copies
the tree, records a ninth into the copy and runs the assertions issue 51
scoped against a directory that has one.

The order the cases appear in is the order the rules appear on
[issue 1](https://github.com/l3a0/quantitative-trading/issues/1).
"""

import hashlib
import json
import sys
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
    vintage_filename,
    write_checksums,
)
from tests.support.committed_vintages import (
    BACKFILLED,
    committed_copy,
    identity_of,
    rewrite_entry,
)

ROWS = [("2026-08-25", 50.0), ("2026-08-26", 51.25), ("2026-08-27", 52.0)]
SOURCE = dict(vendor="yfinance", symbol="GDX", price_basis="raw", download_date="2026-08-27")
RECORDED_NAME = "yfinance_gdx_raw_2026-08-25_2026-08-27_dl2026-08-27.csv"
RECORDED_ON_29 = "yfinance_gdx_raw_2026-08-25_2026-08-27_dl2026-08-29.csv"
NINTH_NAME = "yfinance_zzz_adjusted_2026-08-25_2026-08-27_dl2026-09-17.csv"


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

    def test_a_line_that_will_not_parse_names_itself_and_holds_one_line_number(self, data_dir):
        """A manifest is read to find out what went wrong, so it says which line.

        And which column, without a second line number beside the first.
        `json` is handed one line at a time, so its own message ends in
        "line 1 column 2 (char 1)" however far down the manifest the line sits.
        Concatenating that would put two numbers meaning two different things
        in one message, and the manifest's is the one an operator needs.
        `JSONDecodeError` carries `msg` and `colno` separately, which gives the
        column without the line.
        """
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        manifest.write_text(manifest.read_text() + "{not json}\n", encoding="utf-8")
        try:
            json.loads("{not json}")
        except json.JSONDecodeError as unparsed:
            said = unparsed.msg

        with pytest.raises(ValueError) as refused:
            read_manifest(data_dir)

        # The parser's own words, read off `json` here rather than written out,
        # so this holds that they are carried without pinning CPython's
        # wording. Asserting only the prefix and the column left the reason
        # free to go missing again, which is the defect this change exists to
        # end.
        assert f"line 2 is not a vintage entry: it is not JSON: {said!r} at column 2" in str(
            refused.value
        )
        assert "line 1" not in str(refused.value)

    def test_a_parser_message_that_ends_mid_phrase_still_reads_as_a_sentence(self, data_dir):
        """Several of CPython's own messages are finished by the position text.

        `Unterminated string starting at` is one, and the position text is the
        half dropped here, because it carries a line number that would sit
        beside the manifest's meaning something else. Quoting what `json` said
        is what keeps the fragment reading as the parser's sentence rather than
        dangling into this module's.
        """
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        good = manifest_lines(data_dir)[0]
        broken = '{"vendor": "yfinance'
        try:
            json.loads(broken)
        except json.JSONDecodeError as unparsed:
            said = unparsed.msg
        assert said.endswith(" at"), "this test is pointless if CPython stopped dangling"
        manifest.write_text(f"{good}\n{broken}\n", encoding="utf-8")

        with pytest.raises(ValueError) as refused:
            read_manifest(data_dir)

        assert f"it is not JSON: {said!r} at column" in str(refused.value)

    def test_a_refused_line_carries_the_reason_it_was_refused(self, data_dir):
        """A line number says which line and not what, and the fixes differ.

        The funnel dropped eight causes into one message, so a date a hand edit
        broke, a key a hand edit dropped and a line that is not JSON all
        reached an operator as the same sentence. The reason arrives in three
        shapes and one message shape has to hold all three.

        1. What `__post_init__` raises already names the entry's own path and
           the value, so it carries through as it stands.
        2. What `json` raises is checked in the test above, which owns the
           collision between its line number and the manifest's. It appears
           here only to show one message shape holding all three.
        3. What Python raises describes `VintageEntry.__init__` rather than the
           manifest, and names only the first key it does not recognise, so
           this is the shape that is restated. Its three sub-cases all arrive
           as a bare `TypeError` that only the message string tells apart,
           which is why the shape is decided from the parsed object instead.

        Asserted as substrings rather than through `pytest.raises(match=...)`,
        which takes a regex and no test in this suite calls `re.escape`. Every
        fragment below holds a committed-style path, so the dot before `csv`
        would read as any character and quietly weaken the assertion that is
        written on the page.
        """
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        good = manifest_lines(data_dir)[0]
        recorded = json.loads(good)

        def without(*keys):
            return {key: held for key, held in recorded.items() if key not in keys}

        refused = [
            (
                {**recorded, "saved_date": "2026-08-27"},
                f"{RECORDED_NAME}: an entry carries a download date or a saved date, not both "
                f"and not neither",
            ),
            (
                {**recorded, "download_date": "2026-02-30"},
                f"{RECORDED_NAME}: download date '2026-02-30' is not a day that exists",
            ),
            ([recorded], "an entry's fields are a JSON object, and this line is a JSON array"),
            ("a.csv", "an entry's fields are a JSON object, and this line is a JSON string"),
            (7, "an entry's fields are a JSON object, and this line is a JSON number"),
            (7.5, "an entry's fields are a JSON object, and this line is a JSON number"),
            (True, "an entry's fields are a JSON object, and this line is a JSON boolean"),
            (None, "an entry's fields are a JSON object, and this line is the JSON literal null"),
            (without("symbol", "sha256"), "it does not carry 'sha256', 'symbol'"),
            # Two of them, because Python names one. A hand edit that misspells
            # a key produces one of each at once, so both halves are said.
            ({**recorded, "extra": 1, "also": 2}, "an entry has no field named 'also', 'extra'"),
            (
                {**without("symbol"), "also": 2, "extra": 1},
                "it does not carry 'symbol' and an entry has no field named 'also', 'extra'",
            ),
        ]

        for line, reason in refused:
            manifest.write_text(f"{good}\n{json.dumps(line)}\n", encoding="utf-8")

            with pytest.raises(ValueError) as caught:
                read_manifest(data_dir)

            assert f"line 2 is not a vintage entry: {reason}" in str(caught.value)

        manifest.write_text(f"{good}\n{{not json}}\n", encoding="utf-8")

        with pytest.raises(ValueError) as caught:
            read_manifest(data_dir)

        assert "line 2 is not a vintage entry: it is not JSON: " in str(caught.value)

    def test_a_key_a_line_carries_cannot_forge_the_message(self, data_dir):
        """An unknown key is printed, and it is the line that decides what it says.

        The reason is the first thing to put a field a manifest controls into
        an operator's terminal, so a key holding a newline would print further
        lines reading as this module's own words. Quoting it is what keeps the
        refusal one line. The eight sites that print a path have the same
        defect and are
        [issue 99](https://github.com/l3a0/quantitative-trading/issues/99),
        which this must not add a ninth to.
        """
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        good = manifest_lines(data_dir)[0]
        forged = "x\nno vintage is missing, this run is fine"
        line = json.dumps({**json.loads(good), forged: 1})
        manifest.write_text(f"{good}\n{line}\n", encoding="utf-8")

        with pytest.raises(ValueError) as caught:
            read_manifest(data_dir)

        assert len(str(caught.value).splitlines()) == 1
        assert "no vintage is missing" not in str(caught.value).splitlines()[0].split("named ")[0]
        assert repr(forged) in str(caught.value)

    def test_a_number_json_will_not_build_still_names_its_line(self, data_dir):
        """`json.loads` raises more than `JSONDecodeError`, and the funnel takes both.

        A JSON integer literal longer than `sys.get_int_max_str_digits` raises
        a bare `ValueError` out of `int`. Catching only the subclass sent that
        to an operator as a CPython message naming no manifest, no line and no
        field, which is what this whole refusal exists to stop.
        """
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        good = manifest_lines(data_dir)[0]
        huge = "9" * (sys.get_int_max_str_digits() + 100)
        manifest.write_text(f'{good}\n{{"row_count": {huge}}}\n', encoding="utf-8")

        with pytest.raises(ValueError) as caught:
            read_manifest(data_dir)

        assert "line 2 is not a vintage entry: it is not JSON: " in str(caught.value)
        assert "integer string conversion" in str(caught.value)

    def test_neither_date_field_is_required_on_its_own(self, data_dir):
        """The shape check asks for eight fields, and the two dates are not among them.

        `__post_init__` takes exactly one of `download_date` and `saved_date`,
        so a plain difference against every declared field would report both as
        missing on every valid line, including the eight committed ones. The
        line that carries neither still refuses, and it refuses for the reason
        `__post_init__` gives rather than for a shape the check invented.
        """
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        good = manifest_lines(data_dir)[0]
        recorded = json.loads(good)
        neither = {key: held for key, held in recorded.items() if key != "download_date"}
        manifest.write_text(f"{good}\n{json.dumps(neither)}\n", encoding="utf-8")

        with pytest.raises(ValueError) as caught:
            read_manifest(data_dir)

        assert "does not carry" not in str(caught.value)
        assert "not both and not neither" in str(caught.value)

        saved = {**neither, "saved_date": "2026-08-27"}
        manifest.write_text(f"{good}\n{json.dumps(saved)}\n", encoding="utf-8")

        assert [entry.obtained_verb for entry in read_manifest(data_dir)] == [
            "downloaded",
            "saved",
        ]

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

    def test_the_writer_checks_its_input_before_it_builds_anything(self, data_dir):
        """The reader's guard catches the same values later and in worse words.

        `record_vintage` validates its own arguments first, then builds a
        filename, then reads the manifest. `VintageEntry` now refuses the same
        values, which makes the writer's own calls look redundant to whoever
        reads the two together. Deleting either costs two messages.

        1. The refusal names `..._dlbanana.csv`, a path that never existed.
        2. Against a directory with no manifest, the read runs first and the
           refusal reports a missing manifest rather than a bad value, which is
           the conflation `read_manifest`'s own docstring exists to stop.

        The price basis is pinned here as well as in
        `test_an_unknown_price_basis_is_refused`, which is the test that reads
        as owning it. The guard raises that test's sentence from
        `__post_init__` too, and that test matches it unanchored, so it cannot
        tell which of the two sites raised. Deleting the writer's
        `_validated_identity` call leaves it green.

        The assertions anchor at the start of the message, because the reader's
        guard prefixes the entry's path and the writer's does not.
        """
        with pytest.raises(ValueError, match=r"^download date 'banana' is not"):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "download_date": "banana"})

        with pytest.raises(ValueError, match=r"^price basis 'unadjusted' is not"):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "price_basis": "unadjusted"})

        unrecorded = data_dir / "no-manifest-here"
        unrecorded.mkdir()

        with pytest.raises(ValueError, match=r"^download date 'banana' is not"):
            record_vintage(ROWS, data_dir=unrecorded, **{**SOURCE, "download_date": "banana"})

        with pytest.raises(ValueError, match=r"^price basis 'unadjusted' is not"):
            record_vintage(ROWS, data_dir=unrecorded, **{**SOURCE, "price_basis": "unadjusted"})

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
        # Which half of `_validated_date` each value is expected to reach. The
        # calendar half was held by no test in this repo before this one: it
        # could be reworded to anything and the suite stayed green, because
        # every assertion stopped at the line number.
        no_such_day = {"2026-02-31", "2026-13-01"}

        for field in ["download_date", "saved_date"]:
            for value in refused:
                line = {key: held for key, held in recorded.items() if key != "download_date"}
                line[field] = value
                manifest.write_text(f"{good}\n{json.dumps(line)}\n", encoding="utf-8")

                with pytest.raises(ValueError) as caught:
                    read_manifest(data_dir)

                half = (
                    "is not a day that exists"
                    if value in no_such_day
                    else "is not an ISO calendar date"
                )
                # `download_date` names itself "download date" in the refusal,
                # which is how the message says which of the two fields it read.
                named = f"{RECORDED_NAME}: {field.replace('_', ' ')}"
                assert f"line 2 is not a vintage entry: {named} {value!r} {half}" in str(
                    caught.value
                )

        # The same second line with a date the writer would have written, so the
        # refusals above are the date's doing rather than the line's shape.
        readable = {key: held for key, held in recorded.items() if key != "download_date"}
        readable["saved_date"] = "2026-08-27"
        manifest.write_text(f"{good}\n{json.dumps(readable)}\n", encoding="utf-8")

        assert [entry.obtained for entry in read_manifest(data_dir)] == ["2026-08-27"] * 2

    def test_an_identity_the_writer_would_not_have_written_is_refused_on_the_way_back(
        self, data_dir
    ):
        """`resolve_vintage` matches three fields as strings, so a spelling is the record.

        A misspelled field is worse than a missing line. Deleting an entry
        leaves its file named by nothing, so the no-match refusal lists the file
        and says to go look. A line spelling the vendor `Yfinance` still names
        its own path, so before this guard the reader answered that no such
        vintage was committed and listed nothing as unrecorded, which is a wrong
        fact rather than a stopped run.

        Three classes are driven, because a guard holding one accepts the
        others. `Yfinance` and `gdx` are the ones that matter most: the
        validator accepts both and rewrites them, so a guard calling it for its
        refusals alone lets them through. What refuses them is comparing the
        triple it returns against the triple the line holds. `Raw` and
        `unadjusted` are refused outright, and the rest are what the writer's
        two patterns and its type check refuse.

        Each case is pinned on the cause rather than on `read_manifest`'s own
        message, because the cause is what says which field was wrong and both
        spellings, and it is what [issue
        85](https://github.com/l3a0/quantitative-trading/issues/85) will carry
        out to an operator. The vendor cases also pin that a refusal quotes the
        line's own spelling, since lowering before matching would report
        `'yahoo finance'` for a line nothing in the manifest spells that way.
        The last case differs in two fields at once, which is what a badly
        merged line looks like, and it holds the message naming both rather
        than the first.

        The bad line is written rather than placed through a helper, because a
        helper builds the entry first and the guard would refuse it there,
        which tests nothing about reading. It is the second line, so the refusal
        is shown naming the line it came from rather than the only one there is.
        """
        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        manifest = data_dir / MANIFEST_NAME
        good = manifest_lines(data_dir)[0]
        recorded = json.loads(good)
        refused = [
            ("vendor", "Yfinance", "vendor reads 'Yfinance' and the recorder writes 'yfinance'"),
            ("symbol", "gdx", "symbol reads 'gdx' and the recorder writes 'GDX'"),
            ("price_basis", "Raw", "price basis 'Raw' is not one of"),
            ("price_basis", "unadjusted", "price basis 'unadjusted' is not one of"),
            ("vendor", "Yahoo Finance", "vendor 'Yahoo Finance' carries a character"),
            ("vendor", "alpha_vantage", "vendor 'alpha_vantage' carries a character"),
            ("symbol", "A/B", "symbol 'A/B' carries a character"),
            ("symbol", "", "symbol '' carries a character"),
            ("vendor", ["yfinance"], "vendor and symbol are strings, not <class 'list'>"),
            (
                "symbol",
                {"a": 1},
                "vendor and symbol are strings, not <class 'str'> and <class 'dict'>",
            ),
            ("price_basis", 7, "price basis 7 is not one of"),
        ]

        for field, value, says in refused:
            line = json.dumps({**recorded, field: value})
            manifest.write_text(f"{good}\n{line}\n", encoding="utf-8")

            with pytest.raises(ValueError, match="line 2") as refusal:
                read_manifest(data_dir)
            assert f"{RECORDED_NAME}: {says}" in str(refusal.value.__cause__)

        both = json.dumps({**recorded, "vendor": "Yfinance", "symbol": "gdx"})
        manifest.write_text(f"{good}\n{both}\n", encoding="utf-8")

        with pytest.raises(ValueError, match="line 2") as refusal:
            read_manifest(data_dir)
        said = str(refusal.value.__cause__)
        assert "vendor reads 'Yfinance' and the recorder writes 'yfinance'" in said
        assert "symbol reads 'gdx' and the recorder writes 'GDX'" in said

        # The same second line rewritten to a spelling the writer would have
        # produced, so the refusals above are the identity field's doing rather
        # than the line's shape. A different vendor rather than the one already
        # there, which is what says the line was rewritten at all.
        manifest.write_text(
            f"{good}\n{json.dumps({**recorded, 'vendor': 'fred'})}\n", encoding="utf-8"
        )

        assert [entry.vendor for entry in read_manifest(data_dir)] == ["yfinance", "fred"]

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


class TestTheBytesEveryWriteProduces:
    """Every file the recorder writes, held to the bytes the code built.

    Python's text mode writes ``os.linesep`` for every newline when no
    ``newline`` argument is given, and that is CRLF on Windows. No runner this
    suite meets writes CRLF, so the case forces the same translation through
    the same code path rather than waiting for a Windows runner. That is the
    writer side of what `tests/test_checkout_bytes.py` asks of a checkout.
    """

    def test_no_write_translates_a_newline(self, data_dir, tmp_path_factory, monkeypatch):
        """Both write surfaces are patched, and a control says the patches are live.

        A test that patches a translating write in and then finds no carriage
        return passes just as well when the patch never took hold, so three
        writes performed here go through those same patches, and the case
        asserts each one comes out CRLF. They land in their own directory,
        because the sweep below reports every file the recorder left behind
        rather than three names, which covers a fourth write without anyone
        remembering it.

        `pathlib.Path.open` is the second surface rather than
        `pathlib.Path.write_text`, because `write_text` opens the file through
        it. Patching the narrower one holds both spellings, and a write spelled
        `manifest.open("a", encoding="utf-8")` would otherwise translate with
        nothing here reporting it.
        """
        real_open = open
        real_path_open = Path.open

        # A read is left alone. `Path.read_text` opens through the same method,
        # and forcing a terminator on it would change what the reader sees
        # rather than what a writer produces.
        def translated(mode, newline):
            # `newline=""` is falsy, so the comparison is against None. A
            # `newline or "\r\n"` here would override the very argument a fix
            # passes and make this case unable to see it.
            writing = any(character in mode for character in "wax+")
            return writing and "b" not in mode and newline is None

        def translating_open(file, mode="r", *arguments, **keywords):
            if translated(mode, keywords.get("newline")):
                keywords["newline"] = "\r\n"
            return real_open(file, mode, *arguments, **keywords)

        def translating_path_open(self, mode="r", *arguments, **keywords):
            if translated(mode, keywords.get("newline")):
                keywords["newline"] = "\r\n"
            return real_path_open(self, mode, *arguments, **keywords)

        monkeypatch.setattr(vintage, "open", translating_open, raising=False)
        monkeypatch.setattr(Path, "open", translating_path_open)

        control = tmp_path_factory.mktemp("translating-writes")
        with vintage.open(control / "builtin.txt", "w", encoding="utf-8") as handle:
            handle.write("line\n")
        with (control / "method.txt").open("w", encoding="utf-8") as handle:
            handle.write("line\n")
        (control / "written.txt").write_text("line\n", encoding="utf-8")
        untranslated = sorted(
            path.name for path in control.iterdir() if b"\r\n" not in path.read_bytes()
        )
        assert not untranslated, (
            f"the patched writes left {', '.join(untranslated)} alone, so a text-mode "
            f"write is no longer reaching them and the sweep below asserts nothing. "
            f"Either chan.vintage stopped calling the builtin open, or pathlib.Path.open "
            f"is no longer what Path.write_text and Path.open both go through."
        )

        def assert_untranslated(stage):
            # Every file under the directory rather than its own children, so a
            # write into a subdirectory is reported by name. A directory is
            # skipped, because it has no bytes to read and naming one would
            # report a file nothing wrote.
            translated_files = sorted(
                str(path.relative_to(data_dir))
                for path in data_dir.rglob("*")
                if path.is_file() and b"\r" in path.read_bytes()
            )
            assert not translated_files, (
                f"{', '.join(translated_files)} came out of {stage} carrying a carriage "
                f"return. Python's text mode writes os.linesep for every newline when a "
                f"file is opened with no newline argument, and os.linesep is CRLF on "
                f"Windows. Every write in chan.vintage takes bytes so the file holds what "
                f"the code built, and putting a text-mode write back undoes that."
            )

        record_vintage(ROWS, data_dir=data_dir, **SOURCE)
        # Checked here rather than at the end, because the rollback below
        # replaces the whole manifest and would hide a translating append.
        assert_untranslated("recording a vintage")

        monkeypatch.setattr(
            vintage, "_write_new_file", lambda path, payload: (_ for _ in ()).throw(OSError("disk"))
        )
        with pytest.raises(OSError):
            record_vintage(ROWS, data_dir=data_dir, **{**SOURCE, "download_date": "2026-08-29"})

        assert_untranslated("rolling a failed record back out")


# The three assertions below take a directory rather than reading `DATA_DIR`
# through a name bound at import. Issue 51's first completion condition is that
# a recorded ninth vintage leaves the suite green, and a name bound at import
# cannot be redirected, so the condition had no mechanical check. A directory
# argument gives it one: `TestARecordedVintageIsHeldToo` copies the committed
# tree, records into the copy and runs all three against it. That is the same
# choice issue 1 made for the recorder and `tests/test_series.py` made for the
# reader, both under the rule that a test must not write into `data/`.


def the_backfill_identity_is_pinned(directory: Path) -> None:
    """The eight entries that predate the recorder carry the identity they were given.

    Nothing in the bytes says which vendor sent a file or on what day, and the
    backfill is committed data with no generator, so a hand edit to any of
    these is a hand edit to the record. This is the assertion that makes one
    fail.

    Held by path rather than by set equality over the whole manifest, which is
    what lets a recorded vintage sit beside the eight. Name what that gives up,
    and name it accurately, because the first draft of this paragraph claimed
    more than the code does.

    Set equality failed on any ninth entry at all, a forged one included, for
    the same reason it failed on a recorded one: it enumerated eight. Keying on
    paths gives that up entirely. A hand-written entry that brings its own
    file, hashes it correctly and takes the name its own fields produce passes
    every assertion here, measured. That is not a hole that can be closed. Such
    an entry is byte for byte what the recorder would have written, so no test
    can separate the two, and what separates them is the commit that added one.

    What the remaining assertions catch is an entry that is inconsistent with
    itself. `test_every_committed_series_has_exactly_one_entry` fails one
    naming a file that is not on disk or repeating a path that is, and
    `the_recorded_entries_name_themselves` fails one whose fields and whose
    name disagree.
    """
    by_path = {entry.path: entry for entry in read_manifest(directory)}

    for path, pinned in BACKFILLED.items():
        assert path in by_path, path
        assert identity_of(by_path[path]) == pinned, path


def the_backfill_names_the_series_its_file_holds(directory: Path) -> None:
    """The hash, the row count and the span say nothing about which series it is.

    All three would pass with the vendor, the symbol and the price basis
    swapped, and those are the three fields that say what a reader is looking
    at. The symbol is recoverable from these eight files, because each carries
    yfinance's `Ticker,` header row, so it is derived rather than restated.

    Only these eight. A recorded vintage carries a single `Date,Close` header
    and no symbol anywhere in its bytes, which is the shape `_serialize` writes
    and `data/README.md`'s `## Header shape` section explains. Its symbol is
    held by `the_recorded_entries_name_themselves` instead, out of the path.

    The symbol compared is the entry's rather than the one `BACKFILLED` pins,
    which is what keeps this a second hold rather than a restatement of the
    first. Reading the pin on both sides would compare the pin against itself
    and pass over a manifest naming a series its file does not carry.
    """
    for entry in read_manifest(directory):
        if entry.path not in BACKFILLED:
            continue
        header = (directory / entry.path).read_text(encoding="utf-8").splitlines()[1]
        assert header == f"Ticker,{entry.symbol}", entry.path


def the_recorded_entries_name_themselves(directory: Path) -> None:
    """Every entry the recorder wrote agrees with the path it took.

    `vintage_filename` joins all five identity fields, so a recorded vintage's
    vendor, symbol, price basis and span are recoverable from `entry.path`
    without reading a byte. Comparing the two is what stands between an entry
    and a file it does not describe. Scoping the two assertions above leaves
    vendor, symbol, price basis and download date covered by no other test,
    and `docs/design.md`'s register carries why that matters and why the
    symbol is not written into the bytes instead.

    What it catches is a one-sided edit. The recorder builds the name from the
    fields it then writes, so for anything it wrote the comparison holds at
    write time and only a later edit to one side can break it. It is not a
    check on what the bytes contain.

    Two limits are worth naming rather than leaving to be found.

    1. The symbol's case is not recoverable, because the join lowercases it,
       so an entry edited from `SPY` to `spy` agrees with its own name here.
       What catches that edit is `VintageEntry` refusing a line whose identity
       fields are not the spelling the recorder would have written, which means
       `read_manifest` refuses before this check sees the entry at all.
    2. The predicate is "not one of the eight" where the intent is "the
       recorder wrote it". They part on a ninth workbook column added by hand,
       which would fail here. Nothing can write one: `record_vintage` has no
       saved-date parameter, and this module's docstring says so.

    Vacuous against the committed manifest, which holds no recorded entry yet.
    `TestARecordedVintageIsHeldToo` is what exercises it and what shows it
    bites.
    """
    for entry in read_manifest(directory):
        if entry.path in BACKFILLED:
            continue
        assert entry.download_date is not None, f"{entry.path} carries no download date"
        assert entry.path == vintage_filename(
            vendor=entry.vendor,
            symbol=entry.symbol,
            price_basis=entry.price_basis,
            first_date=entry.first_date,
            last_date=entry.last_date,
            download_date=entry.download_date,
        ), entry.path


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

    def test_every_backfilled_entry_names_the_series_its_file_actually_holds(self):
        the_backfill_names_the_series_its_file_holds(DATA_DIR)

    def test_the_identity_of_all_eight_is_pinned(self):
        the_backfill_identity_is_pinned(DATA_DIR)

    def test_every_recorded_entry_agrees_with_the_path_it_took(self):
        """Vacuous today. `TestARecordedVintageIsHeldToo` is where it bites."""
        the_recorded_entries_name_themselves(DATA_DIR)

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

    def test_the_committed_record_carries_no_carriage_return(self):
        """The writer is one producer of the manifest and a hand edit is the other.

        `data/README.md` says the manifest's eight lines were written by hand,
        and `.gitattributes` holds `data/** -text`, so git commits whatever an
        editor saved rather than normalising it. `read_manifest` normalises on
        the way in, so no run reports a carriage return. The projection is
        regenerated from the manifest rather than edited, and it is read here
        beside it because both files reach git through that same attribute,
        and `shasum -a 256 -c` on a projection carrying one reads the carriage
        return as part of the filename and says eight vintages are missing
        when none of them is.
        """
        for name in (MANIFEST_NAME, CHECKSUMS_NAME):
            assert b"\r" not in (DATA_DIR / name).read_bytes(), name

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


class TestARecordedVintageIsHeldToo:
    """A ninth vintage passes the scoped assertions, and a wrong one does not.

    This is the mechanical check for issue 51's first completion condition,
    which is that recording a vintage into `data/` leaves the suite green.
    The three assertions it scopes take a directory, so the condition is
    exercised against a copy of the committed tree rather than by editing the
    committed tree and remembering to put it back.

    Name what the copy does not cover. The rest of the suite reads `DATA_DIR`
    through names bound at import, so "the whole suite is green against a real
    ninth" is still a claim this cannot make. What it holds is the three
    assertions that were measured red, plus the check that replaces what the
    scoping gives up. The full run was done by hand once, on the pull request
    that built this.
    """

    @pytest.fixture
    def with_a_ninth(self, tmp_path):
        """The eight, copied, with a ninth recorded into the copy.

        A series the eight do not carry. A second download of one they do is a
        different failure with a different owner, which is
        [issue 83](https://github.com/l3a0/quantitative-trading/issues/83), so
        the symbol is asserted unused rather than assumed so.
        """
        directory = committed_copy(tmp_path)
        assert not [e for e in read_manifest(directory) if e.symbol == "ZZZ"]
        entry = record_vintage(
            ROWS,
            vendor="yfinance",
            symbol="ZZZ",
            price_basis="adjusted",
            download_date="2026-09-17",
            data_dir=directory,
        )

        assert entry.path == NINTH_NAME
        return directory

    def test_a_recorded_ninth_leaves_the_three_scoped_assertions_green(self, with_a_ninth):
        recorded = [entry.path for entry in read_manifest(with_a_ninth)]

        assert NINTH_NAME in recorded
        assert set(BACKFILLED) <= set(recorded)
        the_backfill_identity_is_pinned(with_a_ninth)
        the_backfill_names_the_series_its_file_holds(with_a_ninth)
        the_recorded_entries_name_themselves(with_a_ninth)

    @pytest.mark.parametrize(
        ("path", "field", "value"),
        [
            ("gdx_20yr_prices.csv", "vendor", "acme"),
            ("gdx_20yr_prices.csv", "symbol", "QQQ"),
            ("gdx_20yr_prices.csv", "price_basis", "raw"),
            ("gdx_20yr_prices.csv", "download_date", "2026-09-18"),
            ("ko_chan.csv", "saved_date", "2008-01-24"),
        ],
    )
    def test_a_hand_edit_to_a_backfilled_entry_still_fails(self, with_a_ninth, path, field, value):
        """Scoping to the eight must not stop the eight being held.

        A ninth vintage sits in the manifest while this runs, because that is
        the state the scoping was for and a pin that only holds against eight
        entries would not have been scoped at all.
        """
        rewrite_entry(with_a_ninth, path, **{field: value})

        with pytest.raises(AssertionError):
            the_backfill_identity_is_pinned(with_a_ninth)

    def test_a_backfilled_entry_dropped_from_the_manifest_still_fails(self, with_a_ninth):
        """Set equality caught an absence by counting. A paths pin has to ask."""
        manifest = with_a_ninth / MANIFEST_NAME
        kept = [
            line
            for line in manifest.read_text(encoding="utf-8").splitlines()
            if json.loads(line)["path"] != "pep_chan.csv"
        ]
        manifest.write_text("".join(line + "\n" for line in kept), encoding="utf-8")

        with pytest.raises(AssertionError):
            the_backfill_identity_is_pinned(with_a_ninth)

    def test_a_backfilled_entry_renamed_to_a_series_its_file_does_not_hold_still_fails(
        self, with_a_ninth
    ):
        """The `Ticker,` row is derived from the file, so the symbol has two holds."""
        rewrite_entry(with_a_ninth, "gld_chan.csv", symbol="KO")

        with pytest.raises(AssertionError):
            the_backfill_names_the_series_its_file_holds(with_a_ninth)

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("vendor", "acme"),
            ("symbol", "QQQ"),
            ("price_basis", "raw"),
            ("download_date", "2026-09-18"),
            ("first_date", "2026-08-24"),
            ("last_date", "2026-08-28"),
        ],
    )
    def test_a_recorded_entry_that_names_the_wrong_thing_fails(self, with_a_ninth, field, value):
        """Every field the comparison reads, so no half of it can go tautological.

        Four of these are the fields no other test covers once the scoping
        lands, and each was measured green under the scoping alone. A manifest
        naming the wrong symbol is the sharpest, because the reader then hands
        one series' closes back under another's name and the sha256 verifies.

        The span is the other two, and they are driven here because a
        comparison is only held where a case moves each side of it. Replacing
        either span field with a value read back out of the path makes that
        half compare a string to itself, and the suite was green under both
        until these rows existed. The span is separately held against the file
        by `test_every_entry_describes_the_file_it_names`, which speaks for
        every entry, and that test reads the committed directory rather than
        this copy.
        """
        rewrite_entry(with_a_ninth, NINTH_NAME, **{field: value})

        with pytest.raises(AssertionError):
            the_recorded_entries_name_themselves(with_a_ninth)

    def test_a_recorded_entry_carrying_a_saved_date_fails(self, with_a_ninth):
        """`vintage_filename` takes a download date and does not refuse `None`.

        Handed one it returns a name ending `dlNone.csv` rather than raising,
        so the check asks first and names the entry. Nothing reaches that
        through `record_vintage`, which validates the date before it writes,
        and this is the state a hand-edited line produces.
        """
        rewrite_entry(with_a_ninth, NINTH_NAME, download_date=None, saved_date="2026-09-17")

        with pytest.raises(AssertionError, match="carries no download date"):
            the_recorded_entries_name_themselves(with_a_ninth)

    def test_rewriting_an_entry_no_manifest_line_names_is_refused(self, with_a_ninth):
        """A negative case is only negative while its edit lands.

        A mistyped path would leave the manifest untouched, and the case using
        it would report that nothing raised rather than that nothing was
        edited. The guard is what makes the second failure say so.
        """
        with pytest.raises(AssertionError, match="absent.csv"):
            rewrite_entry(with_a_ninth, "absent.csv", vendor="acme")
