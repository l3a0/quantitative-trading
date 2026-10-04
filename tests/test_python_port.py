"""The currency series lifted from Chan's 2018 Python port, held to their source and to each other.

[Issue 301](https://github.com/l3a0/quantitative-trading/issues/301) committed
seven members of ``PythonCodesAndData.zip`` byte for byte under
``data/pythoncodesanddata/``. The manifest checks in ``tests/test_vintage.py``
hold each file to its own entry, which says the bytes did not move since they
were committed. These say what the bytes are.

1. Each committed file is its zip member, by the member's sha256.
2. The minute file's 16:59 closes equal the daily USD.CAD file on every date
   the two share.
3. The AUD.USD and USD.CAD daily files carry the same dates, which Example
   5.1's script assumes.
4. AUD.CAD agrees with AUD.USD times USD.CAD.
5. AUD.CAD agrees with the inverse of the committed yfinance ``CADAUD=X``
   download, loosely.

The sixth check the issue names, the rate and return files against the ``.mat``
files Chan's MATLAB loaded, is a measurement written in ``data/README.md``
rather than a test, because the ``.mat`` files are not committed.

The figures pinned here are the zip fetched from ericnberwick/EpchanPreview at
``e4bc46f`` and the yfinance ``CADAUD=X`` raw vintage downloaded on 2026-10-02.
"""

from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd
import pytest

from chan.paths import DATA_DIR
from chan.series import (
    DAILY_CLOSE_MINUTE,
    _parse_close,
    load_minute_close,
    load_vintage,
    minute_close,
)
from chan.vintage import VintageUnavailable, read_vintage, resolve_vintage
from tests.support.committed_vintages import PYTHON_PORT

#: The sha256 of each member of ``PythonCodesAndData.zip``, as ``unzip -p`` hands it over.
#:
#: The manifest records the committed file's sha256 and a test holds the file
#: to it, so a hand edit to both would still pass there. This pin is the zip's
#: rather than the file's, measured from the zip whose own sha256
#: ``data/README.md`` records, so it fails that edit.
ZIP_MEMBERS = {
    "inputData_USDCAD.csv": "6e0ed7f24792b26825fd4b6fa37685b82a5e434dbd39e4a0df00d04f8d1e6a0e",
    "inputData_USDCAD_20120426.csv": (
        "c6adf99f0ec940be7d5387f608ae1855fe8f3a8f2919013531e2d223e8c5e352"
    ),
    "inputData_AUDUSD_20120426.csv": (
        "7fc04e1916e47b3789916c24005ea57d3ce068e5f4e28b7d46f7eb8956d6b9b8"
    ),
    "inputData_AUDCAD_20120426.csv": (
        "ed353c9367c4b61dbaeeb64f04b57500d5c2ccf5a51cf4a5b756133795516873"
    ),
    "AUD_interestRate.csv": "8938e1d2eee437661ec3c634ce4b29c2e613013c84598aa97309fa307e4c7f9e",
    "CAD_interestRate.csv": "73145afbd54f17ed6d1687eb13f18f8d193eb31c3bb80e80a9c3842adc120183",
    "AUDCAD_unequal_ret.csv": "b0b67c8e989d75fb2ae5607d1a6358123a496e7bed02072b0898f7993624d978",
}

#: The saved date of the minute file, which tells it apart from the daily USD.CAD file.
MINUTES = "2018-10-13"


def daily(symbol: str) -> pd.Series:
    """One of the port's three daily files, through the parse every daily series takes."""
    (saved,) = [pin[3] for pin in PYTHON_PORT.values() if pin[1] == symbol and pin[5] == "daily"]
    entry = resolve_vintage(vendor="chan-py", symbol=symbol, price_basis="raw", dated=saved)
    return _parse_close(read_vintage(entry), symbol)


@pytest.fixture(scope="module")
def at_1659() -> pd.Series:
    return load_minute_close("USDCAD", dated=MINUTES)[1]


class TestEachFileIsItsZipMember:
    def test_every_committed_file_hashes_to_its_member(self) -> None:
        """Every file in the directory, and no member missing from it."""
        committed = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (DATA_DIR / "pythoncodesanddata").iterdir()
        }

        assert committed == ZIP_MEMBERS

    def test_the_pin_names_the_same_seven(self) -> None:
        assert {path.rpartition("/")[2] for path in PYTHON_PORT} == set(ZIP_MEMBERS)


