"""The pins for issue 526's holdout of Chan's low-beta leverage rule, and the rules behind them.

This file is the single authority for every number any prose surface quotes
about [issue 526](https://github.com/l3a0/quantitative-trading/issues/526).
``docs/replication-log.md`` Entry 49 carries the verdict and points here.
``blog/low-beta-holdout-lessons.md`` quotes most of these figures, so a change
to an assertion here moves that post too. ``TestWhatThePostCounted`` and
``TestWhatThePostMeasured`` hold the numbers it added after the run.

Every archive pin reads one set of vintages under one specification, so both
are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintages.** The members, ``research/filings/ivv/members.csv``, and its
  holes file, at the sha256s :data:`MEMBERS_SHA256` and :data:`HOLES_SHA256`
  hold, read from IVV's 70 quarter-end schedules from 2008-12-31 to
  2026-06-30, each carried forward. The members' closes and volumes, Alpha
  Vantage's ``TIME_SERIES_DAILY_ADJUSTED`` in the 817 ``sp500`` lines the
  members file maps to, downloaded 2026-10-05. SPY's ``adjusted_close``, the
  ``sp500`` line downloaded 2026-10-11 for this run. The calendar, the
  committed raw SPY vintage downloaded 2026-10-03. FRED's TB3MS, downloaded
  2026-09-30. The bytes of the Alpha Vantage lines sit in the owner's archive.
- **Specification.** Issue 275's plan, registered 2026-10-11, with its ruin
  amendment, as :mod:`chan.low_beta_leverage` computes it, and the changes
  issue 526 registered the same day before any beta or return was computed on
  this panel: IVV's covered members at t without Example 7.7's ``rank``
  reason, each series cut at its last row that traded and earning its return
  to its last close, SPY from the archive on the committed calendar, and
  formations from 2008-12-31 to 2026-07-31. Issue 526's second amendment of
  2026-10-11 skips a formation whose low group's mean beta is zero or below.

The result is **registered**, under both amendments of 2026-10-11. The skip
rule was chosen after the first non-positive formation, 2026-04-30, was
visible, and before anything the criterion reads had been computed. Every
holding month comes after the book, so the span is a holdout. Membership is
only as complete as the monthly coverage rule allows, which the survivor label
pins.

The archive pins skip where no archive is configured or ``QT_ARCHIVE_RUN`` is
not 1, the way ``tests/conftest.py``'s ``archive_skip_reason`` decides. Every
other test reads committed files or frames built by hand, and runs
everywhere, so CI exercises the ``members`` and ``skip_non_positive``
keywords of :func:`chan.low_beta_leverage.build_portfolios`, the
holding-month rule and the run's helpers. The figures are pinned at four
decimals, which is what the log quotes. The run first ran here on 2026-10-11.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter

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
    next_reads,
    refuse_uncovered,
    skipped_line,
    survivor_gap,
)
from chan.low_beta_leverage import (
    BETA_DAYS,
    CRITICAL,
    NonPositiveBeta,
    build_portfolios,
    daily_excess,
    differences,
    fit_beta,
    growth,
    kelly,
    read_sources,
    realised_beta,
    ruin_line,
    ruinous_leverage,
    sharpe,
    verdict,
)
from chan.paths import DATA_DIR
from chan.series import row_month_ends
from chan.vintage import VintageUnavailable
from tests.conftest import archive_skip_reason
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

    def test_a_month_end_listed_twice_is_refused(self) -> None:
        closes = frame()
        days = ENDS.append(ENDS[-1:])
        with pytest.raises(ValueError, match="increasing date order"):
            build_portfolios(closes, spy(), rates(), members=everyone(closes, days))

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


def negative_in_one_month() -> tuple[pd.DataFrame, pd.DataFrame]:
    """A panel whose low group is N, at a beta of −0.5, only at the formation of 2001-01-31."""
    closes = panel(rates(0.06), N=-0.5, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5)
    mask = everyone(closes)
    mask["N"] = mask.index == HELD_TO
    return closes, mask


class TestTheSkipAmendment:
    """Issue 526's amendment of 2026-10-11: a non-positive low group's formation is skipped."""

    def test_without_the_keyword_it_still_refuses(self) -> None:
        closes, mask = negative_in_one_month()
        with pytest.raises(NonPositiveBeta, match="formed 2001-01-31 has a mean beta of -0.5000"):
            build_portfolios(closes, spy(), rates(0.06), members=mask)

    def test_the_formation_is_listed_with_both_groups_mean_betas(self) -> None:
        closes, mask = negative_in_one_month()
        p = build_portfolios(closes, spy(), rates(0.06), members=mask, skip_non_positive=True)
        assert len(p.skipped) == 1
        (skip,) = p.skipped
        assert (skip.formed, skip.held_to) == (HELD_TO, NEXT)
        assert skip.low_beta == pytest.approx(-0.5, abs=1e-9)
        assert skip.high_beta == pytest.approx(2.5, abs=1e-9)

    def test_its_holding_month_leaves_every_series(self) -> None:
        closes, mask = negative_in_one_month()
        kept = build_portfolios(closes, spy(), rates(0.06), members=mask, skip_non_positive=True)
        whole = build_portfolios(
            closes, spy(), rates(0.06), members=mask.assign(N=False), skip_non_positive=True
        )
        assert whole.skipped == ()
        assert len(kept.formed) == len(whole.formed) - 1
        assert HELD_TO not in kept.formed and NEXT not in kept.held_to
        remaining = [day for day in whole.held_to if day != NEXT]
        for name in ("low", "high", "levered", "rf", "spy", "low_beta", "high_beta", "leverage"):
            series = getattr(kept, name)
            assert list(series.index) == remaining, name
            assert series.equals(getattr(whole, name).drop(NEXT)), name
        assert kept.eligible == tuple(
            count for day, count in zip(whole.formed, whole.eligible, strict=True) if day != HELD_TO
        )
        for name in ("low_members", "high_members"):
            assert getattr(kept, name) == tuple(
                held
                for day, held in zip(whole.formed, getattr(whole, name), strict=True)
                if day != HELD_TO
            ), name
        assert list(kept.betas.index) == list(kept.formed)
        assert kept.window_start == tuple(
            start
            for day, start in zip(whole.formed, whole.window_start, strict=True)
            if day != HELD_TO
        )

    def test_the_verdict_counts_only_the_months_that_remain(self) -> None:
        closes, mask = negative_in_one_month()
        p = build_portfolios(closes, spy(), rates(0.06), members=mask, skip_non_positive=True)
        assert verdict(p).months == len(p.held_to) == len(p.levered)

    def test_the_report_line_names_the_count_and_the_first(self) -> None:
        closes, mask = negative_in_one_month()
        p = build_portfolios(closes, spy(), rates(0.06), members=mask, skip_non_positive=True)
        assert skipped_line(p) == (
            "  1 formation skipped under issue 526's amendment of 2026-10-11, the first formed "
            "2001-01-31: a low group's mean beta of zero or below has no beta-matched leverage."
        )
        none = build_portfolios(closes, spy(), rates(0.06), members=mask.assign(N=False))
        assert "none is skipped" in skipped_line(none)

    def test_two_skips_are_both_listed_and_the_line_names_the_first(self) -> None:
        closes, mask = negative_in_one_month()
        mask["N"] = mask.index.isin([HELD_TO, NEXT])
        p = build_portfolios(closes, spy(), rates(0.06), members=mask, skip_non_positive=True)
        assert [skip.formed for skip in p.skipped] == [HELD_TO, NEXT]
        assert skipped_line(p).startswith(
            "  2 formations skipped under issue 526's amendment of 2026-10-11, the first formed "
            "2001-01-31:"
        )

    def test_a_low_group_mean_beta_of_exactly_zero_is_skipped(self) -> None:
        """The amendment skips zero as well as below, since zero has no leverage either."""
        closes = panel(rates(), Z=0.0, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5)
        mask = everyone(closes)
        mask["Z"] = mask.index == HELD_TO
        p = build_portfolios(closes, spy(), rates(), members=mask, skip_non_positive=True)
        assert [(skip.formed, skip.low_beta) for skip in p.skipped] == [(HELD_TO, 0.0)]


class TestTheRunsHelpers:
    def test_the_frame_starts_252_rows_before_2008_12_31_and_ends_2026_08_31(self) -> None:
        days = frame_days(sp500_panel.calendar())
        assert days[BETA_DAYS] == pd.Timestamp("2008-12-31")
        assert days[0] == pd.Timestamp("2008-01-02")
        assert days[-1] == pd.Timestamp("2026-08-31")
        assert len(days) == 4695

    def test_a_calendar_short_of_252_rows_before_2008_12_31_is_refused(self) -> None:
        calendar = sp500_panel.calendar()
        short = calendar[calendar >= pd.Timestamp("2008-06-02")]
        with pytest.raises(HoldoutRefused, match="rows before 2008-12-31, not 252"):
            frame_days(short)

    def test_a_close_on_a_day_the_calendar_lacks_is_counted(self) -> None:
        """2001-01-04 is off the calendar and only A has a close there. 2001-01-08 is past it."""
        days = pd.DatetimeIndex(["2001-01-02", "2001-01-03", "2001-01-05"])
        series = pd.DataFrame(
            {"A": [1.0, 2.0, 3.0, 4.0], "B": [1.0, np.nan, 3.0, 4.0]},
            index=pd.DatetimeIndex(["2001-01-02", "2001-01-04", "2001-01-05", "2001-01-08"]),
        )
        assert low_beta_holdout.off_calendar(series, days) == 1

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

    def test_a_member_covered_at_t_only_is_still_refused_with_no_close_at_t_plus_1(self) -> None:
        """Its formation reads t + 1, so the check cannot wait for the month that covers it."""
        closes = frame()
        closes.loc[HELD_TO, "C"] = np.nan
        mask = everyone(closes, ENDS[ENDS >= FORMED])
        mask.loc[HELD_TO, "C"] = False
        with pytest.raises(HoldoutRefused, match="formed 2000-12-29: covered member C"):
            refuse_uncovered(closes, mask)

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

    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(**_: object) -> None:
            raise HoldoutRefused("no")

        monkeypatch.setattr(low_beta_holdout, "run", refuse)
        monkeypatch.setattr("sys.argv", ["low_beta_holdout"])
        with pytest.raises(SystemExit, match="^no$"):
            low_beta_holdout.main()


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
        assert sum(tally.values()) == 107115 - 100188 == 6927

    def test_the_survivor_label_counts(self) -> None:
        """Point 9: the rule leaves out 6,927 of 107,115, and 6,816 fail the row check.

        4,614 of the 6,816 carry a ticker absent from the 2026-06-30 schedule,
        and 697 of the 2,187 failing rows carry one still in it.
        """
        rows = sp500_panel.load()
        args = (rows, sp500_panel.spans(), sp500_panel.read_holes(), sp500_panel.calendar())
        unranked = sp500_panel.monthly_coverage(*args, previous={}, rank=False)
        gap = survivor_gap(tuple(rows), tuple(unranked))
        assert (gap.left_out, gap.member_months) == (6927, 107115)
        assert (gap.failed_member_months, gap.absent_member_months) == (6816, 4614)
        assert (gap.still_listed, gap.failed_rows) == (697, 2187)
        assert gap.last_schedule == "2026-06-30"

    def test_the_rank_reason_leaves_the_row_check_failures_unchanged(self) -> None:
        rows = sp500_panel.load()
        gap = survivor_gap(tuple(rows), tuple(sp500_panel.coverage_from_committed(rows)))
        assert (gap.failed_member_months, gap.absent_member_months) == (6816, 4614)
        assert gap.left_out == 6927 + 1852


def formation_days(calendar: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """The 212 formation month-ends the span allows, 2008-12-31 to 2026-07-31."""
    months = pd.period_range(sp500_panel.FIRST_MONTH, low_beta_holdout.LAST_HELD - 1, freq="M")
    return pd.DatetimeIndex([sp500_panel.month_end(calendar, month) for month in months])


class TestTheExclusionsThatReadTPlus1:
    """Point 4 keeps two exclusions that read t + 1: a last row at t and a hole at t + 1.

    On the manifest's spans, before each series is cut at its last row that
    traded, the rule's ``next`` reason leaves out 14 member-months at the 212
    formations, which is the count issue 526 cites from issue 336. They split
    5 and 9. The run's cut moves both, so its own split, held below the archive
    line, differs.
    """

    def test_the_audits_14_split_5_with_a_last_row_at_t_and_9_with_a_hole(self) -> None:
        rows = sp500_panel.load()
        calendar = sp500_panel.calendar()
        args = (rows, sp500_panel.spans(), sp500_panel.read_holes(), calendar)
        coverage = tuple(sp500_panel.monthly_coverage(*args, previous={}, rank=False))
        reads = next_reads(tuple(rows), coverage, *args[1:], formation_days(calendar))
        assert reads.last_row_at_t == (
            ("2015-10", "HCBK"),
            ("2016-05", "ARG"),
            ("2018-05", "WYN"),
            ("2018-09", "ANDV"),
            ("2018-12", "SCG"),
        )
        assert len(reads.hole_at_t1) == 9
        assert reads.hole_at_t1[0] == ("2012-05", "NVLS")

    def test_only_the_formations_passed_are_read(self) -> None:
        rows = sp500_panel.load()
        calendar = sp500_panel.calendar()
        args = (rows, sp500_panel.spans(), sp500_panel.read_holes(), calendar)
        coverage = tuple(sp500_panel.monthly_coverage(*args, previous={}, rank=False))
        days = formation_days(calendar)
        reads = next_reads(tuple(rows), coverage, *args[1:], days[days <= "2016-12-31"])
        assert [month for month, _ in reads.last_row_at_t] == ["2015-10", "2016-05"]

    def test_a_next_miss_with_neither_cause_is_refused(self) -> None:
        rows = sp500_panel.load()
        calendar = sp500_panel.calendar()
        args = (rows, sp500_panel.spans(), sp500_panel.read_holes(), calendar)
        coverage = tuple(sp500_panel.monthly_coverage(*args, previous={}, rank=False))
        with pytest.raises(HoldoutRefused, match="NVLS misses 2012-05 for next"):
            next_reads(
                tuple(rows), coverage, args[1], frozenset(), calendar, formation_days(calendar)
            )


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

    def test_spy_as_a_member_ticker_is_refused_before_any_read(self, monkeypatch) -> None:
        monkeypatch.setattr(sp500_panel, "tickers", lambda rows: ["AAA", low_beta_holdout.MARKET])
        with pytest.raises(HoldoutRefused, match="SPY is a member ticker"):
            low_beta_holdout.read_holdout()

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


#: The label every number ``blog/low-beta-holdout-lessons.md`` added carries.
AFTER_THE_RUN = "measured by the write-up after the run, so exploratory, and it decides nothing"


class TestWhatThePostCounted:
    """Counts ``blog/low-beta-holdout-lessons.md`` quotes from committed files alone.

    The write-up counted every one of them after the run. Those on IVV's
    members read the members file and holes file whose sha256s
    :data:`MEMBERS_SHA256` and :data:`HOLES_SHA256` hold, the manifest's spans
    and the committed SPY calendar, with Example 7.7's ``rank`` reason left out
    as point 3 of the registration says. The one on Chan's file reads his
    committed files through :func:`chan.low_beta_leverage.read_sources`. None
    decides anything.
    """

    def test_most_row_check_failures_fall_in_2009_to_2015(self) -> None:
        """5,891 of the 6,816 member-months failing the row check against the filing."""
        rows = sp500_panel.load()
        args = (rows, sp500_panel.spans(), sp500_panel.read_holes(), sp500_panel.calendar())
        coverage = sp500_panel.monthly_coverage(*args, previous={}, rank=False)
        years = [
            month.month[:4]
            for month in coverage
            for reason in month.reasons
            if reason not in sp500_panel.MISSES
        ]
        early = sum(1 for year in years if "2009" <= year <= "2015")
        assert (early, len(years)) == (5891, 6816), AFTER_THE_RUN

    def test_70_schedules_each_carried_two_months_or_five_once(self) -> None:
        """Each schedule sets its own month and the months up to the next one.

        So a change in the index between two schedules is dated up to two
        months late, or five after 2013-06-30, because 2013-09-30 has no full
        schedule.
        """
        schedules = sp500_panel.schedule_months()
        assert len(schedules) == 70
        assert (schedules[0][0], schedules[-1][0]) == ("2008-12-31", "2026-06-30")
        carried = {
            date: (after - first).n - 1
            for (date, first), (_, after) in zip(schedules[:-1], schedules[1:], strict=True)
        }
        assert {date: n for date, n in carried.items() if n != 2} == {"2013-06-30": 5}
        assert sum(1 for n in carried.values() if n == 2) == 68, AFTER_THE_RUN
        last, first = schedules[-1]
        assert (last, (sp500_panel.LAST_MONTH - first).n) == ("2026-06-30", 2), AFTER_THE_RUN

    def test_the_failing_rows_split_by_the_row_checks_three_outcomes(self) -> None:
        """No close on the price date, a close the filing disagrees with, or no series.

        The 6,816 failing member-months split 3,654, 2,229 and 933 the same
        way, which ``TestTheCoverageWithoutRank`` holds from the audit.
        """
        failing = Counter(row.check for row in sp500_panel.load() if row.check != "pass")
        assert failing == {"no-row": 1186, "price": 697, "no-series": 304}, AFTER_THE_RUN
        assert failing.total() == 2187

    def test_three_member_rows_in_four_carry_a_ticker_still_listed_against_one_failing_in_three(
        self,
    ) -> None:
        """The base rate the failing rows' 697 of 2,187 is read against.

        A ticker absent from the 2026-06-30 schedule marks a company that left
        the index or one that only changed its ticker, and the count cannot
        tell the two apart.
        """
        rows = sp500_panel.load()
        last = sp500_panel.schedule_months()[-1][0]
        listed = {row.ticker for row in rows if row.report_date == last and row.ticker}
        failing = [row for row in rows if row.check != "pass"]
        every = (sum(1 for row in rows if row.ticker in listed), len(rows))
        failed = (sum(1 for row in failing if row.ticker in listed), len(failing))
        assert (every, failed) == ((26353, 35205), (697, 2187)), AFTER_THE_RUN
        assert [f"{100 * n / of:.1f}" for n, of in (every, failed)] == ["74.9", "31.9"]

    def test_on_chans_file_the_close_at_t_plus_1_left_out_only_missing_closes(self) -> None:
        """17 stocks at 6 formations, each with closes after the month-end it lacks.

        Issue 275's rule asks for a close at the formation and at the next
        month-end. No series in Chan's file ends before the file's last day, so
        the rule never removed a company that left. It removed only a stock
        with a hole at the next month-end, which is still a look ahead.
        """
        _, closes, _, spy, _, bills = read_sources()
        p = build_portfolios(closes, spy, bills)
        cut = closes.loc[closes.index.isin(spy.index)]
        assert (cut.apply(pd.Series.last_valid_index) == cut.index[-1]).all(), AFTER_THE_RUN
        stock = daily_excess(cut, bills).to_numpy()
        market = daily_excess(spy.loc[cut.index].to_frame(), bills).to_numpy()[:, 0]
        left_out = {}
        for formed, held_to, eligible in zip(p.formed, p.held_to, p.eligible, strict=True):
            end = cut.index.get_loc(formed)
            window = slice(end - BETA_DAYS + 1, end + 1)
            gone = [
                j
                for j in np.flatnonzero(cut.loc[formed].notna() & cut.loc[held_to].isna())
                if np.isfinite(fit_beta(stock[window, j], market[window]))
            ]
            if gone:
                after_it = cut.iloc[cut.index.get_loc(held_to) + 1 :, gone]
                assert after_it.notna().any().all(), formed
                left_out[str(formed.date())] = (eligible + len(gone), eligible)
        assert left_out == {
            "2000-11-30": (454, 453),
            "2001-01-31": (455, 444),
            "2001-11-30": (464, 463),
            "2002-09-30": (475, 474),
            "2004-09-30": (481, 480),
            "2005-10-31": (488, 486),
        }, AFTER_THE_RUN
        assert sum(before - kept for before, kept in left_out.values()) == 17, AFTER_THE_RUN


# --- the archive pins ------------------------------------------------------------

SPEC = (
    "IVV's covered members 2008-12-31 to 2026-07-31 without the rank reason, sp500 Alpha "
    "Vantage adjusted dl 2026-10-05, SPY's sp500 line dl 2026-10-11, raw SPY calendar dl "
    "2026-10-03, TB3MS dl 2026-09-30, series cut at their last traded row, 252-day "
    "excess-return betas with an intercept and 200 finite, lowest and highest fifth ties by "
    "symbol, equal-weighted, low levered to the high fifth's mean beta at the bill, registered "
    "2026-10-11 with issue 275's ruin amendment and issue 526's skip amendment"
)

#: The members file and its holes file, the hashes ``tests/test_equity_seasonals.py``
#: holds for issue 336's run on the same panel.
MEMBERS_SHA256 = "0b8e0f8ca7eaf388eda4784ebe30bd787b5bd4a857ffaf49c38a25676435445b"
HOLES_SHA256 = "85c6c9498610e82f2852eafb9fcffcedabbfe8870ccc4f334f311f62de770158"


def pin(value: float, full: float, printed: str) -> None:
    """The full value at 1e-9, and the figure at the four decimals the log quotes."""
    assert value == pytest.approx(full, abs=1e-9), SPEC
    assert f"{value:.4f}" == printed, SPEC


@pytest.fixture(scope="module")
def holdout() -> low_beta_holdout.Holdout:
    """One run on the owner's archive, or a skip naming what is missing."""
    reason = archive_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    return low_beta_holdout.read_holdout()


