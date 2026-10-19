"""Pins for the Open Source Asset Pricing long-short returns, and refusals of their reader.

Every pin reads release 202510 of Chen and Zimmermann's project, downloaded on
2026-10-19 through ``OpenAP(202510).dl_port('op', 'pandas')``, whose one source file is
``PredictorPortsFull.csv``. Each committed file holds one signal's long-short
rows of that file, byte for byte: equal-weighted, long the extreme quantile the
signal predicts high and short the other, with each signal's quantile, filter
and rebalancing as ``data/README.md`` names them. Every return is in percent a
month, dated the last trading day of the month.

These are the project's portfolios and not Chan's rules, so no number here is
a replication. The comparison issues read them.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from chan import open_asset_pricing
from chan.open_asset_pricing import (
    HEADER,
    SIGNALS,
    long_short_returns,
    long_short_symbol,
    long_short_vintage,
)
from chan.paths import DATA_DIR
from chan.vintage import MANIFEST_NAME, VintageEntry, VintageUnavailable

#: The month every signal's return is pinned at, picked because all five hold it.
PINNED_MONTH = "2008-10-31"

#: Signal to ``(path, rows, first month, last month, return in PINNED_MONTH, sha256)``.
#:
#: The return is the float the file's text spells, compared exactly, so a
#: restated month in a later release fails here by name.
PINS = {
    "MomSeasonShort": (
        "openassetpricing-202510_momseasonshort-ls_return_1927-01-31_2024-12-31_dl2026-10-19.csv",
        1176,
        "1927-01-31",
        "2024-12-31",
        -2.60678312550788,
        "225556addb0f6353ffa3517aed55ab8bc587d2733dc312b05f405db34e2483ce",
    ),
    "Mom12m": (
        "openassetpricing-202510_mom12m-ls_return_1927-01-31_2024-12-31_dl2026-10-19.csv",
        1176,
        "1927-01-31",
        "2024-12-31",
        4.92501120098039,
        "04edd873b117fb0e70db2638ad15df7e54cc18c58e75740eb82ef62277aaa53b",
    ),
    "STreversal": (
        "openassetpricing-202510_streversal-ls_return_1926-02-27_2024-12-31_dl2026-10-19.csv",
        1187,
        "1926-02-27",
        "2024-12-31",
        -8.72404176272541,
        "78c0a48bf7fe096f8e9b683f00a502c6bdde236e7dd6f8c628d25bfb4154c812",
    ),
    "BetaFP": (
        "openassetpricing-202510_betafp-ls_return_1928-04-30_2024-12-31_dl2026-10-19.csv",
        1161,
        "1928-04-30",
        "2024-12-31",
        -18.9350781472844,
        "8268b2edb52ab5e5b7f5b8bdb24139aeb03eba789eab053bc6d9898b765bc62c",
    ),
    "AnnouncementReturn": (
        "openassetpricing-202510_announcementreturn-ls_return_1971-09-30_2024-12-31_dl2026-10-19.csv",
        640,
        "1971-09-30",
        "2024-12-31",
        4.23835753193976,
        "99c408d4db5af9e7341141a32be1eacf3a221afd7a921ea9300a1612016ac607",
    ),
}


class TestTheVintages:
    """Which file each signal reads, so a second download or release cannot slip in."""

    def test_every_committed_signal_is_pinned(self) -> None:
        assert set(PINS) == set(SIGNALS)

    @pytest.mark.parametrize("signal", SIGNALS)
    def test_the_entry_is_the_pinned_download(self, signal: str) -> None:
        path, rows, first, last, _, sha256 = PINS[signal]
        entry = long_short_vintage(signal)

        assert (entry.path, entry.row_count, entry.first_date, entry.last_date) == (
            path,
            rows,
            first,
            last,
        )
        assert entry.sha256 == sha256
        assert (entry.vendor, entry.symbol, entry.price_basis, entry.download_date) == (
            "openassetpricing-202510",
            f"{signal.upper()}-LS",
            "return",
            "2026-10-19",
        )
        assert entry.vendor_column == (
            f"rows signalname={signal} port=LS of PredictorPortsFull.csv, "
            f"OpenAP(202510).dl_port('op', 'pandas')"
        )

    @pytest.mark.parametrize("signal", SIGNALS)
    def test_the_file_keeps_the_source_header_and_holds_only_its_signals_long_short_rows(
        self, signal: str
    ) -> None:
        """Read off the bytes rather than through the reader, so the two checks are separate."""
        lines = (DATA_DIR / PINS[signal][0]).read_text(encoding="utf-8").splitlines()

        assert lines[0] == ",".join(HEADER)
        assert {tuple(line.split(",")[:2]) for line in lines[1:]} == {(signal, "LS")}


class TestTheReturns:
    @pytest.mark.parametrize("signal", SIGNALS)
    def test_the_first_and_last_month_and_one_return(self, signal: str) -> None:
        _, rows, first, last, pinned, _ = PINS[signal]
        _, returns = long_short_returns(signal)

        assert len(returns) == rows
        assert returns.index[0] == pd.Timestamp(first)
        assert returns.index[-1] == pd.Timestamp(last)
        assert returns.loc[PINNED_MONTH] == pinned

    @pytest.mark.parametrize("signal", SIGNALS)
    def test_every_calendar_month_of_the_span_has_exactly_one_row(self, signal: str) -> None:
        """A comparison joining on months can rely on no month missing from the release."""
        _, returns = long_short_returns(signal)
        months = returns.index.to_period("M")

        assert list(months) == list(pd.period_range(months[0], months[-1], freq="M"))

    def test_the_returns_are_in_percent_a_month(self) -> None:
        """Short-term reversal's worst month is a double-digit percent, not a fraction of one."""
        _, returns = long_short_returns("STreversal")

        assert returns.abs().max() > 10
        assert returns.name == "STreversal long-short, percent a month"


