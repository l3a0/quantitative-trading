"""The pins for the reader: which vintage a run resolves, and that it is that one.

A run reads a committed vintage or it does not run. These cases hold both
halves. The resolution half turns identity fields into one manifest entry and
refuses rather than choosing between two. The verification half recomputes the
sha256 from the bytes it is about to parse and stops the run when they disagree.

Every refusal is asserted on its message rather than only on its type. Absent,
unreadable, altered and never-recorded are four different problems with four
different fixes, and one message for all of them sends the reader to the wrong
one. That is the same rule ``tests/test_ithildincore_contract.py`` exists to
serve one level up: a red replication has to say whether the data moved or the
dependency did, and a refusal naming the vintage is a better answer than "the
data".

The states below are built rather than described. A deleted file is not a
dangling symlink and neither is a file at mode ``000``, and a case that deletes
a file and calls the trap covered passes against the implementation it exists
to catch.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from pathlib import Path

import pytest

from chan import paths, series, vintage
from chan.paths import DATA_DIR
from chan.series import close_identity, load_close, load_vintage
from chan.vintage import (
    MANIFEST_NAME,
    VintageEntry,
    VintageUnavailable,
    read_manifest,
    record_vintage,
)
from tests.support.committed_vintages import BACKFILLED, rewrite_entry

# Root ignores mode bits, so a file at mode 000 opens and the case reads as a
# pass while asserting nothing. Windows has no such bit at all.
NOT_ROOT = pytest.mark.skipif(
    os.name != "posix" or os.geteuid() == 0,
    reason="mode bits only bite a non-root POSIX user",
)

SERIES = [("2026-01-02", 10.0), ("2026-01-05", 11.0), ("2026-01-06", 12.5)]


def payload_of(rows: list[tuple[str, float]]) -> bytes:
    """The bytes the recorder would write for ``rows``."""
    return ("Date,Close\n" + "".join(f"{day},{value!r}\n" for day, value in rows)).encode("utf-8")


def place(
    directory: Path,
    *,
    name: str,
    rows: list[tuple[str, float]] = SERIES,
    vendor: str = "yfinance",
    symbol: str = "ZZZ",
    price_basis: str = "adjusted",
    download_date: str | None = "2026-02-01",
    saved_date: str | None = None,
    write_file: bool = True,
) -> VintageEntry:
    """Leave one vintage in ``directory``, the way the recorder leaves one.

    ``write_file=False`` leaves the entry alone, which is the state a crash
    between the append and the write produces. The recorder appends first on
    purpose, so this is a designed state rather than a hypothetical.
    """
    payload = payload_of(rows)
    entry = VintageEntry(
        vendor=vendor,
        symbol=symbol,
        price_basis=price_basis,
        first_date=rows[0][0],
        last_date=rows[-1][0],
        path=name,
        row_count=len(rows),
        sha256=hashlib.sha256(payload).hexdigest(),
        download_date=download_date,
        saved_date=saved_date,
    )
    with open(directory / MANIFEST_NAME, "a", encoding="utf-8") as manifest:
        manifest.write(entry.as_json() + "\n")
    if write_file:
        (directory / name).write_bytes(payload)
    return entry


def _replace_with_directory(path: Path) -> None:
    path.unlink()
    path.mkdir()


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """An empty data directory with an empty manifest, never the committed one."""
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / MANIFEST_NAME).write_text("", encoding="utf-8")
    return directory


@pytest.fixture
def committed_copy(tmp_path: Path) -> Path:
    """The eight committed vintages, copied so a case may break one."""
    directory = tmp_path / "committed"
    shutil.copytree(DATA_DIR, directory)
    return directory


# The eight, as the reader returned them at 42978ce, before it consulted a
# manifest at all: path, row count, span, the first and last close, and the
# sum. Asserted against that captured output rather than against a fresh
# expectation, because the claim is that the conversion changed nothing about
# what comes back.
#
# The sum stands in for every value between the two ends, and it is compared
# with a tolerance rather than exactly. A hash of the parsed doubles is not a
# pin anybody can keep: the four yfinance files carry full float64 reprs like
# `56.36000061035156`, and parsing those gives answers that differ in the last
# bit between a macOS arm64 run and CI's linux x86_64, measured on PR 71 rather
# than predicted. The four workbook columns carry two decimals and agree
# everywhere. `TestTheParseDoesNotDependOnWhereTheBytesCameFrom` below covers
# what a hash was reaching for.
COMMITTED = [
    (
        "GLD",
        {},
        "gld_20yr_prices.csv",
        5030,
        "2006-06-19",
        "2026-06-16",
        56.36000061035156,
        397.6300048828125,
        753957.9496269226,
    ),
    (
        "GLD",
        {"unadjusted": True},
        "gld_20yr_prices_unadjusted.csv",
        5477,
        "2004-11-18",
        "2026-08-27",
        44.380001068115234,
        422.6000061035156,
        792556.8096580505,
    ),
    (
        "GDX",
        {},
        "gdx_20yr_prices.csv",
        5099,
        "2006-05-22",
        "2026-08-27",
        31.594470977783203,
        103.69000244140624,
        171276.68938541412,
    ),
    (
        "GDX",
        {"unadjusted": True},
        "gdx_20yr_prices_unadjusted.csv",
        5099,
        "2006-05-22",
        "2026-08-27",
        37.22999954223633,
        103.69000244140624,
        187504.61998081207,
    ),
    ("GLD", {"chan": True}, "gld_chan.csv", 764, "2004-11-18", "2007-11-30", 44.38, 77.32, 43361.5),
    (
        "GDX",
        {"chan": True},
        "gdx_chan.csv",
        385,
        "2006-05-23",
        "2007-11-30",
        37.85,
        46.36,
        15325.119999999999,
    ),
    (
        "KO",
        {"chan": True},
        "ko_chan.csv",
        11592,
        "1962-01-02",
        "2008-01-18",
        0.63,
        60.74,
        173128.16,
    ),
    (
        "PEP",
        {"chan": True},
        "pep_chan.csv",
        7835,
        "1977-01-03",
        "2008-01-18",
        0.66,
        71.46,
        154041.09,
    ),
]


def the_reader_reaches_every_backfilled_vintage(directory: Path) -> None:
    """The map is total over the eight, which is what lets the filename go.

    A partial map would leave a committed vintage the reader cannot name, and
    the only way to notice is to count both sides.

    The right-hand side counts the backfilled entries rather than the whole
    manifest. A recorded vintage is not in `COMMITTED`, which is the captured
    output of the reader at 42978ce, so counting it on one side and not the
    other would fail this the moment `data/` gains a ninth series while saying
    nothing about whether the map is partial. The left-hand side keeps its own
    count in `len(resolved) == 8`.

    It takes a directory rather than reading the committed one through a name
    bound at import, so `TestARecordedNinthLeavesTheReaderAlone` can run it
    against a copy that has a ninth vintage in it.
    """
    resolved = {
        load_vintage(ticker, **flags, data_dir=directory)[0].path for ticker, flags, *_ in COMMITTED
    }

    assert resolved == {
        entry.path for entry in read_manifest(directory) if entry.path in BACKFILLED
    }
    assert len(resolved) == 8


class TestTheEightStillReadAsTheyDid:
    """Rule 1. The conversion changes where the path comes from and nothing else."""

    @pytest.mark.parametrize(
        ("ticker", "flags", "path", "rows", "first", "last", "opening", "closing", "total"),
        COMMITTED,
    )
    def test_a_committed_vintage_returns_the_series_it_returned_before(
        self, ticker, flags, path, rows, first, last, opening, closing, total
    ) -> None:
        entry, values = load_vintage(ticker, **flags)

        assert entry.path == path
        assert len(values) == rows
        assert str(values.index[0].date()) == first
        assert str(values.index[-1].date()) == last
        assert float(values.iloc[0]) == pytest.approx(opening, rel=1e-14)
        assert float(values.iloc[-1]) == pytest.approx(closing, rel=1e-14)
        assert float(values.sum()) == pytest.approx(total, rel=1e-10)

    def test_the_row_count_the_manifest_records_survives_the_parse(self) -> None:
        """The header rows are dropped and nothing else is. Four of the eight
        carry yfinance's three-row header and still record the row count of the
        series, so the manifest can say it for all eight."""
        for ticker, flags, path, rows, *_ in COMMITTED:
            entry, values = load_vintage(ticker, **flags)
            assert entry.row_count == rows, path
            assert len(values) == rows, path

    def test_the_three_arguments_map_onto_the_manifest_and_nothing_is_left_over(self) -> None:
        the_reader_reaches_every_backfilled_vintage(DATA_DIR)


class TestWhatTellsTwoDownloadsApart:
    """Rule 2. The discriminator is a date, read from whichever field carries it.

    An argument named for the download date could name only four of the eight
    committed vintages, because the other four are columns lifted from Ernest
    Chan's workbooks and carry a saved date instead. A rule that the latest date
    wins would compare `None` against a string, and where it did work it would
    let a new download move a pinned number with nothing in the diff to explain
    it. So the date is explicit and ambiguity stops the run.
    """

    def test_two_downloads_of_one_series_are_told_apart(self, data_dir: Path) -> None:
        june = place(
            data_dir, name="june.csv", rows=SERIES, download_date="2026-06-16", symbol="ZZZ"
        )
        august = place(
            data_dir,
            name="august.csv",
            rows=[*SERIES, ("2026-01-07", 13.0)],
            download_date="2026-08-27",
            symbol="ZZZ",
        )

        first, _ = load_vintage("ZZZ", dated="2026-06-16", data_dir=data_dir)
        second, later = load_vintage("ZZZ", dated="2026-08-27", data_dir=data_dir)

        assert (first.path, second.path) == (june.path, august.path)
        assert len(later) == 4

    def test_a_saved_date_entry_resolves_through_the_same_argument(self) -> None:
        """The four workbook columns carry no download date at all."""
        entry, _ = load_vintage("KO", chan=True, dated="2008-01-23")

        assert (entry.path, entry.download_date) == ("ko_chan.csv", None)
        assert (entry.saved_date, entry.obtained_verb) == ("2008-01-23", "saved")

    def test_an_ambiguous_request_names_both_candidates_rather_than_choosing(
        self, data_dir: Path
    ) -> None:
        place(data_dir, name="june.csv", download_date="2026-06-16")
        place(data_dir, name="august.csv", download_date="2026-08-27")

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        assert "june.csv (downloaded 2026-06-16)" in message
        assert "august.csv (downloaded 2026-08-27)" in message
        assert "2 recorded vintages" in message

    def test_a_partial_date_names_nothing(self, data_dir: Path) -> None:
        """A prefix match would let ``2026`` stand for a year's downloads, which
        is a filter rather than a name. The argument identifies one vintage."""
        place(data_dir, name="june.csv", download_date="2026-06-16")

        for partial in ("2026", "2026-06", "2026-06-1", " 2026-06-16", "2026-06-16 "):
            with pytest.raises(VintageUnavailable):
                load_close("ZZZ", dated=partial, data_dir=data_dir)

    def test_one_entry_written_twice_says_so_rather_than_offering_a_date(
        self, data_dir: Path
    ) -> None:
        """A bad merge of an append-only file duplicates a line. Naming a date
        cannot separate two identical entries, so a message offering that
        remedy sends the reader to a fix that does not exist."""
        entry = place(data_dir, name="june.csv", download_date="2026-06-16")
        with open(data_dir / MANIFEST_NAME, "a", encoding="utf-8") as manifest:
            manifest.write(entry.as_json() + "\n")

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        assert "2 identical entries for june.csv" in message
        assert "Name which one with the date" not in message

    def test_a_date_that_names_nothing_refuses_rather_than_falling_back(
        self, data_dir: Path
    ) -> None:
        """Falling back to the one entry there is would make the argument a hint."""
        place(data_dir, name="june.csv", download_date="2026-06-16")

        with pytest.raises(VintageUnavailable, match="dated 2026-06-17"):
            load_close("ZZZ", dated="2026-06-17", data_dir=data_dir)


class TestTheChanSetIgnoresUnadjusted:
    """Rule 3. The docstring's promise is kept rather than overturned.

    Chan's workbooks hold one price column per symbol and it is the adjusted
    one, so `(chan-xls, raw)` matches no manifest entry and never will. A lookup
    that trusted the triple would turn a silently ignored argument into a
    refusal naming a vintage nobody meant to ask for.
    """

    def test_the_flag_is_ignored_rather_than_refused(self) -> None:
        with_flag = load_close("GLD", chan=True, unadjusted=True)
        without = load_close("GLD", chan=True)

        assert len(with_flag) == 764
        assert with_flag.equals(without)

    def test_a_lower_case_ticker_resolves_and_is_named_upper(self) -> None:
        """Both entry points take a ticker string and normalise it, and every
        other case here passes one that is already upper."""
        lower = load_close("gld", chan=True)
        upper = load_close("GLD", chan=True)

        assert lower.name == "GLD"
        assert lower.equals(upper)

    def test_the_identity_says_so_where_the_lookup_is_built(self) -> None:
        assert close_identity("GLD", chan=True, unadjusted=True) == ("chan-xls", "adjusted")
        assert close_identity("GLD", unadjusted=True) == ("yfinance", "raw")
        assert close_identity("GLD") == ("yfinance", "adjusted")


class TestTheBytesAreCheckedAgainstTheRecord:
    """Rule 4. Verify on every read, and name the vintage when it fails."""

    def test_a_changed_byte_stops_the_run_and_names_which_vintage(self, data_dir: Path) -> None:
        entry = place(data_dir, name="one.csv")
        (data_dir / "one.csv").write_bytes(payload_of([("2026-01-02", 10.5)]))

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        assert message.startswith("one.csv:")
        assert entry.sha256 in message

    def test_every_committed_vintage_verifies_as_it_stands(self, committed_copy: Path) -> None:
        """The check has to pass on the eight before it is worth anything."""
        for ticker, flags, path, *_ in COMMITTED:
            assert load_vintage(ticker, **flags, data_dir=committed_copy)[0].path == path

    def test_the_bytes_that_were_hashed_are_the_bytes_that_come_back(
        self, data_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`read_vintage`'s own half of rule 5, which the parse's half does not hold.

        A version ending in `return path.read_bytes()` re-opens the file after
        the hash and hands back whatever is on disk at that second instant. The
        parse-side case below patches `read_vintage` itself, so it cannot see
        this. The file is swapped from inside the hash to hit the window.
        """
        entry = place(data_dir, name="one.csv")
        other = payload_of([("2026-01-02", 99.0)])
        genuine = hashlib.sha256

        def swap_the_file_while_it_is_being_hashed(payload=b""):
            (data_dir / "one.csv").write_bytes(other)
            return genuine(payload)

        monkeypatch.setattr(vintage.hashlib, "sha256", swap_the_file_while_it_is_being_hashed)
        returned = vintage.read_vintage(entry, data_dir=data_dir)

        assert returned == payload_of(SERIES)
        assert (data_dir / "one.csv").read_bytes() == other

    def test_a_hash_that_agrees_on_its_first_characters_is_not_a_match(
        self, data_dir: Path
    ) -> None:
        """Comparing a prefix accepts bytes the record does not describe, and a
        changed byte moves the whole digest, so no ordinary case can tell the
        two comparisons apart."""
        entry = place(data_dir, name="one.csv")
        truncated = VintageEntry(
            **{
                **{
                    field: getattr(entry, field)
                    for field in (
                        "vendor",
                        "symbol",
                        "price_basis",
                        "first_date",
                        "last_date",
                        "path",
                        "row_count",
                        "download_date",
                    )
                },
                "sha256": entry.sha256[:8] + "0" * 56,
            }
        )

        with pytest.raises(VintageUnavailable, match="not the file the record describes"):
            vintage.read_vintage(truncated, data_dir=data_dir)

    def test_the_refusal_names_what_the_file_hashes_to_and_what_was_recorded(
        self, data_dir: Path
    ) -> None:
        """Printing the recorded hash twice reads as a match that was refused."""
        entry = place(data_dir, name="one.csv")
        altered = payload_of([("2026-01-02", 10.5)])
        (data_dir / "one.csv").write_bytes(altered)

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        assert hashlib.sha256(altered).hexdigest() in message
        assert entry.sha256 in message

    def test_a_truncated_vintage_is_caught_though_it_still_parses(self, data_dir: Path) -> None:
        """pandas reads a short file without complaining, which is the point."""
        place(data_dir, name="one.csv")
        (data_dir / "one.csv").write_bytes(payload_of(SERIES[:2]))

        with pytest.raises(VintageUnavailable, match="not the file the record describes"):
            load_close("ZZZ", data_dir=data_dir)