class TestTheCommittedVintage:
    """The committed half of the vintage, which runs everywhere."""

    def test_the_members_and_holes_files(self) -> None:
        for path, digest in (
            (sp500_panel.MEMBERS_PATH, MEMBERS_SHA256),
            (sp500_panel.HOLES_PATH, HOLES_SHA256),
        ):
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path


class TestTheVintages:
    def test_817_member_series_downloaded_2026_10_05(self, holdout) -> None:
        assert len(holdout.entries) == 817
        assert {entry.download_date for entry in holdout.entries} == {"2026-10-05"}

    def test_the_market_is_spys_sp500_line_downloaded_2026_10_11(self, holdout) -> None:
        entry = holdout.spy_entry
        assert (entry.path, entry.download_date) == ("sp500/daily_SPY.csv", "2026-10-11")
        assert entry.sha256 == "09aaccd95d3418ecee946a9091d65e517958b07143c144373143aa4726744350"

    def test_the_calendar_and_the_bills(self, holdout) -> None:
        assert holdout.calendar.path == "yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv"
        assert holdout.bill_entry.path == "fred_tb3ms_rate_1934-01-01_2026-08-01_dl2026-09-30.csv"

    def test_121_series_stop_before_their_files_last_row_and_none_is_off_the_calendar(
        self, holdout
    ) -> None:
        assert (holdout.moved, holdout.off_calendar) == (121, 0)


