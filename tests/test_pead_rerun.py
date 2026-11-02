"""The pins for Example 7.2 rerun on EDGAR's calendar and the archive's prices, issue 251.

This file is the authority for the rerun's figures that any prose surface
quotes, Entry 46 of ``docs/replication-log.md`` among them: each run's
figures, the attribution, each calendar's agreement with Chan's flags, and the
checks run beside them on late filings and on the archive's opens.
``tests/test_earnings_filings.py`` is the authority for the counts about the
ticker table and the index that the universes are cut from, Entry 46's rows
15 and 16 and the 48 renamed companies among them.

Every pin names its vintage and its specification, stated once here.
:data:`SPEC` and :data:`ARCHIVE_SPEC` repeat them in the failure messages of
the runs' own figures, and a pin without either reads the same vintages under
the same specification.

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

``blog/pead-edgar-rerun-lessons.md`` quotes most of these figures, so a change
to any of them moves that post too. ``TestWhatThePostMeasured`` holds the
numbers the post added, all measured after the runs, and
``TestTheTradeReturns`` holds the one helper they come through, on toy prices.
``TestWhatThePostQuotes`` reads the post itself, and checks one copy of each
figure it quotes against the runs, its docstring naming what it reads.
``tests/test_pead_rerun_figures.py`` holds what the post's figure draws, and
``tests/test_pead_rerun_whiteboard.py`` what its two sketches draw.

Exploratory, all of it. The audit on issue 251 spent part of the sample
before the registration, and it first ran here on 2026-10-10.
"""

from __future__ import annotations

import itertools
import re
from collections import Counter
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from chan import earnings_filings, pead_rerun
from chan.archive import ArchiveUnavailable, read_archive_manifest
from chan.earnings_filings import (
    Release,
    holding_price,
    name_keys,
    read_table,
    serialize_table,
)
from chan.pead import (
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    DENOMINATOR,
    ENTRY,
    LOOKBACK,
    TRADING_DAYS,
    Drift,
    pead,
)
from chan.pead_figures import cumulative_return, longest_spell
from chan.pead_rerun import (
    Agreement,
    agreement,
    derived_flags,
    next_trading_day,
    r1_day,
    r5_day,
)
from chan.vintage import VintageUnavailable
from tests.conftest import archive_skip_reason
from tests.test_earnings_filings import OWN_NAMES, ivv_names, meets

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

    def test_every_comparison_prints_with_the_interaction_after_its_total(self) -> None:
        runs = {spec.name: self.drift(0.01, 0.1) for spec in pead_rerun.SPECS}
        assert [e.label for e in pead_rerun.attribution(runs)] == [
            "universe", "calendar", "calendar, R5", "vendor", "basis",
            "all of it, E1 against A_U", "interaction, what E1 − A_U leaves",
            "E1 against A", "E5 against A_U", "E5 against A",
        ]  # fmt: skip

    def test_each_further_comparison_reads_its_own_two_runs(self) -> None:
        values = {spec.name: 0.01 * (i + 1) for i, spec in enumerate(pead_rerun.SPECS)}
        runs = {name: self.drift(value, value * 10) for name, value in values.items()}
        effects = {e.label: e for e in pead_rerun.attribution(runs)}
        for label, run, reference in (
            ("calendar, R5", "B5", "A_CAL"),
            ("E1 against A", "E1", "A"),
            ("E5 against A_U", "E5", "A_U"),
            ("E5 against A", "E5", "A"),
        ):
            assert effects[label].arithmetic == pytest.approx(values[run] - values[reference])
            assert effects[label].sharpe == pytest.approx(10 * (values[run] - values[reference]))


class TestTheReturnPerTrade:
    def test_it_is_the_days_summed_returns_times_the_denominator_over_the_trades(self) -> None:
        """Two trades on one day, +3% and −1%, give 2% over 30 that day and 1% a trade."""
        positions = np.array([[1.0, -1.0, 0.0], [0.0, 0.0, 0.0]])
        daily = np.array([0.02 / DENOMINATOR, 0.0])
        drift = Drift(pd.DatetimeIndex(DAYS[:2]), positions, daily, 0.0, 0.0, 0.0, 0.0, 0)
        assert pead_rerun.per_trade(drift) == pytest.approx(0.01)


class TestTheTradeReturns:
    """Each stock-day's signed return from the open to the close, on three stocks and two days."""

    INDEX = pd.DatetimeIndex(DAYS[:3])

    def toy(self) -> tuple[Drift, pd.DataFrame, pd.DataFrame]:
        """The first day is outside the run, so its prices must not be read."""
        opens = pd.DataFrame(
            {"X": [1.0, 100.0, 50.0], "Y": [1.0, 20.0, np.nan], "Z": [1.0, 10.0, 10.0]},
            index=self.INDEX,
        )
        closes = pd.DataFrame(
            {"X": [9.0, 103.0, 49.0], "Y": [9.0, 21.0, 30.0], "Z": [9.0, 11.0, 12.0]},
            index=self.INDEX,
        )
        positions = np.array([[1.0, -1.0, 0.0], [-1.0, 1.0, 0.0]])
        days = self.INDEX[1:]
        return Drift(days, positions, np.zeros(2), 0.0, 0.0, 0.0, 0.0, 0), opens, closes

    def test_a_long_earns_the_move_and_a_short_its_negative(self) -> None:
        drift, opens, closes = self.toy()
        returns = pead_rerun.trade_returns(drift, opens, closes)
        assert returns.at[DAYS[1], "X"] == pytest.approx(0.03)
        assert returns.at[DAYS[1], "Y"] == pytest.approx(-0.05)
        assert returns.at[DAYS[2], "X"] == pytest.approx(0.02)

    def test_a_stock_not_held_and_a_missing_price_count_as_0(self) -> None:
        """``smartsum`` reads a missing return as 0, so the run does too."""
        drift, opens, closes = self.toy()
        returns = pead_rerun.trade_returns(drift, opens, closes)
        assert (returns["Z"] == 0).all()
        assert returns.at[DAYS[2], "Y"] == 0.0

    def test_a_zero_open_on_a_held_stock_counts_as_0(self) -> None:
        """``smartsum`` skips any return that is not finite, an infinite one included."""
        drift, opens, closes = self.toy()
        opens.at[DAYS[2], "X"] = 0.0
        returns = pead_rerun.trade_returns(drift, opens, closes)
        assert returns.at[DAYS[2], "X"] == 0.0
        assert np.isfinite(returns.to_numpy()).all()

    def test_a_day_after_the_run_is_not_read_either(self) -> None:
        """The run's days are picked by date, not by counting back from the last row."""
        drift, opens, closes = self.toy()
        before = pead_rerun.trade_returns(drift, opens, closes)
        later = DAYS[3:4]
        opens = pd.concat([opens, pd.DataFrame({"X": [7.0], "Y": [7.0], "Z": [7.0]}, index=later)])
        closes = pd.concat(
            [closes, pd.DataFrame({"X": [8.0], "Y": [8.0], "Z": [8.0]}, index=later)]
        )
        after = pead_rerun.trade_returns(drift, opens, closes)
        pd.testing.assert_frame_equal(after, before)

    def test_it_has_the_runs_days_and_the_frames_stocks(self) -> None:
        drift, opens, closes = self.toy()
        returns = pead_rerun.trade_returns(drift, opens, closes)
        assert returns.index.equals(drift.days)
        assert list(returns.columns) == ["X", "Y", "Z"]

    def test_each_row_over_30_is_the_runs_daily_return(self) -> None:
        """On a real run, which is the identity the post's split of A rests on."""
        opens = pd.DataFrame({"X": np.linspace(10, 12, 120), "Y": np.linspace(20, 15, 120)})
        opens.index = pd.bdate_range("2011-01-03", periods=120)
        wiggle = np.sin(np.arange(120)) / 50
        closes = opens * (1 + wiggle[:, None])
        closes["Y"] = opens["Y"] * (1 - wiggle)
        flags = pd.DataFrame(1.0, index=opens.index, columns=opens.columns)
        drift = pead(opens, closes, flags)
        assert drift.trades > 0
        returns = pead_rerun.trade_returns(drift, opens, closes)
        np.testing.assert_allclose(returns.sum(axis=1) / DENOMINATOR, drift.daily, atol=1e-15)


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

#: Each run's mean signed return from the open to the close of one trade.
PER_TRADE = {
    "A": 0.002446,
    "A_CAL": 0.002035,
    "A_PX": 0.002164,
    "A_U": 0.001808,
    "B1": 0.002162,
    "B5": 0.001679,
    "C": 0.002168,
    "D": 0.002194,
    "E1": 0.001927,
    "E5": 0.001685,
}

#: The attribution, arithmetic annual return and Sharpe ratio, from the runs above.
EFFECTS = {
    "universe": (-0.023065, -0.2094),
    "calendar": (0.016568, 0.3792),
    "calendar, R5": (0.008661, -0.0265),
    "vendor": (0.000107, -0.0123),
    "basis": (0.000078, 0.0350),
    "all of it, E1 against A_U": (0.013811, 0.3770),
    "interaction, what E1 − A_U leaves": (-0.002942, -0.0249),
    "E1 against A": (-0.009254, 0.1677),
    "E5 against A_U": (0.013748, 0.1303),
    "E5 against A": (-0.009317, -0.0790),
}

COMMITTED = ("A", "A_CAL", "A_PX", "A_U", "B1", "B5")

#: A filing accepted at least this many days after its ``reportDate`` is the
#: kind R5's late rule carries back to a quarter's first trading day. Chosen
#: after reading the lags, so the checks reading it decide nothing.
LONG_LATE_DAYS = 7


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


def days_late(release: Release) -> int:
    """How many calendar days the acceptance date trails the ``reportDate``."""
    return (pd.Timestamp(release.accepted[:10]) - pd.Timestamp(release.report_date)).days


def long_late(sources) -> tuple[list[Release], list[Release]]:
    """The 8-Ks accepted at least :data:`LONG_LATE_DAYS` after their date, and the rest."""
    late, rest = [], []
    for release in sources.releases:
        is_late = release.report_date and days_late(release) >= LONG_LATE_DAYS
        (late if is_late else rest).append(release)
    return late, rest