def _with_one_vintage(tmp_path: Path, signal: str, payload: bytes | None = None) -> Path:
    """A data directory holding one signal's committed line, and either its file or ``payload``.

    The line is the committed one with its sha256 recomputed from ``payload``,
    so a refusal below comes from the reader's own checks rather than from the
    hash.
    """
    entry = long_short_vintage(signal)
    directory = tmp_path / "data"
    directory.mkdir()
    if payload is None:
        shutil.copyfile(DATA_DIR / entry.path, directory / entry.path)
        line = entry.as_json()
    else:
        (directory / entry.path).write_bytes(payload)
        fields = json.loads(entry.as_json())
        fields["sha256"] = hashlib.sha256(payload).hexdigest()
        line = VintageEntry(**fields).as_json()
    (directory / MANIFEST_NAME).write_text(line + "\n", encoding="utf-8")
    return directory


class TestTheReaderRefuses:
    def test_bytes_whose_checksum_does_not_match(self, tmp_path: Path) -> None:
        directory = _with_one_vintage(tmp_path, "Mom12m")
        target = directory / PINS["Mom12m"][0]
        target.write_bytes(target.read_bytes().replace(b"4.92501120098039", b"4.92501120098038"))

        with pytest.raises(VintageUnavailable, match="hash to .* and the manifest records"):
            long_short_returns("Mom12m", data_dir=directory)

    def test_the_copy_reads_before_it_is_altered(self, tmp_path: Path) -> None:
        """So the refusal above is the alteration's and not the copy's."""
        _, returns = long_short_returns("Mom12m", data_dir=_with_one_vintage(tmp_path, "Mom12m"))

        assert returns.loc[PINNED_MONTH] == PINS["Mom12m"][4]

    def test_another_signals_rows_under_a_matching_hash(self, tmp_path: Path) -> None:
        other = (DATA_DIR / PINS["MomSeasonShort"][0]).read_bytes()
        directory = _with_one_vintage(tmp_path, "Mom12m", other)

        with pytest.raises(VintageUnavailable, match="line 2 is the 'LS' row of 'MomSeasonShort'"):
            long_short_returns("Mom12m", data_dir=directory)

    def test_a_decile_row_among_the_long_short_rows(self, tmp_path: Path) -> None:
        payload = (",".join(HEADER) + "\nMom12m,10,1927-01-31,1.5,NA,50,0\n").encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(VintageUnavailable, match="line 2 is the '10' row of 'Mom12m'"):
            long_short_returns("Mom12m", data_dir=directory)

    def test_a_header_that_is_not_the_sources(self, tmp_path: Path) -> None:
        payload = b"Date,Close\n1927-01-31,1.5\n"
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(VintageUnavailable, match="the header reads 'Date,Close'"):
            long_short_returns("Mom12m", data_dir=directory)

    @pytest.mark.parametrize(
        "rows",
        [
            ["1927-02-28", "1927-01-31"],
            ["1927-01-31", "1927-01-31"],
            ["1927-01-31", "1927-02"],
        ],
    )
    def test_dates_out_of_order_repeated_or_malformed(self, tmp_path: Path, rows) -> None:
        body = "".join(f"Mom12m,LS,{day},1.5,NA,50,50\n" for day in rows)
        payload = (",".join(HEADER) + "\n" + body).encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(VintageUnavailable, match=f"line 3 is dated '{rows[1]}'"):
            long_short_returns("Mom12m", data_dir=directory)

    @pytest.mark.parametrize("value", ["NA", "inf", "nan", ""])
    def test_a_return_that_is_not_a_finite_number(self, tmp_path: Path, value: str) -> None:
        payload = (",".join(HEADER) + f"\nMom12m,LS,1927-01-31,{value},NA,50,50\n").encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(VintageUnavailable, match=f"line 2 holds the return '{value}'"):
            long_short_returns("Mom12m", data_dir=directory)

    def test_a_row_missing_a_cell(self, tmp_path: Path) -> None:
        payload = (",".join(HEADER) + "\nMom12m,LS,1927-01-31,1.5,NA,50\n").encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(
            VintageUnavailable, match="line 2 holds 6 cells where the header names 7"
        ):
            long_short_returns("Mom12m", data_dir=directory)

    def test_a_header_and_no_rows(self, tmp_path: Path) -> None:
        directory = _with_one_vintage(tmp_path, "Mom12m", (",".join(HEADER) + "\n").encode())

        with pytest.raises(VintageUnavailable, match="holds a header and no rows"):
            long_short_returns("Mom12m", data_dir=directory)

    @pytest.mark.parametrize("signal", ["momseasonshort", "MomSeason", "Mom12M"])
    def test_a_signal_not_committed_under_that_spelling(self, signal: str) -> None:
        with pytest.raises(ValueError, match=f"{signal!r} is not a committed signal"):
            long_short_symbol(signal)


