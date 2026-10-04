"""What reading one of Chan's ``.mat`` files must do, on a file built here.

Chan's ``.mat`` files are not committed, so every case writes a small MATLAB 5 file
with ``scipy.io.savemat`` and stamps the header's creation date in by hand,
because ``savemat`` writes today's. The committed result of reading the real
files is pinned in ``tests/test_series.py``, where
``TestTheCommittedPanelsAreChansArrays`` reads the panels back.
"""

from __future__ import annotations

import hashlib
import io
from pathlib import Path

import numpy as np
import pytest
import scipy.io

from chan import mat_columns
from chan.mat_columns import (
    ARRAYS,
    CSV_VENDOR,
    VENDOR,
    columns_of,
    continuous_round_trip_differs,
    csv_round_trip_differs,
    flag_round_trip_differs,
    read_arrays,
    read_continuous,
    read_csv_rows,
    read_flags,
    read_strip,
    record_continuous_file,
    record_csv_file,
    record_flag_file,
    record_mat_file,
    record_strip_file,
    root_of,
    round_trip_differs,
    saved_date_of,
    shape_of,
    strip_round_trip_differs,
)
from chan.series import load_panel
from chan.vintage import LIFTED_FIELDS, MANIFEST_NAME, read_manifest
from tests.support.committed_vintages import rewrite_entry

CREATED = "Sat Nov 24 13:12:39 2007"
DAYS = [20071119, 20071120, 20071121, 20071123]
SYMBOLS = ["AA", "BF.B", "KO"]
NAN = float("nan")
CLOSES = np.array(
    [
        [30.0, NAN, 60.0],
        [31.0, 70.0, NAN],
        [NAN, 71.0, 61.0],
        [32.5, 72.0, 62.3],
    ]
)


def arrays_from(closes: np.ndarray) -> dict[str, np.ndarray]:
    """Five arrays the way Chan's files hold them, NaN together on an unpriced day.

    The other fields are derived from the close so that every one differs from
    every other, which is what lets a case notice a field read from the wrong
    column.
    """
    volume = np.where(np.isnan(closes), NAN, np.arange(closes.size).reshape(closes.shape) * 100.0)
    return {
        "cl": closes,
        "hi": closes + 1.25,
        "lo": closes - 0.75,
        "op": closes + 0.5,
        "vol": volume,
    }


def cell_array(symbols: list[str]) -> np.ndarray:
    """A list of symbols as MATLAB's cell array of strings, written as an object array."""
    cells = np.empty((len(symbols), 1), dtype=object)
    for index, symbol in enumerate(symbols):
        cells[index, 0] = symbol
    return cells


def mat_bytes(
    *,
    created: str = CREATED,
    days: list[int] = DAYS,
    symbols: list[str] = SYMBOLS,
    arrays: dict[str, np.ndarray] | None = None,
    omit: tuple[str, ...] = (),
    symbols_under: tuple[str, ...] = ("stocks",),
) -> bytes:
    """A MATLAB 5 file holding ``tday``, ``stocks`` and the five arrays the way Chan's do.

    ``stocks`` is a cell array of strings, written as an object array, and the
    header's first 116 bytes are replaced with one carrying ``created``.
    ``symbols_under`` names where the list goes instead, so a case can write it
    as ``syms`` the way ``inputData_ETF.mat`` does, under both names, or under
    neither.
    """
    held = {
        "tday": np.array(days, dtype=np.int32).reshape(-1, 1),
        **{name: cell_array(symbols) for name in symbols_under},
        **(arrays_from(CLOSES) if arrays is None else arrays),
    }
    buffer = io.BytesIO()
    scipy.io.savemat(buffer, {key: value for key, value in held.items() if key not in omit})
    header = f"MATLAB 5.0 MAT-file, Platform: PCWIN, Created on: {created}".encode("ascii")
    return header.ljust(116, b" ") + buffer.getvalue()[116:]


@pytest.fixture
def mat(tmp_path: Path) -> Path:
    path = tmp_path / "SPX_20071123.mat"
    path.write_bytes(mat_bytes())
    return path


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / MANIFEST_NAME).write_text("", encoding="utf-8")
    return directory


class TestTheHeaderGivesTheSavedDate:
    def test_the_creation_date_is_read_out_of_the_header(self) -> None:
        assert saved_date_of(mat_bytes()) == "2007-11-24"

    def test_a_single_digit_day_padded_with_a_space_still_reads(self) -> None:
        assert saved_date_of(mat_bytes(created="Tue Jan  5 12:46:04 2008")) == "2008-01-05"

    def test_a_file_that_is_not_matlab_5_is_refused(self) -> None:
        with pytest.raises(ValueError, match="MATLAB 5.0 header"):
            saved_date_of(b"\x89HDF\r\n" + b" " * 200)

    def test_a_header_with_no_creation_date_is_refused(self) -> None:
        payload = b"MATLAB 5.0 MAT-file, Platform: PCWIN".ljust(116, b" ") + b"rest"

        with pytest.raises(ValueError, match="carries no creation date"):
            saved_date_of(payload)


class TestTheArraysAreCheckedAgainstEachOther:
    def test_the_days_the_symbols_and_every_field_come_back_together(self) -> None:
        days, symbols, arrays = read_arrays(mat_bytes())

        assert days == ["2007-11-19", "2007-11-20", "2007-11-21", "2007-11-23"]
        assert symbols == SYMBOLS
        assert list(arrays) == list(LIFTED_FIELDS)
        assert all(array.shape == (4, 3) for array in arrays.values())
        assert np.array_equal(arrays["Open"], CLOSES + 0.5, equal_nan=True)

    @pytest.mark.parametrize("name", ["cl", "op", "vol"])
    def test_a_missing_array_is_named(self, name: str) -> None:
        with pytest.raises(ValueError, match=f"carries no {name}"):
            read_arrays(mat_bytes(omit=(name,)))

    def test_days_out_of_order_are_refused(self) -> None:
        with pytest.raises(ValueError, match="not strictly increasing"):
            read_arrays(mat_bytes(days=[20071119, 20071121, 20071120, 20071123]))

    def test_a_symbol_named_twice_is_refused(self) -> None:
        with pytest.raises(ValueError, match="more than once: AA"):
            read_arrays(mat_bytes(symbols=["AA", "AA", "KO"]))

    def test_an_array_that_does_not_fit_the_days_and_symbols_is_refused(self) -> None:
        arrays = {**arrays_from(CLOSES), "hi": (CLOSES + 1.25)[:, :2]}

        with pytest.raises(ValueError, match="hi is 4 by 2 and the file carries 4 days and 3"):
            read_arrays(mat_bytes(arrays=arrays))


#: A flag array for :func:`flag_bytes`, defined here because the class below
#: reads it before :data:`FLAGS` further down is reached.
NO_FLAGS = np.zeros((len(DAYS), len(SYMBOLS)), dtype=int)


class TestTheSymbolListHasTwoSpellings:
    """Chan's stock files name their symbols ``stocks`` and his ETF file ``syms``.

    Issue 299 found ``inputData_ETF.mat`` refused on that one name. Both readers
    go through one lookup, so each case runs against both.
    """

    READERS = {
        "prices": lambda under: read_arrays(mat_bytes(symbols_under=under)),
        "flags": lambda under: read_flags(flag_bytes(flags=NO_FLAGS, symbols_under=under)),
    }

    @pytest.mark.parametrize("reader", READERS)
    @pytest.mark.parametrize("under", ["stocks", "syms"])
    def test_either_name_gives_the_same_symbols(self, reader: str, under: str) -> None:
        _, symbols, _ = self.READERS[reader]((under,))

        assert symbols == SYMBOLS

    @pytest.mark.parametrize("reader", READERS)
    @pytest.mark.parametrize(("under", "held"), [(("stocks", "syms"), "both"), ((), "neither")])
    def test_a_file_with_both_names_or_neither_is_refused_naming_both(
        self, reader: str, under: tuple[str, ...], held: str
    ) -> None:
        with pytest.raises(
            ValueError,
            match=f"the file carries {held} of stocks and syms, so it names no single list",
        ):
            self.READERS[reader](under)

    def test_a_syms_file_records_and_round_trips(self, tmp_path: Path, data_dir: Path) -> None:
        path = tmp_path / "inputData_ETF.mat"
        path.write_bytes(mat_bytes(symbols_under=("syms",)))

        entries = record_mat_file(path, price_basis="adjusted", data_dir=data_dir)

        assert [entry.symbol for entry in entries] == SYMBOLS
        assert round_trip_differs(path, data_dir=data_dir) is None