class TestTheWindow:
    def test_212_formations_of_which_4_are_skipped_leave_208_months(self, holdout) -> None:
        p = holdout.portfolios
        assert len(p.formed) + len(p.skipped) == 212, SPEC
        assert len(p.formed) == len(p.levered) == holdout.verdict.months == 208, SPEC

    def test_formed_2008_12_31_to_2026_03_31_held_to_2009_01_30_to_2026_04_30(
        self, holdout
    ) -> None:
        p = holdout.portfolios
        assert (p.formed[0], p.formed[-1]) == (
            pd.Timestamp("2008-12-31"),
            pd.Timestamp("2026-03-31"),
        )
        assert (p.held_to[0], p.held_to[-1]) == (
            pd.Timestamp("2009-01-30"),
            pd.Timestamp("2026-04-30"),
        )
        assert p.window_start[0] == pd.Timestamp("2008-01-03")

    def test_the_four_skipped_formations_are_the_last_four(self, holdout) -> None:
        skipped = [
            (str(s.formed.date()), str(s.held_to.date()), f"{s.low_beta:.4f}", f"{s.high_beta:.4f}")
            for s in holdout.portfolios.skipped
        ]
        assert skipped == [
            ("2026-04-30", "2026-05-29", "-0.0037", "1.8278"),
            ("2026-05-29", "2026-06-30", "-0.0652", "1.8696"),
            ("2026-06-30", "2026-07-31", "-0.1429", "1.9202"),
            ("2026-07-31", "2026-08-31", "-0.2083", "1.9536"),
        ], SPEC


