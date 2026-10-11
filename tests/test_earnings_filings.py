"""The Item 2.02 record and the ticker table for Chan's 497 stocks, issue 251.

This file is the authority for every count quoted about
``research/filings/earnings/``: how many of Chan's tickers each check passed,
which routes proposed them, and how many filings the index holds. It also
holds the two checks themselves, and the fetch, with an injected download so
no test touches the network.

Every count reads the ticker table and the index as committed, which the
build session wrote on 2026-10-10 from EDGAR as it stood that day and from the
owner's archive at the ``sp500`` lines of ``data/archive_vintages.jsonl``.
The CIK check is rerun here on committed files alone: Chan's closes in
``inputdataohlcdaily_stocks_20120424/`` and IVV's schedule at 2012-03-31 in
``research/filings/ivv/2012-03-31.csv``. The archive check needs the archive,
so its rerun skips without one.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pandas as pd
import pytest

from chan import earnings_filings
from chan.earnings_filings import (
    DAYS_ALLOWED,
    PRICE_DAY,
    PRICE_TOLERANCE,
    RETURN_TOLERANCE,
    Release,
    TickerRow,
    acceptance,
    candidates,
    check_cik,
    check_series,
    fetch,
    header_url,
    holding_price,
    name_keys,
    name_on,
    page_url,
    pages_to_read,
    read_index,
    read_table,
    serialize_table,
    submissions_url,
)
from chan.fund_holdings import REQUEST_SPACING_SECONDS, FilingRefused
from chan.pead import read_sources
from tests.conftest import archive_skip_reason


def header(accession: str, stamp: str, form: str = "8-K") -> bytes:
    """A header file as EDGAR serves one, cut to the lines the reader reads."""
    return (
        f"<SEC-HEADER>\n<ACCEPTANCE-DATETIME>{stamp}\n<ACCESSION-NUMBER>{accession}\n"
        f"<TYPE>{form}\n<PUBLIC-DOCUMENT-COUNT>3\n</SEC-HEADER>\n"
    ).encode()


def block(*filings: tuple[str, str, str, str, str]) -> dict[str, list[str]]:
    """A ``filings.recent`` block: accession, form, items, report date, filing date."""
    keys = ("accessionNumber", "form", "items", "reportDate", "filingDate")
    return {key: [filing[i] for filing in filings] for i, key in enumerate(keys)}


class TestTheNameKeys:
    @pytest.mark.parametrize(
        ("edgar", "schedule"),
        [
            ("HORTON D R INC /DE/", "D.R. Horton Inc."),
            ("AMAZON COM INC", "Amazon.com Inc."),
            ("LILLY ELI & CO", "Eli Lilly and Co."),
            ("US BANCORP \\DE\\", "U.S. Bancorp"),
            ("COSTCO WHOLESALE CORP /NEW", "Costco Wholesale Corp."),
            ("PRICE T ROWE GROUP INC", "T. Rowe Price Group Inc."),
            ("BERKSHIRE HATHAWAY INC", "Berkshire Hathaway Inc. Class B"),
            ("COCA COLA CO", "Coca-Cola Co. (The)"),
            ("STARWOOD HOTEL & RESORTS WORLDWIDE, INC", "Starwood Hotels & Resorts Worldwide Inc."),
            ("ZIONS BANCORPORATION /UT/", "Zions Bancorp"),
            ("KOHLS Corp", "Kohl's Corp."),
            ("MCDONALDS CORP", "McDonald’s Corp."),
            ("HEINZ H J CO", "H.J. Heinz Co."),
            ("Noble Corp / Switzerland", "Noble Corp."),
            ("NEWS CORP", "News Corp. Class A NVS"),
            ("DIRECTV", "DIRECTV Class A"),
            ("PENNEY J C CO INC", "J.C. Penney Co. Inc."),
            ("GENERAL ELECTRIC CO", "General Electric Company"),
        ],
    )
    def test_edgar_and_the_schedule_meet(self, edgar: str, schedule: str) -> None:
        assert name_keys(edgar) & name_keys(schedule)

    @pytest.mark.parametrize(
        ("edgar", "schedule"),
        [
            ("ACE LTD", "Chubb Corp. (The)"),
            ("TYCO INTERNATIONAL LTD", "Johnson Controls Inc."),
            ("NEWS LIMITED", "News Corp. Class A NVS"),
            ("DIRECTV, LLC", "DIRECTV Class A"),
            ("H. J. Heinz Company, L.P.", "H.J. Heinz Co."),
            ("TIME WARNER COMPANIES INC", "Time Warner Inc."),
            ("NYSE Euronext", "NYSE Euronext Inc."),
        ],
    )
    def test_two_companies_do_not(self, edgar: str, schedule: str) -> None:
        assert not name_keys(edgar) & name_keys(schedule)


class TestTheNameOnADay:
    SUBMISSION = {
        "name": "Chubb Ltd",
        "formerNames": [
            {
                "name": "ACE LTD",
                "from": "1993-01-27T00:00:00.000Z",
                "to": "2016-01-14T00:00:00.000Z",
            }
        ],
        "filings": {
            "recent": {"filingDate": ["2026-01-01"]},
            "files": [{"filingFrom": "1993-01-27", "filingTo": "2015-12-31"}],
        },
    }

    def test_a_former_name_whose_span_holds_the_day_wins(self) -> None:
        assert name_on(self.SUBMISSION) == "ACE LTD"

    def test_the_current_name_holds_after_every_former_one(self) -> None:
        assert name_on(self.SUBMISSION, "2020-01-02") == "Chubb Ltd"

    def test_a_cik_that_had_filed_nothing_has_no_name(self) -> None:
        young = {"name": "Dow Inc.", "filings": {"recent": {"filingDate": ["2018-08-30"]}}}
        assert name_on(young) is None

    def test_a_cik_that_had_stopped_filing_has_no_name(self) -> None:
        """Westinghouse's old CIK, which EDGAR names "CBS CORP" today."""
        shell = {
            "name": "CBS CORP",
            "filings": {
                "recent": {"filingDate": []},
                "files": [{"filingFrom": "1994-02-14", "filingTo": "2001-03-30"}],
            },
        }
        assert name_on(shell) is None

    def test_a_cik_filing_on_both_sides_of_the_day_has_a_name(self) -> None:
        both = {
            "name": "CBS CORP",
            "filings": {
                "recent": {"filingDate": ["2019-12-04"]},
                "files": [{"filingFrom": "1994-01-01", "filingTo": "2012-03-30"}],
            },
        }
        assert name_on(both) == "CBS CORP"