def b5_reading_long_late_filings(sources, reading: str) -> Drift:
    """B5 with the long-late filings read another way, which the registration did not fix.

    ``"R1's day"`` puts each on the day R1 gives it. ``"no late rule"``
    applies R5 without its late rule, which is R5 on an empty ``reportDate``.
    ``"dropped"`` leaves them out.
    """
    stocks = sources.universe("CAL")
    late, rest = long_late(sources)
    flags = derived_flags(rest, stocks, sources.window, sources.days, "R5")
    if reading == "R1's day":
        moved = derived_flags(late, stocks, sources.window, sources.days, "R1")
    elif reading == "no late rule":
        undated = [replace(release, report_date="") for release in late]
        moved = derived_flags(undated, stocks, sources.window, sources.days, "R5")
    else:
        moved = flags * 0
    return pead(sources.opens[stocks], sources.closes[stocks], np.maximum(flags, moved))


#: How far an open may sit from Chan's, once the archive's close is scaled to his.
OPEN_TOLERANCE = 0.02


def opens_off_chans(sources, prices) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Each PX stock-day's adjusted open against Chan's, and the scale that compares them.

    The scale is Chan's close over the archive's adjusted close that day, so a
    series that agrees with his on the close and the open gives 0.
    """
    stocks = sources.universe("PX")
    scale = sources.closes.loc[sources.window, stocks] / prices.adjusted_close[stocks]
    off = prices.adjusted_open[stocks] * scale / sources.opens.loc[sources.window, stocks] - 1
    return off.abs(), scale


def opens_with_chans(sources, prices) -> pd.DataFrame:
    """The archive's adjusted opens with every one off by more than the tolerance replaced."""
    off, scale = opens_off_chans(sources, prices)
    stocks = sources.universe("PX")
    chans = sources.opens.loc[sources.window, stocks] / scale
    opens = prices.adjusted_open.copy()
    opens[stocks] = prices.adjusted_open[stocks].where(off <= OPEN_TOLERANCE, chans)
    return opens


def runs_on_chans_opens(sources, prices) -> dict[str, Drift]:
    """C, E1 and E5 with every open off by more than the tolerance replaced by Chan's."""
    opens = opens_with_chans(sources, prices)
    runs = {}
    for name, universe, flags in (
        ("C", "PX", sources.flags),
        ("E1", "U", sources.calendar_flags("R1")),
        ("E5", "U", sources.calendar_flags("R5")),
    ):
        chosen = sources.universe(universe)
        runs[name] = pead(opens[chosen], prices.adjusted_close[chosen], flags[chosen])
    return runs


def trades_moved_by_chans_opens(sources, prices, runs, fixed) -> dict[str, pd.Series]:
    """In E1 and E5, each stock-day whose share of the run's return Chan's opens change.

    A trade's change in signed return, over 30 and times 252 over the 330
    days, is its share of the move in the arithmetic annual return.
    """
    opens = opens_with_chans(sources, prices)
    u = sources.universe("U")
    closes = prices.adjusted_close[u]
    moved = {}
    for name in ("E1", "E5"):
        before = pead_rerun.trade_returns(runs[name], prices.adjusted_open[u], closes)
        after = pead_rerun.trade_returns(fixed[name], opens[u], closes)
        share = (after - before) * TRADING_DAYS / (DENOMINATOR * len(runs[name].days))
        changed = share.stack()
        moved[name] = changed[changed.abs() > 1e-12]
    return moved


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

    def test_the_spy_calendar_is_chans_over_the_days_the_filings_reach(self, sources) -> None:
        spy = sources.days[(sources.days >= "2010-11-01") & (sources.days <= "2012-04-24")]
        assert spy.equals(sources.closes.index[sources.closes.index >= "2010-11-01"])

    def test_the_attribution_without_the_archive(self, runs) -> None:
        expected = {label: EFFECTS[label] for label in ("universe", "calendar", "calendar, R5")}
        assert effects_of(runs) == expected, SPEC

    @pytest.mark.parametrize("name", COMMITTED)
    def test_the_return_per_trade(self, runs, name) -> None:
        assert round(pead_rerun.per_trade(runs[name]), 6) == PER_TRADE[name], f"{name}: {SPEC}"

    @pytest.mark.parametrize("name", COMMITTED)
    def test_the_return_is_the_trades_times_their_mean(self, runs, name) -> None:
        """Over a fixed 30, so more trades at the same mean raise the return in proportion."""
        drift = runs[name]
        rebuilt = drift.trades * pead_rerun.per_trade(drift) * TRADING_DAYS
        rebuilt /= DENOMINATOR * len(drift.days)
        assert rebuilt == pytest.approx(drift.arithmetic_annual, rel=1e-12)

    def test_r1_earns_more_a_trade_and_r5_less_than_chans_flags_on_cal(self, runs) -> None:
        """So most of B1's rise and all of B5's come from the extra trades."""
        a_cal, b1, b5 = (runs[name] for name in ("A_CAL", "B1", "B5"))
        assert (b1.trades, a_cal.trades, b5.trades) == (1291, 1052, 1477)
        assert pead_rerun.per_trade(b5) < pead_rerun.per_trade(a_cal) < pead_rerun.per_trade(b1)
        assert round(pead_rerun.per_trade(b1) / pead_rerun.per_trade(a_cal) - 1, 2) == 0.06
        # The rise had B1 taken A_CAL's mean on its own trades, over the whole rise.
        from_trades = (b1.trades - a_cal.trades) * pead_rerun.per_trade(a_cal)
        whole = b1.trades * pead_rerun.per_trade(b1) - a_cal.trades * pead_rerun.per_trade(a_cal)
        assert round(from_trades / whole, 2) == 0.75, SPEC

    def test_b5_with_its_long_late_filings_read_three_other_ways(self, sources) -> None:
        """None of these readings was registered. They show what the late rule's reach costs."""
        figures_of = {
            reading: (round(drift.arithmetic_annual, 6), round(drift.sharpe, 4))
            for reading in ("R1's day", "no late rule", "dropped")
            for drift in [b5_reading_long_late_filings(sources, reading)]
        }
        assert figures_of == {
            "R1's day": (0.062600, 1.2802),
            "no late rule": (0.064813, 1.2880),
            "dropped": (0.059903, 1.2407),
        }, SPEC


#: Said in every failure message of :class:`TestWhatThePostMeasured`.
AFTER_THE_RUNS = (
    "measured for blog/pead-edgar-rerun-lessons.md after the runs' figures were seen, "
    "so it decides nothing"
)


def a_trades(sources, runs) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run A's signed return on each stock-day, and its position there."""
    a = runs["A"]
    stocks = sources.universe("ALL")
    returns = pead_rerun.trade_returns(a, sources.opens[stocks], sources.closes[stocks])
    return returns, pd.DataFrame(a.positions, index=a.days, columns=stocks)


def cal_without_a_series(sources) -> list[str]:
    """The 47 stocks of CAL outside U, in the order of Chan's files."""
    u, cal = set(sources.universe("U")), set(sources.universe("CAL"))
    return [s for s in sources.universe("ALL") if s in cal and s not in u]


def to_annual(drift: Drift) -> float:
    """What one unit of summed trade return adds to a run's arithmetic annual return."""
    return TRADING_DAYS / (DENOMINATOR * len(drift.days))


