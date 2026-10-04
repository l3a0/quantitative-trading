"""The pins for buy on gap and its mirror, *Algorithmic Trading*'s Example 4.1.

This file is the single authority for every number any prose surface quotes
about Example 4.1. ``docs/replication-log.md`` Entry 18 carries the verdicts
and points here row by row.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** ``inputdataohlcdaily_stocks_20120424/``, the 497 stocks lifted
  from Chan's ``inputDataOHLCDaily_stocks_20120424.mat``, read for the Open,
  High, Low and Close columns. Its identity is the row of ``LIFTED_SOURCES``
  in ``tests/support/committed_vintages.py``, which ``TestTheVintages`` holds
  the members to. The file is the S&P 500 as Chan held it on 2012-04-24, so
  every figure is a figure about survivors.
- **Specification.** ``bog.m`` at the mirror commit :mod:`chan.buy_on_gap`
  names, over all 1,500 days. The spread is book two's ``smartMovingStd`` over
  90 rows of close-to-close returns and the average is ``smartMovingAvg`` over
  20 rows of closes, both moved one row later. Entry is one spread beyond the
  previous low, at most ten positions a day, and each day's sum is divided by
  10. The APR is compounded over 252 days a year and the Sharpe ratio uses
  MATLAB's n − 1 ``std``. The mirror is the rule issue 295 declared, which the
  module docstring states.

The buy side's two figures are pinned at the precision that is real, six
decimals for a return and four for the Sharpe ratio, and again at the one
decimal ``bog.m``'s closing comment and location 1974 print. ``bog.m``'s
``fprintf`` would print more, but nothing records what it printed, so the
comment is the published figure. The mirror's are pinned against location
1993's whole percent and two decimals.

``TestTheHelperMovesBothFigures`` holds the mistake a port is most likely to
make. The first edition's ``smartstd`` carries the same MATLAB name, and with
it neither printed figure lands.

Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a
rule he chose. It first ran here on 2026-10-04.
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from chan import buy_on_gap, matlab_helpers
from chan.buy_on_gap import (
    AVERAGE_LOOKBACK,
    BOOK_APR_PERCENT,
    BOOK_SHARPE,
    ENTRY_ZSCORE,
    MIRROR_BOOK_APR_PERCENT,
    MIRROR_BOOK_SHARPE,
    PRICE_FILE,
    SCRIPT_COMMENT,
    SCRIPT_PRICE_FILE,
    SCRIPT_WINDOW,
    SPREAD_LOOKBACK,
    TOP_N,
    TRADING_DAYS,
    Side,
    daily_returns,
    drop_qualifiers,
    entry_spread,
    gap_down_positions,
    gap_up_positions,
    jump_qualifiers,
    main,
    read_sources,
    run,
    trailing_average,
)
from chan.matlab_helpers import calculate_returns, smartstd_first_edition
from chan.series import WindowCrossesScaleBreak, refuse_window_crossing_a_break, scale_breaks
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "inputdataohlcdaily_stocks_20120424/ Open, High, Low and Close over 1,500 days, "
    "90-row spread with book two's smartstd, 20-row average, entry at 1 spread, "
    "at most 10 positions, each day over 10, compounded APR, n - 1 Sharpe ratio"
)

# --- the committed file --------------------------------------------------------


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def arrays(sources) -> dict[str, np.ndarray]:
    _, frames = sources
    return {field: frame.to_numpy(dtype=float) for field, frame in frames.items()}


@pytest.fixture(scope="module")
def long(sources) -> Side:
    _, f = sources
    return buy_on_gap.buy_on_gap(f["Open"], f["Low"], f["Close"])


@pytest.fixture(scope="module")
def short(sources) -> Side:
    _, f = sources
    return buy_on_gap.short_on_gap(f["Open"], f["High"], f["Close"])


@pytest.fixture(scope="module")
def first_edition(sources) -> tuple[Side, Side]:
    """Both sides with the first edition's ``smartstd`` inside the moving spread."""
    _, f = sources
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(matlab_helpers, "smartstd_book_two", smartstd_first_edition)
        return (
            buy_on_gap.buy_on_gap(f["Open"], f["Low"], f["Close"]),
            buy_on_gap.short_on_gap(f["Open"], f["High"], f["Close"]),
        )