class TestTheVerdict:
    def test_the_claim_is_not_decided(self, holdout) -> None:
        result = holdout.verdict
        assert result.outcome == "Not decided", SPEC
        assert result.log_verdict == "did not reproduce"
        assert not result.by_ruin

    def test_the_gap_its_newey_west_t_and_y(self, holdout) -> None:
        result = holdout.verdict
        pin(result.gap, -0.0589652916025023, "-0.0590")
        pin(result.t, -0.49744786548357683, "-0.4974")
        pin(result.detectable, 0.29475067494007157, "0.2948")
        assert result.lag == 4

    def test_the_wording(self, holdout) -> None:
        assert holdout.verdict.line() == (
            "No gap in compounded growth detectable above about 0.2948 a year over 208 months, "
            "where the point estimate is -0.0590."
        )
        assert skipped_line(holdout.portfolios) == (
            "  4 formations skipped under issue 526's amendment of 2026-10-11, the first formed "
            "2026-04-30: a low group's mean beta of zero or below has no beta-matched leverage."
        )

    def test_no_month_is_ruined(self, holdout) -> None:
        pin(float(holdout.portfolios.levered.min()), -0.8014142983510244, "-0.8014")
        assert holdout.portfolios.levered.idxmin() == pd.Timestamp("2024-12-31")

    def test_the_worst_month_levered_the_low_fifth_by_12_3588(self, holdout) -> None:
        p = holdout.portfolios
        worst = pd.Timestamp("2024-12-31")
        pin(float(p.leverage[worst]), 12.358835874284544, "12.3588")
        pin(float(p.low[worst]), -0.06157503682164154, "-0.0616")


