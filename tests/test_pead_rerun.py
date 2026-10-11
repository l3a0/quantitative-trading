"""The pins for Example 7.2 rerun on EDGAR's calendar and the archive's prices, issue 251.

This file is the single authority for every number any prose surface quotes
about the rerun, Entry 40 of ``docs/replication-log.md`` among them.
``tests/test_earnings_filings.py`` holds the counts about the ticker table and
the index that the universes are cut from.

Every pin names its vintage and its specification, stated once here and
carried in each failure message as :data:`SPEC`.

- **Vintages.** Chan's ``inputdataohlcdaily_stocks_20120424/`` and
  ``earnannfile/``, read as :mod:`chan.pead` reads them. The ticker table and
  the Item 2.02 index under ``research/filings/earnings/``, written on
  2026-10-10. For C, D, E1 and E5, the owner archive's ``sp500`` Alpha Vantage
  files, downloaded 2026-10-05 and pinned by the sha256s in
  ``data/archive_vintages.jsonl``, read for the raw open, the raw close and
  the adjusted close.
- **Specification.** :func:`chan.pead.pead` unchanged: the flag file's 330
  days, a lookback of 90, an entry of 0.5, a denominator of 30, 252-day
  annualisation, book two's ``smartstd`` and no costs. The trading calendar
  the derived flags move along is the committed raw SPY vintage. The
  universes and runs are those registered on issue 251, which
  :mod:`chan.pead_rerun` lists.

The archive pins skip where no archive is configured or ``QT_ARCHIVE_RUN`` is
not 1, the way ``tests/conftest.py``'s ``archive_skip_reason`` decides for
Example 7.1. Every other pin reads committed files and runs everywhere.

Exploratory, all of it. The audit on issue 251 spent part of the sample
before the registration, and it first ran here on 2026-10-10.
"""

from __future__ import annotations

import itertools

import pandas as pd
import pytest

from chan import pead_rerun
from chan.earnings_filings import Release
from chan.pead_rerun import (
    Agreement,
    agreement,
    derived_flags,
    next_trading_day,
    r1_day,
    r5_day,
)
from tests.conftest import archive_skip_reason

#: The trading days around Martin Luther King Day, Monday 2011-01-17.
DAYS = pd.DatetimeIndex(
    [
        "2011-01-12",
        "2011-01-13",
        "2011-01-14",
        "2011-01-18",
        "2011-01-19",
        "2011-01-20",
        "2011-01-21",
        "2011-01-24",
    ]
)


_NUMBERS = itertools.count(1)


def at(stamp: str) -> pd.Timestamp:
    return pd.Timestamp(stamp)


def release(
    accepted: str, report_date: str = "", ticker: str = "AAPL", form: str = "8-K"
) -> Release:
    return Release(
        ticker=ticker,
        cik=320193,
        accession=f"0000320193-11-{next(_NUMBERS):06d}",
        form=form,
        items="2.02,9.01",
        report_date=report_date or accepted[:10],
        filing_date=accepted[:10],
        accepted=accepted,
        header_sha256="0" * 64,
    )


class TestR1:
    def test_a_filing_before_the_open_flags_that_day(self) -> None:
        assert r1_day(at("2011-01-13 09:29:59"), DAYS) == at("2011-01-13")

    def test_a_filing_at_the_open_flags_nothing(self) -> None:
        assert r1_day(at("2011-01-13 09:30:00"), DAYS) is None

    def test_a_filing_in_the_last_second_of_the_session_flags_nothing(self) -> None:
        assert r1_day(at("2011-01-13 15:59:59"), DAYS) is None

    def test_a_filing_at_the_close_flags_the_next_trading_day(self) -> None:
        assert r1_day(at("2011-01-13 16:00:00"), DAYS) == at("2011-01-14")

    def test_a_friday_evening_filing_crosses_the_weekend_and_the_holiday(self) -> None:
        assert r1_day(at("2011-01-14 16:30:00"), DAYS) == at("2011-01-18")

    def test_a_weekend_morning_filing_flags_the_next_trading_day(self) -> None:
        assert r1_day(at("2011-01-15 08:00:00"), DAYS) == at("2011-01-18")

    def test_a_holiday_morning_filing_flags_the_next_trading_day(self) -> None:
        """Before 09:30, but on a day the market was shut, so the next day's gap reads it."""
        assert r1_day(at("2011-01-17 07:00:00"), DAYS) == at("2011-01-18")

    def test_a_holiday_session_hour_filing_still_flags_the_next_day(self) -> None:
        assert r1_day(at("2011-01-17 11:00:00"), DAYS) == at("2011-01-18")

    def test_a_filing_past_the_calendar_flags_nothing(self) -> None:
        assert r1_day(at("2011-01-24 16:30:00"), DAYS) is None
        assert next_trading_day(at("2011-01-24"), DAYS) is None