def _first_held(side: Side) -> str:
    held = np.count_nonzero(side.positions, axis=1) > 0
    return str(side.days[held][0].date())


class TestTheSpecification:
    def test_the_rule_is_bog_m(self) -> None:
        assert (TOP_N, ENTRY_ZSCORE, AVERAGE_LOOKBACK, SPREAD_LOOKBACK, TRADING_DAYS) == (
            10,
            1,
            20,
            90,
            252,
        )

    def test_the_source_is_the_file_bog_m_loads_under_its_other_name(self) -> None:
        assert PRICE_FILE == "inputDataOHLCDaily_stocks_20120424.mat"
        assert SCRIPT_PRICE_FILE == "inputDataOHLCDaily_20120424"


class TestTheVintages:
    def test_the_members_are_the_pinned_source(self, sources) -> None:
        members, frames = sources
        vendor, basis, saved, folder, count = LIFTED_SOURCES[PRICE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert {m.path.split("/")[0] for m in members} == {folder}
        assert len(members) == count == 497
        assert all(frame.shape == (1500, 497) for frame in frames.values())

    def test_the_window_is_the_one_bog_m_prints(self, long: Side) -> None:
        """``bog.m`` prints ``tday(1)`` and ``tday(end)``, location 1974's "May 11, 2006,
        to April 24, 2012"."""
        printed = f"{long.days[0].strftime('%Y%m%d')} - {long.days[-1].strftime('%Y%m%d')}"
        assert printed == SCRIPT_WINDOW == "20060511 - 20120424", SPEC

    def test_the_four_prices_share_one_missing_mask(self, sources) -> None:
        """So no day has an open without a low, a high or a close to go with it."""
        _, frames = sources
        mask = frames["Open"].isna()
        assert int(mask.to_numpy().sum()) == 10981
        assert all(frame.isna().equals(mask) for frame in frames.values())


class TestTheFigures:
    """Buy on gap's two figures beside what ``bog.m`` and the book print, and three more."""

    def test_the_apr_is_chans_8_7_percent(self, long: Side) -> None:
        """``prod(1 + ret)^(252/1500) − 1``, which ``bog.m`` labels APR."""
        assert long.apr == pytest.approx(0.087385, abs=5e-7), SPEC
        assert round(100 * long.apr, 1) == BOOK_APR_PERCENT == 8.7, SPEC
        assert "APR=8.7%" in SCRIPT_COMMENT

    def test_the_sharpe_ratio_is_chans_1_5(self, long: Side) -> None:
        """``mean · √252 / std`` with MATLAB's n − 1 ``std``."""
        assert long.sharpe == pytest.approx(1.5371, abs=5e-5), SPEC
        assert round(long.sharpe, 1) == BOOK_SHARPE == 1.5, SPEC
        assert "Sharpe=1.5" in SCRIPT_COMMENT
        daily = long.daily
        assert long.sharpe == np.sqrt(252) * daily.mean() / daily.std(ddof=1), SPEC

    def test_the_arithmetic_return_does_not_reach_location_3509s_8_7(self, long: Side) -> None:
        """Location 3509 calls the 8.7 percent an "annualized average return", the
        phrase that named Example 7.2's arithmetic figure. Here ``252 · mean`` is
        8.5 percent at the book's precision, so the 8.7 is the compounded one."""
        assert long.arithmetic_annual == pytest.approx(0.085279, abs=5e-7), SPEC
        assert round(100 * long.arithmetic_annual, 1) == 8.5 != BOOK_APR_PERCENT, SPEC

    def test_the_maximum_drawdown_and_its_duration(self, long: Side) -> None:
        assert long.max_drawdown == pytest.approx(-0.052459, abs=5e-7), SPEC
        assert long.max_drawdown_days == 159, SPEC

    def test_the_positions_and_the_busiest_day(self, long: Side) -> None:
        assert long.trades == 695, SPEC
        assert long.days_held == 391, SPEC
        assert long.most_held == TOP_N, SPEC
        assert int((np.count_nonzero(long.positions, axis=1) == TOP_N).sum()) == 10, SPEC

    def test_nothing_is_held_before_the_spread_exists(self, long: Side, short: Side) -> None:
        """The spread first exists on row 90, 2006-09-19, and each side's first
        position comes a few days after it."""
        assert str(long.days[SPREAD_LOOKBACK].date()) == "2006-09-19"
        for side in (long, short):
            assert not side.positions[:SPREAD_LOOKBACK].any(), SPEC
            assert (side.daily[:SPREAD_LOOKBACK] == 0).all(), SPEC
            assert np.isfinite(side.daily).all(), SPEC
        assert _first_held(long) == "2006-09-22", SPEC
        assert _first_held(short) == "2006-09-25", SPEC

    def test_the_comparison_as_written_selects_what_the_algebra_does(
        self, arrays, long: Side
    ) -> None:
        """``op < buyPrice`` against ``drop < −spread``, the same 972 qualifiers."""
        op, hi, lo, cl = (arrays[k] for k in ("Open", "High", "Low", "Close"))
        spread, average = entry_spread(cl), trailing_average(cl)
        qualifies, drop = drop_qualifiers(op, lo, spread, average)
        with np.errstate(invalid="ignore"):
            algebra = np.isfinite(drop) & (drop < -spread) & (op > average)
        assert int(qualifies.sum()) == 972, SPEC
        assert (qualifies == algebra).all(), SPEC
        rises, jump = jump_qualifiers(op, hi, spread, average)
        with np.errstate(invalid="ignore"):
            mirrored = np.isfinite(jump) & (jump > spread) & (op < average)
        assert int(rises.sum()) == 1308, SPEC
        assert (rises == mirrored).all(), SPEC

    def test_reversing_the_tie_order_moves_nothing_because_nothing_ties(
        self, sources, arrays, long: Side, short: Side, monkeypatch
    ) -> None:
        """What ``chan.matlab_helpers``' docstring claims for this file: no two
        qualifiers on one day share a key, so no tie exists for the order to break."""
        op, hi, lo, cl = (arrays[k] for k in ("Open", "High", "Low", "Close"))
        spread, average = entry_spread(cl), trailing_average(cl)
        for qualifies, key in (
            drop_qualifiers(op, lo, spread, average),
            jump_qualifiers(op, hi, spread, average),
        ):
            for t in range(1, len(op)):
                keys = key[t, qualifies[t]]
                assert len(np.unique(keys)) == len(keys), SPEC

        def reversed_ties(x):
            x = np.asarray(x, dtype=float)
            return len(x) - 1 - np.argsort(x[::-1], kind="stable")

        _, f = sources
        monkeypatch.setattr(buy_on_gap, "matlab_sort", reversed_ties)
        assert reversed_ties([1.0, 1.0, 0.0]).tolist() == [2, 1, 0]
        again = buy_on_gap.buy_on_gap(f["Open"], f["Low"], f["Close"])
        mirror = buy_on_gap.short_on_gap(f["Open"], f["High"], f["Close"])
        assert (again.positions == long.positions).all(), SPEC
        assert (mirror.positions == short.positions).all(), SPEC


class TestTheMirror:
    """The rule issue 295 declared from location 1993, against the figures printed there."""

    def test_the_apr_lands_far_from_46_percent(self, short: Side) -> None:
        assert short.apr == pytest.approx(0.122030, abs=5e-7), SPEC
        assert round(100 * short.apr) == 12 != MIRROR_BOOK_APR_PERCENT == 46, SPEC

    def test_the_sharpe_ratio_lands_above_1_27(self, short: Side) -> None:
        assert short.sharpe == pytest.approx(1.7853, abs=5e-5), SPEC
        assert round(short.sharpe, 2) == 1.79 != MIRROR_BOOK_SHARPE == 1.27, SPEC

    def test_the_arithmetic_return_and_the_positions(self, short: Side) -> None:
        assert short.arithmetic_annual == pytest.approx(0.117301, abs=5e-7), SPEC
        assert short.trades == 725, SPEC
        assert short.days_held == 338, SPEC
        assert short.most_held == TOP_N, SPEC
        assert int((np.count_nonzero(short.positions, axis=1) == TOP_N).sum()) == 16, SPEC
        assert set(np.unique(short.positions)) == {-1.0, 0.0}, SPEC

    def test_its_drawdown_is_the_steeper_as_location_1993_says(
        self, long: Side, short: Side
    ) -> None:
        """The criterion issue 295 fixed before any run: the deeper ``calculateMaxDD``."""
        assert short.max_drawdown == pytest.approx(-0.064928, abs=5e-7), SPEC
        assert short.max_drawdown_days == 363, SPEC
        assert short.max_drawdown < long.max_drawdown, SPEC

    def test_chans_two_figures_need_four_and_a_half_times_this_volatility(
        self, short: Side
    ) -> None:
        """A floor on the volatility location 1993's pair implies, from the pair alone.

        ``ln(1 + r) ≤ r`` for every day, so ``252 · mean`` is at least
        ``ln(1 + APR)``, and the annual volatility, ``252 · mean / Sharpe``, is at
        least ``ln(1.46) / 1.27``. The declared rule's is a fraction of that.
        """
        floor = np.log(1 + MIRROR_BOOK_APR_PERCENT / 100) / MIRROR_BOOK_SHARPE
        assert floor == pytest.approx(0.2980, abs=5e-5)
        here = short.arithmetic_annual / short.sharpe
        assert here == pytest.approx(short.daily.std(ddof=1) * np.sqrt(252), rel=1e-12)
        assert here == pytest.approx(0.0657, abs=5e-5), SPEC
        assert floor / here == pytest.approx(4.5, abs=0.05), SPEC


class TestTheHelperMovesBothFigures:
    """The first edition's ``smartstd`` inside the spread, everything else kept."""

    def test_neither_printed_figure_lands_with_the_first_editions_helper(
        self, first_edition: tuple[Side, Side], long: Side
    ) -> None:
        swapped, _ = first_edition
        assert swapped.apr == pytest.approx(0.083629, abs=5e-7), SPEC
        assert swapped.sharpe == pytest.approx(1.6503, abs=5e-5), SPEC
        assert round(100 * swapped.apr, 1) == 8.4 != BOOK_APR_PERCENT, SPEC
        assert round(swapped.sharpe, 1) == 1.7 != BOOK_SHARPE, SPEC
        assert swapped.trades == 693 == long.trades - 2, SPEC

    def test_the_mirror_moves_too(self, first_edition: tuple[Side, Side]) -> None:
        _, swapped = first_edition
        assert swapped.apr == pytest.approx(0.116340, abs=5e-7), SPEC
        assert swapped.sharpe == pytest.approx(1.7234, abs=5e-5), SPEC
        assert swapped.trades == 726, SPEC


class TestTheLateListings:
    """A stock listed inside the window reaches the rule before 90 returns stand behind it."""

    def test_23_stocks_are_listed_late_and_none_has_a_gap_after(self, sources) -> None:
        _, frames = sources
        closes = frames["Close"]
        first = closes.apply(lambda c: c.first_valid_index())
        late = first[first > closes.index[0]]
        assert len(late) == 23
        assert (str(late.min().date()), str(late.max().date())) == ("2006-05-25", "2011-10-13")
        for symbol in closes:
            held = closes[symbol].loc[first[symbol] :]
            assert held.notna().all(), symbol

    def test_three_positions_rest_on_fewer_than_90_returns(
        self, sources, arrays, long: Side, short: Side
    ) -> None:
        """After row 90, only the late listings can, and none on a spread of 0."""
        _, frames = sources
        cl = arrays["Close"]
        finite = np.isfinite(calculate_returns(cl, 1)).astype(float)
        behind = matlab_helpers.backshift(
            1, pd.DataFrame(finite).rolling(SPREAD_LOOKBACK).sum().to_numpy()
        )
        spread = entry_spread(cl)
        symbols = frames["Close"].columns
        found = {}
        for side in (long, short):
            thin = (side.positions != 0) & (behind < SPREAD_LOOKBACK)
            thin[: SPREAD_LOOKBACK + 1] = False
            found[side.name] = sorted(symbols[np.argwhere(thin)[:, 1]])
            assert not ((side.positions != 0) & (spread == 0)).any(), SPEC
        assert found == {"buy on gap": ["CFN", "MPC"], "short on gap": ["DPS"]}, SPEC


class TestTheScaleBreakDecision:
    """Issue 295 decided the guard is not called. These hold what that decision rests on."""

    @staticmethod
    def _from_first_price(members, closes: pd.DataFrame):
        legs = []
        for entry in members:
            series = closes[entry.symbol]
            legs.append((entry, series.loc[series.first_valid_index() :]))
        return legs

    def test_the_guard_would_refuse_this_window_over_the_30_flagged_days(
        self, sources, long: Side
    ) -> None:
        members, frames = sources
        legs = self._from_first_price(members, frames["Close"])
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(legs, start=long.days[0], end=long.days[-1])
        message = str(refused.value)
        assert message.count(" changes scale on ") == 17
        assert "inputdataohlcdaily_stocks_20120424/aig.csv changes scale on" in message
        assert "2008-09-15" in message
        assert "no readable day-over-day move" not in message

    def test_one_position_falls_on_a_flagged_day(self, sources, long: Side, short: Side) -> None:
        """A short in MS on 2008-10-13, and nothing on the buy side."""
        members, frames = sources
        closes = frames["Close"]
        flagged = np.zeros(closes.shape, dtype=bool)
        for entry, series in self._from_first_price(members, closes):
            for day in scale_breaks(series):
                flagged[closes.index.get_loc(day), closes.columns.get_loc(entry.symbol)] = True
        assert int(flagged.sum()) == 30
        assert not ((long.positions != 0) & flagged).any(), SPEC
        hits = np.argwhere((short.positions != 0) & flagged)
        assert [(str(closes.index[i].date()), closes.columns[j]) for i, j in hits] == [
            ("2008-10-13", "MS")
        ], SPEC


class TestTheRun:
    def test_it_prints_each_figure_beside_chans(self, sources, monkeypatch, capsys) -> None:
        monkeypatch.setattr(buy_on_gap, "read_sources", lambda data_dir=None: sources)
        long, short = run()
        out = capsys.readouterr().out
        assert "20060511 - 20120424, 1500 trading days, 497 stocks" in out
        assert f"{long.trades} positions on {long.days_held} days" in out
        assert "Issue 295 declared it before any run" in out
        for line, figures in (
            ("Buy on gap, APR", ["0.087385", "0.0874", "8.7%", "8.7", "percent"]),
            ("Buy on gap, Sharpe ratio", ["1.5371", "1.54", "1.5"]),
            ("Buy on gap, 252 x mean", ["0.085279", "8.7"]),
            ("Short on gap, APR", ["0.122030", "0.1220", "46", "percent"]),
            ("Short on gap, Sharpe ratio", ["1.7853", "1.79", "1.27"]),
            ("Short on gap, maximum drawdown", ["-0.064928", "steeper"]),
        ):
            (row,) = [each for each in out.splitlines() if line in each]
            assert all(figure in row.split() for figure in figures), row
        assert "about survivors" in out
        assert "Exploratory." in out


# --- the rule, on arrays small enough to read ----------------------------------


def _one_day(opens, previous, spread, average, *, mirror: bool = False) -> np.ndarray:
    """Row 1 of a two-row array whose row 0 holds ``previous`` as the low, or the high."""
    opens = np.array([[np.nan] * len(opens), opens], dtype=float)
    previous = np.array([previous, [np.nan] * len(previous)], dtype=float)
    spread = np.array([[np.nan] * len(spread), spread], dtype=float)
    average = np.array([[np.nan] * len(average), average], dtype=float)
    select = gap_up_positions if mirror else gap_down_positions
    return select(opens, previous, spread, average)[1]


class TestTheRule:
    def test_an_open_below_the_entry_price_and_above_the_average_is_bought(self) -> None:
        """Previous low 100, spread 0.5, so the entry price is 50."""
        assert _one_day([49.9], [100.0], [0.5], [40.0]).tolist() == [1.0]

    def test_an_open_equal_to_the_entry_price_is_not(self) -> None:
        assert _one_day([50.0], [100.0], [0.5], [40.0]).tolist() == [0.0]

    def test_an_open_equal_to_the_average_is_not(self) -> None:
        assert _one_day([40.0], [100.0], [0.5], [40.0]).tolist() == [0.0]
        assert _one_day([40.0], [100.0], [0.5], [39.9]).tolist() == [1.0]

    def test_a_nan_spread_or_average_qualifies_nothing(self) -> None:
        assert _one_day([49.0], [100.0], [np.nan], [40.0]).tolist() == [0.0]
        assert _one_day([49.0], [100.0], [0.5], [np.nan]).tolist() == [0.0]
        assert _one_day([49.0], [np.nan], [0.5], [40.0]).tolist() == [0.0]

    def test_the_comparison_is_against_buy_price_as_written_not_the_algebra(self) -> None:
        """An open equal to ``buyPrice`` whose drop still rounds below the spread.

        ``bog.m`` refuses it, because ``op < buyPrice`` is false. Comparing the
        drop against the spread, the same test in algebra, would buy it.
        """
        low, spread = 104.81, 0.09529405115096386
        price = low * (1 - spread)
        qualifies, drop = drop_qualifiers(
            np.array([[np.nan], [price]]),
            np.array([[low], [np.nan]]),
            np.array([[np.nan], [spread]]),
            np.array([[np.nan], [0.0]]),
        )
        assert not qualifies[1, 0]
        assert drop[1, 0] < -spread

    def test_a_previous_high_of_zero_qualifies_nothing_for_the_mirror(self) -> None:
        """Its jump is infinite, and an infinite jump would otherwise rank first."""
        assert _one_day([5.0], [0.0], [0.5], [200.0], mirror=True).tolist() == [0.0]

    def test_ten_deepest_drops_among_many_ties_keep_column_order(self) -> None:
        """Forty tied qualifiers, past the size where numpy's default sort stops being stable."""
        held = _one_day([45.0] * 40, [100.0] * 40, [0.5] * 40, [30.0] * 40)
        assert held.tolist() == [1.0] * 10 + [0.0] * 30

    def test_the_ranking_loop_starts_on_the_second_row(self) -> None:
        """Row 0 qualifies here by construction, and ``bog.m``'s loop never reaches it."""
        qualifies = np.array([[True], [True]])
        held = buy_on_gap._ranked(qualifies, np.array([[-0.1], [-0.1]]), 1.0)
        assert held.tolist() == [[0.0], [1.0]]

    def test_the_ten_deepest_drops_are_bought(self) -> None:
        """Twelve qualifiers, opens 49 down to 38, so the last two columns miss out."""
        opens = [49.0 - k for k in range(12)][::-1]
        held = _one_day(opens, [100.0] * 12, [0.5] * 12, [30.0] * 12)
        assert held.tolist() == [1.0] * 10 + [0.0] * 2

    def test_ties_at_the_cut_keep_column_order(self) -> None:
        held = _one_day([45.0] * 12, [100.0] * 12, [0.5] * 12, [30.0] * 12)
        assert held.tolist() == [1.0] * 10 + [0.0] * 2

    def test_the_mirror_shorts_an_open_above_the_previous_high_and_below_the_average(
        self,
    ) -> None:
        """Previous high 100, spread 0.5, so the open must clear 150 and stay under 200."""
        assert _one_day([150.1], [100.0], [0.5], [200.0], mirror=True).tolist() == [-1.0]
        assert _one_day([150.0], [100.0], [0.5], [200.0], mirror=True).tolist() == [0.0]
        assert _one_day([200.0], [100.0], [0.5], [200.0], mirror=True).tolist() == [0.0]

    def test_the_mirror_shorts_the_ten_largest_jumps(self) -> None:
        opens = [151.0 + k for k in range(12)]
        held = _one_day(opens, [100.0] * 12, [0.5] * 12, [300.0] * 12, mirror=True)
        assert held.tolist() == [0.0] * 2 + [-1.0] * 10
        tied = _one_day([160.0] * 12, [100.0] * 12, [0.5] * 12, [300.0] * 12, mirror=True)
        assert tied.tolist() == [-1.0] * 10 + [0.0] * 2

    def test_the_first_row_is_never_traded(self) -> None:
        """``bog.m``'s loop starts at the second row."""
        held = gap_down_positions(
            np.array([[1.0]]), np.array([[100.0]]), np.array([[0.5]]), np.array([[0.0]])
        )
        assert held.tolist() == [[0.0]]

    def test_a_day_with_fewer_than_ten_still_divides_by_ten(self) -> None:
        positions = np.array([[1.0, 0.0, -1.0]])
        opens = np.array([[100.0, 100.0, 100.0]])
        closes = np.array([[103.0, 50.0, 98.0]])
        assert daily_returns(positions, opens, closes)[0] == pytest.approx(0.05 / 10, abs=1e-15)

    def test_a_day_that_sums_nothing_is_zero_rather_than_nan(self) -> None:
        """``bog.m`` sets it to 0, where ``chan.pead`` leaves ``smartsum``'s NaN."""
        positions = np.zeros((1, 2))
        nan = np.full((1, 2), np.nan)
        assert daily_returns(positions, nan, nan).tolist() == [0.0]

    def test_the_spread_reads_the_returns_ending_the_day_before(self) -> None:
        """A 50 percent jump on row 4 enters the spread on row 5, not row 4."""
        closes = np.array([[100.0], [101.0], [100.0], [101.0], [151.5], [151.5]])
        returns = calculate_returns(closes, 1)
        spread = buy_on_gap.backshift(1, matlab_helpers.smart_moving_std(returns, 3))
        assert spread[4, 0] < 0.01 < spread[5, 0]

    def test_the_first_row_with_a_spread_is_row_90(self) -> None:
        closes = 100 * np.cumprod(np.where(np.arange(95) % 2 == 0, 1.01, 0.99))[:, None]
        spread = entry_spread(closes)
        assert np.isnan(spread[:SPREAD_LOOKBACK]).all()
        assert np.isfinite(spread[SPREAD_LOOKBACK:]).all()
        average = trailing_average(closes)
        assert np.isnan(average[:AVERAGE_LOOKBACK]).all()
        assert np.isfinite(average[AVERAGE_LOOKBACK:]).all()

    def test_frames_that_disagree_are_refused(self) -> None:
        days = pd.bdate_range("2011-01-03", periods=3)
        a = pd.DataFrame({"AAA": [1.0, 2.0, 3.0]}, index=days)
        with pytest.raises(ValueError, match="one index and one column order"):
            buy_on_gap.buy_on_gap(a, a.rename(columns={"AAA": "BBB"}), a)
        later = a.set_axis(pd.bdate_range("2011-01-04", periods=3))
        with pytest.raises(ValueError, match="one index and one column order"):
            buy_on_gap.buy_on_gap(a, later, a)


class TestTheRefusals:
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable(f"no committed vintage is lifted from {PRICE_FILE}")

        monkeypatch.setattr(buy_on_gap, "run", refuse)
        monkeypatch.setattr("sys.argv", ["buy_on_gap"])
        with pytest.raises(SystemExit, match="no committed vintage is lifted from inputData"):
            main()

    def test_a_missing_field_reaches_the_reader_by_name(self, monkeypatch) -> None:
        def fake(source, *, field, data_dir=None):
            if field == "High":
                raise VintageUnavailable(f"{source} carries no High")
            return [SimpleNamespace(symbol="AAA")], pd.DataFrame()

        monkeypatch.setattr(buy_on_gap, "load_panel", fake)
        with pytest.raises(VintageUnavailable, match="carries no High"):
            read_sources()