class TestTheSideFigures:
    """Point estimates nothing tests. They decide nothing."""

    @pytest.mark.parametrize(
        ("name", "grew", "sharpe_ratio", "beta"),
        [
            ("levered", (0.10230235253506925, "0.1023"), (0.5223232626340111, "0.5223"),
             (1.831587431296448, "1.8316")),
            ("low", (0.10692577887607406, "0.1069"), (0.8607134994409417, "0.8607"),
             (0.5580005873941899, "0.5580")),
            ("high", (0.16126764413757155, "0.1613"), (0.6769965150953369, "0.6770"),
             (1.646059705686792, "1.6461")),
        ],
    )  # fmt: skip
    def test_growth_sharpe_and_realised_beta(
        self, holdout, name: str, grew: tuple, sharpe_ratio: tuple, beta: tuple
    ) -> None:
        p = holdout.portfolios
        series = getattr(p, name)
        pin(growth(series), *grew)
        pin(sharpe(series, p.rf), *sharpe_ratio)
        pin(realised_beta(series, p), *beta)

    def test_spys_growth(self, holdout) -> None:
        pin(growth(holdout.portfolios.spy), 0.13781540996129263, "0.1378")

    def test_the_leverage_path(self, holdout) -> None:
        k = holdout.portfolios.leverage
        pin(float(k.mean()), 3.824675314178739, "3.8247")
        pin(float(k.min()), 1.8988305642817076, "1.8988")
        pin(float(k.max()), 27.97270893593621, "27.9727")
        # Indexed by the month-end each holding month ends on, so the highest k
        # was formed 2025-03-31 and the lowest 2015-12-31.
        assert (k.idxmin(), k.idxmax()) == (pd.Timestamp("2016-01-29"), pd.Timestamp("2025-04-30"))
        p = holdout.portfolios
        formed = dict(zip(p.held_to, p.formed, strict=True))
        assert (formed[k.idxmin()], formed[k.idxmax()]) == (
            pd.Timestamp("2015-12-31"),
            pd.Timestamp("2025-03-31"),
        ), SPEC

    def test_the_low_groups_mean_beta_over_the_formations_kept(self, holdout) -> None:
        low = holdout.portfolios.low_beta
        pin(float(low.min()), 0.05626349094593196, "0.0563")
        pin(float(low.max()), 0.7317092155167064, "0.7317")
        # The low group's lowest mean beta and the highest k share a formation.
        assert low.idxmin() == holdout.portfolios.leverage.idxmax() == pd.Timestamp("2025-04-30")

    def test_the_kelly_reading_labelled_look_ahead(self, holdout) -> None:
        reading = kelly(holdout.portfolios)
        pin(reading.leverage, 7.363247579568249, "7.3632")
        pin(reading.bill, 0.013585576923076926, "0.0136")
        pin(reading.moments.levered_growth, 0.3704138640599359, "0.3704")
        pin(reading.growth, 0.38399944098301286, "0.3840")

    def test_the_counts(self, holdout) -> None:
        p = holdout.portfolios
        sizes = [len(held) for held in p.low_members]
        assert (min(p.eligible), max(p.eligible)) == (389, 501), SPEC
        assert (min(sizes), max(sizes), sum(sizes)) == (77, 100, 19377), SPEC
        assert (sum(holdout.members), sum(holdout.covered), sum(p.eligible)) == (
            104600,
            97667,
            97302,
        ), SPEC

    def test_the_survivor_label(self, holdout) -> None:
        s = holdout.survivors
        assert (s.left_out, s.member_months) == (6943, 107115), SPEC
        assert (s.failed_member_months, s.absent_member_months) == (6816, 4614)
        assert (s.still_listed, s.failed_rows, s.last_schedule) == (697, 2187, "2026-06-30")

    def test_the_exclusions_that_read_t_plus_1(self, holdout) -> None:
        reads = holdout.reads_next
        assert reads.last_row_at_t == (
            ("2010-02", "PBG"),
            ("2011-02", "MFE"),
            ("2012-03", "MHS"),
            ("2014-06", "FRX"),
            ("2015-10", "HCBK"),
            ("2016-06", "GAS"),
            ("2016-06", "CPGX"),
            ("2017-10", "LVLT"),
            ("2018-05", "WYN"),
            ("2018-09", "ANDV"),
            ("2018-12", "SCG"),
            ("2022-09", "DRE"),
        ), SPEC
        assert reads.hole_at_t1 == (
            ("2012-05", "NVLS"),
            ("2014-10", "WAG"),
            ("2016-02", "PCL"),
            ("2016-03", "CAM"),
        ), SPEC