class TestR5:
    def test_a_late_filing_flags_the_trading_day_after_its_report_date(self) -> None:
        """The release went out on 2011-01-18 and the 8-K followed two days later."""
        assert r5_day(at("2011-01-20 08:00:00"), "2011-01-18", DAYS) == at("2011-01-19")

    def test_a_late_filing_whose_report_date_is_a_friday_flags_past_the_holiday(self) -> None:
        assert r5_day(at("2011-01-19 17:00:00"), "2011-01-14", DAYS) == at("2011-01-18")

    def test_a_session_filing_flags_that_same_day(self) -> None:
        assert r5_day(at("2011-01-13 09:30:00"), "2011-01-13", DAYS) == at("2011-01-13")
        assert r5_day(at("2011-01-13 15:59:59"), "2011-01-13", DAYS) == at("2011-01-13")

    def test_otherwise_it_is_r1(self) -> None:
        assert r5_day(at("2011-01-13 09:29:59"), "2011-01-13", DAYS) == at("2011-01-13")
        assert r5_day(at("2011-01-13 16:00:00"), "2011-01-13", DAYS) == at("2011-01-14")
        assert r5_day(at("2011-01-17 11:00:00"), "2011-01-17", DAYS) == at("2011-01-18")

    def test_an_empty_report_date_is_never_late(self) -> None:
        assert r5_day(at("2011-01-13 18:00:00"), "", DAYS) == at("2011-01-14")


class TestTheDerivedFlags:
    WINDOW = DAYS[1:-1]

    def flags(self, releases: list[Release], rule: str = "R1") -> pd.DataFrame:
        return derived_flags(releases, ["AAPL", "IBM"], self.WINDOW, DAYS, rule)

    def test_two_filings_on_one_day_make_one_flag(self) -> None:
        flags = self.flags([release("2011-01-13 07:00:00"), release("2011-01-13 08:00:00")])
        assert flags.at[at("2011-01-13"), "AAPL"] == 1.0
        assert flags.to_numpy().sum() == 1.0

    def test_two_filings_landing_on_one_day_from_two_days_make_one_flag(self) -> None:
        flags = self.flags([release("2011-01-14 17:00:00"), release("2011-01-18 06:00:00")])
        assert flags["AAPL"].tolist() == [0, 0, 1, 0, 0, 0]

    def test_an_amendment_is_dropped(self) -> None:
        flags = self.flags([release("2011-01-13 07:00:00", form="8-K/A")])
        assert flags.to_numpy().sum() == 0.0

    def test_a_stock_outside_the_universe_gets_no_column(self) -> None:
        flags = self.flags([release("2011-01-13 07:00:00", ticker="CB")])
        assert list(flags.columns) == ["AAPL", "IBM"]
        assert flags.to_numpy().sum() == 0.0

    def test_a_flag_outside_the_window_is_dropped(self) -> None:
        flags = self.flags([release("2011-01-12 07:00:00"), release("2011-01-21 17:00:00")])
        assert flags.to_numpy().sum() == 0.0

    def test_every_day_of_the_window_is_kept_with_its_zeros(self) -> None:
        flags = self.flags([])
        assert flags.index.equals(self.WINDOW)
        assert flags.shape == (6, 2)

    def test_r5_moves_a_session_filing_onto_its_own_day(self) -> None:
        session = [release("2011-01-19 10:00:00")]
        assert self.flags(session, "R1").to_numpy().sum() == 0.0
        assert self.flags(session, "R5").at[at("2011-01-19"), "AAPL"] == 1.0


class TestAgreement:
    def test_cells_are_counted_four_ways(self) -> None:
        index = DAYS[:3]
        mine = pd.DataFrame({"A": [1, 0, 1], "B": [0, 0, 1]}, index=index, dtype=float)
        his = pd.DataFrame(
            {"A": [1, 1, 0], "B": [0, 0, 1], "C": [1, 1, 1]}, index=index, dtype=float
        )
        assert agreement(mine, his) == Agreement(both=2, chan_only=1, derived_only=1, neither=2)
        assert agreement(mine, his).cells == 6


