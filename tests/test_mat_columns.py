"""What reading one of Chan's ``.mat`` files must do, on a file built here.

Chan's two files are not committed, so every case writes a small MATLAB 5 file
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
    VENDOR,
    columns_of,
    read_closes,
    record_mat_closes,
    round_trip_differs,
    saved_date_of,
)
from chan.series import load_panel
from chan.vintage import MANIFEST_NAME, read_manifest
from tests.support.committed_vintages import rewrite_entry

CREATED = "Sat Nov 24 13:12:39 2007"
DAYS = [20071119, 20071120, 20071121, 20071123]
SYMBOLS = ["AA", "BF.B", "KO"]
NAN = float("nan")
CLOSES = [
    [30.0, NAN, 60.0],
    [31.0, 70.0, NAN],
    [NAN, 71.0, 61.0],
    [32.5, 72.0, 62.3],
]


def mat_bytes(
    *,
    created: str = CREATED,
    days: list[int] = DAYS,
    symbols: list[str] = SYMBOLS,
    closes: list[list[float]] = CLOSES,
    omit: tuple[str, ...] = (),
) -> bytes:
    """A MATLAB 5 file holding ``tday``, ``stocks`` and ``cl`` the way Chan's do.

    ``stocks`` is a cell array of strings, written as an object array, and the
    header's first 116 bytes are replaced with one carrying ``created``.
    """
    stocks = np.empty((len(symbols), 1), dtype=object)
    for index, symbol in enumerate(symbols):
        stocks[index, 0] = symbol
    held = {
        "tday": np.array(days, dtype=np.int32).reshape(-1, 1),
        "stocks": stocks,
        "cl": np.array(closes, dtype=float),
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


class TestTheThreeArraysAreCheckedAgainstEachOther:
    def test_the_days_the_symbols_and_the_closes_come_back_together(self) -> None:
        days, symbols, closes = read_closes(mat_bytes())

        assert days == ["2007-11-19", "2007-11-20", "2007-11-21", "2007-11-23"]
        assert symbols == SYMBOLS
        assert closes.shape == (4, 3)

    def test_a_missing_array_is_named(self) -> None:
        with pytest.raises(ValueError, match="carries no cl"):
            read_closes(mat_bytes(omit=("cl",)))

    def test_days_out_of_order_are_refused(self) -> None:
        with pytest.raises(ValueError, match="not strictly increasing"):
            read_closes(mat_bytes(days=[20071119, 20071121, 20071120, 20071123]))

    def test_a_symbol_named_twice_is_refused(self) -> None:
        with pytest.raises(ValueError, match="more than once: AA"):
            read_closes(mat_bytes(symbols=["AA", "AA", "KO"]))

    def test_closes_that_do_not_fit_the_days_and_symbols_are_refused(self) -> None:
        with pytest.raises(ValueError, match="cl is 4 by 3 and the file carries 4 days and 2"):
            read_closes(mat_bytes(symbols=["AA", "KO"]))


class TestAMissingCellIsAMissingRow:
    def test_each_column_holds_only_the_days_it_was_priced(self) -> None:
        columns = columns_of(*read_closes(mat_bytes()))

        assert columns["AA"] == [("2007-11-19", 30.0), ("2007-11-20", 31.0), ("2007-11-23", 32.5)]
        assert columns["BF.B"] == [
            ("2007-11-20", 70.0),
            ("2007-11-21", 71.0),
            ("2007-11-23", 72.0),
        ]
        assert [day for day, _ in columns["KO"]] == ["2007-11-19", "2007-11-21", "2007-11-23"]


class TestRecordingAFile:
    def test_every_column_is_recorded_under_the_vendor_with_the_header_s_date(
        self, mat: Path, data_dir: Path
    ) -> None:
        entries = record_mat_closes(mat, price_basis="adjusted", data_dir=data_dir)

        assert [entry.path for entry in entries] == [
            "spx_20071123/aa.csv",
            "spx_20071123/bf.b.csv",
            "spx_20071123/ko.csv",
        ]
        assert {(e.vendor, e.saved_date, e.source_workbook) for e in entries} == {
            (VENDOR, "2007-11-24", "SPX_20071123.mat")
        }
        assert read_manifest(data_dir) == entries

    def test_the_vendor_is_not_the_workbooks_one(self) -> None:
        """KO and PEP are in the S&P 500 file and already committed from his workbooks."""
        assert VENDOR == "chan-mat"

    def test_the_round_trip_finds_the_file_s_array_and_says_nothing(
        self, mat: Path, data_dir: Path
    ) -> None:
        record_mat_closes(mat, price_basis="adjusted", data_dir=data_dir)

        assert round_trip_differs(mat, data_dir=data_dir) is None
        _, panel = load_panel("SPX_20071123.mat", data_dir=data_dir)
        assert np.array_equal(panel.to_numpy(), np.array(CLOSES), equal_nan=True)

    def test_the_round_trip_says_when_a_member_is_missing(self, mat: Path, data_dir: Path) -> None:
        record_mat_closes(mat, price_basis="adjusted", data_dir=data_dir)
        rewrite_entry(data_dir, "spx_20071123/ko.csv", source_workbook="OTHER.mat")

        assert (
            round_trip_differs(mat, data_dir=data_dir) == "the panel's symbols are not the file's"
        )

    def test_the_round_trip_says_when_a_close_moved(self, mat: Path, data_dir: Path) -> None:
        record_mat_closes(mat, price_basis="adjusted", data_dir=data_dir)
        mat.write_bytes(mat_bytes(closes=[[*row[:2], row[2] * 2] for row in CLOSES]))

        assert round_trip_differs(mat, data_dir=data_dir) == (
            "the panel's closes are not the file's cl array"
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
            "recorded 3 vintages, 9 closes, under spx_20071123/, saved 2007-11-24"
        )
        assert printed[2].startswith("round trip: the panel read back is the file's cl array")

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
