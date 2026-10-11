"""The rules of issue 526's holdout of Chan's low-beta leverage rule, on frames built by hand.

[Issue 526](https://github.com/l3a0/quantitative-trading/issues/526) runs issue
275's registered specification on IVV's S&P 500 from 2008, through
:mod:`chan.low_beta_holdout`. The tests here read no archive. They hold the
``members`` keyword of :func:`chan.low_beta_leverage.build_portfolios`, the
holding-month rule of the registration's point 4, and the run's helpers, and
the counts behind the survivor label of point 9, which read only committed
files: ``research/filings/ivv/members.csv``, its holes file, the manifest and
the committed raw SPY calendar.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from chan import low_beta_holdout, sp500_panel
from chan.archive import read_archive_manifest
from chan.equity_seasonals import stopped_closes
from chan.low_beta_holdout import (
    HoldoutRefused,
    frame_days,
    market_closes,
    month_end_mask,
    refuse_uncovered,
    survivor_gap,
)
from chan.low_beta_leverage import BETA_DAYS, build_portfolios
from chan.paths import DATA_DIR
from chan.series import row_month_ends
from chan.vintage import VintageUnavailable
from tests.test_low_beta_leverage import DAYS, month_return, panel, rates, spy

ENDS = DAYS[row_month_ends(DAYS)]
FORMED = pd.Timestamp("2000-12-29")
HELD_TO = pd.Timestamp("2001-01-31")
NEXT = pd.Timestamp("2001-02-28")


def frame() -> pd.DataFrame:
    return panel(rates(), A=0.5, B=1.0, C=1.5, D=2.0, E=2.5, F=3.0)


def everyone(closes: pd.DataFrame, days: pd.DatetimeIndex = ENDS) -> pd.DataFrame:
    return pd.DataFrame(True, index=days, columns=closes.columns)


def stopped(closes: pd.DataFrame, symbol: str, day: str) -> pd.DataFrame:
    stops = pd.Series(pd.NaT, index=closes.columns, dtype="datetime64[ns]")
    stops[symbol] = pd.Timestamp(day)
    return stopped_closes(closes, stops, DAYS)


class TestTheMembersKeyword:
    def test_everyone_on_the_same_month_ends_changes_nothing(self) -> None:
        closes = frame()
        bare = build_portfolios(closes, spy(), rates())
        masked = build_portfolios(closes, spy(), rates(), members=everyone(closes))
        assert masked.levered.equals(bare.levered)
        assert masked.eligible == bare.eligible
        assert masked.formed == bare.formed

    def test_a_stock_not_a_member_at_t_is_not_eligible_at_t_only(self) -> None:
        closes = frame()
        mask = everyone(closes)
        mask.loc[FORMED, "F"] = False
        p = build_portfolios(closes, spy(), rates(), members=mask)
        assert p.formed[0] == FORMED
        assert (p.eligible[0], p.eligible[1]) == (5, 6)
        assert p.high_members[0] == ("E",) and p.high_members[1] == ("F",)
        assert np.isnan(p.betas.loc[FORMED, "F"])

    def test_membership_at_t_plus_1_is_not_asked(self) -> None:
        closes = frame()
        mask = everyone(closes)
        mask.loc[HELD_TO, "F"] = False
        p = build_portfolios(closes, spy(), rates(), members=mask)
        assert p.high_members[0] == ("F",)

    def test_its_index_names_the_month_ends_so_the_last_row_can_close_a_month(self) -> None:
        closes = frame()
        days = ENDS.append(pd.DatetimeIndex([DAYS[-1]]))
        p = build_portfolios(closes, spy(), rates(), members=everyone(closes, days))
        assert p.held_to[-1] == DAYS[-1] == pd.Timestamp("2001-12-31")
        assert build_portfolios(closes, spy(), rates()).held_to[-1] == pd.Timestamp("2001-11-30")

    def test_a_month_end_off_the_calendar_is_refused(self) -> None:
        closes = frame()
        days = ENDS.append(pd.DatetimeIndex(["2002-01-31"]))
        with pytest.raises(VintageUnavailable, match="not on the panel's calendar"):
            build_portfolios(closes, spy(), rates(), members=everyone(closes, days))

    def test_month_ends_out_of_order_are_refused(self) -> None:
        closes = frame()
        with pytest.raises(ValueError, match="increasing date order"):
            build_portfolios(closes, spy(), rates(), members=everyone(closes, ENDS[::-1]))

    def test_a_stock_with_no_column_in_the_mask_is_never_a_candidate(self) -> None:
        closes = frame()
        mask = everyone(closes).drop(columns="F")
        p = build_portfolios(closes, spy(), rates(), members=mask)
        assert set(p.eligible) == {5}


class TestTheHoldingMonth:
    def test_a_stock_stopping_inside_the_month_earns_its_return_to_its_last_close(self) -> None:
        closes = frame()
        cut = stopped(closes, "F", "2001-01-15")
        p = build_portfolios(cut, spy(), rates(), members=everyone(cut))
        assert p.high_members[0] == ("F",)
        expected = month_return(closes["F"], FORMED, pd.Timestamp("2001-01-15"))
        assert p.high.iloc[0] == pytest.approx(expected)

    def test_its_carried_close_does_not_make_it_eligible_the_month_after(self) -> None:
        cut = stopped(frame(), "F", "2001-01-15")
        assert cut.at[HELD_TO, "F"] == cut.at[pd.Timestamp("2001-01-15"), "F"]
        p = build_portfolios(cut, spy(), rates(), members=everyone(cut))
        assert p.formed[1] == HELD_TO
        assert p.eligible[1] == 5
        assert "F" not in p.high_members[1]

    def test_a_stock_whose_last_row_is_t_is_not_eligible_at_t(self) -> None:
        cut = stopped(frame(), "F", str(FORMED.date()))
        assert np.isnan(cut.at[HELD_TO, "F"])
        p = build_portfolios(cut, spy(), rates(), members=everyone(cut))
        assert p.eligible[0] == 5

    def test_a_stock_with_no_close_at_t_is_not_eligible_at_t(self) -> None:
        closes = frame()
        closes.loc[FORMED, "F"] = np.nan
        p = build_portfolios(closes, spy(), rates(), members=everyone(closes))
        assert p.eligible[0] == 5

    def test_a_hole_at_t_plus_1_with_rows_after_it_is_not_eligible_at_t(self) -> None:
        closes = frame()
        closes.loc[HELD_TO, "F"] = np.nan
        p = build_portfolios(closes, spy(), rates(), members=everyone(closes))
        assert (p.eligible[0], p.eligible[1], p.eligible[2]) == (5, 5, 6)
        assert p.formed[2] == NEXT


class TestTheRunsHelpers:
    def test_the_frame_starts_252_rows_before_2008_12_31_and_ends_2026_08_31(self) -> None:
        days = frame_days(sp500_panel.calendar())
        assert days[BETA_DAYS] == pd.Timestamp("2008-12-31")
        assert days[0] == pd.Timestamp("2008-01-02")
        assert days[-1] == pd.Timestamp("2026-08-31")
        assert len(days) == 4695

    def test_spy_missing_a_close_on_a_calendar_day_stops_the_run(self) -> None:
        market = spy().drop(pd.Timestamp("2001-03-15"))
        with pytest.raises(HoldoutRefused, match="no finite close on 2001-03-15"):
            market_closes(market, DAYS)

    def test_spy_on_every_day_passes_through(self) -> None:
        assert market_closes(spy(), DAYS).equals(spy())

    def test_a_covered_member_with_no_close_at_t_plus_1_is_refused(self) -> None:
        closes = frame()
        closes.loc[HELD_TO, "C"] = np.nan
        with pytest.raises(HoldoutRefused, match="covered member C has no close on 2001-01-31"):
            refuse_uncovered(closes, everyone(closes, ENDS[ENDS >= FORMED]))

    def test_an_uncovered_member_with_no_close_passes(self) -> None:
        closes = frame()
        closes.loc[HELD_TO, "C"] = np.nan
        mask = everyone(closes, ENDS[ENDS >= FORMED])
        mask.loc[FORMED, "C"] = False
        mask.loc[HELD_TO, "C"] = False
        refuse_uncovered(closes, mask)

    def test_the_mask_is_indexed_by_each_months_last_trading_day(self) -> None:
        rows = sp500_panel.load()
        coverage = sp500_panel.coverage_from_committed(rows)
        mask = month_end_mask(rows, coverage, sp500_panel.tickers(rows), sp500_panel.calendar())
        assert len(mask) == 213
        assert mask.index[0] == pd.Timestamp("2008-12-31")
        assert mask.index[-1] == pd.Timestamp("2026-08-31")
        assert pd.Timestamp("2013-03-28") in mask.index
        assert int(mask.to_numpy().sum()) == sum(month.covered for month in coverage)


class TestTheCoverageWithoutRank:
    """Point 3 of the registration: Example 7.7's ``rank`` reason is left out.

    Read on the committed members file, holes file and the manifest's spans,
    before each series is cut at its last row that traded, so these are the
    audit's counts rather than the run's.
    """

    def test_no_member_misses_for_rank_and_every_other_reason_is_unchanged(self) -> None:
        rows = sp500_panel.load()
        args = (rows, sp500_panel.spans(), sp500_panel.read_holes(), sp500_panel.calendar())
        ranked = sp500_panel.monthly_coverage(*args)
        unranked = sp500_panel.monthly_coverage(*args, previous={}, rank=False)
        tally = pd.Series([r for m in unranked for r in m.reasons]).value_counts().to_dict()
        assert tally == {
            "no-row": 3654,
            "price": 2229,
            "no-series": 933,
            "stopped": 89,
            "next": 14,
            "close": 8,
        }
        assert sum(m.covered for m in unranked) == 100188
        assert sum(m.covered for m in ranked) + 1852 == 100188

    def test_the_survivor_label_counts(self) -> None:
        """Point 9: 6,816 of 107,115 member-months fail, and 697 of 2,187 failing rows remain."""
        rows = sp500_panel.load()
        gap = survivor_gap(tuple(rows), tuple(sp500_panel.coverage_from_committed(rows)))
        assert (gap.failed_member_months, gap.member_months) == (6816, 107115)
        assert (gap.still_listed, gap.failed_rows) == (697, 2187)
        assert gap.last_schedule == "2026-06-30"


class TestTheMarketLine:
    """SPY's line in the ``sp500`` cross-section, recorded for this run on 2026-10-11."""

    def test_spy_is_one_alpha_vantage_line_downloaded_2026_10_11(self) -> None:
        lines = [
            e
            for e in read_archive_manifest()
            if e.cross_section == "sp500" and e.symbol == low_beta_holdout.MARKET
        ]
        assert len(lines) == 1
        (line,) = lines
        assert line.download_date == "2026-10-11"
        assert line.path == "sp500/daily_SPY.csv"
        assert (line.first_date, line.last_date, line.row_count) == (
            "1999-11-01",
            "2026-10-09",
            6776,
        )
        assert line.sha256 == "09aaccd95d3418ecee946a9091d65e517958b07143c144373143aa4726744350"
        assert line.vendor_call == "TIME_SERIES_DAILY_ADJUSTED, outputsize=full, datatype=csv"

    def test_spy_is_not_a_member_ticker(self) -> None:
        assert low_beta_holdout.MARKET not in sp500_panel.tickers(sp500_panel.load())

    def test_every_other_sp500_line_was_downloaded_2026_10_05(self) -> None:
        text = (DATA_DIR / "archive_vintages.jsonl").read_text(encoding="utf-8")
        dates = {
            json.loads(line)["download_date"]
            for line in text.splitlines()
            if line.strip()
            and json.loads(line).get("cross_section") == "sp500"
            and json.loads(line)["symbol"] != low_beta_holdout.MARKET
        }
        assert dates == {"2026-10-05"}