class TestTheCikCheck:
    HOLDINGS = [("ACE Ltd.", 73.20), ("Chubb Corp. (The)", 69.11), ("Apple Inc.", 599.55)]

    def test_a_name_and_a_price_that_agree_pass(self) -> None:
        assert check_cik("CHUBB CORP", self.HOLDINGS, 69.11, 6) == ("pass", 2)

    def test_the_right_name_at_the_wrong_price_fails(self) -> None:
        """ACE's CIK against the old Chubb's close, which is what company_tickers.json proposes."""
        assert check_cik("ACE LTD", self.HOLDINGS, 69.11, 6) == ("price", 1)

    def test_the_tolerance_is_inclusive_and_no_wider(self) -> None:
        inside = 69.11 / (1 + PRICE_TOLERANCE) * 1.0000001
        outside = 69.11 / (1 + PRICE_TOLERANCE) * 0.999
        assert check_cik("CHUBB CORP", self.HOLDINGS, inside, 6)[0] == "pass"
        assert check_cik("CHUBB CORP", self.HOLDINGS, outside, 6)[0] == "price"

    def test_a_name_no_holding_carries_fails(self) -> None:
        assert check_cik("CONCHO RESOURCES INC", self.HOLDINGS, 69.11, 6) == ("name", None)

    def test_a_name_two_holdings_carry_fails(self) -> None:
        twice = [*self.HOLDINGS, ("Chubb Corp.", 69.11)]
        assert check_cik("CHUBB CORP", twice, 69.11, 6) == ("name", None)

    def test_a_cik_not_filing_on_the_day_fails(self) -> None:
        assert check_cik(None, self.HOLDINGS, 69.11, 6) == ("dates", None)

    def test_a_cik_that_announced_nothing_under_item_2_02_fails(self) -> None:
        """Westinghouse's old CIK carries CBS's name in 2012 and filed no release."""
        assert check_cik("CHUBB CORP", self.HOLDINGS, 69.11, 0) == ("silent", 2)

    def test_a_holding_price_is_value_over_shares(self) -> None:
        assert holding_price("12020743", "1053527") == pytest.approx(11.41, abs=0.005)