class TestTheAttribution:
    def drift(self, arithmetic: float, sharpe: float):
        return type("D", (), {"arithmetic_annual": arithmetic, "sharpe": sharpe})()

    def test_the_interaction_is_what_e1_less_a_u_leaves_after_three_effects(self) -> None:
        runs = {
            name: self.drift(value, value * 10)
            for name, value in {
                "A": 0.07, "A_U": 0.03, "A_CAL": 0.05, "B1": 0.02, "A_PX": 0.04,
                "C": 0.035, "D": 0.036, "E1": 0.01,
            }.items()
        }  # fmt: skip
        effects = {e.label: e for e in pead_rerun.attribution(runs)}
        assert effects["universe"].arithmetic == pytest.approx(-0.04)
        assert effects["calendar"].arithmetic == pytest.approx(-0.03)
        assert effects["vendor"].arithmetic == pytest.approx(-0.005)
        assert effects["basis"].arithmetic == pytest.approx(0.001)
        total = effects["all of it, E1 against A_U"].arithmetic
        assert total == pytest.approx(-0.02)
        interaction = effects["interaction, what E1 − A_U leaves"]
        assert interaction.arithmetic == pytest.approx(-0.02 - (-0.03 - 0.005 + 0.001))
        assert interaction.sharpe == pytest.approx(10 * interaction.arithmetic)

    def test_without_the_archive_runs_only_two_effects_and_no_interaction_print(self) -> None:
        runs = {name: self.drift(0.01, 0.1) for name in ("A", "A_U", "A_CAL", "B1", "A_PX")}
        assert [e.label for e in pead_rerun.attribution(runs)] == ["universe", "calendar"]


SPEC = (
    "chan.pead.pead on the flag file's 330 days, 90-day lookback, entry at 0.5 moving std, "
    "each day's return over 30; universes from research/filings/earnings/tickers.csv and "
    "calendars from its index.jsonl as written 2026-10-10, trading days from the raw SPY vintage"
)
ARCHIVE_SPEC = SPEC + "; prices from the archive's sp500 Alpha Vantage files downloaded 2026-10-05"

#: Each run's arithmetic annual return, Sharpe ratio, compounded APR, maximum
#: drawdown, its duration in days, the trades taken and the busiest day.
FIGURES = {
    "A": (0.066743, 1.4909, 0.067952, -0.026052, 109, 1072, 30),
    "A_CAL": (0.054481, 1.3253, 0.055101, -0.029402, 115, 1052, 28),
    "A_PX": (0.053099, 1.5028, 0.053874, -0.023386, 112, 964, 27),
    "A_U": (0.043678, 1.2815, 0.044038, -0.023176, 114, 949, 25),
    "B1": (0.071050, 1.7045, 0.072696, -0.027258, 63, 1291, 49),
    "B5": (0.063142, 1.2988, 0.063923, -0.031029, 80, 1477, 55),
    "C": (0.053206, 1.4905, 0.053973, -0.025224, 113, 964, 27),
    "D": (0.053283, 1.5255, 0.054083, -0.023066, 112, 954, 27),
    "E1": (0.057489, 1.6585, 0.058532, -0.023984, 63, 1172, 44),
    "E5": (0.057426, 1.4118, 0.058229, -0.029106, 80, 1339, 48),
}

#: The attribution, arithmetic annual return and Sharpe ratio, from the runs above.
EFFECTS = {
    "universe": (-0.023065, -0.2094),
    "calendar": (0.016568, 0.3792),
    "vendor": (0.000107, -0.0123),
    "basis": (0.000078, 0.0350),
    "all of it, E1 against A_U": (0.013811, 0.3770),
    "interaction, what E1 − A_U leaves": (-0.002942, -0.0249),
}

COMMITTED = ("A", "A_CAL", "A_PX", "A_U", "B1", "B5")


@pytest.fixture(scope="module")
def sources() -> pead_rerun.Sources:
    return pead_rerun.read_committed()


@pytest.fixture(scope="module")
def runs(sources):
    return pead_rerun.committed_runs(sources)