class TestTheParseTakesTwoColumnsAndStaysQuiet:
    """Two arguments in ``_parse_close`` that every committed vintage leaves inert."""

    def test_a_third_column_is_ignored_rather_than_shifting_the_series(
        self, data_dir: Path
    ) -> None:
        """All eight committed vintages carry two columns, so `usecols` reads as
        decoration. Without it pandas puts the first column into the index and
        the close is read out of the wrong field, silently."""
        entry = place(data_dir, name="one.csv")
        with_volume = b"Date,Close,Volume\n" + b"".join(
            f"{day},{value!r},1000\n".encode() for day, value in SERIES
        )
        (data_dir / "one.csv").write_bytes(with_volume)
        repointed = VintageEntry(
            **{
                **{
                    field: getattr(entry, field)
                    for field in (
                        "vendor",
                        "symbol",
                        "price_basis",
                        "first_date",
                        "last_date",
                        "path",
                        "row_count",
                        "download_date",
                    )
                },
                "sha256": hashlib.sha256(with_volume).hexdigest(),
            }
        )
        with open(data_dir / MANIFEST_NAME, "w", encoding="utf-8") as manifest:
            manifest.write(repointed.as_json() + "\n")

        values = load_close("ZZZ", data_dir=data_dir)

        assert list(values) == [10.0, 11.0, 12.5]
        assert [str(day.date()) for day in values.index] == [day for day, _ in SERIES]

    def test_reading_a_vintage_warns_about_nothing(self) -> None:
        """The three-row header does not parse as a date and pandas says so. The
        suppression is deliberate and nothing held it, so an operator running a
        replication would have seen the noise it is written to hide."""
        import warnings

        with warnings.catch_warnings(record=True) as raised:
            warnings.simplefilter("always")
            load_close("GLD")

        assert [str(warning.message) for warning in raised] == []


