"""Pins for Chan's two commodity seasonal trades, Entry 11 of the replication log.

Every figure ``docs/replication-log.md`` quotes for Entry 11 is derived here.
The vintages are EIA's NYMEX settlements, downloaded 2026-10-02 and recorded in
``data/vintages.jsonl``: contract 1 of New York Harbor regular gasoline and of
RBOB gasoline, and contracts 1 to 4 of Henry Hub natural gas. The gap fills in
``TestTheGapFills`` also read contract 2 of New York Harbor regular gasoline. The rules are the
sidebars' at Kindle locations 4536 and 4590, and every choice they leave open
was pinned on [issue 19](https://github.com/l3a0/quantitative-trading/issues/19)
before a trade was computed.
"""

from __future__ import annotations

import math
import re
import statistics
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from scipy import stats

from chan import futures
from chan.commodity_seasonals import (
    FILL_TEST_YEARS,
    GASOLINE_ENTRY,
    GASOLINE_EXIT,
    GASOLINE_YEARS,
    HARBOR_GASOLINE,
    HARBOR_GASOLINE_2,
    NATURAL_GAS,
    NG_ENTRY,
    NG_EXIT,
    NG_YEARS,
    RBOB_GASOLINE,
    RUN_START,
    Trade,
    change_p_value,
    count_test_days,
    daily_marks,
    easter,
    gap_fills,
    gasoline_symbol,
    gasoline_trade,
    gasoline_trades,
    is_trading_day,
    june_contract_number,
    main,
    max_drawdown,
    mean_interval,
    mean_return,
    natural_gas_trade,
    natural_gas_trades,
    ng_last_trade,
    ng_lead_days,
    on_or_after,
    on_or_before,
    pairs_won,
    profitable_count,
    rank_p_value,
    runs_ending,
    settlements,
    sharpe_ratio,
    sharpe_standard_error,
)
from chan.vintage import resolve_vintage


def outcomes(trades) -> dict[int, str]:
    word = {True: "profit", False: "loss", None: "missing"}
    return {trade.year: word[trade.profitable] for trade in trades}


GASOLINE = gasoline_trades(*GASOLINE_YEARS)
GAS = natural_gas_trades(*NG_YEARS)


class TestTheCalendar:
    """The trading calendar the four dates and the expiries are read on."""

    @pytest.mark.parametrize(
        ("year", "sunday"),
        [(1995, date(1995, 4, 16)), (2001, date(2001, 4, 15)), (2024, date(2024, 3, 31))],
    )
    def test_easter(self, year: int, sunday: date) -> None:
        assert easter(year) == sunday

    @pytest.mark.parametrize(
        "closed", [date(2018, 1, 15), date(2018, 7, 4), date(2001, 9, 11), date(2005, 12, 26)]
    )
    def test_holidays_and_closures_away_from_the_trades(self, closed: date) -> None:
        """No trade date reads these, so only this case holds the calendar to the exchange's."""
        assert not is_trading_day(closed)

    def test_good_friday_is_closed_and_the_day_before_is_open(self) -> None:
        assert not is_trading_day(date(2022, 4, 15))
        assert is_trading_day(date(2022, 4, 14))

    def test_a_holiday_row_in_the_files_is_not_a_trading_day(self) -> None:
        """The natural gas files carry 2018-12-25 as a row repeating the previous trading day."""
        _, rows = settlements(NATURAL_GAS[1])
        assert rows[date(2018, 12, 25)] == rows[date(2018, 12, 24)]
        assert not is_trading_day(date(2018, 12, 25))

    def test_holiday_rows_fill_2018_and_most_of_2019_and_almost_nothing_else(self) -> None:
        """Which of NYMEX's 261 holidays from 1994 to 2023 the natural gas files hold a row on.

        Every holiday from January 2018 to November 2019 has one, repeating the
        previous trading day's settlement in all four files, and outside those
        years only 2014-01-20 does. So only 2 of the 30 Good Fridays have a row.
        The 2007-01-02 closure, which is not a holiday, carries one too.
        """
        files = [settlements(NATURAL_GAS[number])[1] for number in (1, 2, 3, 4)]
        holidays = sorted(day for year in range(1994, 2024) for day in futures.nymex_holidays(year))
        rowed = [day for day in holidays if any(day in rows for rows in files)]
        assert len(holidays) == 261
        late = [day for day in holidays if date(2018, 1, 1) <= day <= date(2019, 11, 30)]
        assert rowed == [date(2014, 1, 20), *late]
        for day in rowed:
            before = futures.previous_trading_day(day)
            assert all(rows[day] == rows[before] for rows in files)
        good_fridays = [futures.good_friday(year) for year in range(1994, 2024)]
        assert [day for day in good_fridays if day in rowed] == [
            date(2018, 3, 30),
            date(2019, 4, 19),
        ]
        closed = [
            day
            for day in sorted(futures.UNSCHEDULED_CLOSURES)
            if date(1994, 1, 1) <= day <= date(2023, 12, 31) and any(day in rows for rows in files)
        ]
        assert closed == [date(2007, 1, 2)]
        before = futures.previous_trading_day(closed[0])
        assert all(rows[closed[0]] == rows[before] for rows in files)

    def test_good_friday_moves_exactly_these_trade_dates(self) -> None:
        """Every trade date in 1994 to 2023 that Good Friday moved, against weekends alone."""
        moved = []
        for year in range(1994, 2024):
            for (month, day), forward in (
                ((4, 13), True),
                ((4, 25), False),
                ((2, 25), True),
                ((4, 15), False),
            ):
                asked = date(year, month, day)
                got = on_or_after(asked) if forward else on_or_before(asked)
                weekend_only = asked
                while weekend_only.weekday() >= 5:
                    weekend_only = date.fromordinal(
                        weekend_only.toordinal() + (1 if forward else -1)
                    )
                if got != weekend_only:
                    moved.append((asked.isoformat(), got.isoformat()))
        assert moved == [
            ("1995-04-15", "1995-04-13"),
            ("2001-04-13", "2001-04-16"),
            ("2001-04-15", "2001-04-12"),
            ("2006-04-15", "2006-04-13"),
            ("2017-04-15", "2017-04-13"),
            ("2022-04-15", "2022-04-14"),
        ]