class TestAMissingCellIsAMissingRow:
    def test_each_stock_holds_only_the_days_it_was_priced_with_every_field(self) -> None:
        columns = columns_of(*read_arrays(mat_bytes()))

        assert columns["AA"] == [
            ("2007-11-19", 30.0, 31.25, 29.25, 30.5, 0.0),
            ("2007-11-20", 31.0, 32.25, 30.25, 31.5, 300.0),
            ("2007-11-23", 32.5, 33.75, 31.75, 33.0, 900.0),
        ]
        assert [row[0] for row in columns["KO"]] == ["2007-11-19", "2007-11-21", "2007-11-23"]

    def test_a_field_priced_on_a_day_the_close_is_not_is_refused(self) -> None:
        arrays = arrays_from(CLOSES)
        arrays["op"] = arrays["op"].copy()
        arrays["op"][1, 2] = 60.5

        with pytest.raises(ValueError, match="KO's Open and close disagree on whether 2007-11-20"):
            columns_of(*read_arrays(mat_bytes(arrays=arrays)))

    def test_a_field_missing_on_a_day_the_close_is_priced_is_refused(self) -> None:
        arrays = arrays_from(CLOSES)
        arrays["vol"] = arrays["vol"].copy()
        arrays["vol"][0, 0] = NAN

        with pytest.raises(
            ValueError, match="AA's Volume and close disagree on whether 2007-11-19"
        ):
            columns_of(*read_arrays(mat_bytes(arrays=arrays)))