class TestTheArchiveCheck:
    DAYS = pd.bdate_range("2011-01-03", periods=12)

    def series(self, values: list[float]) -> pd.Series:
        return pd.Series(values, index=self.DAYS, dtype=float)

    def test_the_same_returns_on_another_scale_pass(self) -> None:
        chan = self.series([10, 11, 12, 11, 10, 11, 12, 13, 12, 11, 12, 13])
        assert check_series(chan, chan * 3.7) == ("pass", 0)

    def test_days_allowed_pass_and_one_more_fails(self) -> None:
        chan = self.series([10.0] * 12)
        # A step in the level moves one return, so each step costs one day.
        steps = pd.Series(range(12), index=self.DAYS, dtype=float)
        assert check_series(chan, chan * 1.05 ** steps.clip(upper=DAYS_ALLOWED)) == (
            "pass",
            DAYS_ALLOWED,
        )
        assert check_series(chan, chan * 1.05 ** steps.clip(upper=DAYS_ALLOWED + 1)) == (
            "returns",
            DAYS_ALLOWED + 1,
        )
        assert DAYS_ALLOWED == 5

    def test_a_difference_at_the_tolerance_does_not_count(self) -> None:
        chan = self.series([10.0] * 12)
        archive = chan.copy()
        archive.iloc[6:] = 10.0 * (1 + RETURN_TOLERANCE * 0.99)
        assert check_series(chan, archive) == ("pass", 0)
        archive.iloc[6:] = 10.0 * (1 + RETURN_TOLERANCE * 1.01)
        assert check_series(chan, archive) == ("pass", 1)

    def test_a_close_missing_from_the_archive_fails_outright(self) -> None:
        chan = self.series([10.0] * 12)
        archive = chan.copy()
        archive.iloc[3] = float("nan")
        assert check_series(chan, archive) == ("missing", 1)

    def test_a_day_chan_has_no_close_on_is_not_asked_of_the_archive(self) -> None:
        """MPC and XYL start inside the window, in Chan's file and the archive alike."""
        chan = self.series([float("nan")] * 4 + [10.0] * 8)
        assert check_series(chan, chan.dropna()) == ("pass", 0)


ACCESSION = "0000320193-11-000006"
FILINGS = block(
    (ACCESSION, "8-K", "2.02,9.01", "2011-01-18", "2011-01-18"),
    ("0000320193-11-000007", "8-K/A", "2.02", "2011-01-18", "2011-01-19"),
    ("0000320193-11-000008", "8-K", "5.02", "2011-01-17", "2011-01-17"),
    ("0000320193-12-000040", "8-K", "2.02", "2012-05-30", "2012-05-30"),
    ("0000320193-12-000041", "8-K", "2.02", "2012-04-24", "2012-04-25"),
)


class TestTheCandidates:
    def test_only_original_8ks_carrying_item_2_02_inside_the_window_are_kept(self) -> None:
        kept = candidates([FILINGS])
        assert [c["accession"] for c in kept] == [ACCESSION, "0000320193-12-000041"]

    def test_an_amendment_is_dropped(self) -> None:
        assert "0000320193-11-000007" not in [c["accession"] for c in candidates([FILINGS])]

    def test_a_filing_listed_on_two_pages_is_kept_once(self) -> None:
        assert len(candidates([FILINGS, FILINGS])) == 2

    def test_only_pages_overlapping_the_window_are_read(self) -> None:
        submission = {
            "filings": {
                "files": [
                    {"name": "a.json", "filingFrom": "2002-01-01", "filingTo": "2009-12-31"},
                    {"name": "b.json", "filingFrom": "2010-01-01", "filingTo": "2011-06-30"},
                    {"name": "c.json", "filingFrom": "2012-04-30", "filingTo": "2014-01-01"},
                    {"name": "d.json", "filingFrom": "2012-05-01", "filingTo": "2014-01-01"},
                ]
            }
        }
        assert pages_to_read(submission) == ["b.json", "c.json"]