class TestTheNaturalGasExpiries:
    """Which numbered file holds the June contract rests on these dates."""

    #: Each contract's last trading day as the Massive futures API's contracts
    #: endpoint recorded it, for every year its records hold. They begin on
    #: 2017-01-01, so 2017 is the first year. Each year was read as of its own
    #: early January, on 2026-10-26: tickers such as NGH7 through 2025 and
    #: NGH26 after Massive's 2025-03-12 change of format. A first read on
    #: 2026-10-03 covered 2017, 2018, 2021 and 2024 and gave the same dates.
    #: Nothing here can re-read them, so they are pinned as a measurement.
    EXCHANGE = {
        2017: ("2017-02-24", "2017-03-29", "2017-04-26", "2017-05-26"),
        2018: ("2018-02-26", "2018-03-27", "2018-04-26", "2018-05-29"),
        2019: ("2019-02-26", "2019-03-27", "2019-04-26", "2019-05-29"),
        2020: ("2020-02-26", "2020-03-27", "2020-04-28", "2020-05-27"),
        2021: ("2021-02-24", "2021-03-29", "2021-04-28", "2021-05-26"),
        2022: ("2022-02-24", "2022-03-29", "2022-04-27", "2022-05-26"),
        2023: ("2023-02-24", "2023-03-29", "2023-04-26", "2023-05-26"),
        2024: ("2024-02-27", "2024-03-26", "2024-04-26", "2024-05-29"),
        2025: ("2025-02-26", "2025-03-27", "2025-04-28", "2025-05-28"),
        2026: ("2026-02-25", "2026-03-27", "2026-04-28", "2026-05-27"),
    }

    @pytest.mark.parametrize("year", sorted(EXCHANGE))
    def test_the_rule_gives_the_exchange_s_last_trading_days(self, year: int) -> None:
        """2024's April contract is the case Good Friday moves, on 2024-03-29."""
        got = tuple(ng_last_trade(year, month).isoformat() for month in (3, 4, 5, 6))
        assert got == self.EXCHANGE[year]

    @pytest.mark.parametrize("year", [2014, 2019])
    def test_contract_1_holds_the_expiring_contract_on_its_last_day(self, year: int) -> None:
        """The next day, contract 1 continues contract 2 rather than itself."""
        last = ng_last_trade(year, 3)
        after = on_or_after(date.fromordinal(last.toordinal() + 1))
        one, two = settlements(NATURAL_GAS[1])[1], settlements(NATURAL_GAS[2])[1]
        assert abs(one[after] - two[last]) < abs(one[after] - one[last])

    @staticmethod
    def handover_fit(last: date) -> Decimal | None:
        """The files' handover fit after ``last``, from :func:`chan.futures.handover_fit`."""
        return futures.handover_fit(futures.NATURAL_GAS_CONTRACTS, last)

    def test_the_lead_time_by_era(self) -> None:
        assert [ng_lead_days(1996, 1), ng_lead_days(1996, 2)] == [6, 5]
        assert [ng_lead_days(1997, 5), ng_lead_days(1997, 6)] == [5, 3]

    def test_the_march_1996_handover_fits_five_days_and_not_three(self) -> None:
        """The handover a three-day rule predicts, after 1996-02-27, is not in the files."""
        assert ng_last_trade(1996, 3) == date(1996, 2, 23)
        assert self.handover_fit(date(1996, 2, 23)) == Decimal("-0.284")
        assert self.handover_fit(date(1996, 2, 27)) == Decimal("0.068")

    def test_the_1996_and_1997_entries_read_contract_3(self) -> None:
        """Both years are profitable on contract 4 too, so the correction moved no count."""
        four = settlements(NATURAL_GAS[4])[1]
        for year, price in ((1996, Decimal("2.033")), (1997, Decimal("1.930"))):
            trade = natural_gas_trade(year)
            assert (trade.entry_symbol, trade.entry_price) == (NATURAL_GAS[3], price)
            assert four[trade.entry_day] < trade.exit_price

    def test_nixon_s_funeral_closed_the_exchange(self) -> None:
        assert not is_trading_day(date(1994, 4, 27))

    def test_june_s_number_through_the_spring(self) -> None:
        assert june_contract_number(date(2018, 2, 26)) == 4  # March's own last day
        assert june_contract_number(date(2018, 2, 27)) == 3
        assert june_contract_number(date(2018, 4, 13)) == 2

    def test_ten_entries_fall_on_march_s_last_day_and_none_flips_on_the_other_file(self) -> None:
        """Reading contract 3 on those days, as if EIA rolled a day early, changes no year."""
        edge = [
            year
            for year in range(1994, 2024)
            if on_or_after(date(year, 2, 25)) == ng_last_trade(year, 3)
        ]
        assert edge == [1998, 2000, 2001, 2004, 2007, 2009, 2012, 2015, 2016, 2018]
        three = settlements(NATURAL_GAS[3])[1]
        for year in edge:
            trade = natural_gas_trade(year)
            assert trade.entry_symbol == NATURAL_GAS[4]
            assert (trade.exit_price > three[trade.entry_day]) is trade.profitable


class TestGasoline:
    def test_the_contract_is_the_harbor_one_through_2005_and_rbob_after(self) -> None:
        assert gasoline_symbol(2005) == HARBOR_GASOLINE
        assert gasoline_symbol(2006) == RBOB_GASOLINE

    def test_every_year(self) -> None:
        profit, loss, missing = "profit", "loss", "missing"
        assert outcomes(GASOLINE) == {
            1995: profit, 1996: profit, 1997: missing, 1998: missing, 1999: missing,
            2000: profit, 2001: profit, 2002: profit, 2003: profit, 2004: profit,
            2005: profit, 2006: profit, 2007: profit, 2008: profit, 2009: loss,
            2010: profit, 2011: profit, 2012: loss, 2013: profit, 2014: profit,
            2015: profit, 2016: loss, 2017: loss, 2018: profit, 2019: profit,
            2020: loss, 2021: profit, 2022: loss, 2023: loss,
        }  # fmt: skip

    def test_the_three_missing_years_are_gaps_in_the_file(self) -> None:
        """Each date is a trading day the harbor file holds no row for."""
        _, rows = settlements(HARBOR_GASOLINE)
        for gap in (date(1997, 4, 14), date(1998, 4, 24), date(1999, 4, 23)):
            assert is_trading_day(gap)
            assert gap not in rows

    def test_three_settlements(self) -> None:
        harbor = gasoline_trade(2005)
        assert (harbor.entry_price, harbor.exit_price) == (Decimal("1.484"), Decimal("1.651"))
        worst = gasoline_trade(2012)
        assert (worst.entry_price, worst.exit_price) == (Decimal("3.346"), Decimal("3.156"))
        assert gasoline_trade(2008).change == Decimal("0.232")

    def test_the_2006_side_row_on_the_harbor_contract_is_missing(self) -> None:
        side = gasoline_trade(2006, symbol=HARBOR_GASOLINE)
        assert side.entry_price is None and side.profitable is None


class TestNaturalGas:
    def test_every_year(self) -> None:
        profit, loss = "profit", "loss"
        assert outcomes(GAS) == {
            **{year: profit for year in range(1994, 2009)},
            2009: loss, 2010: loss, 2011: profit, 2012: loss, 2013: profit,
            2014: profit, 2015: loss, 2016: profit, 2017: profit, 2018: profit,
            2019: loss, 2020: loss, 2021: loss, 2022: profit, 2023: loss,
        }  # fmt: skip

    def test_three_settlements(self) -> None:
        assert natural_gas_trade(1996).change == Decimal("0.308")
        assert natural_gas_trade(2008).change == Decimal("1.006")
        assert natural_gas_trade(2022).change == Decimal("2.895")

    def test_the_runs_counted_from_1995(self) -> None:
        runs = runs_ending([trade for trade in GAS if trade.year >= RUN_START])
        assert (runs[2007], runs[2008]) == (13, 14)
        assert {year: run for year, run in runs.items() if run >= 13} == {2007: 13, 2008: 14}

    def test_the_runs_counted_from_the_files_first_year(self) -> None:
        """Counted from 1994, the runs of 13 and 14 end a year early, in 2006 and 2007.

        1994 is the files' first whole trade, which the post says twice: 1993 has
        neither price.
        """
        runs = runs_ending(GAS)
        assert (runs[2006], runs[2007], runs[2008]) == (13, 14, 15)
        assert natural_gas_trade(1993).entry_price is None
        assert natural_gas_trade(1993).exit_price is None

    def test_a_missing_year_breaks_a_run_in_any_order(self) -> None:
        trades = [gasoline_trade(year) for year in (2000, 1997, 1996, 1995)]
        assert runs_ending(trades) == {1995: 1, 1996: 2, 1997: 0, 2000: 1}

    def test_the_exit_reads_contract_2(self) -> None:
        assert natural_gas_trade(2018).exit_symbol == NATURAL_GAS[2]

    def test_a_zero_change_is_not_a_profit(self) -> None:
        flat = Trade(
            year=2000,
            entry_day=date(2000, 2, 25),
            exit_day=date(2000, 4, 14),
            entry_symbol=NATURAL_GAS[4],
            exit_symbol=NATURAL_GAS[2],
            entry_price=Decimal("2.500"),
            exit_price=Decimal("2.5"),
        )
        assert flat.change == 0 and flat.profitable is False


