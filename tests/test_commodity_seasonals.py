"""Pins for Chan's two commodity seasonal trades, Entry 11 of the replication log.

Every figure ``docs/replication-log.md`` quotes for Entry 11 is derived here.
The vintages are EIA's NYMEX settlements, downloaded 2026-10-02 and recorded in
``data/vintages.jsonl``: contract 1 of New York Harbor regular gasoline and of
RBOB gasoline, and contracts 1 to 4 of Henry Hub natural gas. The rules are the
sidebars' at Kindle locations 4536 and 4590, and every choice they leave open
was pinned on [issue 19](https://github.com/l3a0/quantitative-trading/issues/19)
before a trade was computed.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from chan import futures
from chan.commodity_seasonals import (
    GASOLINE_YEARS,
    HARBOR_GASOLINE,
    NATURAL_GAS,
    NG_YEARS,
    RBOB_GASOLINE,
    RUN_START,
    Trade,
    easter,
    gasoline_symbol,
    gasoline_trade,
    gasoline_trades,
    is_trading_day,
    june_contract_number,
    main,
    natural_gas_trade,
    natural_gas_trades,
    ng_last_trade,
    ng_lead_days,
    on_or_after,
    on_or_before,
    profitable_count,
    runs_ending,
    settlements,
)


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
        """The natural gas files carry 2018-12-25 as a row repeating the day before."""
        _, rows = settlements(NATURAL_GAS[1])
        assert rows[date(2018, 12, 25)] == rows[date(2018, 12, 24)]
        assert not is_trading_day(date(2018, 12, 25))

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
    #: endpoint recorded it, read on 2026-10-03 for the four years queried.
    #: Nothing here can re-read them, so they are pinned as a measurement.
    EXCHANGE = {
        2017: ("2017-02-24", "2017-03-29", "2017-04-26", "2017-05-26"),
        2018: ("2018-02-26", "2018-03-27", "2018-04-26", "2018-05-29"),
        2021: ("2021-02-24", "2021-03-29", "2021-04-28", "2021-05-26"),
        2024: ("2024-02-27", "2024-03-26", "2024-04-26", "2024-05-29"),
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
        for year, price in ((1996, Decimal("2.033")), (1997, Decimal("1.930"))):
            trade = natural_gas_trade(year)
            assert (trade.entry_symbol, trade.entry_price) == (NATURAL_GAS[3], price)

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
        """Counted from 1994, the runs of 13 and 14 end a year early, in 2006 and 2007."""
        runs = runs_ending(GAS)
        assert (runs[2006], runs[2007], runs[2008]) == (13, 14, 15)

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


def test_the_report_prints_the_derived_counts(capsys: pytest.CaptureFixture[str]) -> None:
    """The printed lines carry the same figures the verdicts read, beside the book's."""
    main()
    out = capsys.readouterr().out
    assert "1995 to 2015: 16 of 21 profitable   (the book prints 19 of 21)" in out
    assert "the run ending in 2007: 13   (the main text prints 13)" in out
    assert "the run ending in 2008: 14   (the sidebar prints 14)" in out
