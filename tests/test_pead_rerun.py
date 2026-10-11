"""The pins for Example 7.2 rerun on EDGAR's calendar and the archive's prices, issue 251.

This file is the authority for the rerun's figures that any prose surface
quotes, Entry 46 of ``docs/replication-log.md`` among them: each run's
figures, the attribution, each calendar's agreement with Chan's flags, and the
checks run beside them on late filings and on the archive's opens.
``tests/test_earnings_filings.py`` is the authority for the counts about the
ticker table and the index that the universes are cut from, Entry 46's rows
15 and 16 and the 48 renamed companies among them.

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
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from chan import pead_rerun
from chan.archive import ArchiveUnavailable
from chan.earnings_filings import Release, read_table, serialize_table
from chan.pead import DENOMINATOR, TRADING_DAYS, Drift, pead
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


def runs_on_chans_opens(sources, prices) -> dict[str, Drift]:
    """C, E1 and E5 with every open off by more than the tolerance replaced by Chan's."""
    off, scale = opens_off_chans(sources, prices)
    stocks = sources.universe("PX")
    chans = sources.opens.loc[sources.window, stocks] / scale
    opens = prices.adjusted_open.copy()
    opens[stocks] = prices.adjusted_open[stocks].where(off <= OPEN_TOLERANCE, chans)
    runs = {}
    for name, universe, flags in (
        ("C", "PX", sources.flags),
        ("E1", "U", sources.calendar_flags("R1")),
        ("E5", "U", sources.calendar_flags("R5")),
    ):
        chosen = sources.universe(universe)
        runs[name] = pead(opens[chosen], prices.adjusted_close[chosen], flags[chosen])
    return runs


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