class TestTheVerdicts:
    """The counts each row of Entry 11 reads, under the rules pinned on issue 19."""

    def test_19_of_21_reproduces_with_a_gap_the_missing_years_explain(self) -> None:
        years = [trade for trade in GASOLINE if 1995 <= trade.year <= 2015]
        assert len(years) == 21
        assert profitable_count(years) == 16
        assert sum(1 for trade in years if trade.profitable is False) == 2
        assert sum(1 for trade in years if trade.profitable is None) == 3

    def test_the_nine_out_of_sample_years(self) -> None:
        years = [trade for trade in GASOLINE if 2007 <= trade.year <= 2015]
        assert (profitable_count(years), len(years)) == (7, 9)

    def test_every_year_since_1995_has_no_loss_and_three_unreadable_years(self) -> None:
        for last, readable in ((2008, 11), (2007, 10)):
            years = [trade for trade in GASOLINE if trade.year <= last]
            assert profitable_count(years) == readable
            assert all(trade.profitable is not False for trade in years)

    def test_13_and_14_consecutive_years_reproduce(self) -> None:
        runs = runs_ending([trade for trade in GAS if trade.year >= RUN_START])
        assert runs[2007] == 13
        assert runs[2008] == 14

    def test_natural_gas_before_and_after_the_first_edition(self) -> None:
        through = [trade for trade in GAS if trade.year <= 2008]
        after = [trade for trade in GAS if trade.year >= 2009]
        assert (profitable_count(through), len(through)) == (15, 15)
        assert (profitable_count(after), len(after)) == (7, 15)

    def test_both_trades_after_the_book(self) -> None:
        gasoline = [trade for trade in GASOLINE if trade.year >= 2016]
        gas = [trade for trade in GAS if trade.year >= 2016]
        assert (profitable_count(gasoline), len(gasoline)) == (3, 8)
        assert (profitable_count(gas), len(gas)) == (4, 8)


class TestTheReturns:
    """Each trade's yearly return, Sharpe ratio and drawdown, in the book's years and after.

    A return is the change over the entry price, before costs. The book's years
    run to 2008 for natural gas and 2015 for gasoline, as for the counts above.
    """

    SPLITS = {
        "natural gas, 1994 to 2008": (GAS, 1994, 2008),
        "natural gas, 2009 to 2023": (GAS, 2009, 2023),
        "gasoline, 1995 to 2015": (GASOLINE, 1995, 2015),
        "gasoline, 2016 to 2023": (GASOLINE, 2016, 2023),
    }
    #: mean yearly return, Sharpe ratio, largest drawdown, each to four places
    PINS = {
        "natural gas, 1994 to 2008": (0.1060, 1.0008, 0.2151),
        "natural gas, 2009 to 2023": (-0.0040, -0.0184, 0.6042),
        "gasoline, 1995 to 2015": (0.0321, 0.7764, 0.1085),
        "gasoline, 2016 to 2023": (-0.0194, -0.4014, 0.2987),
    }

    @staticmethod
    def years(split: str) -> list[Trade]:
        trades, first, last = TestTheReturns.SPLITS[split]
        return [trade for trade in trades if first <= trade.year <= last]

    @pytest.mark.parametrize("split", list(PINS))
    def test_the_return_sharpe_ratio_and_drawdown(self, split: str) -> None:
        years = self.years(split)
        got = (mean_return(years), sharpe_ratio(years), max_drawdown(years))
        assert got == pytest.approx(self.PINS[split], abs=5e-5)

    #: the 95% range of the mean yearly return, and the Sharpe ratio's standard error
    UNCERTAINTY = {
        "natural gas, 1994 to 2008": ((0.0473, 0.1646), 0.3163),
        "natural gas, 2009 to 2023": ((-0.1236, 0.1156), 0.2582),
        "gasoline, 1995 to 2015": ((0.0115, 0.0526), 0.2689),
        "gasoline, 2016 to 2023": ((-0.0597, 0.0210), 0.3675),
    }

    @pytest.mark.parametrize("split", list(UNCERTAINTY))
    def test_one_trade_a_year_leaves_wide_ranges(self, split: str) -> None:
        years = self.years(split)
        (low, high), error = self.UNCERTAINTY[split]
        assert mean_interval(years) == pytest.approx((low, high), abs=5e-5)
        assert sharpe_standard_error(years) == pytest.approx(error, abs=5e-5)

    def test_welch_compares_the_two_periods(self) -> None:
        gas = change_p_value(
            self.years("gasoline, 1995 to 2015"), self.years("gasoline, 2016 to 2023")
        )
        ng = change_p_value(
            self.years("natural gas, 1994 to 2008"), self.years("natural gas, 2009 to 2023")
        )
        assert (gas, ng) == pytest.approx((0.0227, 0.0916), abs=5e-5)

    def test_the_rank_test_and_welch_split_on_natural_gas(self) -> None:
        gas = (self.years("gasoline, 1995 to 2015"), self.years("gasoline, 2016 to 2023"))
        ng = (self.years("natural gas, 1994 to 2008"), self.years("natural gas, 2009 to 2023"))
        assert (rank_p_value(*gas), rank_p_value(*ng)) == pytest.approx((0.0111, 0.0066), abs=5e-5)

    def test_the_rank_test_is_exact_where_scipy_would_approximate(self) -> None:
        """scipy's default normal approximation gives natural gas 0.79%, which
        the docstring of rank_p_value quotes, and the exact count 0.66%."""
        from scipy import stats

        ng = (self.years("natural gas, 1994 to 2008"), self.years("natural gas, 2009 to 2023"))
        one, two = ([t.relative_change for t in p if t.change is not None] for p in ng)
        assert len(set(one + two)) == len(one + two)
        default = stats.mannwhitneyu(one, two, alternative="two-sided").pvalue
        assert (default, rank_p_value(*ng)) == pytest.approx((0.0079, 0.0066), abs=5e-5)

    def test_the_earlier_years_win_most_pairs(self) -> None:
        """The count the rank test tests: earlier years beating later ones, of all pairings."""
        gas = (self.years("gasoline, 1995 to 2015"), self.years("gasoline, 2016 to 2023"))
        ng = (self.years("natural gas, 1994 to 2008"), self.years("natural gas, 2009 to 2023"))
        assert (pairs_won(*gas), pairs_won(*ng)) == ((117, 144), (177, 225))

    def test_2022_alone_holds_up_natural_gas_s_average(self) -> None:
        before, after = (
            self.years("natural gas, 1994 to 2008"),
            self.years("natural gas, 2009 to 2023"),
        )
        best = max(after, key=lambda trade: trade.relative_change)
        rest = [trade for trade in after if trade is not best]
        assert best.year == 2022
        assert mean_return(rest) == pytest.approx(-0.0499, abs=5e-5)
        assert change_p_value(before, rest) == pytest.approx(0.0014, abs=5e-5)

    def test_the_marks_start_and_end_at_the_trade_s_prices(self) -> None:
        for trade in GASOLINE + GAS:
            if trade.change is not None:
                marks = daily_marks(trade)
                assert (marks[0], marks[-1]) == (trade.entry_price, trade.exit_price)

    def test_the_marks_skip_a_holiday_row(self) -> None:
        """2018's files hold a row on Good Friday, inside the gas trade, and it is no mark."""
        trade = natural_gas_trade(2018)
        friday = futures.good_friday(2018)
        assert trade.entry_day < friday < trade.exit_day
        assert any(friday in settlements(NATURAL_GAS[n])[1] for n in (2, 3, 4))
        days = [
            date.fromordinal(n)
            for n in range(trade.entry_day.toordinal(), trade.exit_day.toordinal() + 1)
        ]
        assert len(daily_marks(trade)) == sum(map(is_trading_day, days))

    def test_the_drawdown_reads_inside_a_trade(self) -> None:
        """Natural gas lost no year through 2008, yet fell 22% of a stake inside 2002's trade."""
        years = self.years("natural gas, 1994 to 2008")
        assert all(trade.profitable for trade in years)
        alone = max_drawdown([natural_gas_trade(2002)])
        assert alone == pytest.approx(max_drawdown(years), abs=5e-5)

    def test_the_missing_years_are_left_out(self) -> None:
        years = self.years("gasoline, 1995 to 2015")
        readable = [trade for trade in years if trade.change is not None]
        assert (len(years), len(readable)) == (21, 18)
        assert mean_return(years) == mean_return(readable)


