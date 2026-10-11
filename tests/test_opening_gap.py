"""The pins for the opening gap strategy on FSTX, *Algorithmic Trading*'s Example 7.1.

This file is the single authority for every number a prose surface quotes
about this replication, with one exception, in ``blog/opening-gap-lessons.md``.
``TestWhatThePostMeasures`` holds that post's own numbers, and the post's
figure labels are held by ``tests/test_opening_gap_figures.py``.
``docs/replication-log.md`` Entry 40 carries the verdicts and points here row
by row.

Every pin on the committed files reads one vintage and one specification
unless it names another, so they are stated once here.

- **Vintage.** ``inputdataohlcdaily_20120517/fstx.csv``, chan-mat, adjusted,
  saved 2012-05-18, lifted from ``inputDataOHLCDaily_20120517.mat``. FSTX's
  own column holds 2,000 days from 2004-07-16 to 2012-05-17 on each of the
  open, high, low and close, read through ``chan.series.load_panel`` as
  ``frame["FSTX"].dropna()`` once per field. Its identity is its row of
  ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``.
- **The two earlier saves.** ``inputdataohlcdaily_20120511/fstx.csv``, saved
  2012-05-12, and ``inputdataohlcdaily_20120507/fstx.csv``, saved
  2012-05-09, both chan-mat and adjusted. ``TestTheEarlierSaves``,
  ``TestWhatThePostMeasures``, ``TestTheGuardAndTheReads`` and
  ``TestTheReport`` read them.
- **Specification.** ``gapFutures_FSTX.m``, git blob ``02db940`` at
  EpchanPreview ``e4bc46f``, as ``chan.opening_gap`` transcribes it. The
  spread is ``backshift(1, smartMovingStd(calculateReturns(cl, 1), 90))``. A
  day is long when ``op >= backshift(1, hi) · (1 + 0.1 · spread)`` and short
  when ``op <= backshift(1, lo) · (1 − 0.1 · spread)``, the short assigned
  after the long. The literal reading earns ``positions · (op − cl) / op``,
  as line 23 writes it, and the momentum reading
  ``positions · (cl − op) / op``, with NaN set to 0 in both. The APR is
  ``prod(1 + ret)^(252 / 2000) − 1`` and the Sharpe ratio
  ``mean · √252 / std`` with the std dividing by n − 1, with no risk-free
  rate and no cost.
- **The Python port.** ``TestChansPythonPort`` runs the arithmetic of
  ``gapFutures_FSTX.py``, as ``chan.opening_gap.python_port`` carries it, on
  the vintage above. The port itself, member sha256
  ``8b005cee1114fd019ca761c1df7331d5f66ba9a3be8d6dcb2e614b6615a095fc`` in
  Chan's ``PythonCodesAndData.zip``, is not committed, and no test reads it.
  The class docstring names where the port's rule differs from the script's.

Each computed figure is held at six decimals or more, ten for Entry 40's
rows 10 and 11, so a change cannot move it inside the published rounding
unnoticed, and each published figure at the precision Chan printed it,
through ``matches``.

Exploratory. Reproducing Chan's figure spends his 2004 to 2012 sample on his
rule. The run first ran here on 2026-10-10, and the port's rows on
2026-10-11.
"""

from __future__ import annotations

import dataclasses
import io
import math
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest

from chan import matlab_helpers, paths
from chan import opening_gap as module
from chan.khandani_lo_book_two import gap, matches
from chan.matlab_helpers import backshift, smartstd_first_edition
from chan.opening_gap import (
    BOOK_APR_PERCENT,
    BOOK_FIRST_DAY,
    BOOK_LAST_DAY,
    BOOK_SHARPE,
    EARLIER_SAVES,
    ENTRY_ZSCORE,
    FIELDS,
    PORT_APR,
    PORT_MAX_DRAWDOWN,
    PORT_MAX_DRAWDOWN_DAYS,
    PORT_SHARPE,
    READINGS,
    SCRIPT_APR,
    SCRIPT_SHARPE,
    SIDES,
    SOURCE_FILE,
    SPREAD_LOOKBACK,
    SYMBOL,
    OpeningGap,
    PythonPort,
    by_side,
    daily_returns,
    figures,
    main,
    on_shared_days,
    open_to_close,
    opening_gap,
    positions,
    python_port,
    python_port_qualifiers,
    python_port_sharpe,
    python_port_spread,
    qualifiers,
    read_sources,
    run,
    spread,
)
from chan.series import WindowCrossesScaleBreak, load_panel, scale_breaks
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

#: Six decimals, the precision every computed pin is held at.
SIX = 1e-6

day = pd.Timestamp


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def prices(sources) -> pd.DataFrame:
    return sources[1]


@pytest.fixture(scope="module")
def result(prices) -> OpeningGap:
    return opening_gap(prices)


@pytest.fixture(scope="module")
def printed() -> str:
    """What ``run`` prints, captured once for the tests that read it."""
    out = io.StringIO()
    with redirect_stdout(out):
        run()
    return out.getvalue()


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.opening_gap"])


class TestTheVintage:
    def test_fstx_is_its_pinned_source(self, sources) -> None:
        entry, _ = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert (vendor, basis, saved, folder) == (
            "chan-mat",
            "adjusted",
            "2012-05-18",
            "inputdataohlcdaily_20120517",
        )
        assert entry.symbol == SYMBOL == "FSTX"
        assert (entry.vendor, entry.price_basis, entry.obtained) == (vendor, basis, saved)
        assert entry.path == f"{folder}/fstx.csv"

    def test_each_field_holds_2000_days_over_the_book_s_window(self, prices) -> None:
        assert list(prices.columns) == list(FIELDS) == ["Open", "High", "Low", "Close"]
        assert len(prices) == 2000
        assert (prices.index[0], prices.index[-1]) == (BOOK_FIRST_DAY, BOOK_LAST_DAY)
        assert prices.notna().all().all()

    def test_read_sources_is_load_panel_s_column_without_its_nan(self, prices) -> None:
        for field in FIELDS:
            column = load_panel(SOURCE_FILE, field=field)[1][SYMBOL].dropna()
            assert prices[field].equals(column.rename(field))

    def test_no_open_or_close_falls_outside_its_day_s_range(self, prices) -> None:
        for field in ("Open", "Close"):
            assert (prices[field] <= prices["High"]).all()
            assert (prices[field] >= prices["Low"]).all()

    def test_fields_on_different_days_are_refused(self, monkeypatch) -> None:
        real = module.load_panel

        def short_open(source_file, *, field="Close", data_dir=None):
            members, frame = real(source_file, field=field, data_dir=data_dir)
            if field == "Open":
                frame = frame.iloc[:-1]
            return members, frame

        monkeypatch.setattr(module, "load_panel", short_open)
        with pytest.raises(ValueError, match="fstx.csv prices its Open, High, Low, Close on"):
            read_sources()

    @pytest.mark.parametrize("moved", FIELDS)
    def test_a_field_on_as_many_other_days_is_refused(self, moved, monkeypatch) -> None:
        """One field's last day moved a day later, so every field still holds 2,000 days."""
        real = module.load_panel

        def shifted(source_file, *, field="Close", data_dir=None):
            members, frame = real(source_file, field=field, data_dir=data_dir)
            fstx = frame[SYMBOL].dropna()
            if field == moved:
                last = fstx.index[-1]
                fstx = fstx.rename(index={last: last + pd.Timedelta(days=1)})
            assert len(fstx) == 2000
            return members, fstx.to_frame(SYMBOL)

        monkeypatch.setattr(module, "load_panel", shifted)
        with pytest.raises(ValueError, match="on different days"):
            read_sources()