def after(value: float, full: float, printed: str) -> None:
    """:func:`pin` with the label every number the write-up added carries."""
    assert value == pytest.approx(full, abs=1e-9), f"{SPEC}; {AFTER_THE_RUN}"
    assert f"{value:.4f}" == printed, f"{SPEC}; {AFTER_THE_RUN}"


class TestWhatThePostMeasured:
    """Numbers ``blog/low-beta-holdout-lessons.md`` quotes that no row of Entry 49 declared.

    The write-up measured every one of them after the run, on the vintages and
    the specification in :data:`SPEC`, so each is exploratory and none carries
    a verdict. The upper bound reads the registered test's own standard error,
    and the ruin line and the ruinous leverage are the helpers Entry 45's post
    added after its run. A beta or a leverage is named by its formation date,
    and a return or a ruin line by its holding month.
    """

    def test_the_one_sided_upper_bound_on_the_levered_sides_advantage(self, holdout) -> None:
        """The gap plus 1.645 yearly standard errors, which Y's own error is read from."""
        result = holdout.verdict
        error = result.standard_error * 12
        after(error, 0.11853562090407446, "0.1185")
        after(result.gap + CRITICAL * error, 0.13602580478470022, "0.1360")
        # Y is 1.645 + 0.8416 of the same yearly error, written out rather than
        # read from the module's constants, so a wrong constant there fails.
        assert f"{(1.645 + 0.8416) * error:.4f}" == f"{result.detectable:.4f}" == "0.2948"

    def test_unlevered_the_high_fifth_out_compounded_the_low_by_0_0543(self, holdout) -> None:
        """From the full values, since the rounded 0.1613 and 0.1069 differ by 0.0544."""
        p = holdout.portfolios
        after(growth(p.high) - growth(p.low), 0.05434186526149749, "0.0543")

    def test_the_high_fifths_beta_where_k_peaked(self, holdout) -> None:
        p = holdout.portfolios
        peak = pd.Timestamp("2025-04-30")
        assert p.leverage.idxmax() == peak, SPEC
        after(float(p.high_beta[peak]), 1.573842255950237, "1.5738")

    def test_the_low_fifths_beta_fell_below_0_10_twice_and_never_below_0_05(self, holdout) -> None:
        p = holdout.portfolios
        low = pd.Series(p.low_beta.to_numpy(), index=pd.DatetimeIndex(p.formed))
        below = low[low < 0.10]
        assert [str(day.date()) for day in below.index] == ["2025-02-28", "2025-03-31"], (
            f"{SPEC}; {AFTER_THE_RUN}"
        )
        after(float(below.iloc[0]), 0.0818444983180052, "0.0818")
        assert not (low < 0.05).any(), f"{SPEC}; {AFTER_THE_RUN}"

    def test_december_2024_against_its_ruin_line(self, holdout) -> None:
        """The match asked for 0.80 of the leverage that ruins the month, the most of any month."""
        p = holdout.portfolios
        dec = pd.Timestamp("2024-12-31")
        line = ruin_line(p.rf, p.leverage)
        needed = ruinous_leverage(p.low, p.rf)
        after(float(line[dec]), -0.07764335455552938, "-0.0776")
        after(float(p.low[dec] - line[dec]), 0.016068317733887845, "0.0161")
        after(float(needed[dec]), 15.40774461609341, "15.4077")
        share = p.leverage / needed
        assert round(float(share[dec]), 2) == 0.80, f"{SPEC}; {AFTER_THE_RUN}"
        assert share.idxmax() == dec, f"{SPEC}; {AFTER_THE_RUN}"
        assert list(p.low.sort_values().index).index(dec) + 1 == 7, f"{SPEC}; {AFTER_THE_RUN}"

    def test_april_2025_at_the_highest_k_came_closest_to_its_line(self, holdout) -> None:
        p = holdout.portfolios
        apr = pd.Timestamp("2025-04-30")
        line = ruin_line(p.rf, p.leverage)
        after(float(p.low[apr]), -0.01755230845359701, "-0.0176")
        after(float(p.levered[apr]), -0.5856148693764847, "-0.5856")
        after(float(line[apr]), -0.03236621623680636, "-0.0324")
        after(float(ruinous_leverage(p.low, p.rf)[apr]), 47.648516293367805, "47.6485")
        margin = p.low - line
        assert margin.idxmin() == apr, f"{SPEC}; {AFTER_THE_RUN}"
        after(float(margin[apr]), 0.014813907783209353, "0.0148")

    def test_no_month_reached_its_own_ruin_line(self, holdout) -> None:
        p = holdout.portfolios
        reached = p.low <= ruin_line(p.rf, p.leverage)
        assert (int(reached.sum()), len(reached)) == (0, 208), f"{SPEC}; {AFTER_THE_RUN}"

    def test_december_2024_alone_sets_the_sign_of_the_gap(self, holdout) -> None:
        """Twelve times the mean of d over the months left when one or two are dropped.

        Dropping a month is not a test. It shows that the point estimate's sign
        rests on December 2024, the month whose d is furthest below zero.
        """
        d = differences(holdout.portfolios)
        dec, mar = pd.Timestamp("2024-12-31"), pd.Timestamp("2026-03-31")
        assert list(d.sort_values().index[:2]) == [dec, mar], f"{SPEC}; {AFTER_THE_RUN}"
        after(float(d[dec]), -1.562445940052367, "-1.5624")
        after(float(d[mar]), -1.1581706211023435, "-1.1582")
        after(float(d.drop(dec).mean() * 12), 0.03132642815124604, "0.0313")
        after(float(d.drop([dec, mar]).mean() * 12), 0.09894474796376723, "0.0989")

    def test_march_2026_was_the_second_worst_levered_month(self, holdout) -> None:
        p = holdout.portfolios
        mar = pd.Timestamp("2026-03-31")
        assert p.levered.sort_values().index[1] == mar, f"{SPEC}; {AFTER_THE_RUN}"
        after(float(p.levered[mar]), -0.7004677356362444, "-0.7005")
        after(float(p.leverage[mar]), 9.434203067644063, "9.4342")
        after(float(p.low[mar]), -0.07155822665330175, "-0.0716")
        after(float(p.high[mar]), -0.046258414248779016, "-0.0463")

    def test_march_2020_the_low_fifths_worst_month_came_at_a_low_k(self, holdout) -> None:
        p = holdout.portfolios
        mar = pd.Timestamp("2020-03-31")
        assert p.low.idxmin() == mar, f"{SPEC}; {AFTER_THE_RUN}"
        after(float(p.low[mar]), -0.12504426728454085, "-0.1250")
        after(float(p.leverage[mar]), 3.4162225462748657, "3.4162")
        after(float(ruin_line(p.rf, p.leverage)[mar]), -0.29255005082766206, "-0.2926")
        after(float(p.levered[mar]), -0.42776296562855215, "-0.4278")