class TestRecordingAFile:
    def test_every_stock_is_recorded_under_the_vendor_with_the_header_s_date(
        self, mat: Path, data_dir: Path
    ) -> None:
        entries = record_mat_file(mat, price_basis="adjusted", data_dir=data_dir)

        assert [entry.path for entry in entries] == [
            "spx_20071123/aa.csv",
            "spx_20071123/bf.b.csv",
            "spx_20071123/ko.csv",
        ]
        assert {(e.vendor, e.saved_date, e.source_workbook) for e in entries} == {
            (VENDOR, "2007-11-24", "SPX_20071123.mat")
        }
        assert read_manifest(data_dir) == entries

    def test_a_stock_s_file_holds_every_field_with_the_volume_whole(
        self, mat: Path, data_dir: Path
    ) -> None:
        record_mat_file(mat, price_basis="adjusted", data_dir=data_dir)

        assert (data_dir / "spx_20071123" / "aa.csv").read_bytes() == (
            b"Price,Close,High,Low,Open,Volume\n"
            b"Ticker,AA,AA,AA,AA,AA\n"
            b"Date,,,,,\n"
            b"2007-11-19,30.0,31.25,29.25,30.5,0\n"
            b"2007-11-20,31.0,32.25,30.25,31.5,300\n"
            b"2007-11-23,32.5,33.75,31.75,33.0,900\n"
        )

    def test_the_unpriced_day_is_read_off_the_close_rather_than_another_field(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        """A day whose opens survive and whose closes do not is still a day the
        per-stock files could not give back, because a row is keyed on its close."""
        closes = CLOSES.copy()
        closes[1] = NAN
        arrays = arrays_from(closes)
        arrays["op"] = arrays_from(CLOSES)["op"]
        path = tmp_path / "SPX_20071123.mat"
        path.write_bytes(mat_bytes(arrays=arrays))

        with pytest.raises(ValueError, match="prices no column on 2007-11-20"):
            record_mat_file(path, price_basis="adjusted", data_dir=data_dir)
        assert read_manifest(data_dir) == []

    def test_a_day_priced_in_no_column_is_refused_before_anything_is_written(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        """The panel rebuilds days from its members, so such a day could never come back."""
        closes = CLOSES.copy()
        closes[1] = NAN
        path = tmp_path / "SPX_20071123.mat"
        path.write_bytes(mat_bytes(arrays=arrays_from(closes)))

        with pytest.raises(ValueError, match="prices no column on 2007-11-20"):
            record_mat_file(path, price_basis="adjusted", data_dir=data_dir)

        assert read_manifest(data_dir) == []
        assert not (data_dir / "spx_20071123").exists()

    def test_symbols_the_file_spells_in_lowercase_round_trip(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        """The entries uppercase a symbol, so the check compares against that spelling."""
        path = tmp_path / "SPX_20071123.mat"
        path.write_bytes(mat_bytes(symbols=["aa", "bf.b", "ko"]))
        record_mat_file(path, price_basis="adjusted", data_dir=data_dir)

        assert round_trip_differs(path, data_dir=data_dir) is None

    def test_the_vendor_is_not_the_workbooks_one(self) -> None:
        """KO and PEP are in the S&P 500 file and already committed from his workbooks."""
        assert VENDOR == "chan-mat"

    def test_the_round_trip_finds_every_array_and_says_nothing(
        self, mat: Path, data_dir: Path
    ) -> None:
        record_mat_file(mat, price_basis="adjusted", data_dir=data_dir)

        assert round_trip_differs(mat, data_dir=data_dir) is None
        for field, name in ARRAYS.items():
            _, panel = load_panel("SPX_20071123.mat", field=field, data_dir=data_dir)
            assert np.array_equal(panel.to_numpy(), arrays_from(CLOSES)[name], equal_nan=True)

    def test_the_round_trip_says_when_a_member_is_missing(self, mat: Path, data_dir: Path) -> None:
        record_mat_file(mat, price_basis="adjusted", data_dir=data_dir)
        rewrite_entry(data_dir, "spx_20071123/ko.csv", source_workbook="OTHER.mat")

        assert (
            round_trip_differs(mat, data_dir=data_dir) == "the panel's symbols are not the file's"
        )

    @pytest.mark.parametrize(("field", "name"), [("Close", "cl"), ("Low", "lo"), ("Volume", "vol")])
    def test_the_round_trip_names_the_field_that_moved(
        self, mat: Path, data_dir: Path, field: str, name: str
    ) -> None:
        record_mat_file(mat, price_basis="adjusted", data_dir=data_dir)
        arrays = arrays_from(CLOSES)
        arrays[name] = arrays[name] * 2
        mat.write_bytes(mat_bytes(arrays=arrays))

        assert round_trip_differs(mat, data_dir=data_dir) == (
            f"the panel's {field} is not the file's {name} array"
        )


class TestTheCommandLine:
    @pytest.fixture
    def in_data_dir(self, data_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)
        return data_dir

    def test_a_run_prints_the_hash_the_count_and_the_round_trip(
        self, mat: Path, in_data_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert mat_columns.main([str(mat), "--price-basis", "adjusted"]) == 0

        printed = capsys.readouterr().out.splitlines()
        assert printed[0].startswith("SPX_20071123.mat   sha256 ")
        assert printed[1] == (
            "recorded 3 vintages, 9 rows of Close, High, Low, Open, Volume, under "
            "spx_20071123/, saved 2007-11-24"
        )
        assert printed[2] == "round trip: every field read back is the file's array, NaN for NaN"

    def test_a_second_run_is_refused_in_one_line(
        self, mat: Path, in_data_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mat_columns.main([str(mat), "--price-basis", "adjusted"])
        capsys.readouterr()

        assert mat_columns.main([str(mat), "--price-basis", "adjusted"]) == 1

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err.splitlines() == [
            "SPX_20071123.mat: not recorded. SPX_20071123.mat: the manifest already holds "
            "entries lifted from it"
        ]


def flag_bytes(
    *,
    flags: np.ndarray,
    symbols: list[str] = SYMBOLS,
    days: list[int] = DAYS,
    symbols_under: tuple[str, ...] = ("stocks",),
) -> bytes:
    """A MATLAB 5 file holding ``tday``, ``stocks`` and ``earnann``, as Chan's flag file does."""
    buffer = io.BytesIO()
    scipy.io.savemat(
        buffer,
        {
            "tday": np.array(days, dtype=np.int32).reshape(-1, 1),
            **{name: cell_array(symbols) for name in symbols_under},
            "earnann": np.asarray(flags, dtype=np.uint8),
        },
    )
    header = f"MATLAB 5.0 MAT-file, Platform: PCWIN, Created on: {CREATED}".encode("ascii")
    return header.ljust(116, b" ") + buffer.getvalue()[116:]


#: No stock is flagged on the first day, so a recorder keeping only flagged
#: days would start every vintage late.
FLAGS = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 1], [0, 1, 0]])


class TestAFlagFile:
    """``earnannFile.mat``'s shape, which issue 250 records under the ``event`` basis."""

    @pytest.fixture
    def flags(self, tmp_path: Path) -> Path:
        path = tmp_path / "earnannFile.mat"
        path.write_bytes(flag_bytes(flags=FLAGS))
        return path

    def test_every_day_is_kept_with_a_zero_where_nothing_happened(
        self, flags: Path, data_dir: Path
    ) -> None:
        entries = record_flag_file(flags, data_dir=data_dir)

        assert [entry.path for entry in entries] == [
            "earnannfile/aa.csv",
            "earnannfile/bf.b.csv",
            "earnannfile/ko.csv",
        ]
        assert {(e.price_basis, e.first_date, e.last_date, e.row_count) for e in entries} == {
            ("event", "2007-11-19", "2007-11-23", 4)
        }
        assert (data_dir / "earnannfile" / "aa.csv").read_bytes() == (
            b"Price,Flag\nTicker,AA\nDate,\n2007-11-19,0\n2007-11-20,1\n"
            b"2007-11-21,0\n2007-11-23,0\n"
        )

    def test_the_round_trip_finds_the_array_and_says_nothing(
        self, flags: Path, data_dir: Path
    ) -> None:
        record_flag_file(flags, data_dir=data_dir)

        assert flag_round_trip_differs(flags, data_dir=data_dir) is None

    def test_the_round_trip_says_when_a_flag_moved(
        self, flags: Path, data_dir: Path, tmp_path: Path
    ) -> None:
        record_flag_file(flags, data_dir=data_dir)
        moved = FLAGS.copy()
        moved[3, 1] = 0
        other = tmp_path / "elsewhere" / "earnannFile.mat"
        other.parent.mkdir()
        other.write_bytes(flag_bytes(flags=moved))

        assert flag_round_trip_differs(other, data_dir=data_dir) == (
            "the panel's flags are not the file's earnann array"
        )

    def test_symbols_out_of_alphabetical_order_round_trip(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        """The panel comes back sorted by symbol, so the check has to reorder the
        file's columns to compare them, which a sorted fixture would not show."""
        path = tmp_path / "earnannFile.mat"
        path.write_bytes(flag_bytes(flags=FLAGS, symbols=["KO", "AA", "BF.B"]))
        record_flag_file(path, data_dir=data_dir)

        assert flag_round_trip_differs(path, data_dir=data_dir) is None

    def test_the_round_trip_says_when_the_days_differ(
        self, flags: Path, data_dir: Path, tmp_path: Path
    ) -> None:
        record_flag_file(flags, data_dir=data_dir)
        other = tmp_path / "elsewhere" / "earnannFile.mat"
        other.parent.mkdir()
        other.write_bytes(flag_bytes(flags=np.vstack([FLAGS, [0, 0, 0]]), days=[*DAYS, 20071126]))

        assert flag_round_trip_differs(other, data_dir=data_dir) == (
            "the panel's days are not the file's trading days"
        )

    def test_the_round_trip_says_when_the_symbols_differ(
        self, flags: Path, data_dir: Path, tmp_path: Path
    ) -> None:
        record_flag_file(flags, data_dir=data_dir)
        other = tmp_path / "elsewhere" / "earnannFile.mat"
        other.parent.mkdir()
        other.write_bytes(
            flag_bytes(flags=np.hstack([FLAGS, [[0], [0], [0], [0]]]), symbols=[*SYMBOLS, "XOM"])
        )

        assert flag_round_trip_differs(other, data_dir=data_dir) == (
            "the panel's symbols are not the file's"
        )

    @pytest.mark.parametrize(
        ("build", "message"),
        [
            (
                lambda: flag_bytes(flags=FLAGS, days=[DAYS[1], DAYS[0], *DAYS[2:]]),
                "the file's trading days are not strictly increasing",
            ),
            (
                lambda: flag_bytes(flags=FLAGS, symbols=["AA", "AA", "KO"]),
                "the file names a symbol more than once: AA",
            ),
            (
                lambda: flag_bytes(flags=FLAGS[:, :2]),
                "earnann is 4 by 2 and the file carries 4 days and 3 symbols",
            ),
        ],
    )
    def test_a_malformed_flag_file_is_refused_by_name(self, build, message: str) -> None:
        with pytest.raises(ValueError, match=message):
            read_flags(build())

    def test_a_value_other_than_0_or_1_is_refused(self) -> None:
        bad = FLAGS.copy()
        bad[1, 0] = 2

        with pytest.raises(ValueError, match="earnann holds a value other than 0 and 1"):
            read_flags(flag_bytes(flags=bad))

    def test_the_command_records_flags_under_the_event_basis(
        self,
        flags: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)

        assert mat_columns.main([str(flags), "--price-basis", "event"]) == 0

        printed = capsys.readouterr().out.splitlines()
        assert printed[0].startswith("earnannFile.mat   sha256 ")
        assert printed[1] == (
            "recorded 3 vintages, 12 rows of Flag, under earnannfile/, saved 2007-11-24"
        )
        assert printed[2] == "round trip: every flag read back is the file's array, day for day"

    def test_a_failed_flag_round_trip_stops_the_command(
        self,
        flags: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """The flag path runs its own round trip, so a flag file that does not
        read back stops the run rather than printing a clean result."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)
        monkeypatch.setattr(mat_columns, "flag_round_trip_differs", lambda path: "moved")

        assert mat_columns.main([str(flags), "--price-basis", "event"]) == 1

        assert capsys.readouterr().err.startswith("round trip failed: moved.")

    def test_a_price_file_given_the_event_basis_is_refused_in_one_line(
        self,
        mat: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)

        assert mat_columns.main([str(mat), "--price-basis", "event"]) == 1

        assert capsys.readouterr().err.splitlines() == [
            "SPX_20071123.mat: not recorded. the file carries no earnann"
        ]
        assert read_manifest(data_dir) == []


#: A strip the way Chan's are shaped: the spot column first, a contract that
#: stops and restarts, and contracts that start late and stop early.
CONTRACTS = ["0000$", "2007F", "2007G", "2007H"]
STRIP = np.array(
    [
        [14.0, 20.0, NAN, NAN],
        [14.5, NAN, 21.0, NAN],
        [15.0, 20.5, 21.5, 22.0],
        [15.5, NAN, 22.5, 23.0],
    ]
)


def strip_bytes(
    *,
    closes: np.ndarray = STRIP,
    contracts: list[str] | None = CONTRACTS,
    days: list[int] = DAYS,
    extra: dict | None = None,
) -> bytes:
    """A MATLAB 5 file holding ``tday``, ``contracts`` and ``cl``, as Chan's strips do.

    ``contracts=None`` leaves the cell array out, which is the gold file's shape.
    """
    held = {"tday": np.array(days, dtype=np.int32).reshape(-1, 1), "cl": closes}
    if contracts is not None:
        cells = np.empty((1, len(contracts)), dtype=object)
        for index, name in enumerate(contracts):
            cells[0, index] = name
        held["contracts"] = cells
    held.update(extra or {})
    buffer = io.BytesIO()
    scipy.io.savemat(buffer, held)
    header = f"MATLAB 5.0 MAT-file, Platform: PCWIN, Created on: {CREATED}".encode("ascii")
    return header.ljust(116, b" ") + buffer.getvalue()[116:]


class TestAStrip:
    """A futures strip, which issue 300 records as one vintage per contract."""

    NAME = "inputDataDaily_CL_20120813.mat"

    @pytest.fixture
    def strip(self, tmp_path: Path) -> Path:
        path = tmp_path / self.NAME
        path.write_bytes(strip_bytes())
        return path

    def test_each_contract_is_a_close_only_vintage_named_for_the_root(
        self, strip: Path, data_dir: Path
    ) -> None:
        entries = record_strip_file(strip, price_basis="raw", data_dir=data_dir)

        assert [(e.symbol, e.path, e.row_count) for e in entries] == [
            ("CL-2007F", "inputdatadaily_cl_20120813/cl-2007f.csv", 2),
            ("CL-2007G", "inputdatadaily_cl_20120813/cl-2007g.csv", 3),
            ("CL-2007H", "inputdatadaily_cl_20120813/cl-2007h.csv", 2),
            ("CL-SPOT", "inputdatadaily_cl_20120813/cl-spot.csv", 4),
        ]
        assert {(e.vendor, e.price_basis, e.saved_date) for e in entries} == {
            (VENDOR, "raw", "2007-11-24")
        }
        assert (data_dir / "inputdatadaily_cl_20120813" / "cl-2007f.csv").read_bytes() == (
            b"Price,Close\nTicker,CL-2007F\nDate,\n2007-11-19,20.0\n2007-11-21,20.5\n"
        )

    def test_a_settlement_is_written_as_the_file_holds_it(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        """Values a float32 or a rounding would move, written out digit for digit."""
        path = tmp_path / self.NAME
        decimals = np.array([[99.62, 2.8743], [93.04, NAN], [0.1, 1188.45], [21.44, 3.0183]])
        path.write_bytes(strip_bytes(closes=decimals, contracts=["2007F", "0000$"]))
        record_strip_file(path, price_basis="raw", data_dir=data_dir)

        assert (data_dir / "inputdatadaily_cl_20120813" / "cl-2007f.csv").read_bytes() == (
            b"Price,Close\nTicker,CL-2007F\nDate,\n2007-11-19,99.62\n2007-11-20,93.04\n"
            b"2007-11-21,0.1\n2007-11-23,21.44\n"
        )
        assert (data_dir / "inputdatadaily_cl_20120813" / "cl-spot.csv").read_bytes() == (
            b"Price,Close\nTicker,CL-SPOT\nDate,\n2007-11-19,2.8743\n2007-11-21,1188.45\n"
            b"2007-11-23,3.0183\n"
        )

    def test_the_round_trip_finds_the_array_holes_and_all(
        self, strip: Path, data_dir: Path
    ) -> None:
        """The spot sits first in the file and sorts last in the panel, so the
        check has to reorder the columns, and 2007F's hole has to come back."""
        record_strip_file(strip, price_basis="raw", data_dir=data_dir)

        assert strip_round_trip_differs(strip, data_dir=data_dir) is None
        _, panel = load_panel(self.NAME, data_dir=data_dir)
        assert list(panel.columns) == ["CL-2007F", "CL-2007G", "CL-2007H", "CL-SPOT"]
        assert panel["CL-2007F"].isna().tolist() == [False, True, False, True]

    @pytest.mark.parametrize(
        ("change", "message"),
        [
            (
                {"closes": np.where(np.isnan(STRIP), NAN, STRIP + np.eye(4)[1])},
                "the panel's closes are not the file's cl array",
            ),
            (
                {"closes": STRIP + np.outer(np.ones(4), [1e-9, 0, 0, 0])},
                "the panel's closes are not the file's cl array",
            ),
            (
                {"contracts": ["0000$", "2007F", "2007G", "2007J"]},
                "the panel's symbols are not the file's",
            ),
            ({"days": [*DAYS[:3], 20071126]}, "the panel's days are not the file's trading days"),
        ],
    )
    def test_the_round_trip_says_what_moved(
        self, strip: Path, data_dir: Path, tmp_path: Path, change: dict, message: str
    ) -> None:
        record_strip_file(strip, price_basis="raw", data_dir=data_dir)
        other = tmp_path / "elsewhere" / self.NAME
        other.parent.mkdir()
        other.write_bytes(strip_bytes(**change))

        assert strip_round_trip_differs(other, data_dir=data_dir) == message

    def test_a_file_naming_no_contracts_is_one_series_named_for_its_root(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        """The gold file's shape. Its ``hhmm`` is not read."""
        path = tmp_path / "inputData_GC_1600_20100802.mat"
        path.write_bytes(
            strip_bytes(
                closes=STRIP[:, :1],
                contracts=None,
                extra={"hhmm": np.arange(9, dtype=np.uint32).reshape(-1, 1)},
            )
        )
        (entry,) = record_strip_file(path, price_basis="raw", data_dir=data_dir)

        assert (entry.symbol, entry.path, entry.row_count) == (
            "GC",
            "inputdata_gc_1600_20100802/gc.csv",
            4,
        )
        assert strip_round_trip_differs(path, data_dir=data_dir) is None

    @pytest.mark.parametrize(
        ("build", "message"),
        [
            (
                lambda: strip_bytes(contracts=["0000$", "2007F", "2007G", "OOPS"]),
                "the file names a column 'OOPS', which is neither a contract",
            ),
            (
                lambda: strip_bytes(contracts=["0000$", "2007F", "2007F", "2007H"]),
                "the file names a contract more than once: CL-2007F",
            ),
            (
                lambda: strip_bytes(contracts=None),
                "the file names no contracts and its cl has 4 columns",
            ),
            (
                lambda: strip_bytes(closes=STRIP[:, :3]),
                "cl is 4 by 3 and the file carries 4 days and 4 columns",
            ),
            (
                lambda: strip_bytes(days=[DAYS[1], DAYS[0], *DAYS[2:]]),
                "the file's trading days are not strictly increasing",
            ),
            (
                lambda: strip_bytes(days=[DAYS[0], DAYS[0], *DAYS[2:]]),
                "the file's trading days are not strictly increasing",
            ),
            (
                lambda: strip_bytes(contracts=["0000$", "2007F", "2007G", "2007A"]),
                "the file names a column '2007A'",
            ),
            (
                lambda: strip_bytes(contracts=["0000$", "2007F", "2007G", "2007FX"]),
                "the file names a column '2007FX'",
            ),
            (
                lambda: strip_bytes(contracts=["0000S", "2007F", "2007G", "2007H"]),
                "the file names a column '0000S'",
            ),
            (
                lambda: strip_bytes(days=DAYS[:3]),
                "cl is 4 by 4 and the file carries 3 days and 4 columns",
            ),
            (
                lambda: (
                    scipy.io.savemat(
                        buffer := io.BytesIO(), {"tday": np.array(DAYS).reshape(-1, 1)}
                    )
                    or buffer.getvalue()
                ),
                "the file carries no cl",
            ),
        ],
    )
    def test_a_malformed_strip_is_refused_by_name(self, build, message: str) -> None:
        with pytest.raises(ValueError, match=message):
            read_strip(build(), "CL")

    def test_a_day_no_contract_settled_is_refused_before_anything_is_written(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        unpriced = STRIP.copy()
        unpriced[1] = NAN
        path = tmp_path / self.NAME
        path.write_bytes(strip_bytes(closes=unpriced))

        with pytest.raises(ValueError, match="prices no column on 2007-11-20"):
            record_strip_file(path, price_basis="raw", data_dir=data_dir)
        assert read_manifest(data_dir) == []

    def test_the_root_is_read_off_the_name(self) -> None:
        assert root_of("inputDataDaily_HO2_20120813.mat") == "HO2"
        assert root_of("inputData_GC_1600_20100802.mat") == "GC"
        with pytest.raises(ValueError, match="carries no root"):
            root_of("strip.mat")


class TestTheCommandPicksItsReaderByTheFile:
    """The variables a file carries choose the reader, not the basis the caller states."""

    def test_each_shape_is_named_by_what_it_carries(self) -> None:
        assert shape_of(flag_bytes(flags=FLAGS)) == "flags"
        assert shape_of(mat_bytes()) == "stocks"
        assert shape_of(strip_bytes()) == "strip"
        assert shape_of(strip_bytes(closes=STRIP[:, :1], contracts=None)) == "strip"
        assert shape_of(strip_bytes(extra={"hi": STRIP})) == "strip"

    def test_a_file_naming_no_columns_but_holding_other_fields_takes_the_stock_path(
        self,
    ) -> None:
        """Only a lone ``cl`` reads as one series. A stock file with its symbol
        list missing would otherwise be read as a strip of one column, its other
        four fields dropped."""
        assert shape_of(mat_bytes(omit=("stocks",))) == "stocks"

    def test_a_file_naming_its_columns_syms_stays_on_the_stock_path(self) -> None:
        """Chan's ETF file carries ``syms``, and the stock reader is what reads it."""
        assert shape_of(mat_bytes(symbols_under=("syms",))) == "stocks"

    def test_a_strip_is_recorded_and_checked(
        self,
        tmp_path: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)
        path = tmp_path / "inputDataDaily_CL_20120813.mat"
        path.write_bytes(strip_bytes())

        assert mat_columns.main([str(path), "--price-basis", "raw"]) == 0

        printed = capsys.readouterr().out.splitlines()
        assert printed[1] == (
            "recorded 4 vintages, 11 rows of Close, under inputdatadaily_cl_20120813/, "
            "saved 2007-11-24"
        )
        assert printed[2] == "round trip: every close read back is the file's cl array, NaN for NaN"

    def test_a_failed_strip_round_trip_stops_the_command(
        self,
        tmp_path: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)
        monkeypatch.setattr(mat_columns, "strip_round_trip_differs", lambda path: "moved")
        path = tmp_path / "inputDataDaily_CL_20120813.mat"
        path.write_bytes(strip_bytes())

        assert mat_columns.main([str(path), "--price-basis", "raw"]) == 1

        assert capsys.readouterr().err.startswith("round trip failed: moved.")

    def test_a_flag_file_given_a_price_basis_is_refused_in_one_line(
        self,
        tmp_path: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)
        path = tmp_path / "earnannFile.mat"
        path.write_bytes(flag_bytes(flags=FLAGS))

        assert mat_columns.main([str(path), "--price-basis", "raw"]) == 1

        assert capsys.readouterr().err.splitlines() == [
            "earnannFile.mat: not recorded. the file carries earnann, which is recorded under "
            "the event basis rather than raw"
        ]
        assert read_manifest(data_dir) == []

    def test_a_strip_given_another_price_basis_is_refused_in_one_line(
        self,
        tmp_path: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)
        path = tmp_path / "inputDataDaily_CL_20120813.mat"
        path.write_bytes(strip_bytes())

        assert mat_columns.main([str(path), "--price-basis", "adjusted"]) == 1

        assert capsys.readouterr().err.splitlines() == [
            "inputDataDaily_CL_20120813.mat: not recorded. the file is a futures strip, whose "
            "settlements are recorded under the raw basis rather than adjusted"
        ]
        assert read_manifest(data_dir) == []

    def test_a_strip_given_the_event_basis_is_refused_in_one_line(
        self,
        tmp_path: Path,
        data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)
        path = tmp_path / "inputDataDaily_CL_20120813.mat"
        path.write_bytes(strip_bytes())

        assert mat_columns.main([str(path), "--price-basis", "event"]) == 1

        assert capsys.readouterr().err.splitlines() == [
            "inputDataDaily_CL_20120813.mat: not recorded. the file carries no earnann"
        ]


class TestTheCommandLineOffersNoReturnBasis:
    def test_the_return_basis_is_not_offered(self, tmp_path: Path) -> None:
        """No writer records a return, so the parser refuses it before any file is read."""
        with pytest.raises(SystemExit) as stopped:
            mat_columns.main([str(tmp_path / "absent.mat"), "--price-basis", "return"])

        assert stopped.value.code == 2


#: Two symbols on two calendars, the way Chan's continuous futures saves hold
#: them. CL's first row is unpriced and ES's two first rows are, and row 2 of
#: CL is a different day from row 2 of ES.
FUTURES_DAYS = np.array(
    [
        [NAN, NAN],
        [20120502.0, NAN],
        [20120503.0, 20120501.0],
        [20120504.0, 20120504.0],
    ]
)
FUTURES_CLOSES = np.array(
    [
        [NAN, NAN],
        [104.5, NAN],
        [103.0, 1390.25],
        [98.5, 1366.5],
    ]
)
FUTURES_CREATED = "Mon May 07 12:54:08 2012"


def continuous_bytes(
    *,
    symbols: list[object] | None = None,
    days: np.ndarray = FUTURES_DAYS,
    closes: np.ndarray = FUTURES_CLOSES,
    omit: tuple[str, ...] = (),
) -> bytes:
    """A MATLAB 5 file holding a two-dimensional ``tday``, ``syms`` and the five arrays.

    An empty name is passed as an empty array, which is how MATLAB writes a
    cell holding ``''`` and how the 2012-05-07 save's sixth column reads back.
    """
    names = ["CL", "ES"] if symbols is None else symbols
    syms = np.empty((1, len(names)), dtype=object)
    for index, symbol in enumerate(names):
        syms[0, index] = symbol
    held = {"tday": days, "syms": syms, **arrays_from(closes)}
    buffer = io.BytesIO()
    scipy.io.savemat(buffer, {key: value for key, value in held.items() if key not in omit})
    header = f"MATLAB 5.0 MAT-file, Platform: PCWIN, Created on: {FUTURES_CREATED}"
    return header.encode("ascii").ljust(116, b" ") + buffer.getvalue()[116:]


@pytest.fixture
def futures(tmp_path: Path) -> Path:
    path = tmp_path / "inputDataOHLCDaily_20120504.mat"
    path.write_bytes(continuous_bytes())
    return path


class TestAContinuousSave:
    """Chan's continuous futures saves, which issue 313 records one vintage per symbol."""

    def test_each_symbol_keeps_its_own_days_and_drops_its_leading_cells(self) -> None:
        symbols, days, _ = read_continuous(continuous_bytes())

        assert symbols == ["CL", "ES"]
        assert days == [
            ["2012-05-02", "2012-05-03", "2012-05-04"],
            ["2012-05-01", "2012-05-04"],
        ]

    def test_every_field_lands_on_the_symbol_s_own_days(
        self, futures: Path, data_dir: Path
    ) -> None:
        record_continuous_file(futures, price_basis="adjusted", data_dir=data_dir)

        assert (data_dir / "inputdataohlcdaily_20120504" / "es.csv").read_bytes() == (
            b"Price,Close,High,Low,Open,Volume\n"
            b"Ticker,ES,ES,ES,ES,ES\n"
            b"Date,,,,,\n"
            b"2012-05-01,1390.25,1391.5,1389.5,1390.75,500\n"
            b"2012-05-04,1366.5,1367.75,1365.75,1367.0,700\n"
        )
        entries = read_manifest(data_dir)
        assert {(e.vendor, e.saved_date) for e in entries} == {(VENDOR, "2012-05-07")}
        assert [(e.symbol, e.first_date, e.row_count) for e in entries] == [
            ("CL", "2012-05-02", 3),
            ("ES", "2012-05-01", 2),
        ]

    def test_the_round_trip_finds_every_member_and_says_nothing(
        self, futures: Path, data_dir: Path
    ) -> None:
        record_continuous_file(futures, price_basis="adjusted", data_dir=data_dir)

        assert continuous_round_trip_differs(futures, data_dir=data_dir) is None

    def test_the_round_trip_names_the_member_whose_days_moved(
        self, futures: Path, data_dir: Path
    ) -> None:
        record_continuous_file(futures, price_basis="adjusted", data_dir=data_dir)
        moved = FUTURES_DAYS.copy()
        moved[2, 1] = 20120502.0
        futures.write_bytes(continuous_bytes(days=moved))

        assert continuous_round_trip_differs(futures, data_dir=data_dir) == (
            "ES's days are not its tday column's priced rows"
        )

    @pytest.mark.parametrize(
        ("field", "name"), [("Close", "cl"), ("Open", "op"), ("Volume", "vol")]
    )
    def test_the_round_trip_names_the_field_that_moved(
        self, futures: Path, data_dir: Path, field: str, name: str
    ) -> None:
        record_continuous_file(futures, price_basis="adjusted", data_dir=data_dir)
        arrays = arrays_from(FUTURES_CLOSES)
        arrays[name] = arrays[name] * 2
        buffer = io.BytesIO()
        syms = np.empty((1, 2), dtype=object)
        syms[0, 0], syms[0, 1] = "CL", "ES"
        scipy.io.savemat(buffer, {"tday": FUTURES_DAYS, "syms": syms, **arrays})
        header = f"MATLAB 5.0 MAT-file, Platform: PCWIN, Created on: {FUTURES_CREATED}"
        futures.write_bytes(header.encode("ascii").ljust(116, b" ") + buffer.getvalue()[116:])

        assert continuous_round_trip_differs(futures, data_dir=data_dir) == (
            f"CL's {field} is not the file's {name} column"
        )

    def test_the_round_trip_says_when_a_member_is_missing(
        self, futures: Path, data_dir: Path
    ) -> None:
        record_continuous_file(futures, price_basis="adjusted", data_dir=data_dir)
        rewrite_entry(data_dir, "inputdataohlcdaily_20120504/es.csv", source_workbook="OTHER.mat")

        assert continuous_round_trip_differs(futures, data_dir=data_dir) == (
            "the panel's symbols are not the file's"
        )

    def test_an_empty_name_is_refused_when_no_ruling_names_it(self) -> None:
        payload = continuous_bytes(symbols=["CL", np.array([], dtype="<U1")])

        with pytest.raises(ValueError, match="column 2 has no name, and no ruling names it"):
            read_continuous(payload)

    def test_an_empty_name_a_ruling_names_is_recorded_under_its_position(
        self, tmp_path: Path, data_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        payload = continuous_bytes(symbols=["CL", np.array([], dtype="<U1")])
        monkeypatch.setattr(
            mat_columns,
            "UNNAMED_COLUMNS",
            {hashlib.sha256(payload).hexdigest(): {2: "COLUMN-2"}},
        )
        path = tmp_path / "inputDataOHLCDaily_20120504.mat"
        path.write_bytes(payload)

        entries = record_continuous_file(path, price_basis="adjusted", data_dir=data_dir)

        assert [entry.path for entry in entries] == [
            "inputdataohlcdaily_20120504/cl.csv",
            "inputdataohlcdaily_20120504/column-2.csv",
        ]
        assert continuous_round_trip_differs(path, data_dir=data_dir) is None

    def test_a_ruling_names_only_the_position_it_was_made_for(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A second blank in the same file stops the read rather than being named silently."""
        payload = continuous_bytes(symbols=[np.array([], dtype="<U1"), np.array([], dtype="<U1")])
        monkeypatch.setattr(
            mat_columns,
            "UNNAMED_COLUMNS",
            {hashlib.sha256(payload).hexdigest(): {2: "COLUMN-2"}},
        )

        with pytest.raises(ValueError, match="column 1 has no name"):
            read_continuous(payload)

    def test_the_one_ruling_is_the_2012_05_07_save_s_sixth_column(self) -> None:
        """The owner's 2026-10-04 ruling on issue 313, keyed to that file's sha256."""
        assert mat_columns.UNNAMED_COLUMNS == {
            "3cc01a9623031df25aa45abfc2201869d7a1288c018d8a46e62f7cad1fe72892": {6: "COLUMN-6"}
        }

    def test_a_blank_name_is_refused(self) -> None:
        with pytest.raises(ValueError, match="column 2 has no name"):
            read_continuous(continuous_bytes(symbols=["CL", "  "]))

    def test_a_day_with_no_price_is_refused(self) -> None:
        days = FUTURES_DAYS.copy()
        days[0, 0] = 20120501.0

        with pytest.raises(ValueError, match="CL's tday and close disagree on whether row 1"):
            read_continuous(continuous_bytes(days=days))

    def test_a_price_with_no_day_is_refused(self) -> None:
        days = FUTURES_DAYS.copy()
        days[2, 1] = NAN

        with pytest.raises(ValueError, match="ES's tday and close disagree on whether row 3"):
            read_continuous(continuous_bytes(days=days))

    def test_a_gap_after_the_first_price_is_refused(self) -> None:
        days, closes = FUTURES_DAYS.copy(), FUTURES_CLOSES.copy()
        days[2, 0] = closes[2, 0] = NAN

        with pytest.raises(ValueError, match="CL is unpriced on a row after its first price"):
            read_continuous(continuous_bytes(days=days, closes=closes))

    def test_days_out_of_order_are_refused(self) -> None:
        days = FUTURES_DAYS.copy()
        days[3, 0] = 20120502.0

        with pytest.raises(ValueError, match="CL's trading days are not strictly increasing"):
            read_continuous(continuous_bytes(days=days))

    def test_a_symbol_named_twice_is_refused(self) -> None:
        with pytest.raises(ValueError, match="names a symbol more than once: CL"):
            read_continuous(continuous_bytes(symbols=["CL", "CL"]))

    def test_an_array_that_does_not_fit_the_symbols_is_refused(self) -> None:
        with pytest.raises(ValueError, match="carries 3 symbols"):
            read_continuous(continuous_bytes(symbols=["CL", "ES", "TU"]))

    def test_an_array_that_is_not_tday_s_shape_is_refused(self) -> None:
        with pytest.raises(ValueError, match="is not the shape of tday, 3 by 2"):
            read_continuous(continuous_bytes(days=FUTURES_DAYS[1:]))

    @pytest.mark.parametrize("name", ["tday", "cl", "vol"])
    def test_a_missing_array_is_named(self, name: str) -> None:
        with pytest.raises(ValueError, match=f"the file carries no {name}"):
            read_continuous(continuous_bytes(omit=(name,)))

    def test_a_missing_symbol_list_is_refused_through_symbols_of(self) -> None:
        with pytest.raises(ValueError, match="carries neither of stocks and syms"):
            read_continuous(continuous_bytes(omit=("syms",)))

    def test_a_field_missing_on_a_day_the_close_is_priced_is_refused(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        arrays = arrays_from(FUTURES_CLOSES)
        arrays["hi"][3, 1] = NAN
        syms = np.empty((1, 2), dtype=object)
        syms[0, 0], syms[0, 1] = "CL", "ES"
        buffer = io.BytesIO()
        scipy.io.savemat(buffer, {"tday": FUTURES_DAYS, "syms": syms, **arrays})
        path = tmp_path / "inputDataOHLCDaily_20120504.mat"
        path.write_bytes(
            f"MATLAB 5.0 MAT-file, Platform: PCWIN, Created on: {FUTURES_CREATED}".encode(
                "ascii"
            ).ljust(116, b" ")
            + buffer.getvalue()[116:]
        )

        with pytest.raises(ValueError, match="ES's High and close disagree on whether 2012-05-04"):
            record_continuous_file(path, price_basis="adjusted", data_dir=data_dir)
        assert read_manifest(data_dir) == []


VIX_TEXT = (
    "Date,Open,High,Low,Close,Volume,Adj Close\n"
    "2007-02-26,11.5,11.6,11.1,11.15,0,11.15\n"
    "2007-02-27,11.2,19.0,11.2,18.31,1200,18.31\n"
)


@pytest.fixture
def vix(tmp_path: Path) -> Path:
    path = tmp_path / "VIX.csv"
    path.write_bytes(VIX_TEXT.encode("ascii"))
    return path


class TestAChanCsv:
    """Chan's ``VIX.csv``, which issue 313 records under ``chan-csv``."""

    def test_the_rows_come_back_in_the_lifted_order_without_the_adj_close(self) -> None:
        assert read_csv_rows(VIX_TEXT.encode("ascii")) == [
            ("2007-02-26", 11.15, 11.6, 11.1, 11.5, 0.0),
            ("2007-02-27", 18.31, 19.0, 11.2, 11.2, 1200.0),
        ]

    def test_crlf_line_endings_read_the_same(self) -> None:
        crlf = VIX_TEXT.replace("\n", "\r\n").encode("ascii")

        assert read_csv_rows(crlf) == read_csv_rows(VIX_TEXT.encode("ascii"))

    def test_an_adj_close_that_is_not_the_close_is_refused(self) -> None:
        moved = VIX_TEXT.replace("18.31\n", "18.30\n")

        with pytest.raises(ValueError, match="the Adj Close on 2007-02-27 is 18.30"):
            read_csv_rows(moved.encode("ascii"))

    def test_a_header_that_is_not_yahoo_s_is_refused(self) -> None:
        with pytest.raises(ValueError, match="the header is Date,Close rather than"):
            read_csv_rows(b"Date,Close\n2007-02-26,11.15\n")

    def test_a_short_line_is_refused(self) -> None:
        with pytest.raises(ValueError, match="line 4 holds 6 cells, not 7"):
            read_csv_rows((VIX_TEXT + "2007-02-28,1,1,1,1,0\n").encode("ascii"))

    def test_dates_out_of_order_are_refused(self) -> None:
        lines = VIX_TEXT.splitlines()
        swapped = "\n".join([lines[0], lines[2], lines[1]]) + "\n"

        with pytest.raises(ValueError, match="dates are not strictly increasing"):
            read_csv_rows(swapped.encode("ascii"))

    def test_it_is_recorded_under_its_stem_with_the_stated_date(
        self, vix: Path, data_dir: Path
    ) -> None:
        (entry,) = record_csv_file(
            vix, price_basis="raw", saved_date="2012-05-09", data_dir=data_dir
        )

        assert (entry.vendor, entry.symbol, entry.price_basis, entry.saved_date) == (
            CSV_VENDOR,
            "VIX",
            "raw",
            "2012-05-09",
        )
        assert entry.path == "vix/vix.csv"
        assert (data_dir / "vix" / "vix.csv").read_bytes() == (
            b"Price,Close,High,Low,Open,Volume\n"
            b"Ticker,VIX,VIX,VIX,VIX,VIX\n"
            b"Date,,,,,\n"
            b"2007-02-26,11.15,11.6,11.1,11.5,0\n"
            b"2007-02-27,18.31,19.0,11.2,11.2,1200\n"
        )
        assert csv_round_trip_differs(vix, data_dir=data_dir) is None

    def test_the_vendor_is_neither_the_workbooks_nor_the_mat_files(self) -> None:
        assert CSV_VENDOR == "chan-csv"

    @pytest.mark.parametrize(("field", "column"), [("Close", 4), ("Open", 1), ("Volume", 5)])
    def test_the_round_trip_names_the_field_that_moved(
        self, vix: Path, data_dir: Path, field: str, column: int
    ) -> None:
        record_csv_file(vix, price_basis="raw", saved_date="2012-05-09", data_dir=data_dir)
        lines = VIX_TEXT.splitlines()
        cells = lines[2].split(",")
        cells[column] = "7" if field == "Volume" else "9.5"
        if field == "Close":
            cells[6] = "9.5"
        vix.write_text("\n".join([*lines[:2], ",".join(cells)]) + "\n", encoding="ascii")

        assert csv_round_trip_differs(vix, data_dir=data_dir) == (
            f"the vintage's {field} is not the file's"
        )

    def test_the_round_trip_says_when_the_days_differ(self, vix: Path, data_dir: Path) -> None:
        record_csv_file(vix, price_basis="raw", saved_date="2012-05-09", data_dir=data_dir)
        vix.write_text(VIX_TEXT.replace("2007-02-27", "2007-02-28"), encoding="ascii")

        assert csv_round_trip_differs(vix, data_dir=data_dir) == (
            "the vintage's days are not the file's"
        )


class TestTheCommandReadsAContinuousSaveAndACsv:
    """Issue 313's two shapes, a continuous save by its variables and a CSV by its suffix."""

    def test_a_two_dimensional_tday_is_a_continuous_save(self) -> None:
        assert shape_of(continuous_bytes()) == "continuous"

    def test_a_one_column_tday_stays_on_the_stock_path(self) -> None:
        """A continuous save of one symbol would be a stock file's shape, and reads as one."""
        assert shape_of(mat_bytes()) == "stocks"

    @pytest.fixture
    def in_data_dir(self, data_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", data_dir)
        return data_dir

    def test_a_continuous_save_runs_its_own_reader_and_round_trip(
        self, futures: Path, in_data_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert mat_columns.main([str(futures), "--price-basis", "adjusted"]) == 0

        assert capsys.readouterr().out.splitlines()[1:] == [
            "recorded 2 vintages, 5 rows of Close, High, Low, Open, Volume, under "
            "inputdataohlcdaily_20120504/, saved 2012-05-07",
            "round trip: every member read back is its column's priced rows, every field",
        ]

    def test_a_failed_continuous_round_trip_stops_the_command(
        self,
        futures: Path,
        in_data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(mat_columns, "continuous_round_trip_differs", lambda path: "moved")

        assert mat_columns.main([str(futures), "--price-basis", "adjusted"]) == 1

        assert capsys.readouterr().err.startswith("round trip failed: moved.")

    @pytest.mark.parametrize("name", ["VIX.csv", "VIX.CSV"])
    def test_a_csv_runs_with_the_date_it_is_given(
        self, tmp_path: Path, in_data_dir: Path, capsys: pytest.CaptureFixture[str], name: str
    ) -> None:
        path = tmp_path / name
        path.write_bytes(VIX_TEXT.encode("ascii"))
        argv = [str(path), "--price-basis", "raw", "--saved-date", "2012-05-09"]

        assert mat_columns.main(argv) == 0

        assert capsys.readouterr().out.splitlines()[1:] == [
            "recorded 1 vintages, 2 rows of Close, High, Low, Open, Volume, under vix/, "
            "saved 2012-05-09",
            "round trip: every field read back is the file's, row for row",
        ]

    def test_a_failed_csv_round_trip_stops_the_command(
        self,
        vix: Path,
        in_data_dir: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(mat_columns, "csv_round_trip_differs", lambda path: "moved")
        argv = [str(vix), "--price-basis", "raw", "--saved-date", "2012-05-09"]

        assert mat_columns.main(argv) == 1

        assert capsys.readouterr().err.startswith("round trip failed: moved.")

    def test_a_csv_with_no_date_is_refused_in_one_line(
        self, vix: Path, in_data_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert mat_columns.main([str(vix), "--price-basis", "raw"]) == 1

        assert capsys.readouterr().err.splitlines() == [
            "VIX.csv: not recorded. a .csv carries no saved date, so it needs --saved-date"
        ]
        assert read_manifest(in_data_dir) == []

    def test_a_mat_file_given_a_date_is_refused_in_one_line(
        self, futures: Path, in_data_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        argv = [str(futures), "--price-basis", "adjusted", "--saved-date", "2012-05-07"]

        assert mat_columns.main(argv) == 1

        assert capsys.readouterr().err.splitlines() == [
            "inputDataOHLCDaily_20120504.mat: not recorded. the MAT header records the saved "
            "date, so --saved-date is not taken"
        ]

    def test_a_continuous_save_given_the_event_basis_is_refused(
        self, futures: Path, in_data_dir: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert mat_columns.main([str(futures), "--price-basis", "event"]) == 1

        assert capsys.readouterr().err.splitlines() == [
            "inputDataOHLCDaily_20120504.mat: not recorded. the file carries no earnann"
        ]


class TestAnEmptyNameIsRefusedByEveryReader:
    """The refusal lives in ``symbols_of``, so the stock reader holds it too."""

    def test_the_stock_reader_refuses_an_empty_name(self) -> None:
        payload = mat_bytes(symbols=["AA", np.array([], dtype="<U1"), "KO"])

        with pytest.raises(ValueError, match="column 2 has no name"):
            read_arrays(payload)


class TestACsvCellIsAPlainDecimal:
    """``float`` alone takes more than a vendor's file means, so the reader does not."""

    @pytest.mark.parametrize("cell", ["1_0", " 2", "nan", "inf", "1e3", ""])
    def test_a_cell_float_would_take_is_refused(self, cell: str) -> None:
        bad = VIX_TEXT.replace("11.5,11.6", f"{cell},11.6")

        with pytest.raises(ValueError, match="line 2 holds .*which is not a plain decimal"):
            read_csv_rows(bad.encode("ascii"))

    def test_an_empty_file_is_refused_in_words(self) -> None:
        with pytest.raises(ValueError, match="the file is empty"):
            read_csv_rows(b"")


def continuous_with(arrays: dict[str, np.ndarray], symbols: list[str] = ["CL", "ES"]) -> bytes:  # noqa: B006
    """A continuous save holding ``arrays`` as given, for a case that moves one cell."""
    syms = np.empty((1, len(symbols)), dtype=object)
    for index, symbol in enumerate(symbols):
        syms[0, index] = symbol
    buffer = io.BytesIO()
    scipy.io.savemat(buffer, {"tday": FUTURES_DAYS, "syms": syms, **arrays})
    header = f"MATLAB 5.0 MAT-file, Platform: PCWIN, Created on: {FUTURES_CREATED}"
    return header.encode("ascii").ljust(116, b" ") + buffer.getvalue()[116:]


class TestTheContinuousChecksAreExact:
    """Cases the mutation review found missing, one per check it could loosen unseen."""

    @pytest.mark.parametrize(("field", "name"), [("Close", "cl"), ("Low", "lo")])
    def test_a_one_cell_move_in_the_last_digit_is_named(
        self, futures: Path, data_dir: Path, field: str, name: str
    ) -> None:
        record_continuous_file(futures, price_basis="adjusted", data_dir=data_dir)
        arrays = arrays_from(FUTURES_CLOSES)
        arrays[name][3, 1] = np.nextafter(arrays[name][3, 1], np.inf)
        futures.write_bytes(continuous_with(arrays))

        assert continuous_round_trip_differs(futures, data_dir=data_dir) == (
            f"ES's {field} is not the file's {name} column"
        )

    def test_an_extra_member_under_the_source_is_named(
        self, futures: Path, tmp_path: Path, data_dir: Path
    ) -> None:
        record_continuous_file(futures, price_basis="adjusted", data_dir=data_dir)
        other = tmp_path / "OTHER.mat"
        other.write_bytes(continuous_bytes(symbols=["TU", "VX"]))
        record_continuous_file(other, price_basis="adjusted", data_dir=data_dir)
        rewrite_entry(data_dir, "other/tu.csv", source_workbook="inputDataOHLCDaily_20120504.mat")

        assert continuous_round_trip_differs(futures, data_dir=data_dir) == (
            "the panel's symbols are not the file's"
        )

    def test_lowercase_symbols_round_trip(self, tmp_path: Path, data_dir: Path) -> None:
        path = tmp_path / "inputDataOHLCDaily_20120504.mat"
        path.write_bytes(continuous_bytes(symbols=["cl", "es"]))
        record_continuous_file(path, price_basis="adjusted", data_dir=data_dir)

        assert continuous_round_trip_differs(path, data_dir=data_dir) is None

    def test_a_repeated_day_is_refused(self) -> None:
        days = FUTURES_DAYS.copy()
        days[3, 0] = 20120503.0

        with pytest.raises(ValueError, match="CL's trading days are not strictly increasing"):
            read_continuous(continuous_bytes(days=days))

    def test_a_trailing_unpriced_row_is_refused(self) -> None:
        days, closes = FUTURES_DAYS.copy(), FUTURES_CLOSES.copy()
        days[3, 0] = closes[3, 0] = NAN

        with pytest.raises(ValueError, match="CL is unpriced on the file's last row"):
            read_continuous(continuous_bytes(days=days, closes=closes))

    def test_a_column_priced_on_no_row_is_refused_in_words(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        days, closes = FUTURES_DAYS.copy(), FUTURES_CLOSES.copy()
        days[:, 1] = closes[:, 1] = NAN
        path = tmp_path / "inputDataOHLCDaily_20120504.mat"
        path.write_bytes(continuous_bytes(days=days, closes=closes))

        with pytest.raises(ValueError, match="ES: an empty series has no span"):
            record_continuous_file(path, price_basis="adjusted", data_dir=data_dir)

    def test_a_ruling_never_renames_a_column_that_has_a_name(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        payload = continuous_bytes()
        monkeypatch.setattr(
            mat_columns, "UNNAMED_COLUMNS", {hashlib.sha256(payload).hexdigest(): {2: "COLUMN-2"}}
        )

        assert read_continuous(payload)[0] == ["CL", "ES"]

    def test_a_ruling_for_other_bytes_names_nothing_here(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The real ruling names position 6 of one file, and a blank there in another is refused."""
        names = ["A", "B", "C", "D", "E", np.array([], dtype="<U1")]
        days = np.repeat(FUTURES_DAYS[:, :1], 6, axis=1)
        closes = np.repeat(FUTURES_CLOSES[:, :1], 6, axis=1)

        with pytest.raises(ValueError, match="column 6 has no name"):
            read_continuous(continuous_bytes(symbols=names, days=days, closes=closes))


class TestTheCsvChecksAreExact:
    def test_a_repeated_date_is_refused(self) -> None:
        lines = VIX_TEXT.splitlines()
        repeated = "\n".join([*lines, lines[2]]) + "\n"

        with pytest.raises(ValueError, match="dates are not strictly increasing"):
            read_csv_rows(repeated.encode("ascii"))

    def test_an_adj_close_spelled_differently_but_equal_is_taken(self) -> None:
        spelled = VIX_TEXT.replace("18.31,1200,18.31", "18.30,1200,18.3")

        assert read_csv_rows(spelled.encode("ascii"))[1][1] == 18.3

    def test_a_lowercase_file_name_records_an_uppercase_symbol(
        self, tmp_path: Path, data_dir: Path
    ) -> None:
        path = tmp_path / "vix.csv"
        path.write_bytes(VIX_TEXT.encode("ascii"))

        (entry,) = record_csv_file(
            path, price_basis="raw", saved_date="2012-05-09", data_dir=data_dir
        )

        assert entry.symbol == "VIX"
        assert csv_round_trip_differs(path, data_dir=data_dir) is None

    def test_an_extra_member_under_the_source_is_named(
        self, vix: Path, tmp_path: Path, data_dir: Path
    ) -> None:
        record_csv_file(vix, price_basis="raw", saved_date="2012-05-09", data_dir=data_dir)
        other = tmp_path / "OTHER.csv"
        other.write_bytes(VIX_TEXT.encode("ascii"))
        record_csv_file(other, price_basis="raw", saved_date="2012-05-09", data_dir=data_dir)
        rewrite_entry(data_dir, "other/other.csv", source_workbook="VIX.csv")

        assert csv_round_trip_differs(vix, data_dir=data_dir) == (
            "the panel holds OTHER, VIX rather than VIX"
        )