class TestTheSpecification:
    """The literal reading of line 23, which is the script as shipped."""

    def test_the_rule_is_a_tenth_of_the_90_day_spread(self) -> None:
        assert (ENTRY_ZSCORE, SPREAD_LOOKBACK) == (0.1, 90)
        assert READINGS == ("literal", "momentum")

    def test_the_apr(self, result) -> None:
        f = result.literal_figures
        assert f.apr == pytest.approx(0.132733, abs=SIX)
        assert matches(f.apr, SCRIPT_APR)
        assert SCRIPT_APR == "0.1327"

    def test_the_sharpe_ratio(self, result) -> None:
        f = result.literal_figures
        assert f.sharpe == pytest.approx(1.441620, abs=SIX)
        assert matches(f.sharpe, SCRIPT_SHARPE)
        assert SCRIPT_SHARPE == "1.44"

    def test_both_reproduce_the_book_s_figures(self, result) -> None:
        """Location 2965's "13 percent" and "1.4", at the precision Chan printed them."""
        f = result.literal_figures
        assert (BOOK_APR_PERCENT, BOOK_SHARPE) == ("13", "1.4")
        assert matches(100 * f.apr, BOOK_APR_PERCENT)
        assert matches(f.sharpe, BOOK_SHARPE)

    def test_252_times_the_mean_also_rounds_to_13_percent(self, result) -> None:
        """Location 3509 calls its figure of around 13 percent an annualized average return."""
        f = result.literal_figures
        assert f.average_annual_return == pytest.approx(0.128622, abs=SIX)
        assert matches(100 * f.average_annual_return, BOOK_APR_PERCENT)

    def test_the_sharpe_ratio_divides_by_n_minus_1(self, result) -> None:
        daily = result.literal
        assert result.literal_figures.sharpe == pytest.approx(
            math.sqrt(252) * daily.mean() / daily.std(ddof=1), abs=1e-12
        )

    def test_every_gap_is_zero_with_the_sign_the_log_prints(self, result) -> None:
        """The replication log's verdict table, computed minus printed at the printed precision."""
        f = result.literal_figures
        gaps = [
            gap(f.apr, SCRIPT_APR),
            gap(f.sharpe, SCRIPT_SHARPE),
            gap(100 * f.apr, BOOK_APR_PERCENT),
            gap(f.sharpe, BOOK_SHARPE),
            gap(100 * f.average_annual_return, BOOK_APR_PERCENT),
        ]
        assert gaps == [0.0] * 5
        assert [math.copysign(1, g) for g in gaps] == [1, 1, 1, 1, -1]

    def test_it_measures_every_day(self, result) -> None:
        assert len(result.literal) == len(result.momentum) == 2000
        assert np.isfinite(result.literal).all()
        assert np.isfinite(result.momentum).all()


class TestTheClaim:
    """Row 5: the sign location 2965 describes does not earn the figures it prints."""

    def test_the_momentum_reading_s_figures(self, result) -> None:
        f = result.momentum_figures
        assert f.apr == pytest.approx(-0.124236, abs=SIX)
        assert f.sharpe == pytest.approx(-1.441620, abs=SIX)

    def test_neither_lands_the_book(self, result) -> None:
        f = result.momentum_figures
        assert not matches(100 * f.apr, BOOK_APR_PERCENT)
        assert not matches(f.sharpe, BOOK_SHARPE)
        assert gap(100 * f.apr, BOOK_APR_PERCENT) == -25
        assert gap(f.sharpe, BOOK_SHARPE) == pytest.approx(-2.8)

    def test_the_momentum_returns_are_the_literal_ones_negated(self, result) -> None:
        assert (result.momentum == -result.literal).all()
        assert result.momentum_figures.sharpe == -result.literal_figures.sharpe


class TestBesideTheReplication:
    """Rows 6 and 7, which no source prints."""

    def test_the_literal_reading_s_drawdown(self, result) -> None:
        f = result.literal_figures
        assert f.max_drawdown == pytest.approx(-0.190023, abs=SIX)
        assert f.max_drawdown_days == 287

    def test_the_momentum_reading_s_drawdown(self, result) -> None:
        f = result.momentum_figures
        assert f.max_drawdown == pytest.approx(-0.651056, abs=SIX)
        assert f.max_drawdown_days == 1909

    def test_the_days_each_side_qualifies(self, result) -> None:
        assert int(result.longs.sum()) == 278
        assert int(result.shorts.sum()) == 191
        assert not (result.longs & result.shorts).any()
        assert int((result.positions == 1).sum()) == 278
        assert int((result.positions == -1).sum()) == 191
        assert int((result.positions == 0).sum()) == 1531

    def test_the_first_position_is_on_2004_11_22(self, result) -> None:
        assert result.first_position == day("2004-11-22")

    def test_the_first_90_rows_carry_no_spread_and_no_position(self, result) -> None:
        unset = np.flatnonzero(np.isnan(result.spread))
        assert (unset == np.arange(SPREAD_LOOKBACK)).all()
        assert not result.positions[:SPREAD_LOOKBACK].any()

    def test_no_day_sits_exactly_on_either_threshold(self, prices, result) -> None:
        """So the non-strict tests decide no day here, and the boundary tests below hold them."""
        op = prices["Open"].to_numpy()
        with np.errstate(invalid="ignore"):
            up = backshift(1, prices["High"].to_numpy()) * (1 + ENTRY_ZSCORE * result.spread)
            down = backshift(1, prices["Low"].to_numpy()) * (1 - ENTRY_ZSCORE * result.spread)
        assert not (op == up).any()
        assert not (op == down).any()


class TestTheEarlierSaves:
    """Rows 8 and 9: the literal rule on the two earlier saves, where FSTX's prices differ."""

    @pytest.mark.parametrize(
        ("source_file", "saved", "first", "last", "apr", "sharpe"),
        [
            (
                "inputDataOHLCDaily_20120511.mat",
                "2012-05-12",
                "2004-07-12",
                "2012-05-11",
                0.131543,
                1.448082,
            ),
            (
                "inputDataOHLCDaily_20120507.mat",
                "2012-05-09",
                "2004-07-07",
                "2012-05-08",
                0.133561,
                1.466345,
            ),
        ],
    )
    def test_each_misses_the_script_s_apr(
        self, source_file, saved, first, last, apr, sharpe
    ) -> None:
        entry, earlier = read_sources(source_file=source_file)
        vendor, basis, pinned_saved, folder, _ = LIFTED_SOURCES[source_file]
        assert (entry.vendor, entry.price_basis, entry.obtained) == (vendor, basis, saved)
        assert pinned_saved == saved
        assert entry.path == f"{folder}/fstx.csv"
        assert len(earlier) == 2000
        assert (earlier.index[0], earlier.index[-1]) == (day(first), day(last))
        f = opening_gap(earlier).literal_figures
        assert f.apr == pytest.approx(apr, abs=SIX)
        assert f.sharpe == pytest.approx(sharpe, abs=SIX)
        assert not matches(f.apr, SCRIPT_APR)
        assert matches(100 * f.apr, BOOK_APR_PERCENT)

    def test_run_reads_both(self) -> None:
        assert EARLIER_SAVES == (
            "inputDataOHLCDaily_20120511.mat",
            "inputDataOHLCDaily_20120507.mat",
        )