class TestTheScaleBreakDecision:
    """Counted, not refused, as ``tests/test_scale_breaks.py`` records for this panel."""

    def test_820_flagged_days_in_98_stocks(self, holdout) -> None:
        days = sum(len(flagged) for flagged in holdout.flags.values())
        assert (days, len(holdout.flags)) == (820, 98)

    def test_34_low_and_321_high_stock_months_carry_a_flag(self, holdout) -> None:
        assert holdout.flagged == (34, 321)


class TestTheReport:
    def test_it_prints_the_verdict_the_skips_the_side_figures_and_every_label(
        self, holdout, capsys
    ) -> None:
        low_beta_holdout.report(holdout)
        out = capsys.readouterr().out
        assert "817 sp500 series" in out and "downloaded 2026-10-05" in out
        assert "sp500/daily_SPY.csv, Alpha Vantage adjusted, downloaded 2026-10-11" in out
        assert "formed 2008-12-31 to 2026-03-31" in out and "208 months" in out
        assert "389 to 501 stocks per formation, each portfolio 77 to 100" in out
        assert "mean 3.8247, min 1.8988, max 27.9727" in out
        assert "NOT DECIDED." in out
        assert "4 formations skipped" in out and "the first formed 2026-04-30" in out
        assert "formed 2026-07-31, held to 2026-08-31, low group's mean beta -0.2083" in out
        assert "mean x 12 -0.0590, Newey-West t -0.4974 at lag 4, Y 0.2948" in out
        assert "levered low      0.1023   0.5223   1.8316" in out
        assert "low              0.1069   0.8607   0.5580" in out
        assert "high             0.1613   0.6770   1.6461" in out
        assert "7.3632, Gaussian growth there r + S^2/2 = 0.0136 + 0.3704 = 0.3840" in out
        assert "34 low and 321 high stock-months of 38754" in out
        assert "leaves out 6943 of 107115 member-months. 6816 of them fail" in out
        assert "4614 of those with a ticker absent" in out and "697 carry a ticker" in out
        assert "12 member-months whose last row is t and 4 with a hole at t + 1" in out
        assert "quite wary of using too much leverage" in out
        assert "skip amendment" in out and "this is a holdout" in out