class TestTheParseDoesNotDependOnWhereTheBytesCameFrom:
    """Rule 5's other half. The buffer and the path must parse to one series.

    Reading from an in-memory buffer is what makes one read answer both the
    hash and the parse. It is worth nothing if it quietly parses differently
    from the path the old reader opened, so the two are compared rather than
    assumed equal. This is also what a hash of the parsed values was reaching
    for, and unlike a hash it holds on every platform.
    """

    @pytest.mark.parametrize(("ticker", "flags", "path"), [case[:3] for case in COMMITTED])
    def test_the_buffer_parse_matches_the_path_parse_exactly(self, ticker, flags, path) -> None:
        import warnings

        import pandas as pd

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            from_path = pd.read_csv(
                str(DATA_DIR / path), header=None, names=["date", "close"], usecols=[0, 1]
            )
            dates = pd.to_datetime(from_path["date"], errors="coerce")
        mask = dates.notna()
        expected = pd.Series(
            pd.to_numeric(from_path["close"][mask], errors="coerce").to_numpy(dtype=float),
            index=pd.DatetimeIndex(dates[mask]),
            name=ticker.upper(),
        ).sort_index()

        assert load_close(ticker, **flags).equals(expected)


class TestTheSeriesComesBackInDateOrder:
    """The recorder writes rows in the order it is handed them, on purpose.

    ``_serialize``'s docstring says the file is meant to be what the vendor
    returned, so a vendor that answers newest-first produces a vintage that is
    committed unsorted. The eight committed ones are sorted already, which is
    why nothing else here would notice the reader dropping the sort.
    """

    def test_a_vintage_written_backwards_reads_forwards(self, data_dir: Path) -> None:
        place(data_dir, name="one.csv", rows=list(reversed(SERIES)))

        values = load_close("ZZZ", data_dir=data_dir)

        assert [str(day.date()) for day in values.index] == [day for day, _ in SERIES]
        assert list(values) == [10.0, 11.0, 12.5]