@pytest.fixture(scope="module")
def earlier() -> dict[str, pd.DataFrame]:
    """FSTX's four fields from the two earlier saves, keyed by the save's date."""
    return {
        "20120511": read_sources(source_file=EARLIER_SAVES[0])[1],
        "20120507": read_sources(source_file=EARLIER_SAVES[1])[1],
    }


class TestWhatThePostMeasures:
    """Pins added with ``blog/opening-gap-lessons.md``, measured after the run.

    Same vintage and specification as the module docstring states, over the
    2,000 days unless a test names a shorter span or another save. Each
    describes this sample and tests nothing.
    """

    def test_the_first_edition_s_smartstd_changes_no_position(self, prices, result) -> None:
        """Book one's ``smartstd`` zero-fills and divides by n − 1 inside the moving spread.

        It moves the spread itself, and still no open crosses a threshold
        because of it, so both printed figures hold at six decimals.
        """
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(matlab_helpers, "smartstd_book_two", smartstd_first_edition)
            first_edition = opening_gap(prices)
        assert not np.allclose(
            first_edition.spread[SPREAD_LOOKBACK:],
            result.spread[SPREAD_LOOKBACK:],
            equal_nan=True,
        )
        assert (first_edition.positions == result.positions).all()
        f = first_edition.literal_figures
        assert f.apr == pytest.approx(0.132733, abs=SIX)
        assert f.sharpe == pytest.approx(1.441620, abs=SIX)

    def test_each_curve_stays_on_its_own_side_of_its_start_from_the_first_position(
        self, result
    ) -> None:
        """From 2004-11-22, the first day holding a position, to 2012-05-17."""
        first = int(np.argmax(result.positions != 0))
        assert (result.days[first], len(result.days) - first) == (day("2004-11-22"), 1909)
        literal = (np.cumprod(1 + result.literal) - 1)[first:]
        momentum = (np.cumprod(1 + result.momentum) - 1)[first:]
        assert literal.min() == pytest.approx(0.002878, abs=SIX)
        assert momentum.max() == pytest.approx(-0.002878, abs=SIX)
        assert (int(np.argmin(literal)), int(np.argmax(momentum))) == (0, 0)
        assert (literal > 0).all() and (momentum < 0).all()

    def test_the_two_earlier_saves_price_all_four_fields_alike(self, earlier) -> None:
        older, newer = earlier["20120507"], earlier["20120511"]
        shared = older.index.intersection(newer.index)
        assert len(shared) == 1997
        assert (older.loc[shared, list(FIELDS)] == newer.loc[shared, list(FIELDS)]).all().all()

    @pytest.mark.parametrize("field", FIELDS)
    def test_the_2012_05_17_save_restates_every_field(self, prices, earlier, field) -> None:
        """Against the 2012-05-11 save, on the 1,996 days the two share.

        Distinct differences are rounded to the micro-unit, zero included, as
        ``tests/test_continuous_futures.py`` counts them for the close.
        """
        older = earlier["20120511"]
        shared = older.index.intersection(prices.index)
        moved = (prices.loc[shared, field] - older.loc[shared, field]).to_numpy()
        assert len(shared) == 1996
        assert int((moved == 0).sum()) == 45
        distinct = set(np.round(moved, 6))
        assert len(distinct) == 25
        assert len(distinct - {0.0}) == 24

    def test_at_a_fixed_window_the_restated_prices_move_the_apr(self, prices, earlier) -> None:
        """The 2012-05-11 save is cut to start on 2004-07-16, the 2012-05-17 save's first day.

        Both spreads then warm up on the same rows, so the two runs differ by
        the restated prices alone. Each move is held to half a unit in its
        sixth decimal, so a wrong last digit fails.
        """
        shared = on_shared_days(prices, earlier["20120511"])
        assert shared.days[0] == day("2004-07-16") == prices.index[0]
        assert (len(shared.days), shared.differ) == (1996, 6)
        assert shared.one.apr == pytest.approx(0.133016, abs=SIX)
        assert shared.one.sharpe == pytest.approx(1.443075, abs=SIX)
        assert shared.other.apr == pytest.approx(0.130360, abs=SIX)
        assert shared.other.sharpe == pytest.approx(1.435907, abs=SIX)
        assert shared.one.apr - shared.other.apr == pytest.approx(0.002655, abs=5e-7)

    def test_at_fixed_prices_the_window_moves_the_apr(self, earlier) -> None:
        """The 2012-05-07 and 2012-05-11 saves price alike, so only their windows differ."""
        apr = {save: opening_gap(earlier[save]).literal_figures.apr for save in earlier}
        assert apr["20120507"] - apr["20120511"] == pytest.approx(0.002017, abs=5e-7)

    def test_each_move_is_over_ten_times_the_comment_s_last_digit(self, prices, earlier) -> None:
        """The comment prints four decimals, so its last digit is 0.0001."""
        last_digit = 10.0 ** -len(SCRIPT_APR.split(".")[1])
        assert last_digit == pytest.approx(0.0001)
        shared = on_shared_days(prices, earlier["20120511"])
        apr = {save: opening_gap(earlier[save]).literal_figures.apr for save in earlier}
        assert shared.one.apr - shared.other.apr > 10 * last_digit
        assert apr["20120507"] - apr["20120511"] > 10 * last_digit

    def test_the_mean_return_on_a_held_day(self, result) -> None:
        held = result.positions != 0
        assert int(held.sum()) == 469
        assert result.literal[held].mean() == pytest.approx(0.002177, abs=SIX)

    def test_each_side_s_days_summed_and_compounded(self, result) -> None:
        sides = by_side(result)
        assert list(sides) == list(SIDES) == ["long", "short"]
        assert (sides["long"].days, sides["short"].days) == (278, 191)
        assert sides["long"].summed == pytest.approx(0.749529, abs=SIX)
        assert sides["short"].summed == pytest.approx(0.271280, abs=SIX)
        assert sides["long"].compounded == pytest.approx(1.084422, abs=SIX)
        assert sides["short"].compounded == pytest.approx(0.290022, abs=SIX)
        assert result.literal.sum() == pytest.approx(1.020809, abs=SIX)
        assert sides["long"].summed + sides["short"].summed == pytest.approx(
            result.literal.sum(), abs=1e-12
        )

    def test_the_two_sides_compound_to_the_whole_curve(self, result) -> None:
        sides = by_side(result)
        whole = np.prod(1 + result.literal) - 1
        assert whole == pytest.approx(1.688951, abs=SIX)
        assert (1 + sides["long"].compounded) * (1 + sides["short"].compounded) == pytest.approx(
            1 + whole, abs=1e-12
        )

    def test_each_side_alone_s_apr_and_sharpe_ratio(self, result) -> None:
        sides = by_side(result)
        assert sides["long"].figures.apr == pytest.approx(0.096964, abs=SIX)
        assert sides["long"].figures.sharpe == pytest.approx(1.534735, abs=SIX)
        assert sides["short"].figures.apr == pytest.approx(0.032607, abs=SIX)
        assert sides["short"].figures.sharpe == pytest.approx(0.527473, abs=SIX)

    def test_fstx_s_move_from_the_open_on_each_kind_of_day(self, prices, result) -> None:
        moves = open_to_close(prices, result)
        assert list(moves) == ["long", "short", "flat"]
        assert (moves["long"].days, moves["short"].days, moves["flat"].days) == (278, 191, 1441)
        assert moves["long"].mean == pytest.approx(-0.002696, abs=SIX)
        assert moves["short"].mean == pytest.approx(0.001420, abs=SIX)
        assert moves["flat"].mean == pytest.approx(0.000025, abs=SIX)

    def test_the_closes_below_and_above_the_open(self, prices, result) -> None:
        moves = open_to_close(prices, result)
        assert (moves["long"].below, moves["short"].above) == (163, 108)

    def test_the_port_earns_the_script_s_long_returns_on_every_upward_jump(
        self, result, port
    ) -> None:
        """The port takes the momentum sign, and still sells every upward jump.

        Its flipped short test makes it short on each of the 278 days the
        script is long, and short times the momentum sign is the script's long
        times the literal sign. Its other 1,440 short days are the script's
        flat days with a spread, less 2004-11-19, where the port's spread is
        not yet set.
        """
        up = result.positions == SIDES["long"]
        assert int(up.sum()) == 278
        assert (port.positions[up] == SIDES["short"]).all()
        assert (port.returns[up] == result.literal[up]).all()
        assert port.returns[up].sum() == pytest.approx(0.749529, abs=SIX)
        rest = (port.positions == SIDES["short"]) & ~up
        flat = (result.positions == 0) & np.isfinite(result.spread)
        assert int(rest.sum()) == 1440
        assert list(result.days[flat & ~rest]) == [day("2004-11-19")]
        assert not (rest & ~flat).any()
        assert port.returns[rest].sum() == pytest.approx(-0.050957, abs=SIX)