class TestTheHeader:
    def test_the_time_is_read_as_eastern_and_printed_as_iso(self) -> None:
        assert acceptance(header(ACCESSION, "20110118163015"), ACCESSION) == "2011-01-18T16:30:15"

    def test_a_header_naming_another_accession_is_refused(self) -> None:
        with pytest.raises(FilingRefused, match="names another accession"):
            acceptance(header("0000320193-11-000099", "20110118163015"), ACCESSION)

    def test_a_header_of_another_form_is_refused(self) -> None:
        with pytest.raises(FilingRefused, match="is not a 8-K"):
            acceptance(header(ACCESSION, "20110118163015", "8-K/A"), ACCESSION)

    def test_a_header_with_no_time_is_refused(self) -> None:
        with pytest.raises(FilingRefused, match="no acceptance time"):
            acceptance(f"<ACCESSION-NUMBER>{ACCESSION}\n<TYPE>8-K\n".encode(), ACCESSION)


ROW = TickerRow(
    ticker="AAPL",
    cik="320193",
    cik_source="tickers",
    edgar_name="APPLE INC",
    ivv_row="1",
    cik_check="pass",
    archive_ticker="AAPL",
    archive_source="same",
    archive_check="pass",
    days_over="0",
)


def edgar(page_filings: dict | None = None, name: str = "APPLE INC") -> dict[str, bytes]:
    """What EDGAR serves for the fetch, by URL."""
    submission = {
        "name": name,
        "formerNames": [],
        "filings": {
            "recent": block(),
            "files": [
                {
                    "name": "CIK0000320193-submissions-001.json",
                    "filingFrom": "2008-01-01",
                    "filingTo": "2012-12-31",
                }
            ],
        },
    }
    served = {
        submissions_url(320193): json.dumps(submission).encode(),
        page_url("CIK0000320193-submissions-001.json"): json.dumps(
            FILINGS if page_filings is None else page_filings
        ).encode(),
        header_url(320193, ACCESSION): header(ACCESSION, "20110118163015"),
        header_url(320193, "0000320193-12-000041"): header(
            "0000320193-12-000041", "20120425060102"
        ),
    }
    return served


class TestTheFetch:
    def run(self, tmp_path: Path, served: dict[str, bytes], rows=(ROW,)):
        asked: list[str] = []
        pauses: list[float] = []

        def download(url: str, contact: str) -> bytes:
            assert contact == "a contact"
            asked.append(url)
            return served[url]

        releases = fetch(
            list(rows),
            record_dir=tmp_path,
            contact="a contact",
            download=download,
            pause=pauses.append,
        )
        return releases, asked, pauses

    def test_it_records_each_kept_filing_with_its_eastern_time_and_header_hash(self, tmp_path):
        served = edgar()
        releases, asked, pauses = self.run(tmp_path, served)
        assert releases == [
            Release(
                ticker="AAPL",
                cik=320193,
                accession=ACCESSION,
                form="8-K",
                items="2.02,9.01",
                report_date="2011-01-18",
                filing_date="2011-01-18",
                accepted="2011-01-18T16:30:15",
                header_sha256=hashlib.sha256(served[header_url(320193, ACCESSION)]).hexdigest(),
            )
        ]
        assert read_index(tmp_path) == releases

    def test_a_filing_accepted_after_the_window_is_dropped_after_its_header_is_read(self, tmp_path):
        _, asked, _ = self.run(tmp_path, edgar())
        assert header_url(320193, "0000320193-12-000041") in asked

    def test_every_request_after_the_first_waits_the_spacing(self, tmp_path):
        _, asked, pauses = self.run(tmp_path, edgar())
        assert len(asked) == 4
        assert pauses == [REQUEST_SPACING_SECONDS] * 3

    def test_a_row_whose_cik_failed_is_not_fetched(self, tmp_path):
        failed = TickerRow(**{**ROW.__dict__, "cik_check": "price"})
        releases, asked, _ = self.run(tmp_path, edgar(), rows=(failed,))
        assert (releases, asked) == ([], [])

    def test_a_cik_whose_name_moved_is_refused(self, tmp_path):
        with pytest.raises(FilingRefused, match="the table records 'APPLE INC'"):
            self.run(tmp_path, edgar(name="APPLE COMPUTER INC"))

    def test_a_header_that_changed_since_the_index_is_refused(self, tmp_path):
        served = edgar()
        self.run(tmp_path, served)
        served[header_url(320193, ACCESSION)] = header(ACCESSION, "20110118163016")
        with pytest.raises(FilingRefused, match="the index records 2011-01-18T16:30:15"):
            self.run(tmp_path, served)

    def test_a_rerun_on_the_same_bytes_writes_the_same_index(self, tmp_path):
        served = edgar()
        self.run(tmp_path, served)
        first = (tmp_path / "index.jsonl").read_bytes()
        self.run(tmp_path, served)
        assert (tmp_path / "index.jsonl").read_bytes() == first