def test_the_release_is_the_one_the_vendor_names() -> None:
    assert open_asset_pricing.VENDOR == f"openassetpricing-{open_asset_pricing.RELEASE}"


class TestTheReaderRefusesWhatTheReviewFound:
    """Cases a mutation review of the reader found no test refusing.

    Each one is a weaker check that let a malformed file through: a header in
    another order, a row with a cell too many, a date out of order against the
    row before it rather than the first row, a date with text after it, and a
    signal named in another case.
    """

    def test_the_sources_names_in_another_order(self, tmp_path: Path) -> None:
        header = "signalname,port,ret,date,signallag,Nlong,Nshort"
        payload = f"{header}\nMom12m,LS,1.5,1927-01-31,NA,50,50\n".encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(VintageUnavailable, match=f"the header reads '{header}'"):
            long_short_returns("Mom12m", data_dir=directory)

    def test_a_row_with_a_cell_too_many(self, tmp_path: Path) -> None:
        payload = (",".join(HEADER) + "\nMom12m,LS,1927-01-31,1.5,NA,50,50,9\n").encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(
            VintageUnavailable, match="line 2 holds 8 cells where the header names 7"
        ):
            long_short_returns("Mom12m", data_dir=directory)

    def test_a_date_earlier_than_the_row_before_it_but_not_the_first(self, tmp_path: Path) -> None:
        body = "".join(
            f"Mom12m,LS,{day},1.5,NA,50,50\n" for day in ("1927-01-31", "1927-03-31", "1927-02-28")
        )
        payload = (",".join(HEADER) + "\n" + body).encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(VintageUnavailable, match="line 4 is dated '1927-02-28'"):
            long_short_returns("Mom12m", data_dir=directory)

    def test_a_date_with_text_after_it(self, tmp_path: Path) -> None:
        payload = (",".join(HEADER) + "\nMom12m,LS,1927-01-31x,1.5,NA,50,50\n").encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(VintageUnavailable, match="line 2 is dated '1927-01-31x'"):
            long_short_returns("Mom12m", data_dir=directory)

    def test_the_signal_named_in_another_case(self, tmp_path: Path) -> None:
        payload = (",".join(HEADER) + "\nmom12m,LS,1927-01-31,1.5,NA,50,50\n").encode()
        directory = _with_one_vintage(tmp_path, "Mom12m", payload)

        with pytest.raises(VintageUnavailable, match="line 2 is the 'LS' row of 'mom12m'"):
            long_short_returns("Mom12m", data_dir=directory)

    def test_the_index_is_named_for_the_sources_date_column(self) -> None:
        _, returns = long_short_returns("Mom12m")

        assert returns.index.name == "date"