class TestTheCloseAt1659:
    """The 16:59 bar is the daily close Chan's MATLAB and his Python both read."""

    def test_it_is_one_close_a_day_over_the_file_s_span(self, at_1659) -> None:
        assert at_1659.name == "USDCAD"
        assert len(at_1659) == 1216
        assert at_1659.index.is_unique
        assert (str(at_1659.index[0].date()), str(at_1659.index[-1].date())) == (
            "2007-07-23",
            "2012-03-28",
        )

    def test_the_days_with_no_close_are_sundays_two_holidays_and_one_early_close(
        self, at_1659
    ) -> None:
        """250 of the file's 1,466 dates hold no bar at 16:59, and none is a trading day lost."""
        frame = pd.read_csv(DATA_DIR / "pythoncodesanddata" / "inputData_USDCAD.csv", dtype=str)
        dates = pd.DatetimeIndex(pd.to_datetime(frame["Date"].unique(), format="%Y%m%d"))
        missing = dates.difference(at_1659.index)

        assert (len(dates), len(missing)) == (1466, 250)
        assert int((missing.dayofweek == 6).sum()) == 245
        assert [str(day.date()) for day in missing[missing.dayofweek != 6]] == [
            "2007-12-25",
            "2008-01-01",
            "2008-12-25",
            "2009-01-01",
            "2011-12-23",
        ]

    def test_no_bar_falls_in_the_pause_after_17_00(self) -> None:
        """What says the clock is New York time with daylight saving.

        The currency market pauses from 17:00 to 17:15 New York time. A file
        kept in a fixed offset would move that gap by an hour twice a year, so
        some bar would land in it.
        """
        frame = pd.read_csv(DATA_DIR / "pythoncodesanddata" / "inputData_USDCAD.csv", dtype=str)
        times = frame["Time"].astype(int)

        assert not ((times >= 1700) & (times < 1715)).any()
        assert not frame.duplicated(["Date", "Time"]).any()

    def test_it_equals_the_daily_file_on_every_shared_date(self, at_1659) -> None:
        """Check 2. No tolerance, because none is needed: the two agree exactly."""
        closes = daily("USDCAD")
        shared = at_1659.index.intersection(closes.index)

        assert len(shared) == 841
        assert (str(shared[0].date()), str(shared[-1].date())) == ("2009-01-02", "2012-03-28")
        assert (at_1659.loc[shared] == closes.loc[shared]).all()
        assert len(closes.index.difference(at_1659.index)) == 21

    def test_another_minute_reads_another_close(self) -> None:
        """``at`` is read, rather than 16:59 being written into the filter."""
        _, at_1658 = load_minute_close("USDCAD", dated=MINUTES, at=1658)

        assert DAILY_CLOSE_MINUTE == 1659
        assert len(at_1658) > 0
        assert not at_1658.equals(load_minute_close("USDCAD", dated=MINUTES)[1])

    def test_the_symbol_is_matched_whatever_its_case(self, at_1659) -> None:
        assert load_minute_close("usdcad", dated=MINUTES)[1].equals(at_1659)

    def test_bars_out_of_date_order_come_back_in_it(self) -> None:
        entry = resolve_vintage(vendor="chan-py", symbol="USDCAD", price_basis="raw", dated=MINUTES)
        payload = b"Date,Time,Close\n20200103,1659,2.5\n20200102,1659,1.25\n"

        closes = minute_close(payload, entry)

        assert [str(day.date()) for day in closes.index] == ["2020-01-02", "2020-01-03"]
        assert list(closes) == [1.25, 2.5]

    def test_a_daily_file_is_refused_by_the_minute_reader(self) -> None:
        with pytest.raises(VintageUnavailable, match="holds no minute bars"):
            load_minute_close("USDCAD", dated="2018-12-12")

    def test_the_minute_file_is_refused_by_the_daily_parse(self) -> None:
        """Its second column is the time, so reading it as a close would hand back times."""
        entry = resolve_vintage(vendor="chan-py", symbol="USDCAD", price_basis="raw", dated=MINUTES)

        with pytest.raises(VintageUnavailable, match="holds minute bars"):
            _parse_close(read_vintage(entry), entry.symbol)

    def test_the_minute_reader_takes_a_buffer_with_either_line_ending(self) -> None:
        entry = resolve_vintage(vendor="chan-py", symbol="USDCAD", price_basis="raw", dated=MINUTES)
        payload = b"Date,Time,Close\n20200102,1658,1.5\n20200102,1659,1.25\n"

        for each in (payload, payload.replace(b"\n", b"\r\n")):
            closes = minute_close(each, entry)
            assert list(closes) == [1.25]
            assert str(closes.index[0].date()) == "2020-01-02"


class TestTheDailyFilesAgree:
    def test_aud_usd_and_usd_cad_carry_the_same_dates(self) -> None:
        """Check 3. Example 5.1's script takes one file's dates for both."""
        aud, usd = daily("AUDUSD"), daily("USDCAD")

        assert len(aud) == 862
        assert aud.index.equals(usd.index)

    def test_aud_cad_is_aud_usd_times_usd_cad(self) -> None:
        """Check 4, on the 862 dates all three share."""
        aud, usd, cross = daily("AUDUSD"), daily("USDCAD"), daily("AUDCAD")
        shared = cross.index.intersection(aud.index)
        gap = (cross.loc[shared] / (aud.loc[shared] * usd.loc[shared]) - 1).abs()

        assert len(shared) == 862
        assert f"{gap.median():.1e}" == "6.0e-05"
        assert (round(gap.max() * 100, 2), str(gap.idxmax().date())) == (0.19, "2009-05-27")

    def test_aud_cad_is_near_the_inverse_of_yfinance_s_cad_aud(self) -> None:
        """Check 5. yfinance does not record the hour its currency close is
        taken at, so this bounds a gross error and no more."""
        cross = daily("AUDCAD")
        _, cad_aud = load_vintage("CADAUD=X", unadjusted=True)
        shared = cross.index.intersection(cad_aud.index)
        gap = (cross.loc[shared] * cad_aud.loc[shared] - 1).abs()

        assert (len(shared), len(cross)) == (1220, 1237)
        assert round(gap.median() * 100, 2) == 0.16
        assert round(float(np.quantile(gap, 0.95)) * 100, 2) == 0.83
        assert int((gap > 0.02).sum()) == 3
        assert (round(gap.max() * 100, 1), str(gap.idxmax().date())) == (6.6, "2008-10-10")