class TestTheTableFile:
    def test_it_round_trips(self, tmp_path):
        (tmp_path / "tickers.csv").write_bytes(serialize_table([ROW]))
        assert read_table(tmp_path) == [ROW]

    def test_other_columns_are_refused(self, tmp_path):
        (tmp_path / "tickers.csv").write_text("ticker,cik\nAAPL,320193\n")
        with pytest.raises(ValueError, match="has columns"):
            read_table(tmp_path)


@pytest.fixture(scope="module")
def table() -> list[TickerRow]:
    return read_table()


@pytest.fixture(scope="module")
def index() -> list[Release]:
    return read_index()


@pytest.fixture(scope="module")
def closes() -> pd.DataFrame:
    return read_sources()[3]


@pytest.fixture(scope="module")
def schedule() -> list[tuple[str, float]]:
    ivv = pd.read_csv(
        earnings_filings.FILINGS_DIR / "ivv" / f"{earnings_filings.IVV_REPORT_DATE}.csv",
        dtype=str,
        keep_default_na=False,
    )
    return [(row["name"], holding_price(row["value"], row["shares"])) for _, row in ivv.iterrows()]


class TestTheCommittedTable:
    """``tickers.csv`` as the build session wrote it on 2026-10-10."""

    def test_it_lists_the_flag_files_stocks_in_their_order(self, table) -> None:
        assert [row.ticker for row in table] == list(read_sources()[4].columns)

    def test_the_universes(self, table) -> None:
        calendar = {row.ticker for row in table if row.calendar}
        priced = {row.ticker for row in table if row.priced}
        assert (len(table), len(calendar), len(priced), len(calendar & priced)) == (
            497, 488, 446, 441,
        )  # fmt: skip

    def test_which_route_proposed_each_cik_and_what_its_check_said(self, table) -> None:
        assert Counter((row.cik_source, row.cik_check) for row in table) == {
            ("tickers", "pass"): 302,
            ("tickers-archive", "pass"): 32,
            ("name", "pass"): 154,
            ("search", "name"): 5,
            ("tickers", "name"): 1,
            ("tickers", "dates"): 1,
            ("name", "name"): 1,
            ("name", "silent"): 1,
        }

    def test_which_route_proposed_each_series_and_what_its_check_said(self, table) -> None:
        assert Counter((row.archive_source, row.archive_check) for row in table) == {
            ("same", "pass"): 398,
            ("search", "pass"): 48,
            ("same", "missing"): 37,
            ("same", "returns"): 4,
            ("none", "none"): 10,
        }

    def test_the_stocks_left_out_of_the_calendar_by_name(self, table) -> None:
        assert {row.ticker: row.cik_check for row in table if not row.calendar} == {
            "AKS": "name", "CPWR": "name", "CVC": "name", "DD": "dates", "LUK": "silent",
            "MWW": "name", "NYX": "name", "TLAB": "name", "WFR": "name",
        }  # fmt: skip

    def test_the_stocks_whose_reused_ticker_holds_another_company(self, table) -> None:
        over = {row.ticker: int(row.days_over) for row in table if row.archive_check == "returns"}
        assert over == {"AGN": 131, "CB": 72, "JCI": 168, "LSI": 194}

    def test_every_passing_cik_passes_again_on_committed_files(
        self, table, index, closes, schedule
    ) -> None:
        """The rerun reads only the table, the index, Chan's closes and IVV's schedule."""
        announced = Counter(release.ticker for release in index)
        day = pd.Timestamp(PRICE_DAY)
        for row in table:
            if row.calendar:
                outcome = check_cik(
                    row.edgar_name, schedule, closes.at[day, row.ticker], announced[row.ticker]
                )
                assert outcome == ("pass", int(row.ivv_row)), row.ticker

    def test_no_holding_and_no_cik_confirms_two_stocks(self, table) -> None:
        passing = [row for row in table if row.calendar]
        assert len({row.ivv_row for row in passing}) == len({row.cik for row in passing}) == 488

    def test_the_price_tolerance_sits_between_the_right_and_the_wrong_company(
        self, table, closes, schedule
    ) -> None:
        """The widest passing gap is RRD's dividend, and the nearest wrong one is ACE against CB.

        Chan's closes are adjusted on 2012-04-24, so a dividend that went ex
        between the price day and then puts the right company's IVV price
        above his close by about the dividend. RRD, which paid near 8 percent
        a year, is the widest at 2.14 percent. ACE's holding sits 5.92 percent
        above the old Chubb's close.
        """
        day = pd.Timestamp(PRICE_DAY)
        gaps = {
            row.ticker: schedule[int(row.ivv_row) - 1][1] / closes.at[day, row.ticker] - 1
            for row in table
            if row.calendar
        }
        widest = max(gaps, key=lambda ticker: abs(gaps[ticker]))
        assert (widest, round(gaps[widest], 4)) == ("RRD", 0.0214)
        (ace,) = [price for name, price in schedule if name == "ACE Ltd."]
        assert round(ace / closes.at[day, "CB"] - 1, 4) == 0.0592
        assert abs(gaps[widest]) < PRICE_TOLERANCE < 0.0592

    def test_the_days_allowed_sit_between_the_same_and_another_company(self, table) -> None:
        """A same-company series differs on at most two days, 2011-10-27 and 2011-10-28.

        Chan's file carries closes on 2011-10-27 that the next day undoes
        across many stocks, so a series agreeing everywhere else still
        differs on those two returns. The closest other company differs on 72.
        """
        passing = [int(row.days_over) for row in table if row.priced]
        failing = [int(row.days_over) for row in table if row.archive_check == "returns"]
        assert (max(passing), min(failing)) == (2, 72)
        assert max(passing) <= DAYS_ALLOWED < min(failing)