class TestWhatThePostMeasured:
    """Numbers ``blog/pead-edgar-rerun-lessons.md`` quotes that no row of Entry 46 declared.

    Every number here was measured after the runs' figures were seen, on the
    same committed vintages and specification as :class:`TestTheCommittedRuns`.
    Each is exploratory and decides nothing. The split of A's stocks into
    three groups, the day singled out, and the comparison of means in
    particular were all chosen after reading the runs.
    """

    def test_a_less_a_u_is_exactly_the_trades_of_the_56_stocks_outside_u(
        self, sources, runs
    ) -> None:
        """Each stock trades on its own gap and deviation, so dropping others changes nothing."""
        returns, _ = a_trades(sources, runs)
        outside = [s for s in returns.columns if s not in set(sources.universe("U"))]
        summed = float(returns[outside].to_numpy().sum()) * to_annual(runs["A"])
        effect = runs["A"].arithmetic_annual - runs["A_U"].arithmetic_annual
        assert len(outside) == 56
        assert summed == pytest.approx(effect, rel=1e-12), f"{SPEC}; {AFTER_THE_RUNS}"
        assert round(summed, 6) == 0.023065

    def test_a_less_a_cal_is_exactly_the_trades_of_the_9_stocks_outside_cal(
        self, sources, runs
    ) -> None:
        """Rounded from the true value. Subtracting the two rounded pins gives 0.012262."""
        returns, _ = a_trades(sources, runs)
        outside = [s for s in returns.columns if s not in set(sources.universe("CAL"))]
        summed = float(returns[outside].to_numpy().sum()) * to_annual(runs["A"])
        effect = runs["A"].arithmetic_annual - runs["A_CAL"].arithmetic_annual
        assert summed == pytest.approx(effect, rel=1e-12), f"{SPEC}; {AFTER_THE_RUNS}"
        assert round(effect, 6) == 0.012261
        assert round(FIGURES["A"][0] - FIGURES["A_CAL"][0], 6) == 0.012262

    def test_the_three_groups_stocks_trades_and_contributions(self, sources, runs) -> None:
        returns, positions = a_trades(sources, runs)
        u, cal = set(sources.universe("U")), set(sources.universe("CAL"))
        groups = {
            "U": [s for s in returns.columns if s in u],
            "CAL, no checked series": [s for s in returns.columns if s in cal and s not in u],
            "no checked CIK": [s for s in returns.columns if s not in cal],
        }
        measured = {
            name: (
                len(stocks),
                int((positions[stocks] != 0).to_numpy().sum()),
                round(float(returns[stocks].to_numpy().sum()) * to_annual(runs["A"]), 6),
            )
            for name, stocks in groups.items()
        }
        assert measured == {
            "U": (441, 949, 0.043678),
            "CAL, no checked series": (47, 103, 0.010803),
            "no checked CIK": (9, 20, 0.012261),
        }, f"{SPEC}; {AFTER_THE_RUNS}"

    def test_why_the_47_stocks_of_cal_have_no_checked_series(self, sources) -> None:
        """36 lack closes, 7 have no series proposed, and 4 hold another company's returns.

        For ``missing``, ``days_over`` counts the closes Chan's file holds and
        the series lacks, so 330 means none of the window's.
        """
        rows = {row.ticker: row for row in sources.table}
        stocks = cal_without_a_series(sources)
        assert Counter(rows[s].archive_check for s in stocks) == {
            "missing": 36,
            "none": 7,
            "returns": 4,
        }, AFTER_THE_RUNS
        assert Counter(rows[s].days_over for s in stocks if rows[s].archive_check == "missing") == {
            "330": 35,
            "35": 1,
        }
        assert [s for s in stocks if rows[s].days_over == "35"] == ["EP"]
        assert sorted(s for s in stocks if rows[s].archive_check == "returns") == [
            "AGN", "CB", "JCI", "LSI",
        ]  # fmt: skip

    def test_each_series_lacking_closes_starts_inside_or_after_the_window(self, sources) -> None:
        """Read from the committed manifest of the archive, so it runs everywhere.

        35 of the 36 series start after 2012-04-24, so the archive holds none
        of the window's closes under those tickers. EP's starts on 2011-02-23,
        after the window's first 35 days. The 7 with no series proposed have
        no line in the ``sp500`` cross-section at all.
        """
        entries = {e.symbol: e for e in read_archive_manifest() if e.cross_section == "sp500"}
        rows = {row.ticker: row for row in sources.table}
        stocks = cal_without_a_series(sources)
        first = {
            s: entries[rows[s].archive_ticker].first_date
            for s in stocks
            if rows[s].archive_check == "missing"
        }
        last_day = str(sources.window[-1].date())
        assert last_day == "2012-04-24"
        after = sorted(s for s, day in first.items() if day > last_day)
        assert len(after) == 35 and "EP" not in after, AFTER_THE_RUNS
        assert first["EP"] == "2011-02-23"
        assert int((sources.window < "2011-02-23").sum()) == 35
        assert (first["ALTR"], first["DELL"], first["DOW"]) == (
            "2017-11-01", "2018-12-21", "2019-03-20",
        )  # fmt: skip
        none = [s for s in stocks if rows[s].archive_check == "none"]
        assert len(none) == 7 and not any(s in entries for s in none)

    def test_the_five_that_left_the_fund_during_the_window(self, sources, runs) -> None:
        """AKS, CPWR, MWW, TLAB and WFR, missing from IVV's schedule of 2012-03-31.

        ``tests/test_earnings_filings.py`` holds that each was in the schedule
        of 2011-09-30 and in neither later one. Chan's closes fell 27 to 69
        percent over the window for all five. Of A's 13 trades in them, 9 are
        shorts, and they average 0.022738, no more than the 0.026587 of the 7
        trades in the other four of the nine. Exploratory, and it tests no
        reason why these stocks earn more.
        """
        five = ["AKS", "CPWR", "MWW", "TLAB", "WFR"]
        returns, positions = a_trades(sources, runs)
        closes = sources.closes.loc[sources.window, five]
        spans = {s: closes[s].dropna() for s in five}
        fell = {s: round(float(c.iloc[-1] / c.iloc[0] - 1), 3) for s, c in spans.items()}
        assert fell == {
            "AKS": -0.558, "CPWR": -0.273, "MWW": -0.671, "TLAB": -0.404, "WFR": -0.694,
        }, AFTER_THE_RUNS  # fmt: skip
        held = positions[five].to_numpy()
        assert (int((held != 0).sum()), int((held < 0).sum())) == (13, 9), AFTER_THE_RUNS
        outside_cal = [s for s in returns.columns if s not in set(sources.universe("CAL"))]
        other = [s for s in outside_cal if s not in five]
        assert other == ["CVC", "DD", "LUK", "NYX"]

        def mean_trade(stocks):
            trades = returns[stocks].stack()[positions[stocks].stack() != 0]
            return len(trades), round(float(trades.mean()), 6)

        assert mean_trade(five) == (13, 0.022738), AFTER_THE_RUNS
        assert mean_trade(other) == (7, 0.026587), AFTER_THE_RUNS

    def test_the_contributions_by_why_a_stock_is_outside_u(self, sources, runs) -> None:
        """The 13 the checks cannot confirm as the right company carry 0.64 of the universe effect.

        They are the 9 outside CAL and the 4 reused tickers whose series holds
        another company's returns. The other 43 are the stocks of CAL whose
        series lacks closes or was never proposed.
        """
        returns, positions = a_trades(sources, runs)
        rows = {row.ticker: row for row in sources.table}
        stocks = cal_without_a_series(sources)
        outside_cal = [s for s in returns.columns if s not in set(sources.universe("CAL"))]
        reused = [s for s in stocks if rows[s].archive_check == "returns"]
        unpriced = [s for s in stocks if rows[s].archive_check in ("missing", "none")]
        scale = to_annual(runs["A"])

        def measured(group):
            return (
                len(group),
                int((positions[group] != 0).to_numpy().sum()),
                round(float(returns[group].to_numpy().sum()) * scale, 6),
            )

        assert measured(reused) == (4, 8, 0.002526), f"{SPEC}; {AFTER_THE_RUNS}"
        assert measured(unpriced) == (43, 95, 0.008278), f"{SPEC}; {AFTER_THE_RUNS}"
        untied = outside_cal + reused
        assert measured(untied) == (13, 28, 0.014787), f"{SPEC}; {AFTER_THE_RUNS}"
        effect = runs["A"].arithmetic_annual - runs["A_U"].arithmetic_annual
        share = float(returns[untied].to_numpy().sum()) * scale / effect
        assert round(share, 2) == 0.64, f"{SPEC}; {AFTER_THE_RUNS}"

    def test_the_stocks_outside_u_carry_0_35_of_a(self, runs) -> None:
        effect = runs["A"].arithmetic_annual - runs["A_U"].arithmetic_annual
        assert round(effect / runs["A"].arithmetic_annual, 2) == 0.35, AFTER_THE_RUNS

    def test_on_2011_08_04_the_stocks_outside_u_add_0_010702(self, sources, runs) -> None:
        """About half the universe effect, on one day, and WFR's short is the largest trade."""
        returns, positions = a_trades(sources, runs)
        outside = [s for s in returns.columns if s not in set(sources.universe("U"))]
        day = pd.Timestamp("2011-08-04")
        added = float(returns.loc[day, outside].sum()) * to_annual(runs["A"])
        assert round(added, 6) == 0.010702, f"{SPEC}; {AFTER_THE_RUNS}"
        effect = runs["A"].arithmetic_annual - runs["A_U"].arithmetic_annual
        assert round(added / effect, 2) == 0.46
        assert int((positions.loc[day, outside] != 0).sum()) == 8
        assert (positions.at[day, "WFR"], round(returns.at[day, "WFR"], 4)) == (-1.0, 0.1108)

    def test_the_five_largest_trades_outside_u_are_shorts_outside_cal(self, sources, runs) -> None:
        returns, positions = a_trades(sources, runs)
        outside = [s for s in returns.columns if s not in set(sources.universe("U"))]
        held = positions[outside].stack()
        trades = returns[outside].stack()[held != 0]
        top = trades.sort_values(ascending=False).head(5)
        assert [
            (str(day.date()), stock, positions.at[day, stock], round(float(value), 4))
            for (day, stock), value in top.items()
        ] == [
            ("2011-08-04", "WFR", -1.0, 0.1108),
            ("2011-10-28", "CVC", -1.0, 0.1093),
            ("2011-11-09", "LUK", -1.0, 0.0915),
            ("2012-01-26", "MWW", -1.0, 0.0915),
            ("2011-10-25", "AKS", -1.0, 0.0866),
        ], f"{SPEC}; {AFTER_THE_RUNS}"
        cal = set(sources.universe("CAL"))
        assert not any(stock in cal for _, stock in top.index)
        assert round(float(top.sum() / trades.sum()), 2) == 0.54

    def test_the_mean_trade_outside_u_and_inside_and_the_welch_t(self, sources, runs) -> None:
        """A t of 1.46 that treats every trade as independent, so chance is not ruled out.

        Welch's t compares two means without assuming the two spreads are
        equal: the difference of the means over the square root of each
        sample's variance over its count, summed.
        """
        returns, positions = a_trades(sources, runs)
        u = set(sources.universe("U"))
        held = positions.stack() != 0
        trades = returns.stack()[held]
        is_inside = np.array([stock in u for _, stock in trades.index])
        inside, outside = trades[is_inside], trades[~is_inside]
        assert (len(outside), round(float(outside.mean()), 6)) == (123, 0.007367), AFTER_THE_RUNS
        assert (len(inside), round(float(inside.mean()), 6)) == (949, PER_TRADE["A_U"])
        t = (outside.mean() - inside.mean()) / np.sqrt(
            outside.var(ddof=1) / len(outside) + inside.var(ddof=1) / len(inside)
        )
        assert round(float(t), 2) == 1.46, f"{SPEC}; {AFTER_THE_RUNS}"

    def test_at_r1s_own_mean_the_extra_trades_are_0_79_of_its_rise(self, runs) -> None:
        """At A_CAL's mean the share is 0.75, which ``TestTheCommittedRuns`` pins."""
        a_cal, b1 = runs["A_CAL"], runs["B1"]
        whole = b1.trades * pead_rerun.per_trade(b1) - a_cal.trades * pead_rerun.per_trade(a_cal)
        from_trades = (b1.trades - a_cal.trades) * pead_rerun.per_trade(b1)
        assert round(from_trades / whole, 2) == 0.79, f"{SPEC}; {AFTER_THE_RUNS}"

    def test_the_days_b1_and_b5_hold_more_than_30_positions(self, runs) -> None:
        past = {
            name: int((np.count_nonzero(runs[name].positions, axis=1) > DENOMINATOR).sum())
            for name in ("B1", "B5")
        }
        assert past == {"B1": 4, "B5": 10}, f"{SPEC}; {AFTER_THE_RUNS}"


