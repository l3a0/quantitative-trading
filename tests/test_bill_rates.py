"""Pins for the three-month Treasury-bill figures the risk parity post quotes.

This file is the single authority for those figures. The risk parity post,
still on [PR #185](https://github.com/l3a0/quantitative-trading/pull/185),
quotes them and derives none of them, and ``src/chan/bill_rates.py`` carries
the reasoning.

Every pin reads one vintage: FRED's TB3MS, downloaded 2026-09-30 and committed
as ``data/fred_tb3ms_rate_1934-01-01_2026-08-01_dl2026-09-30.csv``, 1,112
monthly rows from January 1934 to August 2026, each the month's average rate in
percent a year. The values below are decimals a year, so 1.744% is 0.01744.

The windows come from the risk parity run, whose common span of SPY and AGG
returns is 2003-09-30 to 2026-09-17. The full calendar months inside it are
October 2003 to August 2026. The Federal Reserve's first rise of the cycle was
announced on 16 March 2022, so March 2022 averages days on both sides of it and
is left out of both halves. That is why the halves hold 221 and 53 months and
the whole holds 275.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from chan.bill_rates import (
    average,
    bill_vintage,
    monthly_rates,
    months_below,
    months_in,
)
from chan.paths import DATA_DIR
from chan.vintage import (
    MANIFEST_NAME,
    VintageEntry,
    VintageUnavailable,
    record_vintage,
)

VINTAGE = "fred_tb3ms_rate_1934-01-01_2026-08-01_dl2026-09-30.csv"

#: The risk parity run's full calendar months, and its two sides of March 2022.
WHOLE = ("2003-10", "2026-08")
BEFORE_THE_RISE = ("2003-10", "2022-02")
AFTER_THE_RISE = ("2022-04", "2026-08")

#: The post's "near zero", 0.25% a year as a decimal.
NEAR_ZERO = 0.0025


class TestTheVintage:
    """Which series every pin below reads, so a second download cannot slip in."""

    def test_the_entry_is_the_committed_tb3ms_download(self) -> None:
        entry = bill_vintage()
        assert entry.path == VINTAGE
        assert (entry.vendor, entry.symbol, entry.price_basis) == ("fred", "TB3MS", "rate")
        assert entry.download_date == "2026-09-30"
        assert (entry.first_date, entry.last_date) == ("1934-01-01", "2026-08-01")
        assert entry.row_count == 1112

    def test_it_holds_one_row_a_month_from_january_1934_to_august_2026(self) -> None:
        rates = monthly_rates()
        assert len(rates) == 1112
        assert rates[0] == ("1934-01", 0.0072)
        assert rates[-1] == ("2026-08", 0.0372)

    def test_percent_text_becomes_the_decimal_it_names(self) -> None:
        """0.25 in the file is exactly the float 0.0025, which dividing a float does not give
        for every row. October 2015 is the month the scale-break skip cites."""
        rates = dict(monthly_rates())
        assert rates["1934-11"] == 0.0025
        assert rates["2015-10"] == 0.0002
        assert rates["2015-11"] == 0.0012
        assert all(rate == float(f"{rate:.4f}") for rate in rates.values())


class TestTheRiskParityWindow:
    """The four figures issue 187 named, from the stored bytes."""

    def test_the_whole_span_averages_1_744_percent_over_275_months(self) -> None:
        assert average(*WHOLE) == pytest.approx(0.01744, abs=1e-12)
        assert f"{average(*WHOLE):.2%}" == "1.74%"
        assert months_in(*WHOLE) == 275

    def test_before_the_rise_averages_1_165_percent_over_221_months(self) -> None:
        assert average(*BEFORE_THE_RISE) == pytest.approx(0.0116516, abs=5e-8)
        assert f"{average(*BEFORE_THE_RISE):.2%}" == "1.17%"
        assert months_in(*BEFORE_THE_RISE) == 221

    def test_after_the_rise_averages_4_182_percent_over_53_months(self) -> None:
        assert average(*AFTER_THE_RISE) == pytest.approx(0.0418226, abs=5e-8)
        assert f"{average(*AFTER_THE_RISE):.2%}" == "4.18%"
        assert months_in(*AFTER_THE_RISE) == 53

    def test_march_2022_is_the_one_month_in_neither_half(self) -> None:
        assert months_in(*BEFORE_THE_RISE) + months_in(*AFTER_THE_RISE) + 1 == months_in(*WHOLE)
        assert months_in("2022-03", "2022-03") == 1
        assert average("2022-03", "2022-03") == 0.0044

    def test_108_months_sat_below_a_quarter_percent_which_is_nine_years(self) -> None:
        below = months_below(NEAR_ZERO, *WHOLE)
        assert below == 108
        assert below / 12 == 9.0


class TestTheWindowArithmetic:
    """What the three functions mean, on windows small enough to read by eye."""

    def test_a_one_month_window_is_that_month(self) -> None:
        assert months_in("2015-10", "2015-10") == 1
        assert average("2015-10", "2015-10") == 0.0002

    def test_both_ends_are_included(self) -> None:
        """October to December 1934 reads 0.27, 0.25 and 0.23."""
        assert months_in("1934-10", "1934-12") == 3
        assert average("1934-10", "1934-12") == pytest.approx(0.0025, abs=1e-15)

    def test_a_month_at_the_threshold_is_not_below_it(self) -> None:
        """February and March 1942 sit at exactly 0.25%, and January at 0.27%."""
        assert months_below(NEAR_ZERO, "1942-01", "1942-12") == 0
        assert months_below(NEAR_ZERO, "1934-10", "1934-12") == 1
        assert months_below(0.0026, "1942-01", "1942-03") == 2

    def test_the_window_runs_across_a_year_end(self) -> None:
        assert months_in("1999-11", "2000-02") == 4

    def test_the_first_and_last_months_held_are_windows_too(self) -> None:
        assert months_in("1934-01", "2026-08") == 1112


class TestTheRefusals:
    """A month the series does not hold, or a window run backwards, stops the call."""

    @pytest.mark.parametrize("month", ["1933-12", "2026-09", "2003-1", "2003-10-01", ""])
    def test_a_first_month_the_series_does_not_hold_is_refused(self, month: str) -> None:
        with pytest.raises(ValueError, match=r"first month .* runs from 1934-01 to 2026-08"):
            average(month, "2026-08")

    @pytest.mark.parametrize("month", ["1933-12", "2026-09", "2026-8"])
    def test_a_last_month_the_series_does_not_hold_is_refused(self, month: str) -> None:
        with pytest.raises(ValueError, match=r"last month .* runs from 1934-01 to 2026-08"):
            months_in("2003-10", month)

    def test_a_backwards_window_is_refused_rather_than_read_as_empty(self) -> None:
        with pytest.raises(ValueError, match="runs backwards, from 2026-08 to 2003-10"):
            months_below(NEAR_ZERO, "2026-08", "2003-10")


def _directory_with(tmp_path: Path, text: str) -> Path:
    """A data directory whose only vintage is a hand-written TB3MS file holding ``text``.

    Hand-written because the recorder always writes a good header, so a bad one
    can only arrive the way a hand edit would bring it.
    """
    payload = text.encode("utf-8")
    name = "fred_tb3ms_rate_2020-01-01_2020-03-01_dl2026-09-30.csv"
    (tmp_path / name).write_bytes(payload)
    entry = VintageEntry(
        vendor="fred",
        symbol="TB3MS",
        price_basis="rate",
        first_date="2020-01-01",
        last_date="2020-03-01",
        path=name,
        row_count=3,
        sha256=hashlib.sha256(payload).hexdigest(),
        download_date="2026-09-30",
    )
    (tmp_path / MANIFEST_NAME).write_text(entry.as_json() + "\n", encoding="utf-8")
    return tmp_path


class TestTheRead:
    """The series reads only as one verified row for every month, under the recorded header."""

    def test_a_well_formed_series_reads(self, tmp_path: Path) -> None:
        directory = _directory_with(
            tmp_path, "Date,Close\n2020-01-01,1.52\n2020-02-01,1.52\n2020-03-01,0.29\n"
        )
        assert monthly_rates(data_dir=directory) == [
            ("2020-01", 0.0152),
            ("2020-02", 0.0152),
            ("2020-03", 0.0029),
        ]
        assert months_in("2020-01", "2020-03", data_dir=directory) == 3

    def test_another_header_is_refused(self, tmp_path: Path) -> None:
        directory = _directory_with(
            tmp_path, "Date,Rate\n2020-01-01,1.52\n2020-02-01,1.52\n2020-03-01,0.29\n"
        )
        with pytest.raises(ValueError, match=r"header reads \['Date', 'Rate'\]"):
            monthly_rates(data_dir=directory)

    def test_an_empty_file_is_refused_at_its_header(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="header reads None"):
            monthly_rates(data_dir=_directory_with(tmp_path, ""))

    @pytest.mark.parametrize("day", ["2020-02-15", "2020-02", "20200201", "2020-02-01x"])
    def test_a_row_not_dated_the_first_of_a_month_is_refused(
        self, tmp_path: Path, day: str
    ) -> None:
        directory = _directory_with(
            tmp_path, f"Date,Close\n2020-01-01,1.52\n{day},1.52\n2020-03-01,0.29\n"
        )
        with pytest.raises(ValueError, match=f"line 3 is dated '{day}'"):
            monthly_rates(data_dir=directory)

    def test_a_missing_month_is_refused_rather_than_shrinking_a_count(self, tmp_path: Path) -> None:
        directory = _directory_with(
            tmp_path, "Date,Close\n2020-01-01,1.52\n2020-03-01,0.29\n2020-04-01,0.14\n"
        )
        with pytest.raises(ValueError, match="line 3 holds 2020-03 straight after 2020-01"):
            monthly_rates(data_dir=directory)

    def test_a_repeated_month_is_refused(self, tmp_path: Path) -> None:
        directory = _directory_with(
            tmp_path, "Date,Close\n2020-01-01,1.52\n2020-01-01,1.52\n2020-02-01,1.52\n"
        )
        with pytest.raises(ValueError, match="line 3 holds 2020-01 straight after 2020-01"):
            monthly_rates(data_dir=directory)

    def test_altered_bytes_stop_the_read(self, tmp_path: Path) -> None:
        directory = _directory_with(
            tmp_path, "Date,Close\n2020-01-01,1.52\n2020-02-01,1.52\n2020-03-01,0.29\n"
        )
        (directory / "fred_tb3ms_rate_2020-01-01_2020-03-01_dl2026-09-30.csv").write_bytes(
            b"Date,Close\n2020-01-01,9.99\n2020-02-01,1.52\n2020-03-01,0.29\n"
        )
        with pytest.raises(VintageUnavailable, match="hash to"):
            average("2020-01", "2020-03", data_dir=directory)

    def test_a_second_download_makes_the_read_refuse_rather_than_pick(self, tmp_path: Path) -> None:
        """Resolved by identity, so a newer TB3MS download names both rather than
        moving every pin above with nothing in the diff to say why."""
        for name in (MANIFEST_NAME, VINTAGE):
            shutil.copy(DATA_DIR / name, tmp_path / name)
        manifest = (DATA_DIR / MANIFEST_NAME).read_text(encoding="utf-8").splitlines()
        (tmp_path / MANIFEST_NAME).write_text(
            "".join(line + "\n" for line in manifest if VINTAGE in line), encoding="utf-8"
        )
        record_vintage(
            [("2026-08-01", 3.72), ("2026-09-01", 3.70)],
            vendor="fred",
            symbol="TB3MS",
            price_basis="rate",
            download_date="2026-10-01",
            data_dir=tmp_path,
        )
        with pytest.raises(VintageUnavailable, match="names 2 recorded vintages"):
            monthly_rates(data_dir=tmp_path)