class TestTheRules:
    """Each step on arrays built so the answer is known."""

    def test_the_spread_is_the_90_row_deviation_one_row_later(self) -> None:
        closes = 100 * np.cumprod(1 + np.tile([0.01, -0.01, 0.02], 40))
        found = spread(closes)
        assert np.isnan(found[:SPREAD_LOOKBACK]).all()
        returns = closes[1:91] / closes[:90] - 1
        # Row 90 reads the returns of rows 1 to 89 and row 0's NaN, over n.
        assert found[90] == pytest.approx(np.std(returns[:89], ddof=0))
        assert found[91] == pytest.approx(np.std(returns, ddof=0))

    @staticmethod
    def _day(op, *, prev_hi=100.0, prev_lo=90.0, sd=0.1):
        """Two rows: yesterday's high and low, and today's open, with today's spread."""
        return (
            np.array([95.0, op]),
            np.array([prev_hi, np.nan]),
            np.array([prev_lo, np.nan]),
            np.array([np.nan, sd]),
        )

    def test_an_open_exactly_on_the_long_threshold_is_long(self) -> None:
        # 100 · (1 + 0.1 · 0.1) is 101.0 exactly in floating point.
        assert 100.0 * (1 + ENTRY_ZSCORE * 0.1) == 101.0
        assert positions(*self._day(101.0)).tolist() == [0, 1]
        assert positions(*self._day(np.nextafter(101.0, 0))).tolist() == [0, 0]

    def test_an_open_exactly_on_the_short_threshold_is_short(self) -> None:
        threshold = 90.0 * (1 - ENTRY_ZSCORE * 0.1)
        assert positions(*self._day(threshold)).tolist() == [0, -1]
        assert positions(*self._day(np.nextafter(threshold, 100))).tolist() == [0, 0]

    def test_an_open_inside_the_range_is_flat(self) -> None:
        assert positions(*self._day(95.0)).tolist() == [0, 0]

    def test_the_margin_scales_with_the_spread(self) -> None:
        # An open of 100.5 clears 100 · (1 + 0.1 · 0.04) but not 100 · (1 + 0.1 · 0.06).
        assert positions(*self._day(100.5, sd=0.04)).tolist() == [0, 1]
        assert positions(*self._day(100.5, sd=0.06)).tolist() == [0, 0]

    def test_a_nan_spread_qualifies_nothing(self) -> None:
        assert positions(*self._day(200.0, sd=np.nan)).tolist() == [0, 0]
        assert positions(*self._day(1.0, sd=np.nan)).tolist() == [0, 0]

    def test_the_first_row_has_no_previous_day(self) -> None:
        op = np.array([200.0, 95.0])
        hi = np.array([100.0, 100.0])
        lo = np.array([90.0, 90.0])
        assert positions(op, hi, lo, np.array([0.0, 0.0])).tolist() == [0, 0]

    def test_a_day_qualifying_both_is_short(self) -> None:
        """With no spread and yesterday's high equal to its low, an open there qualifies both."""
        op, hi, lo, sd = self._day(100.0, prev_hi=100.0, prev_lo=100.0, sd=0.0)
        longs, shorts = qualifiers(op, hi, lo, sd)
        assert longs.tolist() == shorts.tolist() == [False, True]
        assert positions(op, hi, lo, sd).tolist() == [0, -1]

    def test_a_day_qualifying_both_is_short_in_the_run_and_counted_as_both(self, sources) -> None:
        """Every price at 100 leaves a spread of 0, so every row from 90 on qualifies both.

        The run's own longs and shorts are the qualifiers rather than the
        positions, so the report counts those five rows as both.
        """
        flat = pd.DataFrame(100.0, index=pd.date_range("2020-01-01", periods=95), columns=FIELDS)
        found = opening_gap(flat)
        assert (found.longs & found.shorts)[SPREAD_LOOKBACK:].all()
        assert (found.positions[SPREAD_LOOKBACK:] == -1).all()
        out = io.StringIO()
        # Every return is 0, so the Sharpe ratio divides 0 by 0 and prints nan.
        with np.errstate(invalid="ignore"), redirect_stdout(out):
            module.report(sources[0], found, [])
        assert "long on 5 days, short on 5, both on 5, first position 2020-03-31" in out.getvalue()

    @pytest.mark.parametrize(("held", "first"), [([0, 1, -1, 0], 1), ([0, 0, -1, 1], 2)])
    def test_the_first_position_is_the_first_held_day_of_either_sign(self, held, first) -> None:
        days = pd.date_range("2020-01-01", periods=4)
        none = np.zeros(4)
        run_on = OpeningGap(
            days=days,
            spread=none,
            longs=none > 0,
            shorts=none > 0,
            positions=np.array(held, dtype=float),
            literal=none,
            momentum=none,
        )
        assert run_on.first_position == days[first]

    def test_the_literal_return_fades_the_jump(self) -> None:
        held = np.array([1.0, -1.0, 0.0])
        op = np.array([100.0, 100.0, 100.0])
        cl = np.array([90.0, 120.0, 50.0])
        # A long earns the fall from the open and a short the rise.
        assert daily_returns(held, op, cl).tolist() == pytest.approx([0.1, 0.2, 0.0])
        assert daily_returns(held, op, cl, reading="literal").tolist() == pytest.approx(
            [0.1, 0.2, 0.0]
        )

    def test_the_momentum_return_follows_it(self) -> None:
        held = np.array([1.0, -1.0, 0.0])
        op = np.array([100.0, 100.0, 100.0])
        cl = np.array([90.0, 120.0, 50.0])
        # A long earns the rise from the open and a short the fall.
        assert daily_returns(held, op, cl, reading="momentum").tolist() == pytest.approx(
            [-0.1, -0.2, 0.0]
        )

    def test_the_return_divides_by_the_open_not_the_close(self) -> None:
        assert daily_returns(np.array([1.0]), np.array([80.0]), np.array([100.0])).tolist() == [
            pytest.approx(-0.25)
        ]

    @pytest.mark.parametrize("reading", READINGS)
    def test_a_nan_return_is_zero(self, reading) -> None:
        held = np.array([1.0, 1.0, 0.0])
        op = np.array([np.nan, 100.0, np.nan])
        cl = np.array([100.0, np.nan, np.nan])
        assert daily_returns(held, op, cl, reading=reading).tolist() == [0.0, 0.0, 0.0]

    def test_an_unknown_reading_is_refused(self) -> None:
        with pytest.raises(ValueError, match="reading is one of"):
            daily_returns(np.array([1.0]), np.array([1.0]), np.array([1.0]), reading="fade")

    def test_figures_on_a_known_series(self) -> None:
        daily = np.array([0.0, 0.02, -0.01, 0.0])
        f = figures(daily)
        assert f.apr == pytest.approx((1.02 * 0.99) ** (252 / 4) - 1)
        assert f.sharpe == pytest.approx(math.sqrt(252) * daily.mean() / daily.std(ddof=1))
        assert f.average_annual_return == pytest.approx(252 * daily.mean())
        assert f.max_drawdown == pytest.approx(0.99 - 1)
        assert f.max_drawdown_days == 2

    @staticmethod
    def _held_days(held, op, cl, spread=None) -> tuple[pd.DataFrame, OpeningGap]:
        """A run built from its positions, so each side's days are known in advance."""
        days = pd.date_range("2020-01-01", periods=len(held))
        held = np.array(held, dtype=float)
        prices = pd.DataFrame({"Open": op, "Close": cl}, index=days, dtype=float)
        sd = np.zeros(len(held)) if spread is None else np.array(spread, dtype=float)
        return prices, OpeningGap(
            days=days,
            spread=sd,
            longs=held > 0,
            shorts=held < 0,
            positions=held,
            literal=daily_returns(held, op, cl, reading="literal"),
            momentum=daily_returns(held, op, cl, reading="momentum"),
        )

    def test_by_side_keeps_each_side_s_returns_and_zero_elsewhere(self) -> None:
        # Long earns 0.1 then 0.2, short earns 0.5, the flat day nothing.
        _, run_on = self._held_days([1, -1, 0, 1], [100, 100, 100, 100], [90, 150, 50, 80])
        sides = by_side(run_on)
        assert sides["long"].daily.tolist() == pytest.approx([0.1, 0, 0, 0.2])
        assert sides["short"].daily.tolist() == pytest.approx([0, 0.5, 0, 0])
        assert (sides["long"].days, sides["short"].days) == (2, 1)
        assert sides["long"].summed == pytest.approx(0.3)
        assert sides["long"].compounded == pytest.approx(1.1 * 1.2 - 1)
        assert sides["short"].compounded == pytest.approx(0.5)
        assert sides["long"].figures == figures(sides["long"].daily)

    def test_by_side_reads_the_reading_it_is_given(self) -> None:
        _, run_on = self._held_days([1, -1], [100, 100], [90, 150])
        sides = by_side(run_on, "momentum")
        assert sides["long"].summed == pytest.approx(-0.1)
        assert sides["short"].summed == pytest.approx(-0.5)
        with pytest.raises(ValueError, match="reading is one of"):
            by_side(run_on, "fade")

    def test_open_to_close_is_the_instrument_s_move_whatever_the_side(self) -> None:
        prices, run_on = self._held_days(
            [1, 1, -1, 0, 0, 0],
            [100, 100, 100, 100, 100, 100],
            [90, 110, 120, 104, 96, 50],
            spread=[0, 0, 0, 0, 0, np.nan],
        )
        moves = open_to_close(prices, run_on)
        assert (moves["long"].days, moves["long"].mean) == (2, pytest.approx(0.0))
        assert (moves["long"].below, moves["long"].above) == (1, 1)
        assert (moves["short"].days, moves["short"].mean) == (1, pytest.approx(0.2))
        assert (moves["short"].below, moves["short"].above) == (0, 1)
        # The last row has no spread, so its fall of a half is no flat day's.
        assert (moves["flat"].days, moves["flat"].mean) == (2, pytest.approx(0.0))
        assert (moves["flat"].below, moves["flat"].above) == (1, 1)

    def test_a_day_qualifying_both_counts_as_short_alone(self) -> None:
        """Line 21 makes such a day short, so neither split may count it long."""
        prices, run_on = self._held_days([-1], [100], [90])
        both = dataclasses.replace(run_on, longs=np.array([True]), shorts=np.array([True]))
        sides = by_side(both)
        assert (sides["long"].days, sides["short"].days) == (0, 1)
        assert sides["short"].summed == pytest.approx(-0.1)
        moves = open_to_close(prices, both)
        assert (moves["long"].days, moves["short"].days, moves["flat"].days) == (0, 1, 0)

    def test_open_to_close_counts_a_close_on_the_open_as_neither(self) -> None:
        prices, run_on = self._held_days([1], [100], [100])
        move = open_to_close(prices, run_on)["long"]
        assert (move.days, move.below, move.above, move.mean) == (1, 0, 0, 0.0)
        # No short day and no flat day, so neither has a mean.
        assert np.isnan(open_to_close(prices, run_on)["short"].mean)
        assert open_to_close(prices, run_on)["flat"].days == 0

    @staticmethod
    def _two_histories(extra: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
        """One series, and the same series with its first ``extra`` rows cut off.

        The longer history's spread is set ``extra`` rows sooner, and an open
        jumps far above the previous high on a row where only the longer
        history has a spread, so a run on the uncut history is long there.
        """
        rng = np.random.default_rng(7)
        rows = SPREAD_LOOKBACK + 20
        closes = 100 * np.cumprod(1 + rng.normal(0, 0.01, rows))
        opens = np.roll(closes, 1)
        opens[0] = closes[0]
        jump = SPREAD_LOOKBACK + 2
        # A second jump, where both histories have a spread, so neither run is all flat.
        for row in (jump, jump + 10):
            opens[row] = 1.2 * closes[row - 1]
        frame = pd.DataFrame(
            {
                "Open": opens,
                "High": np.maximum(opens, closes) * 1.001,
                "Low": np.minimum(opens, closes) * 0.999,
                "Close": closes,
            },
            index=pd.date_range("2020-01-01", periods=rows),
        )
        assert opening_gap(frame).positions[jump] == 1
        assert opening_gap(frame.iloc[extra:]).positions[jump - extra] == 0
        return frame, frame.iloc[extra:]

    def test_on_shared_days_starts_both_runs_on_the_same_row(self) -> None:
        """With the prices equal, the only thing left to differ is the window, and it is cut."""
        longer, shorter = self._two_histories()
        for one, other in ((longer, shorter), (shorter, longer)):
            shared = on_shared_days(one, other)
            assert shared.days.equals(shorter.index)
            assert shared.differ == 0
            assert shared.one == shared.other

    def test_on_shared_days_keeps_each_run_s_own_rows(self) -> None:
        longer, shorter = self._two_histories()
        restated = shorter.assign(Close=shorter["Close"] * 1.01)
        shared = on_shared_days(longer, restated)
        cut = opening_gap(longer.loc[restated.index[0] :])
        assert shared.days.equals(restated.index)
        assert shared.one == figures(cut.literal)
        assert shared.other == figures(opening_gap(restated).literal)
        momentum = on_shared_days(longer, restated, "momentum")
        assert momentum.one == figures(cut.momentum)
        assert momentum.other == figures(opening_gap(restated).momentum)
        assert momentum.other != shared.other


class TestTheGuardAndTheReads:
    @pytest.mark.parametrize("source_file", [SOURCE_FILE, *EARLIER_SAVES])
    @pytest.mark.parametrize("field", FIELDS)
    def test_fstx_carries_no_flagged_day(self, source_file, field) -> None:
        """``tests/test_scale_breaks.py`` names ZB and ZF as the only flagged series here."""
        assert scale_breaks(load_panel(source_file, field=field)[1][SYMBOL].dropna()) == []

    def test_read_sources_guards_the_closes_over_the_whole_span(self, prices, monkeypatch) -> None:
        seen = []
        guarded = []

        def record(legs, *, start, end):
            seen.append(([(entry.path, series.name) for entry, series in legs], start, end))
            guarded.extend(series for _, series in legs)

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert seen == [
            ([("inputdataohlcdaily_20120517/fstx.csv", "Close")], BOOK_FIRST_DAY, BOOK_LAST_DAY)
        ]
        # The name alone would pass the opens renamed, so the values are compared too.
        assert guarded[0].equals(prices["Close"])

    @pytest.mark.parametrize("source_file", [SOURCE_FILE, *EARLIER_SAVES])
    @pytest.mark.parametrize("row", [1, 1000, 1999])
    def test_fstx_changing_scale_anywhere_is_refused(self, row, source_file, monkeypatch) -> None:
        real = module.load_panel

        def broken(source_file, *, field="Close", data_dir=None):
            members, frame = real(source_file, field=field, data_dir=data_dir)
            frame = frame.copy()
            fstx = frame[SYMBOL].dropna()
            frame.loc[fstx.index[row:], SYMBOL] *= 10
            return members, frame

        monkeypatch.setattr(module, "load_panel", broken)
        with pytest.raises(WindowCrossesScaleBreak, match="fstx.csv"):
            read_sources(source_file=source_file)

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputDataOHLCDaily_20120517.mat"):
            run(tmp_path)

    def test_run_hands_its_directory_to_every_read(self, monkeypatch) -> None:
        """The earlier saves too, which a missing directory alone cannot show.

        ``run(tmp_path)`` stops at the first read, so it never reaches them.
        """
        real = module.read_sources
        seen = []

        def record(data_dir=None, *, source_file=SOURCE_FILE):
            seen.append((data_dir, source_file))
            return real(data_dir, source_file=source_file)

        monkeypatch.setattr(module, "read_sources", record)
        with redirect_stdout(io.StringIO()):
            run(paths.DATA_DIR)
        assert seen == [(paths.DATA_DIR, saved) for saved in (SOURCE_FILE, *EARLIER_SAVES)]

    def test_run_returns_the_specification(self) -> None:
        with redirect_stdout(io.StringIO()):
            found = run()
        assert found.literal_figures.apr == pytest.approx(0.132733, abs=SIX)


class TestTheReport:
    @staticmethod
    def _row(out: str, label: str) -> list[str]:
        return next(r for r in out.splitlines() if r.strip().startswith(label)).split()

    def test_it_prints_both_readings_beside_the_script_and_the_book(self, printed) -> None:
        assert self._row(printed, "APR, literal")[-5:] == [
            "0.132733",
            "0.1327",
            "reproduced",
            "13",
            "reproduced",
        ]
        assert self._row(printed, "Sharpe ratio, literal")[-5:] == [
            "1.441620",
            "1.44",
            "reproduced",
            "1.4",
            "reproduced",
        ]
        assert self._row(printed, "APR, momentum")[-6:] == [
            "-0.124236",
            "none",
            "none",
            "13",
            "gap",
            "-25",
        ]
        assert self._row(printed, "Sharpe ratio, momentum")[-6:] == [
            "-1.441620",
            "none",
            "none",
            "1.4",
            "gap",
            "-2.8",
        ]

    def test_it_prints_the_vintages_and_the_rows_beside(self, printed) -> None:
        assert printed.startswith(
            "The opening gap strategy on STOXX Europe 50 futures, Algorithmic Trading's Example 7.1"
        )
        assert "inputdataohlcdaily_20120517/fstx.csv" in printed
        assert "window    2004-07-16 to 2012-05-17, 2000 trading days" in printed
        assert "252 x mean, literal          0.128622" in printed
        assert "maximum drawdown, literal    -0.190023 over 287 days" in printed
        assert "maximum drawdown, momentum   -0.651056 over 1909 days" in printed
        assert "long on 278 days, short on 191, both on 0, first position 2004-11-22" in printed
        assert "inputdataohlcdaily_20120511/fstx.csv" in printed
        assert "2004-07-12 to 2012-05-11, literal APR 0.131543, Sharpe ratio 1.448082" in printed
        assert "inputdataohlcdaily_20120507/fstx.csv" in printed
        assert "2004-07-07 to 2012-05-08, literal APR 0.133561, Sharpe ratio 1.466345" in printed
        assert "Exploratory." in printed

    def test_it_prints_the_rule_and_the_basis(self, printed) -> None:
        assert (
            "rule      long when the open clears the previous high by 0.1 of the 90-day std,"
            in printed
        )
        assert "short when it clears the previous low, held from the open to the close" in printed
        assert (
            "Beside the replication. No source prints these, so none carries a verdict." in printed
        )
        assert "Annualised over 252 days with no risk-free rate and no cost" in printed

    def test_the_script_column_judges_against_the_script(self) -> None:
        """On the 2012-05-11 save, whose APR misses the script's and still lands the book's.

        The 2012-05-17 save reproduces both, so it cannot tell the script's
        verdict from the book's.
        """
        entry, earlier = read_sources(source_file=EARLIER_SAVES[0])
        out = io.StringIO()
        with redirect_stdout(out):
            module.report(entry, opening_gap(earlier), [])
        assert self._row(out.getvalue(), "APR, literal")[-6:] == [
            "0.131543",
            "0.1327",
            "gap",
            "-0.0012",
            "13",
            "reproduced",
        ]

    def test_a_miss_is_reported_as_one(self) -> None:
        assert module._verdict(0.132733, SCRIPT_APR) == "reproduced"
        assert module._verdict(0.131543, SCRIPT_APR) == "gap -0.0012"
        assert module._verdict(-1.44162, BOOK_SHARPE) == "gap -2.8"

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdataohlcdaily_20120517/fstx.csv changes scale")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="fstx.csv changes scale") as stopped:
            main()
        assert str(stopped.value) == "inputdataohlcdaily_20120517/fstx.csv changes scale"

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputDataOHLCDaily_20120517.mat"):
            main()

    def test_main_lets_any_other_error_through(self, monkeypatch, no_arguments) -> None:
        def broken(*_a, **_k):
            raise ValueError("a programming error keeps its traceback")

        monkeypatch.setattr(module, "run", broken)
        with pytest.raises(ValueError, match="keeps its traceback"):
            main()

    def test_main_refuses_an_argument(self, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["chan.opening_gap", "--bogus"])
        with pytest.raises(SystemExit) as refused:
            main()
        assert refused.value.code == 2


#: The Algorithmic Trading Experiments page's record of the port, as issue 358's body cites it.
EXPERIMENTS_PAGE_APR_PERCENT = "7.5"
EXPERIMENTS_PAGE_SHARPE = "0.49"

#: The two spreads and the two short tests a variant can take, the script's or the port's.
SPREADS = {"script": spread, "port": python_port_spread}
SHORT_TESTS = {"script": qualifiers, "port": python_port_qualifiers}


@pytest.fixture(scope="module")
def port(prices) -> PythonPort:
    return python_port(prices)


def _variant(prices, spread_of: str, short_test: str, reading: str) -> np.ndarray:
    """The daily returns with each of the three rule differences set to one program's."""
    op, hi, lo, cl = (prices[field].to_numpy(dtype=float) for field in FIELDS)
    held = module._held(*SHORT_TESTS[short_test](op, hi, lo, SPREADS[spread_of](cl)))
    return daily_returns(held, op, cl, reading=reading)


class TestChansPythonPort:
    """Rows 10 to 16: ``gapFutures_FSTX.py``, Chan's 2018 Python port, on the committed file.

    The vintage is the one above. The specification is the port's, which
    differs from the script's in four places.

    1. The spread is ``Close.pct_change().rolling(90).std().shift()``, dividing
       by n − 1 and first set on 2004-11-22, one row after the script's.
    2. The short test is ``Open >= Low.shift() · (1 − 0.1 · spread)``, the
       script's ``<=`` flipped, assigned after the long.
    3. The return is the momentum sign, ``positions · (cl − op) / op``.
    4. The printed Sharpe ratio divides by ``np.std``, which divides by n.

    The APR and the drawdown are the script's arithmetic. Each variant names
    which of the first three it takes from which program, and its Sharpe ratio
    divides by n − 1, as the script's does.
    """

    def test_the_comments_are_what_the_port_prints(self) -> None:
        assert (PORT_APR, PORT_SHARPE, PORT_MAX_DRAWDOWN, PORT_MAX_DRAWDOWN_DAYS) == (
            "0.074864",
            "0.494857",
            "-0.233629",
            "789",
        )

    def test_row_10_the_apr_and_the_sharpe_ratio_over_n_reproduce_the_comment(self, port) -> None:
        assert port.figures.apr == pytest.approx(0.0748641057, abs=1e-10)
        assert port.sharpe == pytest.approx(0.4948573171, abs=1e-10)
        assert matches(port.figures.apr, PORT_APR)
        assert matches(port.sharpe, PORT_SHARPE)
        assert math.copysign(1, gap(port.figures.apr, PORT_APR)) == 1
        assert math.copysign(1, gap(port.sharpe, PORT_SHARPE)) == 1

    def test_row_10_over_n_minus_1_the_sharpe_ratio_misses_the_comment(self, port) -> None:
        """So the divisor is part of the specification at the six decimals the port prints."""
        assert port.figures.sharpe == pytest.approx(0.4947335873, abs=1e-10)
        assert not matches(port.figures.sharpe, PORT_SHARPE)
        assert gap(port.figures.sharpe, PORT_SHARPE) == pytest.approx(-0.000123)

    def test_row_11_the_drawdown_and_its_days_reproduce_the_comment(self, port) -> None:
        f = port.figures
        assert f.max_drawdown == pytest.approx(-0.2336291171, abs=1e-10)
        assert f.max_drawdown_days == 789
        assert matches(f.max_drawdown, PORT_MAX_DRAWDOWN)
        assert math.copysign(1, gap(f.max_drawdown, PORT_MAX_DRAWDOWN)) == -1
        assert str(f.max_drawdown_days) == PORT_MAX_DRAWDOWN_DAYS

    def test_row_12_the_port_is_never_long(self, port) -> None:
        """Every one of the 278 days passing the long test passes the flipped short test too."""
        held = port.positions
        assert int((held == 1).sum()) == 0
        assert int((held == -1).sum()) == 1718
        assert int((held == 0).sum()) == 282
        assert int(port.longs.sum()) == 278
        assert int((port.longs & port.shorts).sum()) == 278
        assert not (port.longs & ~port.shorts).any()

    def test_the_port_s_long_test_is_the_script_s(self, prices, port) -> None:
        op, hi, lo = (prices[field].to_numpy(dtype=float) for field in ("Open", "High", "Low"))
        assert (port.longs == qualifiers(op, hi, lo, port.spread)[0]).all()

    def test_the_port_s_spread_starts_on_2004_11_22_a_row_after_the_script_s(
        self, result, port
    ) -> None:
        assert np.flatnonzero(~np.isnan(port.spread))[0] == SPREAD_LOOKBACK + 1
        assert port.days[SPREAD_LOOKBACK + 1] == day("2004-11-22")
        assert np.flatnonzero(~np.isnan(result.spread))[0] == SPREAD_LOOKBACK
        assert port.days[SPREAD_LOOKBACK] == day("2004-11-19")

    def test_the_two_spreads_qualify_the_same_days_but_one(self, prices) -> None:
        """Only 2004-11-19 differs, the one row where the script's spread is set and the port's
        is not.

        The divisor decides no day of this file. Under the script's short test
        2004-11-19 qualifies nothing on either spread, so there they agree on
        every day.
        """
        op, hi, lo, cl = (prices[field].to_numpy(dtype=float) for field in FIELDS)
        script_sd, port_sd = spread(cl), python_port_spread(cl)
        for short_test, differing in ((qualifiers, []), (python_port_qualifiers, ["2004-11-19"])):
            longs_a, shorts_a = short_test(op, hi, lo, script_sd)
            longs_b, shorts_b = short_test(op, hi, lo, port_sd)
            assert (longs_a == longs_b).all()
            assert [str(d.date()) for d in prices.index[shorts_a != shorts_b]] == differing

    def test_the_variants_compose_the_port_itself(self, prices, port) -> None:
        assert (_variant(prices, "port", "port", "momentum") == port.returns).all()

    @pytest.mark.parametrize(
        ("row", "spread_of", "short_test", "reading", "apr", "sharpe"),
        [
            (13, "script", "port", "momentum", 0.076926, 0.505364),
            (14, "port", "script", "literal", 0.132733, 1.441620),
            (15, "port", "port", "literal", -0.098670, -0.494734),
        ],
    )
    def test_each_variant_changes_one_difference(
        self, prices, row, spread_of, short_test, reading, apr, sharpe
    ) -> None:
        """Row 13 is the port on the script's spread, row 14 the script on the port's spread,
        and row 15 the port with the script's sign. Each Sharpe ratio divides by n − 1."""
        f = figures(_variant(prices, spread_of, short_test, reading))
        assert f.apr == pytest.approx(apr, abs=SIX)
        assert f.sharpe == pytest.approx(sharpe, abs=SIX)

    def test_row_14_is_the_script_s_literal_reading_day_for_day(self, prices, result) -> None:
        assert (_variant(prices, "port", "script", "literal") == result.literal).all()

    def test_row_15_is_the_port_s_returns_negated(self, prices, port) -> None:
        assert (_variant(prices, "port", "port", "literal") == -port.returns).all()

    def test_row_16_the_experiments_page_rounds_the_comment(self, port) -> None:
        assert (EXPERIMENTS_PAGE_APR_PERCENT, EXPERIMENTS_PAGE_SHARPE) == ("7.5", "0.49")
        assert matches(100 * float(PORT_APR), EXPERIMENTS_PAGE_APR_PERCENT)
        assert matches(float(PORT_SHARPE), EXPERIMENTS_PAGE_SHARPE)
        assert matches(100 * port.figures.apr, EXPERIMENTS_PAGE_APR_PERCENT)
        assert matches(port.sharpe, EXPERIMENTS_PAGE_SHARPE)

    def test_the_spread_is_the_90_row_deviation_over_n_minus_1_one_row_later(self) -> None:
        closes = 100 * np.cumprod(1 + np.tile([0.01, -0.01, 0.02], 40))
        found = python_port_spread(closes)
        assert np.isnan(found[: SPREAD_LOOKBACK + 1]).all()
        # returns[k] is the return ending on row k + 1, so row 91 reads rows 1 to 90.
        returns = closes[1:] / closes[:-1] - 1
        assert found[91] == pytest.approx(np.std(returns[:90], ddof=1))
        assert found[92] == pytest.approx(np.std(returns[1:91], ddof=1))
        assert found[91] != pytest.approx(np.std(returns[:90], ddof=0))

    def test_an_open_clearing_the_previous_high_is_short(self) -> None:
        longs, shorts = python_port_qualifiers(*TestTheRules._day(101.0))
        assert longs.tolist() == shorts.tolist() == [False, True]
        assert module._held(longs, shorts).tolist() == [0, -1]

    def test_the_short_test_is_non_strict_and_flipped(self) -> None:
        threshold = 90.0 * (1 - ENTRY_ZSCORE * 0.1)
        for op, held in ((threshold, -1), (np.nextafter(threshold, 0), 0), (95.0, -1)):
            found = module._held(*python_port_qualifiers(*TestTheRules._day(op)))
            assert found.tolist() == [0, held]

    def test_a_nan_spread_qualifies_nothing(self) -> None:
        for op in (200.0, 95.0, 1.0):
            longs, shorts = python_port_qualifiers(*TestTheRules._day(op, sd=np.nan))
            assert not longs.any()
            assert not shorts.any()

    def test_the_sharpe_ratio_divides_by_n(self) -> None:
        daily = np.array([0.0, 0.02, -0.01, 0.0])
        assert python_port_sharpe(daily) == pytest.approx(
            math.sqrt(252) * daily.mean() / daily.std(ddof=0)
        )
        assert python_port_sharpe(daily) != pytest.approx(figures(daily).sharpe)

    def test_the_sharpe_ratio_keeps_a_negative_mean_s_sign(self) -> None:
        """Every series pinned above has a positive mean, so this one does not."""
        daily = np.array([0.0, -0.02, 0.01, 0.0])
        expected = math.sqrt(252) * daily.mean() / daily.std(ddof=0)
        assert expected < 0
        assert python_port_sharpe(daily) == pytest.approx(expected)
        # The mean is −0.0025 and the variance over n is 1.1875e-4.
        assert python_port_sharpe(daily) == pytest.approx(
            -math.sqrt(252) * 0.0025 / math.sqrt(1.1875e-4)
        )
        assert python_port_sharpe(daily) == pytest.approx(-3.641862, abs=SIX)

    def test_the_run_prints_the_port_beside_its_comments(self, printed) -> None:
        tail = printed[printed.index("Chan's Python port, gapFutures_FSTX.py, on the same save") :]
        assert TestTheReport._row(tail, "APR")[-3:] == ["0.074864", "0.074864", "reproduced"]
        assert TestTheReport._row(tail, "Sharpe ratio, over n")[-3:] == [
            "0.494857",
            "0.494857",
            "reproduced",
        ]
        assert TestTheReport._row(tail, "maximum drawdown ")[-3:] == [
            "-0.233629",
            "-0.233629",
            "reproduced",
        ]
        assert TestTheReport._row(tail, "maximum drawdown days")[-3:] == [
            "789",
            "789",
            "reproduced",
        ]
        assert "long on 0 days, short on 1718, flat on 282, both tests passed on 278" in tail
        assert tail.rstrip().endswith("Exploratory. docs/replication-log.md carries the verdicts.")

    @staticmethod
    def _report(port: PythonPort) -> str:
        out = io.StringIO()
        with redirect_stdout(out):
            module.report_python_port(port)
        return out.getvalue()

    def test_a_figure_off_the_comment_reads_as_a_gap(self, port) -> None:
        """The port's returns scaled by 1.01 move the APR off the comment's six decimals."""
        moved = PythonPort(
            days=port.days,
            spread=port.spread,
            longs=port.longs,
            shorts=port.shorts,
            positions=port.positions,
            returns=port.returns * 1.01,
        )
        row = TestTheReport._row(self._report(moved), "APR")
        assert row[2] == PORT_APR
        assert row[3] == "gap"
        assert "reproduced" not in row

    def test_the_header_and_both_count_read_their_own_inputs(self) -> None:
        """Three days whose longs are not a subset of its shorts, so both differs from long."""
        synthetic = PythonPort(
            days=pd.DatetimeIndex(["2020-01-01", "2020-01-02", "2020-01-03"]),
            spread=np.array([np.nan, 0.1, 0.1]),
            longs=np.array([False, True, True]),
            shorts=np.array([False, False, True]),
            positions=np.array([0.0, 1.0, -1.0]),
            returns=np.array([0.0, 0.01, -0.005]),
        )
        lines = self._report(synthetic).splitlines()
        assert lines[0] == ""
        assert lines[1] == "Chan's Python port, gapFutures_FSTX.py, on the same save"
        assert lines[2].split() == ["Figure", "Computed", "Port", "Verdict"]
        assert lines[-2].strip() == (
            "long on 1 days, short on 1, flat on 1, both tests passed on 1"
        )
        assert lines[-1] == "  Exploratory. docs/replication-log.md carries the verdicts."