def stand_in_prices(sources) -> pead_rerun.ArchivePrices:
    """Chan's own prices for PX in the archive's shape, so the archive's code runs in CI.

    The raw frames are copies, so a test can tell which frame a call was handed.
    """
    px = sources.universe("PX")
    opens, closes = sources.opens.loc[sources.window, px], sources.closes.loc[sources.window, px]
    return pead_rerun.ArchivePrices(
        entries={},
        adjusted_open=opens,
        adjusted_close=closes,
        raw_open=opens.copy(),
        raw_close=closes.copy(),
    )


class TestTheWiring:
    """How the runs, the guards, the reads and the report fit together, on committed files."""

    def test_the_report_prints_the_universes_who_left_and_why(self, sources, runs, capsys):
        pead_rerun.report(sources, runs, ["XYZ"], None)
        out = capsys.readouterr().out
        assert "stocks   ALL 497, CAL 488, PX 446, U 441" in out
        assert "Not in CAL, 9:" in out
        assert "    DD     dates" in out
        assert "    AGN    returns" in out
        assert "would refuse 1 of PX's 446 stocks: XYZ." in out
        assert "both 1540, Chan's only 311, R1's only 914, neither 158,275" in out
        assert "calendar, R5" in out

    def test_run_prints_why_the_archive_runs_did_not_run(self, monkeypatch, capsys):
        def absent(sources, directory=None):
            raise ArchiveUnavailable("no archive here")

        monkeypatch.setattr(pead_rerun, "read_archive", absent)
        runs = pead_rerun.run()
        assert sorted(runs) == sorted(COMMITTED)
        assert "C, D, E1 and E5 did not run: no archive here" in capsys.readouterr().out

    def test_run_reports_the_stocks_the_raw_guard_would_refuse(self, monkeypatch, capsys):
        monkeypatch.setattr(pead_rerun, "read_archive", lambda s, d=None: stand_in_prices(s))
        monkeypatch.setattr(pead_rerun, "archive_runs", lambda s, p: {})
        monkeypatch.setattr(pead_rerun, "raw_breaks", lambda p, w: ["XYZ", "ZZZ"])
        pead_rerun.run()
        assert "would refuse 2 of PX's 446 stocks: XYZ, ZZZ." in capsys.readouterr().out

    def test_the_archive_runs_guard_the_adjusted_open_and_close_once(self, sources, monkeypatch):
        prices = stand_in_prices(sources)
        seen = []
        monkeypatch.setattr(
            pead_rerun,
            "guard_archive",
            lambda entries, frames, window: seen.append([id(frame) for frame in frames]),
        )
        pead_rerun.archive_runs(sources, prices)
        assert seen == [[id(prices.adjusted_open), id(prices.adjusted_close)]]

    def test_the_committed_runs_call_the_scale_break_guard(self, sources, monkeypatch):
        def refuse(*args, **kwargs):
            raise RuntimeError("guarded")

        monkeypatch.setattr(pead_rerun, "refuse_scale_breaks", refuse)
        with pytest.raises(RuntimeError, match="guarded"):
            pead_rerun.committed_runs(sources)

    def test_a_table_in_another_order_is_refused(self, tmp_path):
        """Every universe is a selection from the flag file's columns, by position."""
        (tmp_path / "tickers.csv").write_bytes(serialize_table(list(reversed(read_table()))))
        with pytest.raises(VintageUnavailable, match="in its order"):
            pead_rerun.read_committed(record_dir=tmp_path)

    def test_a_px_stock_the_archive_holds_no_series_for_is_refused(self, sources, tmp_path):
        first = sources.table[0]
        table = [
            replace(row, archive_check="pass", archive_ticker="ZZZZ")
            if row is first
            else replace(row, archive_check="none")
            for row in sources.table
        ]
        with pytest.raises(ArchiveUnavailable, match="hold no series"):
            pead_rerun.read_archive(replace(sources, table=table), directory=tmp_path)

    def test_the_archive_read_rescales_the_open_by_adjusted_over_raw_close(
        self, sources, monkeypatch
    ):
        """A raw series at twice Chan's prices, adjusted back to his, gives his open back.

        The ratio's direction, the two closes and the raw open's scale are
        otherwise held only by the archive pins, which CI skips.
        """
        rows = {row.ticker: row for row in sources.table}
        px = sources.universe("PX")
        window = sources.window
        frames = {
            "open": sources.opens.loc[window, px] * 2,
            "close": sources.closes.loc[window, px] * 2,
            "adjusted_close": sources.closes.loc[window, px],
        }

        def read_cross_section(name, column, symbols, directory=None):
            frame = frames[column].rename(columns={s: rows[s].archive_ticker for s in px})
            return [SimpleNamespace(symbol=symbol) for symbol in symbols], frame[symbols]

        monkeypatch.setattr(pead_rerun, "read_cross_section", read_cross_section)
        prices = pead_rerun.read_archive(sources)
        chans = sources.opens.loc[window, px]
        pd.testing.assert_frame_equal(prices.adjusted_open, chans)
        pd.testing.assert_frame_equal(prices.raw_open, chans * 2)
        pd.testing.assert_frame_equal(prices.adjusted_close, sources.closes.loc[window, px])
        pd.testing.assert_frame_equal(prices.raw_close, sources.closes.loc[window, px] * 2)

    def test_each_archive_run_reads_its_registered_prices_flags_and_stocks(
        self, sources, monkeypatch
    ):
        """C, D, E1 and E5 each get the prices, the flags and the stocks issue 251 fixed.

        The archive pins are what otherwise catch a run wired to the wrong
        frame, and CI skips them. The raw frames here are twice the adjusted
        ones, so a run handed the wrong basis gives the wrong opens.
        """
        prices = stand_in_prices(sources)
        prices = replace(prices, raw_open=prices.raw_open * 2, raw_close=prices.raw_close * 2)
        handed = []

        def record(opens, closes, flags):
            handed.append((opens, closes, flags))
            return len(handed) - 1

        # The stand-in carries no archive entries, and the guard has its own test above.
        monkeypatch.setattr(pead_rerun, "guard_archive", lambda entries, frames, window: None)
        monkeypatch.setattr(pead_rerun, "pead", record)
        runs = pead_rerun.archive_runs(sources, prices)
        assert sorted(runs) == ["C", "D", "E1", "E5"]
        flags = {
            "C": sources.flags,
            "D": sources.flags,
            "E1": sources.calendar_flags("R1"),
            "E5": sources.calendar_flags("R5"),
        }
        bases = {
            "C": (prices.adjusted_open, prices.adjusted_close),
            "D": (prices.raw_open, prices.raw_close),
            "E1": (prices.adjusted_open, prices.adjusted_close),
            "E5": (prices.adjusted_open, prices.adjusted_close),
        }
        universes = {"C": "PX", "D": "PX", "E1": "U", "E5": "U"}
        for name, call in runs.items():
            opens, closes, got = handed[call]
            stocks = sources.universe(universes[name])
            assert list(opens.columns) == list(stocks), name
            pd.testing.assert_frame_equal(opens, bases[name][0][stocks], obj=f"{name} opens")
            pd.testing.assert_frame_equal(closes, bases[name][1][stocks], obj=f"{name} closes")
            pd.testing.assert_frame_equal(got, flags[name][stocks], obj=f"{name} flags")


class TestTheCalendarsAgainstChans:
    """Cell by cell over the 330 days and the 488 stocks of CAL, 161,040 cells."""

    def test_r1(self, sources) -> None:
        counts = pead_rerun.agreement(sources.calendar_flags("R1"), sources.flags)
        assert counts == Agreement(both=1540, chan_only=311, derived_only=914, neither=158275)

    def test_r5(self, sources) -> None:
        counts = pead_rerun.agreement(sources.calendar_flags("R5"), sources.flags)
        assert counts == Agreement(both=1694, chan_only=157, derived_only=1124, neither=158065)

    def test_r1_catches_the_two_apple_releases_chans_flags_miss(self, sources) -> None:
        """Chan's flags hold three of the five Apple releases whose next morning is in the window.

        Issue 20 measured it.
        """
        r1 = sources.calendar_flags("R1")["AAPL"]
        his = sources.flags["AAPL"]
        assert list(r1.index[r1 == 1].strftime("%Y-%m-%d")) == [
            "2011-01-19", "2011-04-21", "2011-07-20", "2011-10-19", "2012-01-25",
        ]  # fmt: skip
        assert list(r1.index[(r1 == 1) & (his == 0)].strftime("%Y-%m-%d")) == [
            "2011-01-19", "2011-10-19",
        ]  # fmt: skip

    def test_r5_carries_73_long_late_filings_back_to_a_quarters_first_day(self, sources) -> None:
        """Mostly a quarter's period end, so the flag lands weeks before the release.

        76 filings were accepted 7 or more days after their ``reportDate``.
        R5 puts 73 of them inside the window, 64 of those dated at a quarter's
        end, and Chan's file flags the stock on that day for 2 of them.
        """
        late, _ = long_late(sources)
        landed = [
            (release, r5_day(pd.Timestamp(release.accepted), release.report_date, sources.days))
            for release in late
        ]
        inside = [(release, day) for release, day in landed if day in sources.window]
        quarter_end = [r for r, _ in inside if pd.Timestamp(r.report_date).is_quarter_end]
        chans = [r for r, day in inside if sources.flags.at[day, r.ticker] != 0]
        assert (len(late), len(inside), len(quarter_end), len(chans)) == (76, 73, 64, 2)
        assert all(
            day == next_trading_day(pd.Timestamp(r.report_date), sources.days) for r, day in inside
        )