class TestOneReadAnswersBothQuestions:
    """Rule 5. Hashing one read and parsing another checks a file it did not use."""

    def test_replacing_the_file_after_the_hash_cannot_change_the_series(
        self, data_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        place(data_dir, name="one.csv")
        genuine = vintage.read_vintage

        def swap_the_file_behind_the_verified_bytes(entry, data_dir=None):
            payload = genuine(entry, data_dir=data_dir)
            (data_dir / entry.path).write_bytes(payload_of([("2026-01-02", 99.0)]))
            return payload

        monkeypatch.setattr(series, "read_vintage", swap_the_file_behind_the_verified_bytes)
        values = load_close("ZZZ", data_dir=data_dir)

        assert list(values) == [10.0, 11.0, 12.5]


class TestFourSilencesAreToldApart:
    """Rules 6 and 7. Absent, unreadable, dangling and empty are four states.

    Python already distinguishes three of them and this class holds that the
    distinction survives the check being added around them. A single
    ``except OSError`` around the read is what actually turns unreadable into
    absent, because ``FileNotFoundError`` is an ``OSError`` too.
    """

    def test_an_entry_whose_file_is_gone_says_the_record_outlived_the_series(
        self, data_dir: Path
    ) -> None:
        place(data_dir, name="one.csv", write_file=False)

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        # Leads with the vintage. Asserting the name appears anywhere is met by
        # the absolute path, which ends in it, so a message that dropped the
        # vintage would still pass.
        assert message.startswith("one.csv:")
        assert "no file is at" in message

    @NOT_ROOT
    def test_a_vintage_that_cannot_be_opened_is_not_reported_as_absent(
        self, data_dir: Path
    ) -> None:
        place(data_dir, name="one.csv")
        (data_dir / "one.csv").chmod(0o000)

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        assert message.startswith("one.csv:")
        assert "could not be read" in message
        assert "no file is at" not in message

    def test_a_dangling_symlink_is_the_state_path_exists_calls_absent(self, data_dir: Path) -> None:
        """``exists`` and ``open`` agree here and both are wrong about the cause.

        Something is at the path. A reader told the vintage was never committed
        goes looking for a download that was in fact made.
        """
        place(data_dir, name="one.csv", write_file=False)
        (data_dir / "one.csv").symlink_to(data_dir / "nowhere.csv")

        assert not (data_dir / "one.csv").exists()
        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        assert message.startswith("one.csv:")
        assert "symlink" in message
        assert "no file is at" not in message

    def test_a_directory_at_the_path_is_reported_as_unreadable(self, data_dir: Path) -> None:
        """``exists`` says True and ``is_file`` says False, and ``open`` raises
        a third errno again. It belongs with unreadable rather than with absent."""
        place(data_dir, name="one.csv", write_file=False)
        (data_dir / "one.csv").mkdir()

        with pytest.raises(VintageUnavailable, match="could not be read"):
            load_close("ZZZ", data_dir=data_dir)

    @NOT_ROOT
    def test_a_parent_directory_with_no_execute_bit_refuses_rather_than_crashing(
        self, data_dir: Path
    ) -> None:
        """The third trap in rule 7's table. ``Path.exists`` raises here rather
        than answering, so a guard written as a look does not lie, it crashes,
        and a ``try`` around the look reports the whole tree as absent. The
        refusal has to come from the read."""
        nested = data_dir / "nested"
        nested.mkdir()
        (nested / "one.csv").write_bytes(payload_of(SERIES))
        place(data_dir, name="nested/one.csv", write_file=False)
        nested.chmod(0o600)
        try:
            with pytest.raises(VintageUnavailable) as refused:
                load_close("ZZZ", data_dir=data_dir)
        finally:
            nested.chmod(0o700)

        message = str(refused.value)
        assert message.startswith("nested/one.csv:")
        assert "could not be read" in message

    def test_a_manifest_holding_nothing_is_a_lost_record_not_a_missing_download(
        self, data_dir: Path
    ) -> None:
        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        assert "records no vintages at all" in message
        assert "no committed vintage is recorded for" not in message

    def test_the_four_messages_are_four_messages(self, tmp_path: Path) -> None:
        """One message for four states sends the reader to the wrong fix, so the
        distinction is asserted as a distinction rather than case by case."""
        messages = []
        for state in ("empty", "unrecorded", "absent", "dangling"):
            directory = tmp_path / state
            directory.mkdir()
            (directory / MANIFEST_NAME).write_text("", encoding="utf-8")
            if state == "unrecorded":
                place(directory, name="other.csv", symbol="AAA")
            if state in ("absent", "dangling"):
                place(directory, name="one.csv", write_file=False)
            if state == "dangling":
                (directory / "one.csv").symlink_to(directory / "nowhere.csv")
            with pytest.raises(VintageUnavailable) as refused:
                load_close("ZZZ", data_dir=directory)
            messages.append(str(refused.value))

        assert len(set(messages)) == 4


class TestAnEntryWithNoFileIsNotAFileWithNoEntry:
    """Rule 8. The second is how an uncommitted download sneaks into a result.

    ``test_every_committed_series_has_exactly_one_entry`` in
    ``tests/test_vintage.py`` answers this for the committed set at suite time.
    These answer it for one vintage at read time, which is a different moment
    and a different reader.
    """

    def test_a_csv_no_entry_names_is_reported_as_that(self, data_dir: Path) -> None:
        place(data_dir, name="recorded.csv", symbol="AAA")
        (data_dir / "stray.csv").write_bytes(payload_of(SERIES))

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        message = str(refused.value)
        assert "No entry names stray.csv" in message
        assert "recorded.csv" not in message

    def test_the_two_directions_give_two_messages(self, tmp_path: Path) -> None:
        orphaned_entry = tmp_path / "entry"
        orphaned_entry.mkdir()
        (orphaned_entry / MANIFEST_NAME).write_text("", encoding="utf-8")
        place(orphaned_entry, name="one.csv", write_file=False)

        orphaned_file = tmp_path / "file"
        orphaned_file.mkdir()
        (orphaned_file / MANIFEST_NAME).write_text("", encoding="utf-8")
        place(orphaned_file, name="recorded.csv", symbol="AAA")
        (orphaned_file / "stray.csv").write_bytes(payload_of(SERIES))

        with pytest.raises(VintageUnavailable) as entry_side:
            load_close("ZZZ", data_dir=orphaned_entry)
        with pytest.raises(VintageUnavailable) as file_side:
            load_close("ZZZ", data_dir=orphaned_file)

        assert str(entry_side.value) != str(file_side.value)

    def test_every_unrecorded_series_is_named_and_they_are_sorted(self, data_dir: Path) -> None:
        """One stray file holds nothing about order, about the separator, or
        about whether the note stops after the first name."""
        place(data_dir, name="recorded.csv", symbol="AAA")
        for name in ("zulu.csv", "alpha.csv", "mike.csv"):
            (data_dir / name).write_bytes(payload_of(SERIES))

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        assert "No entry names alpha.csv, mike.csv, zulu.csv either" in str(refused.value)

    @NOT_ROOT
    def test_a_directory_that_cannot_be_listed_does_not_answer_nothing_unrecorded(
        self, data_dir: Path
    ) -> None:
        """The alarm is the point. A scan that could not run must not give the
        same answer as one that ran and found nothing. A directory at mode 300
        still opens the manifest by name and still fails the listing."""
        place(data_dir, name="recorded.csv", symbol="AAA")
        data_dir.chmod(0o300)
        try:
            with pytest.raises(VintageUnavailable) as refused:
                load_close("ZZZ", data_dir=data_dir)
        finally:
            data_dir.chmod(0o700)

        assert "could not be listed" in str(refused.value)

    def test_a_subdirectory_is_not_reported_as_an_unrecorded_series(self, data_dir: Path) -> None:
        """A glob matches a directory whose name ends in .csv, and reporting one
        as an uncommitted download sends the reader looking for a file."""
        place(data_dir, name="recorded.csv", symbol="AAA")
        (data_dir / "subdir.csv").mkdir()

        with pytest.raises(VintageUnavailable) as refused:
            load_close("ZZZ", data_dir=data_dir)

        assert "subdir.csv" not in str(refused.value)


class TestTheRefusalReachesAnOperatorAsALine:
    """Rule 9. Both entry points that reach a vintage, not only the one measured.

    ``main`` takes no data directory, because it is a command line rather than a
    library call, so these point the default at a temporary tree. That is the
    one place the argument rule 11 chose cannot reach.
    """

    @pytest.fixture
    def broken(self, committed_copy: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        """A copy of the committed vintages with one leg's bytes changed."""
        altered = committed_copy / "gld_20yr_prices_unadjusted.csv"
        altered.write_bytes(altered.read_bytes().replace(b"44.38", b"44.39", 1))
        monkeypatch.setattr(paths, "DATA_DIR", committed_copy)
        return committed_copy

    def test_the_replication_command_prints_a_line(
        self, broken: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from chan import pair_cointegration

        monkeypatch.setattr(sys, "argv", ["chan.pair_cointegration", "--ch7"])
        with pytest.raises(SystemExit) as stopped:
            pair_cointegration.main()

        message = str(stopped.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "\n" not in message

    def test_the_figure_command_prints_a_line(
        self, broken: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from chan import regime_figure

        with pytest.raises(SystemExit) as stopped:
            regime_figure.main()

        message = str(stopped.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "\n" not in message

    @pytest.mark.parametrize(
        ("state", "wreck"),
        [
            ("the manifest is gone", lambda d: (d / MANIFEST_NAME).unlink()),
            ("a line will not parse", lambda d: (d / MANIFEST_NAME).write_text("{\n")),
            ("the manifest is a directory", lambda d: _replace_with_directory(d / MANIFEST_NAME)),
        ],
    )
    def test_a_manifest_that_cannot_be_read_also_reaches_an_operator_as_a_line(
        self, committed_copy: Path, monkeypatch: pytest.MonkeyPatch, state, wreck
    ) -> None:
        """`read_manifest` raises three classes and none of them is the reader's.

        A deleted vintage reached an operator as a line while a deleted manifest
        reached one as a traceback, which is the same failure rule 9 names, one
        level up. A fresh clone with a bad checkout lands in exactly this state.
        """
        from chan import pair_cointegration

        wreck(committed_copy)
        monkeypatch.setattr(paths, "DATA_DIR", committed_copy)
        monkeypatch.setattr(sys, "argv", ["chan.pair_cointegration", "--ch7"])
        with pytest.raises(SystemExit) as stopped:
            pair_cointegration.main()

        message = str(stopped.value)
        assert "manifest could not be read" in message, state
        assert "\n" not in message, state


class TestTheDataDirectoryThreadsAllTheWayDown:
    """Rule 11. Four functions sit between a test and ``chan.paths.DATA_DIR``.

    Issue 1 chose the argument over monkeypatching a module constant for the
    writer, on the grounds that the alternative is a test writing into the
    committed ``data/``. The reader faces the identical choice across a wider
    cascade and follows it.
    """

    def test_the_pair_reader_takes_one(self, committed_copy: Path) -> None:
        from chan.pair_cointegration import aligned_closes

        assert len(aligned_closes("GLD", "GDX", unadjusted=True, data_dir=committed_copy)) == 5099

    def test_the_report_takes_one(
        self, committed_copy: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from chan.pair_cointegration import run

        run("GLD", "GDX", 1, unadjusted=True, data_dir=committed_copy)

        assert "gld_20yr_prices_unadjusted.csv" in capsys.readouterr().out

    def test_the_report_reads_the_directory_it_was_handed(self, data_dir: Path) -> None:
        """A copy of the committed data is indistinguishable from the committed
        data, so passing one proves only that the argument is accepted. This
        passes a directory holding nothing, which only an argument that reaches
        the lookup can answer."""
        from chan.pair_cointegration import run

        with pytest.raises(VintageUnavailable):
            run("GLD", "GDX", 1, unadjusted=True, data_dir=data_dir)

    def test_the_figure_takes_one(self, committed_copy: Path, tmp_path: Path) -> None:
        from chan.regime_figure import make_regime_figure

        out = tmp_path / "figure.png"
        make_regime_figure(out=out, data_dir=committed_copy)

        assert out.exists()

    def test_the_figure_reads_the_directory_it_was_handed(
        self, data_dir: Path, tmp_path: Path
    ) -> None:
        from chan.regime_figure import make_regime_figure

        with pytest.raises(VintageUnavailable):
            make_regime_figure(out=tmp_path / "figure.png", data_dir=data_dir)

    def test_a_reader_pointed_elsewhere_refuses_rather_than_reaching_the_committed_data(
        self, data_dir: Path
    ) -> None:
        """The argument has to decide the lookup, not merely be accepted."""
        with pytest.raises(VintageUnavailable):
            load_close("GLD", data_dir=data_dir)


class TestARecordedNinthLeavesTheReaderAlone:
    """Issue 51's first completion condition, for the assertion this file owns.

    The other two it scopes are in `tests/test_vintage.py`, and
    `TestARecordedVintageIsHeldToo` there covers them the same way. Split
    across two files rather than gathered into one, because each case runs the
    assertion its own file holds and a shared case would leave one file's
    assertion checked somewhere its reader does not look.
    """

    @pytest.fixture
    def with_a_ninth(self, committed_copy: Path) -> Path:
        """The eight, copied, with a series they do not carry recorded into the copy."""
        record_vintage(
            SERIES,
            vendor="yfinance",
            symbol="ZZZ",
            price_basis="adjusted",
            download_date="2026-09-17",
            data_dir=committed_copy,
        )
        return committed_copy

    def test_a_ninth_vintage_does_not_break_the_count_over_the_eight(
        self, with_a_ninth: Path
    ) -> None:
        recorded = {entry.path for entry in read_manifest(with_a_ninth)}

        assert set(BACKFILLED) < recorded
        the_reader_reaches_every_backfilled_vintage(with_a_ninth)

    def test_a_ninth_vintage_is_reachable_under_its_own_name(self, with_a_ninth: Path) -> None:
        """A vintage nothing can read is not the outcome the scoping is for."""
        entry, values = load_vintage("ZZZ", data_dir=with_a_ninth)

        assert entry.path.startswith("yfinance_zzz_adjusted_")
        assert len(values) == len(SERIES)

    def test_a_backfilled_vintage_the_reader_cannot_reach_still_stops_the_case(
        self, with_a_ninth: Path
    ) -> None:
        """A map going partial surfaces as a refusal rather than as a count.

        The three arguments name a price basis, so an entry carrying one no
        triple asks for is an entry the reader resolves nothing for. It stops
        there rather than reaching the comparison, which is why this asserts
        the refusal and not an `AssertionError`. Both stop the case, and the
        refusal names which vintage, which the count could not.
        """
        rewrite_entry(with_a_ninth, "ko_chan.csv", price_basis="raw")

        with pytest.raises(VintageUnavailable, match="chan-xls KO adjusted"):
            the_reader_reaches_every_backfilled_vintage(with_a_ninth)