@pytest.fixture(scope="module")
def archive_runs(sources, runs):
    reason = archive_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    prices = pead_rerun.read_archive(sources)
    return {**runs, **pead_rerun.archive_runs(sources, prices)}, prices


def figures(drift) -> tuple:
    return (
        round(drift.arithmetic_annual, 6),
        round(drift.sharpe, 4),
        round(drift.compounded_apr, 6),
        round(drift.max_drawdown, 6),
        drift.max_drawdown_days,
        drift.trades,
        drift.most_held,
    )


def effects_of(runs) -> dict[str, tuple[float, float]]:
    return {
        effect.label: (round(effect.arithmetic, 6), round(effect.sharpe, 4))
        for effect in pead_rerun.attribution(runs)
    }


class TestTheCommittedRuns:
    """A, A_CAL, A_PX, A_U, B1 and B5, which read only committed files and run everywhere."""

    @pytest.mark.parametrize("name", COMMITTED)
    def test_the_figures(self, runs, name) -> None:
        assert figures(runs[name]) == FIGURES[name], f"{name}: {SPEC}"

    def test_run_a_is_entry_12_unchanged(self, runs) -> None:
        assert figures(runs["A"])[:5] == (0.066743, 1.4909, 0.067952, -0.026052, 109), SPEC

    def test_the_universes(self, sources) -> None:
        sizes = {name: len(sources.universe(name)) for name in pead_rerun.UNIVERSES}
        assert sizes == {"ALL": 497, "CAL": 488, "PX": 446, "U": 441}

    def test_the_attribution_without_the_archive(self, runs) -> None:
        expected = {label: EFFECTS[label] for label in ("universe", "calendar")}
        assert effects_of(runs) == expected, SPEC


class TestTheCalendarsAgainstChans:
    """Cell by cell over the 330 days and the 488 stocks of CAL, 161,040 cells."""

    def test_r1(self, sources) -> None:
        counts = pead_rerun.agreement(sources.calendar_flags("R1"), sources.flags)
        assert counts == Agreement(both=1540, chan_only=311, derived_only=914, neither=158275)

    def test_r5(self, sources) -> None:
        counts = pead_rerun.agreement(sources.calendar_flags("R5"), sources.flags)
        assert counts == Agreement(both=1694, chan_only=157, derived_only=1124, neither=158065)

    def test_r1_catches_the_two_apple_releases_chans_flags_miss(self, sources) -> None:
        """Chan's flags hold three of Apple's five in-window releases, as issue 20 measured."""
        r1 = sources.calendar_flags("R1")["AAPL"]
        his = sources.flags["AAPL"]
        assert list(r1.index[r1 == 1].strftime("%Y-%m-%d")) == [
            "2011-01-19", "2011-04-21", "2011-07-20", "2011-10-19", "2012-01-25",
        ]  # fmt: skip
        assert list(r1.index[(r1 == 1) & (his == 0)].strftime("%Y-%m-%d")) == [
            "2011-01-19", "2011-10-19",
        ]  # fmt: skip


class TestTheArchiveRuns:
    """C, D, E1 and E5, which read the archive's prices. They skip without it."""

    @pytest.mark.parametrize("name", ("C", "D", "E1", "E5"))
    def test_the_figures(self, archive_runs, name) -> None:
        runs, _ = archive_runs
        assert figures(runs[name]) == FIGURES[name], f"{name}: {ARCHIVE_SPEC}"

    def test_the_attribution(self, archive_runs) -> None:
        runs, _ = archive_runs
        assert effects_of(runs) == EFFECTS, ARCHIVE_SPEC

    def test_the_raw_prices_cross_a_split_in_sixteen_stocks(self, sources, archive_runs) -> None:
        """Why D runs without the guard: these are the days D exists to measure."""
        _, prices = archive_runs
        assert pead_rerun.raw_breaks(prices, sources.window) == [
            "BLL", "C", "CERN", "COG", "CSX", "EL", "EMN", "ETN", "FAST", "FCX", "FTI", "HRL",
            "MSI", "ROST", "TJX", "WEC",
        ]  # fmt: skip

    def test_the_adjusted_open_is_the_raw_open_rescaled_by_the_close(self, archive_runs) -> None:
        _, prices = archive_runs
        ratio = prices.adjusted_open / prices.raw_open
        expected = prices.adjusted_close / prices.raw_close
        assert (ratio - expected).abs().max().max() < 1e-12