def test_the_report_prints_the_derived_counts(capsys: pytest.CaptureFixture[str]) -> None:
    """The printed lines carry the same figures the verdicts read, beside the book's."""
    main()
    out = capsys.readouterr().out
    assert "1995 to 2015: 16 of 21 profitable   (the book prints 19 of 21)" in out
    assert "the run ending in 2007: 13   (the main text prints 13)" in out
    assert "the run ending in 2008: 14   (the sidebar prints 14)" in out


class TestTheGapFills:
    """Whether filling a missing gasoline price could decide its year.

    The decisive output is the margin: each year's estimated move over its
    fill's typical miss, measured on hidden April days from 1994 to 2005 in the
    gap's own pattern of trading days. Every raw margin is under one for both
    fills. Fill 2's misses average above zero, so its guess is also corrected
    by that average and set against the spread around it, and even then no
    year's chance of a profit reaches 95%.
    """

    FILLS = gap_fills()

    def test_the_three_gaps_their_rows_and_their_patterns(self) -> None:
        assert [(f.year, f.leg, f.day) for f in self.FILLS] == [
            (1997, "entry", date(1997, 4, 14)),
            (1998, "exit", date(1998, 4, 24)),
            (1999, "exit", date(1999, 4, 23)),
        ]
        assert [(f.before, f.after, f.base) for f in self.FILLS] == [
            (date(1997, 4, 10), date(1997, 4, 15), date(1997, 4, 8)),
            (date(1998, 4, 21), date(1998, 4, 27), date(1998, 4, 21)),
            (date(1999, 4, 21), date(1999, 4, 26), date(1999, 4, 21)),
        ]
        assert [f.steps for f in self.FILLS] == [(2, 1, 4), (3, 1, 3), (2, 1, 2)]
        assert [f.tested for f in self.FILLS] == [80, 90, 102]

    def test_the_fills_and_their_typical_misses(self) -> None:
        """In dollars a gallon, against the trade's other price."""
        assert [f.other for f in self.FILLS] == [
            Decimal("0.625"),
            Decimal("0.498"),
            Decimal("0.522"),
        ]
        assert [f.june for f in self.FILLS] == pytest.approx([0.621, 0.503, 0.528])
        assert [f.linear for f in self.FILLS] == pytest.approx([0.61633, 0.5135, 0.524], abs=1e-5)
        assert [f.june_error for f in self.FILLS] == pytest.approx(
            [0.0089373, 0.0076077, 0.0064679], abs=1e-6
        )
        assert [f.linear_error for f in self.FILLS] == pytest.approx(
            [0.018953, 0.020298, 0.018414], abs=1e-5
        )

    def test_every_raw_move_is_inside_one_typical_miss(self) -> None:
        """Both fills guess a profit every year, inside one typical miss."""
        raw = [f.move(f.june) / f.june_error for f in self.FILLS]
        for f, june in zip(self.FILLS, raw, strict=True):
            assert 0 < june < 1 and 0 < f.linear_margin < 1, f.year
        assert [round(m, 2) for m in raw] == [0.45, 0.66, 0.93]
        assert [round(f.linear_margin, 2) for f in self.FILLS] == [0.46, 0.76, 0.11]

    def test_the_april_days_narrow_to_each_patterns_test_days(self) -> None:
        """All April trading days, those whose pattern fits inside April, those
        with every May price, and those with both June prices too."""
        counts = [count_test_days(f) for f in self.FILLS]
        assert counts == [(247, 187, 108, 80), (247, 199, 126, 90), (247, 211, 139, 102)]
        assert [c[-1] for c in counts] == [f.tested for f in self.FILLS]

    def test_fill_2_guesses_may_low(self) -> None:
        """Its average miss, the true price minus the guess, is above zero by
        between 2.7 and 3.2 standard errors in every pattern. The test days
        overlap, so the true standard errors are larger."""
        assert [f.june_bias for f in self.FILLS] == pytest.approx(
            [0.0025750, 0.0020778, 0.0019510], abs=1e-6
        )
        assert [f.june_spread for f in self.FILLS] == pytest.approx(
            [0.0086118, 0.0073597, 0.0061971], abs=1e-6
        )
        errors = [f.june_bias / (f.june_spread / math.sqrt(f.tested)) for f in self.FILLS]
        assert [round(e, 1) for e in errors] == [2.7, 2.7, 3.2]

    def test_the_corrected_moves_and_no_year_reaches_95_percent(self) -> None:
        moves = [100 * f.move(f.june_corrected) for f in self.FILLS]
        assert moves == pytest.approx([0.14250, 0.70778, 0.79510], abs=1e-4)
        assert [round(f.june_margin, 2) for f in self.FILLS] == [0.17, 0.96, 1.28]
        assert max(f.june_chance for f in self.FILLS) < 0.95

    def test_the_chance_all_three_were_profits(self) -> None:
        """Chan's 19 of 21 needs all three, under normal independent misses."""
        assert [round(100 * f.june_chance) for f in self.FILLS] == [57, 83, 90]
        assert math.prod(f.june_chance for f in self.FILLS) == pytest.approx(0.42368, abs=1e-5)


POST = Path(__file__).resolve().parents[1] / "blog" / "commodity-seasonals-lessons.md"


def _tally(trades, first: int, last: int) -> tuple[int, int]:
    years = [trade for trade in trades if first <= trade.year <= last]
    return profitable_count(years), len(years)


def _day(day: date) -> str:
    return f"{day.day} {day:%B} {day.year}"


