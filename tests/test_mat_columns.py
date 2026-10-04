"""What reading one of Chan's ``.mat`` files must do, on a file built here.

Chan's ``.mat`` files are not committed, so every case writes a small MATLAB 5 file
with ``scipy.io.savemat`` and stamps the header's creation date in by hand,
because ``savemat`` writes today's. The committed result of reading the real
files is pinned in ``tests/test_series.py``, where
``TestTheCommittedPanelsAreChansArrays`` reads the panels back.
"""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pytest
import scipy.io

from chan import mat_columns
from chan.mat_columns import (
    ARRAYS,
    VENDOR,
    columns_of,
    flag_round_trip_differs,
    read_arrays,
    read_flags,
    read_strip,
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


def mat_bytes(
    *,
    created: str = CREATED,
    days: list[int] = DAYS,
    symbols: list[str] = SYMBOLS,
    arrays: dict[str, np.ndarray] | None = None,
    omit: tuple[str, ...] = (),
) -> bytes:
    """A MATLAB 5 file holding ``tday``, ``stocks`` and the five arrays the way Chan's do.

    ``stocks`` is a cell array of strings, written as an object array, and the
    header's first 116 bytes are replaced with one carrying ``created``.
    """
    stocks = np.empty((len(symbols), 1), dtype=object)
    for index, symbol in enumerate(symbols):
        stocks[index, 0] = symbol
    held = {
        "tday": np.array(days, dtype=np.int32).reshape(-1, 1),
        "stocks": stocks,
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


def flag_bytes(*, flags: np.ndarray, symbols: list[str] = SYMBOLS, days: list[int] = DAYS) -> bytes:
    """A MATLAB 5 file holding ``tday``, ``stocks`` and ``earnann``, as Chan's flag file does."""
    stocks = np.empty((len(symbols), 1), dtype=object)
    for index, symbol in enumerate(symbols):
        stocks[index, 0] = symbol
    buffer = io.BytesIO()
    scipy.io.savemat(
        buffer,
        {
            "tday": np.array(days, dtype=np.int32).reshape(-1, 1),
            "stocks": stocks,
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
        """Chan's ETF file carries ``syms``, and the stock reader is what
        refuses it until it learns that spelling."""
        syms = np.empty((1, 3), dtype=object)
        syms[0, :] = SYMBOLS
        payload = mat_bytes(omit=("stocks",))
        buffer = io.BytesIO()
        held = scipy.io.loadmat(io.BytesIO(payload))
        scipy.io.savemat(
            buffer, {**{k: v for k, v in held.items() if not k.startswith("__")}, "syms": syms}
        )

        assert shape_of(buffer.getvalue()) == "stocks"

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