class TestTheArchiveRuns:
    """C, D, E1 and E5, which read the archive's prices. They skip without it."""

    @pytest.mark.parametrize("name", ("C", "D", "E1", "E5"))
    def test_the_figures(self, archive_runs, name) -> None:
        runs, _ = archive_runs
        assert figures(runs[name]) == FIGURES[name], f"{name}: {ARCHIVE_SPEC}"

    def test_the_attribution(self, archive_runs) -> None:
        runs, _ = archive_runs
        assert effects_of(runs) == EFFECTS, ARCHIVE_SPEC

    @pytest.mark.parametrize("name", ("C", "D", "E1", "E5"))
    def test_the_return_per_trade(self, archive_runs, name) -> None:
        runs, _ = archive_runs
        assert round(pead_rerun.per_trade(runs[name]), 6) == PER_TRADE[name], ARCHIVE_SPEC

    def test_the_interaction_without_the_basis_effect(self, archive_runs) -> None:
        """Not registered. E1 and A_U both read adjusted prices, so no basis separates them."""
        runs, _ = archive_runs
        by = {e.label: e for e in pead_rerun.attribution(runs)}
        left = [
            by["all of it, E1 against A_U"].arithmetic
            - by["calendar"].arithmetic
            - by["vendor"].arithmetic,
            by["all of it, E1 against A_U"].sharpe - by["calendar"].sharpe - by["vendor"].sharpe,
        ]
        assert (round(left[0], 6), round(left[1], 4)) == (-0.002865, 0.0102), ARCHIVE_SPEC

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


class TestTheArchiveOpens:
    """The series check reads closes only, so these read the opens. They skip without it."""

    def test_64_stock_days_over_56_stocks_open_more_than_2_percent_off_chans(
        self, sources, archive_runs
    ) -> None:
        _, prices = archive_runs
        off, _ = opens_off_chans(sources, prices)
        over = off > OPEN_TOLERANCE
        assert (int(over.to_numpy().sum()), int(over.any().sum())) == (64, 56), ARCHIVE_SPEC
        # Most fall on two days when many stocks disagree at once, which reads
        # more like two vendors' definitions of the open than like errors.
        by_day = over.sum(axis=1)
        assert (by_day["2011-10-27"], by_day["2011-09-12"]) == (30, 24), ARCHIVE_SPEC

    def test_gci_repeats_a_stale_open_after_each_holiday(self, sources, archive_runs) -> None:
        """Its raw open reads about 15.378 on five days, each the first after a market holiday."""
        _, prices = archive_runs
        stale = prices.raw_open["GCI"].round(3) == 15.378
        assert list(prices.raw_open.index[stale].strftime("%Y-%m-%d")) == [
            "2011-12-27", "2012-01-03", "2012-01-17", "2012-02-21", "2012-04-09",
        ]  # fmt: skip
        off, _ = opens_off_chans(sources, prices)
        assert (off["GCI"][stale] > OPEN_TOLERANCE).all()

    def test_chans_opens_in_their_place_move_e5_more_than_the_vendor_and_basis(
        self, sources, archive_runs
    ) -> None:
        """Not registered. One E5 trade, PNC on 2011-09-12, turns from long to short."""
        runs, prices = archive_runs
        fixed = runs_on_chans_opens(sources, prices)
        moves = {
            name: (
                round(fixed[name].arithmetic_annual - runs[name].arithmetic_annual, 6),
                round(fixed[name].sharpe - runs[name].sharpe, 4),
            )
            for name in fixed
        }
        assert moves == {
            "C": (0.000015, 0.0195),
            "E1": (-0.000539, -0.0098),
            "E5": (-0.004566, -0.1039),
        }, ARCHIVE_SPEC
        before = pd.DataFrame(runs["E5"].positions, index=runs["E5"].days)
        after = pd.DataFrame(fixed["E5"].positions, index=fixed["E5"].days)
        before.columns = after.columns = sources.universe("U")
        changed = (before != after).stack()
        assert list(changed[changed].index) == [(pd.Timestamp("2011-09-12"), "PNC")]
        assert (before.at["2011-09-12", "PNC"], after.at["2011-09-12", "PNC"]) == (1.0, -1.0)
        vendor_and_basis = EFFECTS["vendor"][0] + EFFECTS["basis"][0]
        assert abs(moves["E5"][0]) > abs(vendor_and_basis)

    def test_three_trades_make_each_of_e5s_and_e1s_moves(self, sources, archive_runs) -> None:
        """Measured for ``blog/pead-edgar-rerun-lessons.md`` after the runs, deciding nothing.

        Each trade's change in signed return, over 30 and times 252 over the
        330 days, is its share of the move in the arithmetic annual return.
        In E5, PNC on 2011-09-12 turns from long to short. MCO on 2012-02-08
        stays short and loses more from Chan's open, and TMK on 2011-10-27
        stays long and turns a small gain into a loss.
        In E1, CAM on 2011-10-27 turns from long to short and gains.
        """
        runs, prices = archive_runs
        fixed = runs_on_chans_opens(sources, prices)
        u = sources.universe("U")
        moved = {}
        for name, changed in trades_moved_by_chans_opens(sources, prices, runs, fixed).items():
            moved[name] = {
                (str(day.date()), stock): round(float(value), 6)
                for (day, stock), value in changed.items()
            }
            total = fixed[name].arithmetic_annual - runs[name].arithmetic_annual
            assert float(changed.sum()) == pytest.approx(total, rel=1e-9), ARCHIVE_SPEC
        assert moved == {
            "E1": {
                ("2011-10-27", "CAM"): 0.001766,
                ("2011-10-27", "TMK"): -0.000554,
                ("2012-02-08", "MCO"): -0.001751,
            },
            "E5": {
                ("2011-09-12", "PNC"): -0.002261,
                ("2011-10-27", "TMK"): -0.000554,
                ("2012-02-08", "MCO"): -0.001751,
            },
        }, ARCHIVE_SPEC
        e1_before = pd.DataFrame(runs["E1"].positions, index=runs["E1"].days, columns=u)
        e1_after = pd.DataFrame(fixed["E1"].positions, index=fixed["E1"].days, columns=u)
        changed = (e1_before != e1_after).stack()
        assert list(changed[changed].index) == [(pd.Timestamp("2011-10-27"), "CAM")]
        assert (e1_before.at["2011-10-27", "CAM"], e1_after.at["2011-10-27", "CAM"]) == (1.0, -1.0)
        # The PNC flip alone moves E5 more than the vendor and basis effects together.
        assert abs(moved["E5"][("2011-09-12", "PNC")]) > abs(
            EFFECTS["vendor"][0] + EFFECTS["basis"][0]
        )


POST = Path(__file__).parents[1] / "blog" / "pead-edgar-rerun-lessons.md"

_ONES = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
    "nineteen",
)  # fmt: skip
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")


def spelled(count: int) -> str:
    """A count below 100 in words, as the post writes it, such as forty-three."""
    if count < 20:
        return _ONES[count]
    tens, ones = divmod(count, 10)
    return _TENS[tens] + (f"-{_ONES[ones]}" if ones else "")


def thousands(count: int) -> str:
    """A count with its thousands comma, as the post's prose writes it."""
    return f"{count:,}"


def tex_count(count: int) -> str:
    """A count as the post's LaTeX tables write it, such as 1{,}072."""
    return f"{count:,}".replace(",", "{,}")


def tex_run(name: str) -> str:
    """A run's name as the post's LaTeX tables write it, such as A, an escaped _, then CAL."""
    return r"\_".join(rf"\text{{{part}}}" for part in name.split("_"))


def minus(x: float, places: int) -> str:
    """A figure at the post's precision, with the post's prose minus sign, U+2212."""
    return f"{x:.{places}f}".replace("-", "−")


def signed(x: float, places: int) -> str:
    """A change at the post's precision, signed + or −."""
    return ("+" if x > 0 else "−") + f"{abs(x):.{places}f}"


def clock(hour: int, minute: int = 0) -> str:
    """A time of day as the post writes it, such as 9:30 a.m., 4:00 p.m. or noon."""
    if (hour, minute) == (12, 0):
        return "noon"
    if hour < 12:
        return f"{hour}:{minute:02d} a.m."
    return f"{hour - 12}:{minute:02d} p.m."


def run_rows(runs, names) -> list[str]:
    """The second table's rows: return, Sharpe ratio and trades, as the post prints them."""
    return [
        rf"{tex_run(name)} & {runs[name].arithmetic_annual:.6f} & {runs[name].sharpe:.4f} & "
        f"{tex_count(runs[name].trades)}"
        for name in names
    ]