class TestThePostQuotesThePins:
    """One copy of each count, streak, gap date and split in the post, read from the post itself.

    Other copies of the same figure elsewhere in the post are not always read.

    The prose states these numbers and the tests above derive them, so before
    this class a typo in the post passed every test. Round 1 of the post's
    review changed 26 of its numbers one at a time, and none failed a test.
    """

    text = POST.read_text("utf-8")

    def test_natural_gas_before_and_after_2008(self) -> None:
        won, of = _tally(GAS, 1994, 2008)
        later, later_of = _tally(GAS, 2009, 2023)
        assert "\\text{Natural gas} & \\text{1994 to 2008} & \\text{2009 to 2023}" in self.text
        assert (
            f"\\quad\\text{{Years won}} & {won} \\text{{ of }} {of} & "
            f"{later} \\text{{ of }} {later_of}"
        ) in self.text
        mean = mean_return([trade for trade in GAS if trade.year <= 2008])
        assert (
            f"Natural gas went from winning {won} of {of} years, with a mean return of "
            f"{100 * mean:.1f}%, to winning {later} of {later_of}"
        ) in self.text

    def test_the_streak_table_and_the_start_years(self) -> None:
        assert all(t.exit_day <= date(t.year, 4, 15) for t in GAS)
        assert any(t.exit_day > date(t.year, 4, 15) for t in GASOLINE)
        assert "Each natural gas trade closes by mid-April, so both streaks end before" in self.text
        from_1995 = runs_ending([trade for trade in GAS if trade.year >= RUN_START])
        from_1994 = runs_ending(GAS)
        for year in (2007, 2008):
            assert f"{year} & {from_1995[year]} & {from_1994[year]}" in self.text
        ends = [min(year for year, run in from_1994.items() if run == count) for count in (13, 14)]
        assert f"the streaks of 13 and 14 end in {ends[0]} and {ends[1]} instead" in self.text
        main_text, sidebar = (min(y for y, run in from_1995.items() if run == n) for n in (13, 14))
        assert (
            f"the main text’s 13 is the streak ending in {main_text} and the sidebar’s 14 "
            f"is the streak ending in {sidebar}"
        ) in self.text

    def test_the_gasoline_count_and_its_gaps(self) -> None:
        years = [trade for trade in GASOLINE if trade.year <= 2015]
        losses = [trade.year for trade in years if trade.profitable is False]
        missing = [trade for trade in years if trade.profitable is None]
        assert f"\\text{{Profitable}} & {profitable_count(years)} \\\\" in self.text
        assert f"\\text{{Losing, {losses[0]} and {losses[1]}}} & {len(losses)}" in self.text
        assert (
            f"\\text{{No row, {missing[0].year} to {missing[-1].year}}} & {len(missing)}"
            in self.text
        )
        assert f"\\text{{Total}} & {len(years)}" in self.text
        readable = [trade for trade in years if trade.profitable is not None]
        won, later, later_of = profitable_count(years), *_tally(GASOLINE, 2016, 2023)
        assert (
            f"\\quad\\text{{Years won}} & {won} \\text{{ of }} {len(readable)} & "
            f"{later} \\text{{ of }} {later_of}"
        ) in self.text
        assert (
            f"leaves out the {len(missing)} years each missing one trade date’s price"
        ) in self.text
        assert all((t.entry_price is None) != (t.exit_price is None) for t in missing)
        entry_gap = [trade.entry_day for trade in missing if trade.entry_price is None]
        exit_gap = [trade.exit_day for trade in missing if trade.exit_price is None]
        assert (
            f"no row on {_day(entry_gap[0])}, the entry date that year, or on "
            f"{_day(exit_gap[0])} and {_day(exit_gap[1])}, the exit dates those years"
        ) in self.text

    def test_the_years_inside_and_after_the_book(self) -> None:
        early = [trade for trade in GASOLINE if trade.year <= 2008]
        assert not any(trade.profitable is False for trade in early)
        assert (
            f"no loss, {profitable_count(early)} profitable years and "
            f"{sum(trade.profitable is None for trade in early)} with no price on a trade date"
        ) in self.text
        won, of = _tally(GASOLINE, 2007, 2015)
        assert f"The trade won {won} of those {of}" in self.text
        won, of = _tally(GASOLINE, 2009, 2015)
        assert f"It won {won} of its {of} years from 2009 to 2015" in self.text
        gasoline, gasoline_of = _tally(GASOLINE, 2016, 2023)
        gas, gas_of = _tally(GAS, 2016, 2023)
        assert (
            f"it won {gasoline} of {gasoline_of}, and natural gas won {gas} of the same {gas_of}."
            in self.text
        )

    def test_the_returns_table(self) -> None:
        """Each split's mean return, Sharpe ratio and drawdown, at the table's precision."""

        def sharpe(value: float) -> str:
            text = f"{value:.1f}"
            return "0.0" if text == "-0.0" else text

        for trade, splits in (
            ("natural gas", ("1994 to 2008", "2009 to 2023")),
            ("gasoline", ("1995 to 2015", "2016 to 2023")),
        ):
            before, after = (TestTheReturns.years(f"{trade}, {split}") for split in splits)
            rows = {
                "Mean return": [f"{100 * mean_return(y):+.1f}\\%" for y in (before, after)],
                "Sharpe ratio": [sharpe(sharpe_ratio(y)) for y in (before, after)],
                "Drawdown": [f"{round(100 * max_drawdown(y))}\\%" for y in (before, after)],
            }
            for name, (one, two) in rows.items():
                assert f"\\quad\\text{{{name}}} & {one} & {two}" in self.text, (trade, name)

    def test_lesson_4_works_the_sample_size_out(self) -> None:
        """Lesson 4 reads its inputs, its worked results and its tests from the run."""

        def whole(value: float) -> str:
            return f"{'−' if value < 0 else '+'}{abs(round(100 * value))}%"

        def pct(value: float) -> str:
            return f"{100 * value:.1f}"

        splits = TestTheReturns.SPLITS
        counts = [
            len([t for t in TestTheReturns.years(split) if t.change is not None])
            for split in splits
        ]
        errors = [sharpe_standard_error(TestTheReturns.years(split)) for split in splits]
        text = " ".join(self.text.split())
        assert f"rests on only {min(counts)} to {max(counts)} yearly results" in text
        assert len(splits) == 4
        assert "each of the table’s four periods, two for each trade" in text
        assert f"the standard error runs from {min(errors):.1f} to {max(errors):.1f}" in text
        assert (
            f"range reaches {1.96 * min(errors):.1f} to {1.96 * max(errors):.1f} either side"
            in text
        )

        ng_before = TestTheReturns.years("natural gas, 1994 to 2008")
        ratio, error = sharpe_ratio(ng_before), sharpe_standard_error(ng_before)
        assert (
            f"\\sqrt{{\\frac{{1 + {ratio:.1f}^2 / 2}}{{{len(ng_before)}}}}} = {error:.2f}" in text
        )
        assert f"{ratio:.1f} \\pm 1.96 \\times {error:.2f}" in text
        assert f"&= {ratio - 1.96 * error:.1f} \\text{{ to }} {ratio + 1.96 * error:.1f}" in text

        for split, before, years_word in (
            ("natural gas, 2009 to 2023", "natural gas, 1994 to 2008", "15 years"),
            ("gasoline, 2016 to 2023", "gasoline, 1995 to 2015", "8 years"),
        ):
            after = [t.relative_change for t in TestTheReturns.years(split) if t.change is not None]
            n, mean, sd = len(after), statistics.mean(after), statistics.stdev(after)
            t = stats.t.ppf(0.975, n - 1)
            low, high = mean_interval(TestTheReturns.years(split))
            spread = f"a standard deviation of {pct(sd)}% over {n} years"
            assert re.search(rf"averaged −{pct(-mean)}%( a year)? with {spread}", text), split
            assert f"for {n - 1} degrees of freedom is {t:.2f}" in text, split
            assert (
                f"&-{pct(-mean)}\\% \\pm {t:.2f} \\times \\frac{{{pct(sd)}\\%}}{{\\sqrt{{{n}}}}}"
                in text
            )
            assert f"&= -{pct(-mean)}\\% \\pm {pct(high - mean)}\\%" in text, split
            assert f"That range, {whole(low)} to {whole(high)}," in text, split
            earned = mean_return(TestTheReturns.years(before))
            inside = low < earned < high
            assert (f"still holds the +{pct(earned)}%" in text) == inside, split
            assert (f"leaves out the +{pct(earned)}%" in text) == (not inside), split
            assert years_word in text
        gas = (
            TestTheReturns.years("gasoline, 1995 to 2015"),
            TestTheReturns.years("gasoline, 2016 to 2023"),
        )
        ng = (
            TestTheReturns.years("natural gas, 1994 to 2008"),
            TestTheReturns.years("natural gas, 2009 to 2023"),
        )
        assert max(change_p_value(*gas), rank_p_value(*gas)) < 0.05 < change_p_value(*ng)
        assert "Gasoline’s fall passes both tests, with each chance below the 5% line." in text
        assert "The usual line is 5%" in text
        spreads = [
            statistics.stdev([t.relative_change for t in p if t.change is not None]) for p in ng
        ]
        assert round(spreads[1] / spreads[0]) == 2
        assert "natural gas’s standard deviation doubled after 2008" in text
        assert (
            "15 years give 15 results, about what a strategy that trades every day "
            "collects in three weeks"
        ) in text
        for name, pair in (("Gasoline", gas), ("Natural gas", ng)):
            welch, rank = change_p_value(*pair), rank_p_value(*pair)
            assert f"\\text{{{name}}} & {100 * welch:.1f}\\% & {100 * rank:.1f}\\%" in text, name
            won, pairs = pairs_won(*pair)
            assert (
                f"For {name.lower()} the earlier year won {won:.0f} of {pairs} pairs, "
                f"where chance would give half, {pairs / 2:g}"
            ) in text, name
        won, pairs = pairs_won(*ng)
        assert (
            f"For natural gas’s {won:.0f} pairs, luck alone lands that far from the middle, "
            f"{pairs / 2:g}, on either side, {100 * rank_p_value(*ng):.1f}% of the time."
        ) in text

        before, after = ng
        best = max(after, key=lambda trade: trade.relative_change)
        rest = [trade for trade in after if trade is not best]
        won = [profitable_count(before), len(before), profitable_count(after), len(after)]
        assert (
            f"from {won[0]} wins in {won[1]} years before 2009 to {won[2]} in {won[3]} after"
        ) in text
        assert (
            f"But {best.year}’s +{round(100 * best.relative_change)}% lifts its average "
            f"after 2008 to −{pct(-mean_return(after))}%"
        ) in text
        assert (
            f"Without {best.year} the average after 2008 is −{pct(-mean_return(rest))}%, "
            f"and Welch’s chance falls to {100 * change_p_value(before, rest):.1f}%"
        ) in text
        beaten = sum(1 for trade in before if trade.relative_change < best.relative_change)
        assert beaten == len(before)
        assert (
            f"Welch’s chance, {100 * change_p_value(*ng):.1f}%, sits above the line. "
            f"Mann-Whitney still sees the change, because {best.year} beats each of the {beaten} "
            "earlier years once, however large its gain"
        ) in text

    def test_the_2002_drawdown(self) -> None:
        trade = natural_gas_trade(2002)
        marks = daily_marks(trade)
        high = float((max(marks) - trade.entry_price) / trade.entry_price)
        assert (
            f"came inside 2002’s trade, which rose {round(100 * high)}%, gave back "
            f"{round(100 * max_drawdown([trade]))} points, then recovered to end "
            f"{round(100 * trade.relative_change)}% up"
        ) in self.text

    def test_lesson_4_s_counts(self) -> None:
        """The edge years, the Good Friday moves, the exchange's contracts and the lead days."""
        words = {3: "three", 5: "five", 6: "six"}
        years = range(1994, 2024)
        edge = [y for y in years if on_or_after(date(y, 2, 25)) == ng_last_trade(y, 3)]
        assert (
            f"In {len(edge)} of the {len(years)} years, the entry date falls on the March "
            "contract’s last trading day"
        ) in self.text
        moved = [
            asked
            for y in years
            for asked, roll in (
                (date(y, 4, 13), on_or_after),
                (date(y, 4, 25), on_or_before),
                (date(y, 2, 25), on_or_after),
                (date(y, 4, 15), on_or_before),
            )
            if roll(asked) != _weekend_roll(asked, roll is on_or_after)
        ]
        assert f"it moved {words[len(moved)]} trade dates between 1994 and 2023" in self.text
        exchange = sorted(TestTheNaturalGasExpiries.EXCHANGE)
        assert exchange == list(range(exchange[0], exchange[-1] + 1))
        assert (
            f"For all {4 * len(exchange)} March to June contracts it records from "
            f"{exchange[0]} to {exchange[-1]}, the rule gives"
        ) in self.text
        early = sorted({ng_lead_days(1996, 1), ng_lead_days(1996, 2)})
        assert (
            f"stopping {words[early[0]]} or {words[early[1]]} trading days before delivery "
            f"rather than {words[ng_lead_days(1998, 6)]}"
        ) in self.text
        shifted = [y for y in (1996, 1997) if natural_gas_trade(y).entry_symbol == NATURAL_GAS[3]]
        assert f"moves the {shifted[0]} and {shifted[1]} entries from contract 4 to contract 3" in (
            self.text
        )

    def test_the_chart_s_alt_text(self) -> None:
        """The chart's alt text restates its labels in words, so it reads the same tallies."""
        words = {5: "five", 8: "eight"}
        alt = re.search(r"!\[(Two panels[^\]]*)\]\(\.\./docs/figures/", self.text).group(1)
        missing = [t.year for t in GASOLINE if t.year <= 2015 and t.profitable is None]
        losses = [t.year for t in GASOLINE if t.year <= 2015 and t.profitable is False]
        later = [t for t in GASOLINE if t.year >= 2016]
        won, of = _tally(GASOLINE, 1995, 2015)
        assert f"Its years {missing[0]}, {missing[1]} and {missing[2]} are empty slots" in alt
        assert f"{won} of {of} profitable and {len(missing)} with no row" in alt
        assert f"{profitable_count(later)} of {len(later)} profitable" in alt
        assert f"with losses in {losses[0]} and {losses[1]}" in alt
        lost = sum(t.profitable is False for t in later)
        assert f"{words[lost]} of the {words[len(later)]} after it are losses" in alt
        gas_won, gas_of = _tally(GAS, 1994, 2008)
        after = [t for t in GAS if t.year >= 2009]
        assert f"{gas_won} of {gas_of} profitable, from 2009 to 2023" in alt
        assert f"{profitable_count(after)} of {len(after)} profitable" in alt
        gains = profitable_count(after)
        assert f"After it, {len(after) - gains} years are losses and {gains} are gains" in alt
        biggest = max(after, key=lambda t: t.change)
        assert round(biggest.change) == 3
        assert f"one gain near three dollars in {biggest.year}" in alt

    def test_the_handover_fit_over_every_expiry(self) -> None:
        """The second check's counts, the survey ``tests/test_stationary_candidates.py`` pins."""
        from chan.futures import NATURAL_GAS_CONTRACTS, handover_fit, month_step, shifted

        early_fits = 0

        def survey(shift: int) -> tuple[int, int]:
            nonlocal early_fits
            rule = shifted(NATURAL_GAS_CONTRACTS, shift) if shift else NATURAL_GAS_CONTRACTS
            fits, readable, month = 0, 0, (1994, 2)
            while month <= (2024, 4):
                fit = handover_fit(NATURAL_GAS_CONTRACTS, rule.last_trade(*month))
                if fit is not None:
                    readable += 1
                    fits += fit < 0
                    if not shift and month < (1997, 6) and fit < 0:
                        early_fits += 1
                month = month_step(*month, 1)
            return fits, readable

        (fits, readable), early, late = survey(0), survey(-1), survey(1)
        assert ng_lead_days(1997, 6) == 3 < ng_lead_days(1997, 5)
        assert early[1] == late[1]
        text = " ".join(self.text.split())
        assert (
            f"the handover falls on the rule’s day for {fits} of the {readable} expiries"
        ) in text
        assert (
            f"{early_fits} of the {fits} are contracts delivered before June 1997, where the "
            "rule’s count of days before delivery came from these handovers."
        ) in text
        assert (
            f"the rule fits only {early[0]} and {late[0]} of the {early[1]} expiries the files "
            "hold rows to check on the moved days."
        ) in text

    def test_why_the_rest_of_the_expiries_do_not_count(self) -> None:
        """The paragraph after the coverage sketch: what the unreadable and
        misfitting expiries are, and whether a one-day error in any of them
        could move a trade's file or flip a year."""
        from datetime import timedelta

        from chan.futures import NATURAL_GAS_CONTRACTS, handover_fit, month_step

        unread, misfit, readable, month = [], [], 0, (1994, 2)
        while month <= (2024, 4):
            fit = handover_fit(NATURAL_GAS_CONTRACTS, NATURAL_GAS_CONTRACTS.last_trade(*month))
            if fit is None:
                unread.append(month)
            else:
                readable += 1
            if fit is not None and fit >= 0:
                misfit.append((month, fit))
            month = month_step(*month, 1)

        def nudged(day: date, step: int) -> date:
            day += timedelta(days=step)
            while not is_trading_day(day):
                day += timedelta(days=step)
            return day

        def moves(months) -> list[tuple[int, int, date, int]]:
            found = []
            for year, m in months:
                if m not in (3, 4, 5) or not NG_YEARS[0] <= year <= NG_YEARS[1]:
                    continue
                trade, last = natural_gas_trade(year), ng_last_trade(year, m)
                for step in (-1, 1):
                    for day in (trade.entry_day, trade.exit_day):
                        if (day <= last) != (day <= nudged(last, step)):
                            found.append((year, m, day, step))
            return found

        close = [fit for _, fit in misfit if fit < Decimal("0.09")]
        moved = moves([m for m, _ in misfit])
        assert moves(unread) == []
        flips = 0
        for year, _, day, _ in moved:
            trade = natural_gas_trade(year)
            number = june_contract_number(day)
            other = number - 1 if day <= ng_last_trade(year, 3) else number + 1
            price = settlements(NATURAL_GAS[other])[1][day]
            entry = price if day == trade.entry_day else trade.entry_price
            exit_ = price if day == trade.exit_day else trade.exit_price
            flips += (exit_ > entry) != trade.profitable
        assert ((2023, 3), Decimal("0.012")) in misfit
        assert date(2023, 2, 24).isoformat() in TestTheNaturalGasExpiries.EXCHANGE[2023]
        text = " ".join(self.text.split())
        assert (
            f"Outside those {readable}, the check cannot reach {len(unread)} expiries, because "
            "a file lacks a row on the expiry day or the day after. "
            f"{sum(1997 <= y <= 2005 for y, _ in unread)} of the {len(unread)} fall between "
            "1997 and 2005."
        ) in text
        assert f"{len(close)} fail by under 9 cents" in text
        assert (
            f"One of those {len(close)}, March 2023, fails although the exchange’s own date "
            "matches the rule’s."
        ) in text
        assert (
            f"That is true of {len(moved)} of the {len(misfit)}, all March contracts at an "
            f"entry, and of none of the {len(unread)}"
        ) in text
        assert all(m == 3 and day == natural_gas_trade(y).entry_day for y, m, day, _ in moved)
        assert flips == 0

    def test_the_files_first_whole_trade(self) -> None:
        """1993's trade has neither price and 1994's has both, which the post says twice."""
        first = NG_YEARS[0]
        before, trade = natural_gas_trade(first - 1), natural_gas_trade(first)
        assert (before.entry_price, before.exit_price) == (None, None)
        assert trade.entry_price is not None and trade.exit_price is not None
        assert f"The natural gas files first hold a whole trade in {first}." in self.text
        assert f"{first}, the first year the files hold a whole trade" in self.text

    def test_the_holiday_rows(self) -> None:
        """The longest unbroken run of NYMEX holidays the natural gas files hold a row on.

        One rowed holiday, 2014-01-20, falls outside it.
        """
        files = [settlements(NATURAL_GAS[number])[1] for number in (1, 2, 3, 4)]
        holidays = sorted(day for year in range(1994, 2024) for day in futures.nymex_holidays(year))
        rowed = [any(day in rows for rows in files) for day in holidays]
        runs, start = [], None
        for k, has in enumerate([*rowed, False]):
            if has and start is None:
                start = k
            elif not has and start is not None:
                runs.append((start, k - 1))
                start = None
        first, last = max(runs, key=lambda run: run[1] - run[0])
        assert sum(rowed) - (last - first + 1) == 1
        assert (
            f"On every exchange holiday from {holidays[first]:%B %Y} to "
            f"{holidays[last]:%B %Y}, the natural gas files hold a row"
        ) in self.text

    def test_the_gap_fill_table_and_its_chance(self) -> None:
        """The table names the fill it shows, which the owner asked for, then
        one row per quantity, one column per year."""
        fills = gap_fills()
        years = " & ".join(str(f.year) for f in fills)
        assert f"\\text{{Fill 2}} & {years} \\\\ \\hline" in self.text
        rows = {
            "Move with the guess": [f"{100 * f.move(f.june):+.1f}" for f in fills],
            "Average miss": [f"{100 * f.june_bias:+.2f}" for f in fills],
            "Corrected move": [f"{100 * f.move(f.june_corrected):+.2f}" for f in fills],
            "Spread of misses": [f"{100 * f.june_spread:.2f}" for f in fills],
            "Chance of profit": [f"{100 * f.june_chance:.0f}\\%" for f in fills],
        }
        for name, cells in rows.items():
            assert f"\\text{{{name}}} & {' & '.join(cells)}" in self.text, name
        moves = ", ".join(f"{100 * f.move(f.june):+.1f}" for f in fills[:-1])
        misses = ", ".join(f"{100 * f.june_error:.2f}" for f in fills[:-1])
        last = fills[-1]
        assert (
            f"Fill 2 gives moves of {moves} and {100 * last.move(last.june):+.1f} cents a "
            f"gallon, against typical misses of {misses} and {100 * last.june_error:.2f}."
        ) in self.text
        biases = ", ".join(f"{100 * f.june_bias:.2f}" for f in fills[:-1])
        errors = [f.june_bias / (f.june_spread / math.sqrt(f.tested)) for f in fills]
        assert (
            f"too low by {biases} and {100 * last.june_bias:.2f} cents on average, each "
            f"between {min(errors):.1f} and {max(errors):.1f} standard errors from zero"
        ) in self.text
        assert {f"{100 * f.linear_error:.0f}" for f in fills} == {"2"}
        assert max(f.linear_margin for f in fills) < 1
        assert (
            "Fill 1’s typical miss is about 2 cents in each year, larger than any of its moves."
        ) in self.text
        assert "so neither fill decides a year" in self.text
        chance = math.prod(f.june_chance for f in fills)
        assert f"which Chan’s 19 needs, is {100 * chance:.0f}%" in self.text
        uncorrected = math.prod(
            0.5 * (1 + math.erf(f.move(f.june) / f.june_error / math.sqrt(2))) for f in fills
        )
        assert f"{100 * uncorrected:.0f}" != f"{100 * chance:.0f}"
        assert f"and no correction, gives {100 * uncorrected:.0f}%" in self.text

    def test_the_derivations_of_the_entry_and_exit_moves(self) -> None:
        """A miss lowers the move when the entry is missing and raises it when
        the exit is, in each derivation and in the table of the two cases.
        Which gap is which comes from the run."""
        fills = gap_fills()
        entries = [f.year for f in fills if f.leg == "entry"]
        exits = [f.year for f in fills if f.leg == "exit"]
        assert (entries, exits) == ([1997], [1998, 1999])
        entry_block = (
            "\\text{true move} &= \\text{exit} - (\\text{guess} + e) \\\\\n"
            "&= \\underbrace{(\\text{exit} - \\text{guess})}_{m} - e \\\\\n"
            "&= m - e"
        )
        exit_block = (
            "\\text{true move} &= (\\text{guess} + e) - \\text{entry} \\\\\n"
            "&= \\underbrace{(\\text{guess} - \\text{entry})}_{m} + e \\\\\n"
            "&= m + e"
        )
        assert entry_block in self.text
        assert exit_block in self.text
        assert f"\\text{{Entry, {entries[0]}}} & m - e & m - b" in self.text
        assert f"\\text{{Exit, {exits[0]}, {exits[1]}}} & m + e & m + b" in self.text
        biases = [f"{100 * f.june_bias:.2f}" for f in fills[:2]]
        assert (
            f"The sketch marks each arrow with `e` at that year’s average miss `b`, "
            f"{biases[0]} cents for "
            f"{fills[0].year} and {biases[1]} for {fills[1].year}."
        ) in self.text

    def test_the_table_of_test_days(self) -> None:
        """Each missing year's gap, how far back fill 2 starts, and how many
        test days its pattern leaves, read from the run."""
        fills = gap_fills()
        assert fills[0].base < fills[0].before
        assert (
            "Fill 2 takes May’s price on the last day before the gap, counting only days "
            "both files hold,"
        ) in self.text
        rows = {
            "Missing year": [str(f.year) for f in fills],
            "Missing price": [f"\\text{{{f.leg}}}" for f in fills],
            "Missing day": [f"\\text{{{f.day.day} {f.day:%b}}}" for f in fills],
            "Fill 2 starts": [f"\\text{{{f.base.day} {f.base:%b}}}" for f in fills],
            "Days back": [str(f.steps[2]) for f in fills],
            "Test days": [str(f.tested) for f in fills],
        }
        for name, cells in rows.items():
            assert f"\\text{{{name}}} & {' & '.join(cells)}" in self.text, name
        total, *_, kept = count_test_days(fills[0])
        assert f"For {fills[0].year}, {total} April trading days narrow to {kept}:" in self.text

    def test_the_derivation_of_the_chance(self) -> None:
        """The worked example and the product in the derivation read the run."""
        fills = gap_fills()
        first = fills[0]
        assert (
            f"For {first.year}, `m` is {100 * first.move(first.june):.1f} cents, `b` is "
            f"{100 * first.june_bias:.2f} and `σ` is {100 * first.june_spread:.2f}, so `c` is "
            f"{100 * first.move(first.june_corrected):.2f}. From the unrounded values, "
            "the chance is "
            f"Φ({first.june_margin:.2f}), or {100 * first.june_chance:.0f}%."
        ) in self.text
        product = " \\times ".join(f"{f.june_chance:.3f}" for f in fills)
        total = math.prod(f.june_chance for f in fills)
        assert f"{product} = {total:.3f}" in self.text

    def test_the_june_caption_s_2006_dates(self) -> None:
        """The June sketch's caption says why 2006's entry and exit moved."""
        trade = natural_gas_trade(2006)
        asked_entry, asked_exit = date(2006, 2, 25), date(2006, 4, 15)
        good_friday = futures.good_friday(2006)
        assert trade.entry_day > ng_last_trade(2006, 3)
        assert trade.exit_day < good_friday < asked_exit
        assert (
            f"In 2006, February 25 fell on a {asked_entry:%A}, so the trade entered on "
            f"{trade.entry_day:%A} the {trade.entry_day.day}th, after March had expired. "
            f"April 15 was a {asked_exit:%A} and the {good_friday.day}th was Good Friday, "
            f"so the exit moved back to the {trade.exit_day.day}th."
        ) in self.text

    def test_further_work_s_trade_dates(self) -> None:
        """Further work's list of each trade's dates, and how long gasoline is held."""
        words = "zero one two three four five six seven eight nine ten eleven twelve".split()

        def named(month_day: tuple[int, int]) -> str:
            day = date(2001, *month_day)
            return f"{day:%B} {day.day}"

        held = (date(2001, *GASOLINE_EXIT) - date(2001, *GASOLINE_ENTRY)).days
        assert (
            f"**The entry date**, {named(GASOLINE_ENTRY)} for gasoline and "
            f"{named(NG_ENTRY)} for natural gas."
        ) in self.text
        assert (
            f"**The exit date**, {named(GASOLINE_EXIT)} for gasoline and "
            f"{named(NG_EXIT)} for natural gas."
        ) in self.text
        assert f"Gasoline is held only {words[held]} calendar days" in self.text

    def test_further_work_s_held_back_years(self) -> None:
        """The gasoline Aprils Further work holds back, and why natural gas has none.

        Everything here comes from the manifest's first and last dates, the
        run's year ranges and the exchange's expiry rule, never from a price,
        because a search is meant to test on those Aprils.
        """
        words = "zero one two three four five six seven eight nine ten eleven twelve".split()

        def span(symbol: str) -> tuple[date, date]:
            entry = resolve_vintage(vendor="eia", symbol=symbol, price_basis="raw")
            return date.fromisoformat(entry.first_date), date.fromisoformat(entry.last_date)

        one, two = span(HARBOR_GASOLINE)[0], span(HARBOR_GASOLINE_2)[0]
        # The first April anything here reads, the trades' or the gap fills' test days.
        first_april = min(GASOLINE_YEARS[0], FILL_TEST_YEARS[0])
        held_back = range(one.year, first_april)
        assert one < date(one.year, 4, 1)
        assert date(first_april - 1, 4, 30) < two < date(first_april, 4, 1)
        assert (
            f"The New York Harbor gasoline contract-1 file begins in {one:%B %Y}, and nothing "
            f"here has computed a trade on its Aprils before {first_april}. So "
            f"{held_back[0]} to {held_back[-1]} give {words[len(held_back)]} years"
        ) in self.text
        # June in April and May in March are contract 2, the file that starts too late.
        for year in held_back:
            for day in futures.trading_days(date(year, 3, 1), date(year, 4, 30)):
                month = 6 if day.month == 4 else 5
                assert futures.contract_number(day, year, month, futures.rbob_last_trade) == 2
        assert (
            f"The contract-2 file begins only in {two:%B %Y}, so those years cannot test a "
            "variant that reads it, such as the June contract in April or the May contract "
            "in March."
        ) in self.text
        # Natural gas: no whole trade before the run's first year, and none after its last.
        assert natural_gas_trade(NG_YEARS[0] - 1).entry_price is None
        after = NG_YEARS[1] + 1
        assert all(
            span(symbol)[1] < on_or_before(date(after, *NG_EXIT)) for symbol in NATURAL_GAS.values()
        )
        assert (
            f"so its held-back years would have to come after {NG_YEARS[1]}, which the files "
            "do not reach"
        ) in self.text
        assert f"reaches back to the {NG_YEARS[0] // 10 * 10}s" in self.text

    def test_further_work_s_neighbouring_delivery_months(self) -> None:
        """The June gasoline and May natural gas contracts are among EIA's four on every date.

        The files can still lack a row. The June gasoline file has none on
        25 April 1997, a trading day the May file holds, so that year's June
        trade would read as missing, as Lesson 2 reads May's 1997.
        """
        years = range(NG_YEARS[0], NG_YEARS[1] + 1)
        assert GASOLINE_YEARS[1] == NG_YEARS[1]
        for year in years:
            for day in (
                on_or_after(date(year, *GASOLINE_ENTRY)),
                on_or_before(date(year, *GASOLINE_EXIT)),
            ):
                assert futures.contract_number(day, year, 6, futures.rbob_last_trade) <= 4
            trade = natural_gas_trade(year)
            for day in (trade.entry_day, trade.exit_day):
                assert futures.contract_number(day, year, 5, ng_last_trade) <= 4
        assert (
            f"On every entry and exit date from {years[0]} to {years[-1]}, those include the "
            "June gasoline contract and the May natural gas contract"
        ) in self.text

    def test_further_work_s_decimal_places(self) -> None:
        """EIA prints every settlement the run reads to at most three decimal places.

        It drops trailing zeros, so some rows show fewer. The harbor file is
        read from 1994 only, leaving its earlier Aprils untouched.
        """
        symbols = (HARBOR_GASOLINE, HARBOR_GASOLINE_2, RBOB_GASOLINE, *NATURAL_GAS.values())
        places = {
            -price.as_tuple().exponent
            for symbol in symbols
            for day, price in settlements(symbol)[1].items()
            if day.year >= FILL_TEST_YEARS[0]
        }
        assert max(places) == 3
        assert "at the three decimal places EIA prints" in self.text


def _weekend_roll(day: date, forward: bool) -> date:
    """``day`` moved past weekends alone, the calendar without NYMEX's holidays."""
    while day.weekday() >= 5:
        day = date.fromordinal(day.toordinal() + (1 if forward else -1))
    return day