class TestTheCommittedIndex:
    """``index.jsonl`` as the fetch of 2026-10-10 wrote it, from EDGAR that day."""

    def test_it_holds_2930_filings_for_every_stock_of_the_calendar(self, table, index) -> None:
        assert len(index) == len({release.accession for release in index}) == 2930
        assert {release.ticker for release in index} == {
            row.ticker for row in table if row.calendar
        }

    def test_every_line_is_an_original_item_2_02_8k_accepted_in_the_window(self, index) -> None:
        assert {release.form for release in index} == {"8-K"}
        assert all("2.02" in release.items.split(",") for release in index)
        assert min(release.accepted for release in index) == "2010-12-02T08:34:03"
        assert max(release.accepted for release in index) == "2012-04-24T19:36:25"

    def test_every_line_names_the_cik_the_table_names(self, table, index) -> None:
        ciks = {row.ticker: int(row.cik) for row in table if row.calendar}
        assert all(release.cik == ciks[release.ticker] for release in index)

    def test_when_the_filings_were_accepted(self, index) -> None:
        """Before the open, during the session and from the close, Eastern."""
        times = [release.accepted[11:] for release in index]
        before = sum(t < "09:30:00" for t in times)
        after = sum(t >= "16:00:00" for t in times)
        assert (before, len(times) - before - after, after) == (1460, 405, 1065)

    def test_343_were_accepted_after_the_date_they_report(self, index) -> None:
        late = [r for r in index if r.report_date and r.accepted[:10] > r.report_date]
        assert len(late) == 343

    def test_apple_files_at_half_past_four_eastern(self, index) -> None:
        """The JSON reads these as 8:30 p.m., which is the double conversion the audit found."""
        apple = [release.accepted for release in index if release.ticker == "AAPL"]
        assert apple == [
            "2011-01-18T16:30:27", "2011-04-20T16:30:30", "2011-07-19T16:29:56",
            "2011-10-18T16:31:02", "2012-01-24T16:30:34", "2012-04-24T16:30:55",
        ]  # fmt: skip

    def test_the_file_is_written_in_the_writers_order(self, index) -> None:
        path = earnings_filings.RECORD_DIR / earnings_filings.INDEX_NAME
        assert path.read_bytes() == earnings_filings.serialize_index(index)

    def test_the_record_takes_869661_bytes(self) -> None:
        """Outside data/ and its cap, as the fund record is."""
        directory = earnings_filings.RECORD_DIR
        sizes = {path.name: path.stat().st_size for path in directory.iterdir()}
        assert sizes == {"index.jsonl": 838079, "tickers.csv": 31582}
        assert sum(sizes.values()) == 869661


class TestTheArchive:
    """Runs only where the archive is, under ``QT_ARCHIVE_RUN=1``."""

    def test_every_archive_check_reproduces(self) -> None:
        reason = archive_skip_reason()
        if reason is not None:
            pytest.skip(reason)
        assert earnings_filings.check() == []