class TestWhatThePostQuotes:
    """One copy of each figure ``blog/pead-edgar-rerun-lessons.md`` quotes, read against the run.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built again from the runs and the committed files, at
    the precision the post prints it, and looked for in one copy: a fragment
    holding the number and the words around it that name one place in the
    post. A typo in that copy, or a re-pin that leaves the post behind, fails
    here. A fragment never matches inside a longer number, so a digit added
    beside a figure fails as well as a digit changed, and the four tables
    are rebuilt whole, the first from the registered runs and the others from
    the runs' figures. CI rebuilds only the second table's committed rows.
    Counts the post spells out, such as forty-three, are spelled from the
    count.

    What it reads splits by whether the figure needs the owner's archive.

    1. Everywhere, the six committed runs and the files they read: Chan's
       prices and flags, the ticker table and the Item 2.02 index under
       ``research/filings/earnings/``, IVV's schedules, read for the nine's
       own names that ``tests/test_earnings_filings.py`` lists, and the
       archive's committed manifest. That covers the rule's constants and the
       book's two figures, the universes, calendars and runs, the first
       table, the committed rows of the second, the identity, Lesson 1's
       checks, table, shares and day, the two figures whose only copy is the
       chart's alt text, Lesson 2's counts and times, and Lesson 3.
       ``chan.pead``, ``chan.pead_rerun`` and ``chan.earnings_filings``
       supply the constants, and the hours a time read late moves by come
       from the tz database's offsets for New York.
    2. Only where the archive is configured and ``QT_ARCHIVE_RUN=1`` is set,
       C, D, E1 and E5 and the archive's opens. That covers the second table
       whole, EP's 294 and 181 days, and every number in Lesson 4. CI skips
       this part.

    The post states most figures more than once, in a lesson, a table, the
    chart's alt text and caption, or the closing lists, and the other copies
    are not read, so a typo in one of them passes. Neither are the figures
    README lists as unpinned: Chan's words and pages, the readings of the
    submissions file, the facts read when the record was built, the readings
    in words and the counts of the post's own lists, the alt text's
    approximate readings of the curves, and the references.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        """The fragments not in ``text``, where a digit at either end must not run on."""
        return [
            fragment
            for fragment in fragments
            if not re.search(r"(?<!\d)" + re.escape(fragment) + r"(?!\d)", text)
        ]

    @pytest.fixture(scope="class")
    @classmethod
    def outside_cal(cls, sources) -> SimpleNamespace:
        """The nine outside CAL, split by the fund's schedule and by their EDGAR names.

        ``left`` are those whose own name meets no holding in IVV's schedule
        of 2012-03-31, and ``own`` those whose EDGAR name meets their own,
        both through ``name_keys`` as ``tests/test_earnings_filings.py`` pins
        them. The other four meet exactly one holding that day.
        """
        rows = {row.ticker: row for row in sources.table}
        tickers = [s for s in sources.universe("ALL") if not rows[s].calendar]
        assert sorted(tickers) == sorted(OWN_NAMES)
        holdings = ivv_names(earnings_filings.IVV_REPORT_DATE)
        held = {s: meets(OWN_NAMES[s], holdings) for s in tickers}
        assert set(held.values()) == {0, 1}, "the rest meet exactly one holding"
        return SimpleNamespace(
            all=tickers,
            left=[s for s in tickers if held[s] == 0],
            own=[s for s in tickers if name_keys(rows[s].edgar_name) & name_keys(OWN_NAMES[s])],
        )

    @pytest.fixture(scope="class")
    @classmethod
    def lesson_1(cls, sources, runs, outside_cal) -> SimpleNamespace:
        """A's trades split by why a stock is outside U, as the classes above split them."""
        returns, positions = a_trades(sources, runs)
        scale = to_annual(runs["A"])
        rows = {row.ticker: row for row in sources.table}
        u, cal = set(sources.universe("U")), set(sources.universe("CAL"))
        no_series = cal_without_a_series(sources)
        groups = {
            "U": [s for s in returns.columns if s in u],
            "outside CAL": [s for s in returns.columns if s not in cal],
            "reused": [s for s in no_series if rows[s].archive_check == "returns"],
            "unpriced": [s for s in no_series if rows[s].archive_check in ("missing", "none")],
            "outside U": [s for s in returns.columns if s not in u],
            "ALL": list(returns.columns),
            "left the fund": outside_cal.left,
        }
        groups["untied"] = groups["outside CAL"] + groups["reused"]

        def measured(stocks):
            return (
                len(stocks),
                int((positions[stocks] != 0).to_numpy().sum()),
                float(returns[stocks].to_numpy().sum()) * scale,
            )

        held = positions.stack() != 0
        trades = returns.stack()[held]
        outside = set(groups["outside U"])
        is_outside = np.array([stock in outside for _, stock in trades.index])
        inside, out = trades[~is_outside], trades[is_outside]
        welch = (out.mean() - inside.mean()) / np.sqrt(
            out.var(ddof=1) / len(out) + inside.var(ddof=1) / len(inside)
        )
        spell = longest_spell(cumulative_return(runs["A"]))
        return SimpleNamespace(
            returns=returns,
            positions=positions,
            scale=scale,
            groups=groups,
            by={name: measured(stocks) for name, stocks in groups.items()},
            inside=inside,
            outside=out,
            welch=float(welch),
            largest=out.sort_values(ascending=False).head(5),
            high=runs["A"].days[spell.high],
        )

    def test_the_rule_and_the_book(self, sources, text) -> None:
        window = sources.window
        assert ENTRY == 0.5, "half its moving deviation"
        assert (pead_rerun.SESSION_OPEN.hour, pead_rerun.SESSION_OPEN.minute) == (9, 30)
        assert (pead_rerun.SESSION_CLOSE.hour, pead_rerun.SESSION_CLOSE.minute) == (16, 0)
        fragments = [
            "after the previous close and before the open is bought at the open when its gap "
            "is at least half its moving deviation",
            f"the standard deviation of its gaps over the last {LOOKBACK} days",
            f"divides by a fixed {DENOMINATOR}, whatever the day holds",
            f"an annual percentage rate, or APR, of {BOOK_APR_PERCENT} percent and a Sharpe "
            f"ratio of {BOOK_SHARPE} on the S&P 500 from {window[0]:%B %Y} to "
            f"{window[-1]:%B %Y}",
            f"His APR is the arithmetic annual return, {TRADING_DAYS} times the average daily "
            "return.",
            f"times the square root of {TRADING_DAYS}, so it measures return per unit of risk",
            f"an announcement between the {clock(16)} close and the {clock(9, 30)} open Eastern",
        ]
        assert self.missing(text, fragments) == []

    def test_what_the_rerun_found(self, sources, runs, text) -> None:
        sizes = {name: len(sources.universe(name)) for name in pead_rerun.UNIVERSES}
        fragments = [
            f"drop {sizes['ALL'] - sizes['U']} stocks, and they carry a third of the return.**",
            f"Chan’s arithmetic annual return of {runs['A'].arithmetic_annual:.6f}, the "
            f"{BOOK_APR_PERCENT} percent he prints, falls to {runs['A_U'].arithmetic_annual:.6f} "
            f"on the {sizes['U']} of his {sizes['ALL']} stocks that pass both.",
            f"On the {sizes['CAL']} stocks whose filer passes the check against EDGAR, and on "
            f"Chan’s prices, it lifts the return from {runs['A_CAL'].arithmetic_annual:.6f} on "
            f"Chan’s flags to {runs['B1'].arithmetic_annual:.6f}",
            f"The rerun wrote down its {spelled(len(pead_rerun.SPECS))} runs",
        ]
        assert self.missing(text, fragments) == []

    def test_the_universes_calendars_and_vendor(self, sources, text) -> None:
        sizes = {name: len(sources.universe(name)) for name in pead_rerun.UNIVERSES}
        rows = {row.ticker: row for row in sources.table}
        entries = {e.symbol: e for e in read_archive_manifest() if e.cross_section == "sp500"}
        (downloaded,) = {
            entries[rows[s].archive_ticker].download_date for s in sources.universe("PX")
        }
        edgar = sorted({s.flags for s in pead_rerun.SPECS} - {"Chan"})
        archive = pead_rerun.ARCHIVE_RUNS
        assert [s.name for s in pead_rerun.SPECS if s.name not in archive] == list(COMMITTED)
        fragments = [
            f"That gives {spelled(len(pead_rerun.UNIVERSES))} universes, the sets of stocks",
            f"**ALL**, Chan’s {sizes['ALL']} stocks.",
            f"**CAL**, the {sizes['CAL']} whose filer passed its check.",
            f"**PX**, the {sizes['PX']} whose price series passed its check.",
            f"**U**, the {sizes['U']} that pass both.",
            f"The rerun builds {spelled(len(edgar))} calendars from EDGAR, {' and '.join(edgar)}.",
            f"A filing accepted before {clock(9, 30)} on a trading day flags that day. One "
            f"accepted at {clock(16)} or later",
            f"sit in a private archive, downloaded on {downloaded}.",
            f"{spelled(len(pead_rerun.SPECS)).capitalize()} runs cover the four differences.",
            f"**The {spelled(len(archive))} on Alpha Vantage prices, {', '.join(archive[:-1])} "
            f"and {archive[-1]}, need the private archive, so a reader cannot rerun them.** The "
            f"other {spelled(len(pead_rerun.SPECS) - len(archive))} read only files in the "
            "repository.",
        ]
        assert self.missing(text, fragments) == []

    def test_the_first_table(self, text) -> None:
        """What each run reads, rebuilt from the registered specs."""
        prices = {"Chan": "Chan's", "adjusted": "archive, adjusted", "raw": "archive, raw"}
        flags = {"Chan": "Chan's", "R1": "R1", "R5": "R5"}
        rows = [
            rf"{tex_run(s.name)} & \text{{{s.universe}}} & \text{{{prices[s.prices]}}} & "
            rf"\text{{{flags[s.flags]}}}"
            for s in pead_rerun.SPECS
        ]
        table = (
            r"\small\begin{array}{l|l|l|l}" + "\n"
            r"\text{Run} & \text{Stocks} & \text{Prices} & \text{Flags} \\ \hline" + "\n"
            + " \\\\\n".join(rows)
            + "\n\\end{array}"
        )  # fmt: skip
        assert self.missing(text, [table]) == []

    def test_the_second_table_s_committed_rows(self, runs, text) -> None:
        """The six rows CI can derive. The archive part below rebuilds the table whole."""
        assert self.missing(text, [row + r" \\" for row in run_rows(runs, COMMITTED)]) == []

    def test_the_identity(self, runs, text) -> None:
        days = len(runs["A"].days)
        fragments = [
            f"the trades it takes and their mean return, over the {days} days of the window.",
            rf"\times {TRADING_DAYS}}}{{{DENOMINATOR} \times {days}}}",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1_s_checks(self, sources, outside_cal, text) -> None:
        rows = {row.ticker: row for row in sources.table}
        routes = Counter((row.archive_source, row.archive_check) for row in sources.table)
        passing = [int(row.days_over) for row in sources.table if row.priced]
        reused = [int(row.days_over) for row in sources.table if row.archive_check == "returns"]
        ivv = earnings_filings.FILINGS_DIR / "ivv"
        report_date = earnings_filings.IVV_REPORT_DATE
        schedule = pd.read_csv(ivv / f"{report_date}.csv", dtype=str, keep_default_na=False)
        (ace,) = [
            holding_price(row["value"], row["shares"])
            for _, row in schedule.iterrows()
            if row["name"] == "ACE Ltd."
        ]
        ace_gap = ace / sources.closes.at[pd.Timestamp(earnings_filings.PRICE_DAY), "CB"] - 1
        earlier = sorted(p.stem for p in ivv.glob("2*.csv") if p.stem < report_date)
        no_series = cal_without_a_series(sources)
        entries = {e.symbol: e for e in read_archive_manifest() if e.cross_section == "sp500"}
        first = {
            s: entries[rows[s].archive_ticker].first_date
            for s in no_series
            if rows[s].archive_check == "missing"
        }
        last_day = str(sources.window[-1].date())
        after = [s for s, day in first.items() if day > last_day]
        (inside,) = [s for s, day in first.items() if day <= last_day]
        assert inside == "EP"
        lacks = int((sources.window < first[inside]).sum())
        unproposed = [s for s in no_series if rows[s].archive_check == "none"]
        nine, left, own = len(outside_cal.all), outside_cal.left, outside_cal.own
        five = spelled(len(left))
        # NYX carries its own CIK under a name that misses the schedule's only by
        # the legal form, so the keys leave it out of ``own`` and the post counts it
        # beside LUK, a reading README names among what is not pinned.
        assert "NYX" not in own and [s for s in own if s not in left] == ["LUK"]
        four = len(reused)
        fragments = [
            f"It was filing on {earnings_filings.PRICE_DAY}.",
            f"one holding in the iShares S&P 500 fund’s schedule of {report_date}.",
            f"That holding’s price is within {round(100 * earnings_filings.PRICE_TOLERANCE)} "
            "percent of Chan’s close that day.",
            f"It released earnings under Item {earnings_filings.ITEM} in the window.",
            f"Every series that holds the same company’s prices differs from Chan’s on at most "
            f"{max(passing)} days. The "
            f"{spelled(four)} reused tickers that fail, CB among them, differ on "
            f"{min(reused)} to {max(reused)}. Under Chan’s own tickers, "
            f"{routes[('same', 'pass')]} series pass. Searching the archive by returns rather "
            f"than by ticker finds {routes[('search', 'pass')]} more, companies stored under a "
            f"later ticker, which makes PX’s {len(sources.universe('PX'))}.",
            f"Its holding sits {100 * ace_gap:.2f} percent above the old Chubb’s close",
            f"{spelled(nine).capitalize()} stocks fail the filer check",
            f"{five.capitalize()} are missing from the fund’s schedule of {report_date}",
            f"All {five} were in its schedule of {earlier[-2]} and gone from that of "
            f"{earlier[-1]}, so they left the index inside the window. "
            f"{spelled(len([s for s in left if s not in own])).capitalize()} of those {five} "
            "also carry another company’s filer.",
            f"**{spelled(nine + four).capitalize()} cannot be confirmed as the right company.** "
            f"They are the {spelled(nine)} that fail the filer check",
            f"and the {spelled(four)} reused tickers whose series holds another company’s "
            f"history. {spelled(len(own) + 1).capitalize()} of the {spelled(nine)} carry their "
            f"own company’s filer: {spelled(len([s for s in own if s in left]))} of the {five} "
            "that left the index, NYSE Euronext and Leucadia.",
            f"**{spelled(len(no_series) - four).capitalize()} lack the prices to check.**",
            f"{spelled(len(unproposed)).capitalize()} have no series there at all. For "
            f"{len(after)} the series under that ticker starts after the window ends on "
            f"{last_day}, as ALTR’s starts on {first['ALTR']}, DELL’s on {first['DELL']} and "
            f"DOW’s on {first['DOW']}.",
            f"starts on {first['EP']} and lacks the window’s first {lacks} days.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1_s_table(self, lesson_1, text) -> None:
        """Rebuilt whole from A's trades, each cell at the precision its column prints."""
        by = lesson_1.by
        cells = [
            ("U, both pass", by["U"]),
            ("Filer check fails", by["outside CAL"]),
            ("Reused ticker", by["reused"]),
            ("No full prices", by["unpriced"]),
            ("A, all", by["ALL"]),
        ]
        rows = [
            rf"\text{{{name}}} & {count} & {tex_count(trades)} & {added:.6f}"
            for name, (count, trades, added) in cells
        ]
        table = (
            r"\small\begin{array}{l|r|r|r}" + "\n"
            r"\text{Stocks} & \text{Count} & \text{Trades} & \text{Adds to A} \\ \hline" + "\n"
            + " \\\\\n".join(rows[:-1])
            + " \\\\ \\hline\n"
            + rows[-1]
            + "\n\\end{array}"
        )  # fmt: skip
        assert self.missing(text, [table]) == []

    def test_lesson_1_s_shares_and_the_day(self, sources, runs, lesson_1, text) -> None:
        by, returns, positions = lesson_1.by, lesson_1.returns, lesson_1.positions
        a = runs["A"]
        effect = a.arithmetic_annual - runs["A_U"].arithmetic_annual
        nine = a.arithmetic_annual - runs["A_CAL"].arithmetic_annual
        assert by["outside U"][2] == pytest.approx(effect, rel=1e-12)
        assert by["outside CAL"][2] == pytest.approx(nine, rel=1e-12), "exactly A against A_CAL"
        n_out, t_out, _ = by["outside U"]
        n_untied, t_untied, untied = by["untied"]
        day = lesson_1.high
        outside = lesson_1.groups["outside U"]
        on_the_day = float(returns.loc[day, outside].sum()) * lesson_1.scale
        assert 0.4 < on_the_day / effect < 0.5, "close to half"
        largest = lesson_1.largest
        top_day, top_stock = largest.index[0]
        assert top_day == day, "the largest trade falls on the day"
        cal = set(sources.universe("CAL"))
        assert all(positions.at[d, s] == -1.0 and s not in cal for d, s in largest.index)
        left = lesson_1.groups["left the fund"]
        closes = sources.closes.loc[sources.window, left]
        fell = [1 - c.dropna().iloc[-1] / c.dropna().iloc[0] for _, c in closes.items()]
        cal_effects = effects_of(runs)
        top = float(largest.iloc[0])
        other = [s for s in lesson_1.groups["outside CAL"] if s not in left]

        def mean_trade(stocks: list[str]) -> float:
            return float(returns[stocks].stack()[positions[stocks].stack() != 0].mean())

        assert mean_trade(left) <= mean_trade(other), "no more per trade"
        fragments = [
            f"The {n_out} stocks outside U take {t_out} of A’s {thousands(a.trades)} trades and "
            f"add {effect:.6f}, which is {effect / a.arithmetic_annual:.2f} of A’s return",
            f"The {n_untied} the checks cannot confirm take {t_untied} trades and add "
            f"{untied:.6f}, which is {untied / effect:.2f} of the {effect:.6f}",
            f"The nine that fail the filer check add {nine:.6f} on their own, which is exactly "
            "A against A_CAL.",
            f"Those are the {by['reused'][0] + by['unpriced'][0]} stocks that pass the filer "
            "check and have no checked series.",
            f"On {day.date()}, the day A’s cumulative return reaches the high its longest "
            f"drawdown starts from, the stocks outside U add {on_the_day:.6f}, close to half of "
            f"their {effect:.6f}, through {int((positions.loc[day, outside] != 0).sum())} trades.",
            f"Chan’s {top_stock}, a single trade that returned {top:.4f}, or {100 * top:.2f} "
            "percent,",
            f"The {spelled(len(largest))} largest trades outside U are all shorts, all in the "
            f"{spelled(by['outside CAL'][0])} stocks that fail the filer check, and they carry "
            f"{float(largest.sum() / lesson_1.outside.sum()):.2f} of the {effect:.6f} the stocks "
            "outside U add.",
            f"Per trade, the stocks outside U earn {lesson_1.outside.mean():.6f} on average "
            f"against {lesson_1.inside.mean():.6f} inside.",
            f"is {lesson_1.welch:.2f} (Welch, 1947).",
            f"Chan’s closes for them fell {round(100 * min(fell))} to "
            f"{round(100 * max(fell))} percent over it. Per trade, though, they earn no more "
            f"than the other {spelled(len(other))} of the nine.",
            f"by {-cal_effects['universe'][0]:.6f} against R1’s {cal_effects['calendar'][0]:.6f}",
            f"Dropping the {n_out} stocks moves it by {signed(cal_effects['universe'][1], 4)}, "
            f"and R1 moves it by {signed(cal_effects['calendar'][1], 4)}.",
        ]
        assert self.missing(text, fragments) == []

    def test_the_chart_s_alt_text(self, runs, lesson_1, text) -> None:
        """The two figures whose only copy is the alt text: the brass line's end and the points.

        Its readings of the curves along the way are approximate and not read.
        """
        no_series = lesson_1.by["reused"][2] + lesson_1.by["unpriced"][2]
        point = {
            name: f"{thousands(runs[name].trades)} and "
            f"{100 * pead_rerun.per_trade(runs[name]):.3f} percent"
            for name in COMMITTED
        }
        rest = [f"{name} at {point[name]}" for name in COMMITTED[1:]]
        fragments = [
            f"climbs mostly in 2012 to end at {no_series:.6f}",
            f"A sits at {point['A'].replace(' and ', ' trades and about ')}, "
            + ", ".join(rest[:-1])
            + f", and {rest[-1]}.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2(self, sources, text) -> None:
        """The index's counts and times, and Apple's six read 4 or 5 hours late.

        A late reading adds the hours Eastern sits behind UTC once more, so
        those hours come from the tz database's offsets for New York.
        """
        eastern = "America/New_York"

        def behind(day: str) -> int:
            offset = pd.Timestamp(day).tz_localize(eastern).utcoffset().total_seconds()
            return -int(offset) // 3600

        summer, winter = behind("2011-07-01"), behind("2011-01-03")
        releases = sources.releases
        times = sorted(r.accepted[11:] for r in releases)
        before = sum(t < "09:30:00" for t in times)
        session = sum("09:30:00" <= t < "16:00:00" for t in times)
        window = sources.window
        apple = [
            pd.Timestamp(r.accepted)
            for r in releases
            if r.ticker == "AAPL"
            and window[0] <= pd.Timestamp(r.accepted).normalize() <= window[-1]
        ]
        (about,) = {at.round("30min").time() for at in apple}
        dst = [at for at in apple if at.tz_localize(eastern).dst()]
        standard = [at for at in apple if not at.tz_localize(eastern).dst()]
        assert {at.month for at in standard} == {1}, "the two in January"

        def late(hours: int) -> str:
            shifted = pd.Timestamp.combine(pd.Timestamp("2011-01-03").date(), about)
            shifted += pd.Timedelta(hours=hours)
            return clock(shifted.hour, shifted.minute)

        hour, minute, second = (int(part) for part in times[0].split(":"))
        fragments = [
            f"runs {summer} hours ahead of Eastern time under daylight saving time and {winter} "
            "hours ahead under standard time",
            f"Each of Apple’s {spelled(len(apple))} releases in the window was accepted at about "
            f"{clock(about.hour, about.minute)} Eastern.",
            f"the {spelled(len(dst))} filed under daylight saving time land at about "
            f"{late(summer)}, and the {spelled(len(standard))} in January, on "
            f"{standard[0].date()} and {standard[1].date()}, at about {late(winter)} All are "
            "still after the close",
            "No filing in the rerun’s list was accepted earlier than "
            f"{hour}:{minute:02d}:{second:02d} a.m. Eastern on any day.",
            f"The list holds {thousands(len(releases))} filings, and {thousands(before)} of them "
            "were accepted before the open.",
            f"from {clock(16 - winter)} onward in winter, or from {clock(16 - summer)} onward in "
            f"summer, moves past the {clock(16)} close",
            f"The list holds {session} accepted during the session.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_3(self, sources, runs, text) -> None:
        names = ("A_CAL", "B1", "B5")
        r1 = sources.calendar_flags("R1")["AAPL"]
        missed = int(((r1 == 1) & (sources.flags["AAPL"] == 0)).sum())
        flags = {s.name: ("Chan's" if s.flags == "Chan" else s.flags) for s in pead_rerun.SPECS}
        per = {name: pead_rerun.per_trade(runs[name]) for name in names}

        def row(label: str, cells) -> str:
            return rf"\text{{{label}}} & " + " & ".join(cells)

        table = (
            r"\small\begin{array}{l|r|r|r}" + "\n"
            + " & " + " & ".join(tex_run(n) for n in names) + r" \\ \hline" + "\n"
            + " \\\\\n".join([
                row("Flags", [rf"\text{{{flags[n]}}}" for n in names]),
                row("Trades", [tex_count(runs[n].trades) for n in names]),
                row("Mean per trade", [f"{per[n]:.6f}" for n in names]),
                row("Annual return", [f"{runs[n].arithmetic_annual:.6f}" for n in names]),
                row("Sharpe ratio", [f"{runs[n].sharpe:.4f}" for n in names]),
            ])
            + "\n\\end{array}"
        )  # fmt: skip
        a_cal, b1, b5 = (runs[n] for n in names)
        whole = b1.trades * per["B1"] - a_cal.trades * per["A_CAL"]
        at_chans = (b1.trades - a_cal.trades) * per["A_CAL"] / whole
        at_r1s = (b1.trades - a_cal.trades) * per["B1"] / whole
        gain = b1.arithmetic_annual - a_cal.arithmetic_annual
        past = {
            n: int((np.count_nonzero(runs[n].positions, axis=1) > DENOMINATOR).sum())
            for n in ("B1", "B5")
        }
        assert per["B5"] < per["A_CAL"] and b5.sharpe <= a_cal.sharpe, "gains only by trading more"
        fragments = [
            f"including {spelled(missed)} of Apple’s releases that his file misses.",
            table,
            f"R1 lifts the return by {gain:.6f} in two ways. It takes {thousands(b1.trades)} "
            f"trades against {thousands(a_cal.trades)}, and its mean per trade is "
            f"{per['B1']:.6f} against {per['A_CAL']:.6f}, about "
            f"{round(100 * (per['B1'] / per['A_CAL'] - 1))} percent higher.",
            f"If each extra trade earned the {per['A_CAL']:.6f} of Chan’s flags, the extra trades "
            f"would account for {at_chans:.2f} of the gain",
            f"At R1’s own {per['B1']:.6f}, they account for {at_r1s:.2f}",
            f"The Sharpe ratio rises from {a_cal.sharpe:.4f} to {b1.sharpe:.4f}",
            f"On its busiest day B1 holds {b1.most_held} positions, and on {past['B1']} days it "
            f"holds more than {DENOMINATOR}.",
            f"It takes {thousands(b5.trades)} trades at a mean of {per['B5']:.6f}, below the "
            f"{per['A_CAL']:.6f} of Chan’s flags, and its Sharpe ratio, {b5.sharpe:.4f} against "
            f"A_CAL’s {a_cal.sharpe:.4f}, is no higher. It holds more than {DENOMINATOR} "
            f"positions on {past['B5']} days, and {b5.most_held} on its busiest.",
        ]
        assert self.missing(text, fragments) == []

    def test_the_second_table_whole(self, archive_runs, text) -> None:
        """Every run's row, so a row or a digit added fails too. Skips without the archive."""
        runs, _ = archive_runs
        table = (
            r"\small\begin{array}{l|r|r|r}" + "\n"
            r"\text{Run} & \text{Annual return} & \text{Sharpe ratio} & \text{Trades} \\ \hline"
            + "\n"
            + " \\\\\n".join(run_rows(runs, [s.name for s in pead_rerun.SPECS]))
            + "\n\\end{array}"
        )  # fmt: skip
        assert self.missing(text, [table]) == []

    def test_ep_s_series(self, archive_runs, sources, text) -> None:
        """Read as ``tests/test_earnings_filings.py`` reads it. Skips without the archive."""
        from chan.archive import read_cross_section

        _, archive = read_cross_section("sp500", symbols=["EP"])
        chan = sources.closes["EP"].loc[sources.window]
        theirs = archive["EP"].reindex(sources.window)
        difference = (chan.pct_change() - theirs.pct_change()).abs()
        held = int(difference.notna().sum())
        over = int((difference > earnings_filings.RETURN_TOLERANCE).sum())
        fragment = (
            f"On the {held} days both hold a daily return, its returns differ from those of "
            f"Chan’s closes on {over}."
        )
        assert self.missing(text, [fragment]) == []

    def test_lesson_4(self, archive_runs, sources, text) -> None:
        """Every number in the lesson reads the archive. Skips without it."""
        runs, prices = archive_runs
        by = effects_of(runs)
        off, _ = opens_off_chans(sources, prices)
        over = off > OPEN_TOLERANCE
        n_off, n_stocks = int(over.to_numpy().sum()), int(over.any().sum())
        px = len(sources.universe("PX"))
        assert n_stocks == len(sources.universe("ALL")) - len(sources.universe("U"))
        by_day = over.sum(axis=1).sort_values(ascending=False)
        (first_day, first), (second_day, second) = list(by_day.head(2).items())
        fixed = runs_on_chans_opens(sources, prices)
        moves = {
            name: (
                fixed[name].arithmetic_annual - runs[name].arithmetic_annual,
                fixed[name].sharpe - runs[name].sharpe,
            )
            for name in fixed
        }
        trade = {
            name: {stock: (str(day.date()), float(value)) for (day, stock), value in s.items()}
            for name, s in trades_moved_by_chans_opens(sources, prices, runs, fixed).items()
        }
        e5, e1 = trade["E5"], trade["E1"]
        assert set(e5) == {"PNC", "MCO", "TMK"} and set(e1) == {"CAM", "MCO", "TMK"}
        interaction = by["interaction, what E1 − A_U leaves"][0]
        raw = {e.label: e.arithmetic for e in pead_rerun.attribution(runs)}
        without_basis = raw["all of it, E1 against A_U"] - raw["calendar"] - raw["vendor"]
        assert without_basis < 0, "less than the calendar and vendor effects together"
        e1_a, e5_a = by["E1 against A"], by["E5 against A"]
        assert interaction < 0, "less than the three effects together"
        assert e1_a[0] < 0 and e5_a[0] < 0 and e1_a[1] > 0 > e5_a[1], "lower, above and below"
        fragments = [
            f"On PX’s {px} stocks with Chan’s flags, switching to Alpha Vantage’s adjusted "
            f"prices moves the arithmetic annual return by {signed(by['vendor'][0], 6)}, run C "
            "against A_PX. Switching from adjusted to raw prices moves it by "
            f"{signed(by['basis'][0], 6)} more, run D against C.",
            f"{runs['D'].trades} in D against {runs['C'].trades} in C.",
            f"{n_off} of the archive’s opens for PX’s stocks lie more than "
            f"{round(100 * OPEN_TOLERANCE)} percent from Chan’s, across {n_stocks} of those {px} "
            f"stocks. That {n_stocks} only happens to equal",
            f"Of the {n_off}, {first} fall on {first_day.date()} and {second} on "
            f"{second_day.date()}.",
            f"than like {first + second} separate errors.",
            f"Putting Chan’s open in place of each of the {n_off} moves C by "
            f"{signed(moves['C'][0], 6)} and E1 by {signed(moves['E1'][0], 6)}. It moves E5 by "
            f"{signed(moves['E5'][0], 6)} in return and {signed(moves['E5'][1], 4)} in Sharpe "
            f"ratio, through {spelled(len(e5))} trades.",
            f"**PNC Financial Services on {e5['PNC'][0]}** turns from long to short, worth "
            f"{minus(e5['PNC'][1], 6)}.",
            f"**Moody’s, MCO, on {e5['MCO'][0]}** stays short and loses more from Chan’s open, "
            f"worth {minus(e5['MCO'][1], 6)}.",
            f"**Torchmark, TMK, on {e5['TMK'][0]}** stays long and turns a small gain into a "
            f"loss, worth {minus(e5['TMK'][1], 6)}.",
            f"Cameron International, CAM, on {e1['CAM'][0]}, which turns from long to short and "
            f"gains {e1['CAM'][1]:.6f}.",
            f"give E1 an arithmetic annual return of {runs['E1'].arithmetic_annual:.6f} and a "
            f"Sharpe ratio of {runs['E1'].sharpe:.4f}, above A_U’s "
            f"{runs['A_U'].arithmetic_annual:.6f} and {runs['A_U'].sharpe:.4f}.",
            f"come out lower in return, E1 by {-e1_a[0]:.6f} and E5 by {-e5_a[0]:.6f}. In Sharpe "
            f"ratio, E1 sits {e1_a[1]:.4f} above A and E5 {-e5_a[1]:.4f} below",
            f"E1 against A_U is {signed(by['all of it, E1 against A_U'][0], 6)}, which is "
            f"{-interaction:.6f} less than the calendar, vendor and basis effects together.",
            f"so without the basis effect the remainder is {-without_basis:.6f}.",
        ]
        assert self.missing(text, fragments) == []
