"""The pins for Bollinger bands on GLD and USO, *Algorithmic Trading*'s Example 3.2.

This file is the single authority for every number any prose surface quotes
about Example 3.2, with one exception, in ``blog/bollinger-band-lessons.md``.
That post also quotes Example 3.1's figures, which ``tests/test_price_spread.py``
holds, and its figure's labels, which ``tests/test_bollinger_figures.py`` holds.
README lists what the post says that nothing asserts. ``docs/replication-log.md``
carries the verdicts and points here row by row.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** ``inputdata_etf/gld.csv`` and ``inputdata_etf/uso.csv``, two of
  the 67 ETFs lifted from Chan's ``inputData_ETF.mat``, chan-mat, adjusted,
  saved 2012-04-10, 1,500 days from 2006-04-26 to 2012-04-09.
  ``tests/test_price_spread.py`` holds the members to the row of
  ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``.
- **Specification.** ``bollinger.m`` at the mirror commit :mod:`chan.bollinger`
  names. Example 3.1's price spread, its 20-row rolling hedge ratio from
  ``ols(y, [x ones])`` and its first 20 rows dropped, then the 20-row z-score
  from ``movingAvg`` and ``movingStd``. One unit long below −1 until above 0,
  one unit short above 1 until below 0, carried forward by ``fillMissingData``.
  The return is profit over gross dollars with a NaN day set to 0, the APR is
  compounded over 252 days a year and the Sharpe ratio uses MATLAB's n − 1
  ``std``, over 1,480 rows.

Each figure is pinned twice. Once at the six decimals the script's ``%f``
prints, against its closing comment, and once at eight, so a later change
cannot move it inside the printed digits unnoticed. The book's own rounding at
location 1559 is pinned beside them.

Exploratory. Reproducing Chan's figures spends the 2006 to 2012 sample on a
rule he chose. It first ran here on 2026-10-05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan import bollinger as module
from chan import price_spread
from chan.bollinger import (
    BOOK_BOLLINGER,
    ENTRY_ZSCORE,
    EXIT_ZSCORE,
    SCRIPT_BOLLINGER,
    ExampleThreeTwo,
    band_units,
    bollinger_band,
    example_three_two,
    main,
    run,
)
from chan.matlab_helpers import (
    calculate_max_dd,
    drawdown_path,
    smart_moving_avg,
    smart_moving_std,
)
from chan.price_spread import LOOKBACK, SCRIPT_PRICE_SPREAD, read_sources, zscore
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

SPEC = (
    "inputdata_etf/ GLD and USO closes over 1,500 days, 20-row rolling hedge ratio, "
    "first 20 rows dropped, one unit entered beyond a 20-row z-score of 1 from movingAvg "
    "and movingStd and exited at 0, profit over gross dollars, compounded APR, n - 1 "
    "Sharpe ratio, 1,480 rows"
)

# --- the committed file --------------------------------------------------------


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> ExampleThreeTwo:
    return example_three_two(sources[1])


@pytest.fixture(scope="module")
def by_n(sources) -> ExampleThreeTwo:
    """The run with ``smartMovingStd``, which divides by n, in place of ``movingStd``."""
    _, closes = sources
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(price_spread, "moving_std", smart_moving_std)
        return example_three_two(closes)


def _zero_padded_lag(x: np.ndarray) -> np.ndarray:
    """A ``lag`` that pads its first row with 0 rather than NaN."""
    values = np.asarray(x, dtype=float)
    shifted = np.zeros_like(values)
    shifted[1:] = values[:-1]
    return shifted


class TestTheSpecification:
    def test_the_bands_are_the_scripts(self) -> None:
        """``entryZscore = 1`` and ``exitZscore = 0``, as location 1559 states."""
        assert (ENTRY_ZSCORE, EXIT_ZSCORE, LOOKBACK) == (1, 0, 20)

    def test_the_run_trades_example_3_1s_price_spread(self, sources, result) -> None:
        """``bollinger.m`` keeps ``PriceSpread.m``'s spread, hedge ratio and z-score."""
        _, closes = sources
        spread = price_spread.example_three_one(closes).price_spread
        signal = result.bollinger.signal
        np.testing.assert_array_equal(signal.value, spread.signal.value)
        np.testing.assert_array_equal(signal.unit_dollars, spread.signal.unit_dollars)
        np.testing.assert_array_equal(result.zscore, zscore(spread.signal.value))
        np.testing.assert_array_equal(result.linear.daily, spread.daily)

    def test_the_runs_keep_1480_rows_from_2006_05_24(self, result: ExampleThreeTwo) -> None:
        days = result.bollinger.signal.days
        assert len(days) == len(result.bollinger.daily) == 1480, SPEC
        assert (str(days[0].date()), str(days[-1].date())) == ("2006-05-24", "2012-04-09"), SPEC

    def test_the_units_are_only_ever_minus_1_0_or_1(self, result: ExampleThreeTwo) -> None:
        """One unit at most, long or short, as location 1548 says. Over the 1,480 rows the
        run holds a short on 547, nothing on 334 and a long on 599."""
        values, counts = np.unique(result.bollinger.units, return_counts=True)
        assert list(values) == [-1.0, 0.0, 1.0], SPEC
        assert list(counts) == [547, 334, 599], SPEC

    def test_the_band_changes_its_units_on_162_days(self, result: ExampleThreeTwo) -> None:
        """Example 3.1's linear rule moves its units on every day after its first."""
        assert int(np.count_nonzero(np.diff(result.bollinger.units))) == 162, SPEC
        assert int(np.count_nonzero(np.diff(result.linear.units[LOOKBACK - 1 :]))) == 1460, SPEC

    def test_the_162_changes_are_77_entries_76_exits_and_9_turns(
        self, result: ExampleThreeTwo
    ) -> None:
        """An entry goes from flat to a unit, an exit from a unit to flat, and a turn from
        one side to the other in a single day, which
        ``TestBandUnits::test_a_long_becomes_a_short_in_one_day`` shows these thresholds
        allow. The run starts flat and ends holding a unit, so entries outnumber exits by
        one."""
        units = result.bollinger.units
        before, after = units[:-1], units[1:]
        entries = int(((before == 0) & (after != 0)).sum())
        exits = int(((before != 0) & (after == 0)).sum())
        turns = int((before * after == -1).sum())
        assert (entries, exits, turns) == (77, 76, 9), SPEC
        assert entries + exits + turns == int(np.count_nonzero(np.diff(units))) == 162, SPEC
        assert (units[0], units[-1] != 0) == (0.0, True), SPEC

    def test_62_of_the_334_flat_days_have_a_hedge_ratio_below_zero(
        self, result: ExampleThreeTwo
    ) -> None:
        """Two counts over the same 1,480 days that are both 334 but count different days.

        The band is flat on 334 days, and the 20-day hedge ratio is below zero on 334,
        which ``tests/test_price_spread.py`` pins for Example 3.1. Only 62 days are both.
        """
        flat = result.bollinger.units == 0
        negative = result.bollinger.signal.hedge < 0
        assert (int(flat.sum()), int(negative.sum())) == (334, 334), SPEC
        assert int((flat & negative).sum()) == 62, SPEC

    def test_the_hedge_ratio_changes_on_every_one_of_the_1479_steps(
        self, result: ExampleThreeTwo
    ) -> None:
        """So a held unit's GLD leg is resized every day, even on a day its units stand still.

        The 20-row hedge ratio is refitted on every one of the 1,480 kept rows of
        ``inputdata_etf/`` GLD and USO, and no two neighbouring fits are equal. That covers
        the 1,060 days the band holds a unit unchanged from the day before.
        """
        hedge = result.bollinger.signal.hedge
        assert len(hedge) == 1480, SPEC
        assert int(np.count_nonzero(np.diff(hedge))) == 1479, SPEC
        units = result.bollinger.units
        held = (units[1:] == units[:-1]) & (units[1:] != 0)
        assert int(held.sum()) == 1060, SPEC
        assert (np.diff(hedge)[held] != 0).all(), SPEC


class TestTheFigures:
    """The APR and the Sharpe ratio, beside the script's comment and the book."""

    def test_the_apr_is_chans_0_178249(self, result: ExampleThreeTwo) -> None:
        apr = result.bollinger.apr
        assert apr == pytest.approx(0.17824928, abs=5e-9), SPEC
        assert f"{apr:f}" == SCRIPT_BOLLINGER[0] == "0.178249", SPEC
        assert round(100 * apr, 1) == BOOK_BOLLINGER[0] == 17.8, SPEC

    def test_the_sharpe_ratio_is_chans_0_964673(self, result: ExampleThreeTwo) -> None:
        sharpe = result.bollinger.sharpe
        assert sharpe == pytest.approx(0.96467289, abs=5e-9), SPEC
        assert f"{sharpe:f}" == SCRIPT_BOLLINGER[1] == "0.964673", SPEC
        assert round(sharpe, 2) == BOOK_BOLLINGER[1] == 0.96, SPEC

    def test_the_first_position_is_held_into_2006_06_22(self, result: ExampleThreeTwo) -> None:
        """``movingStd`` first fills on the 20th kept row, 2006-06-21, and the band enters
        there. Its position earns from the next close, the same days as Example 3.1's."""
        run_ = result.bollinger
        first_z = np.flatnonzero(np.isfinite(result.zscore))[0]
        first_units = np.flatnonzero(run_.units)[0]
        first_return = np.flatnonzero(run_.daily)[0]
        assert first_z == first_units == LOOKBACK - 1, SPEC
        assert str(run_.signal.days[first_units].date()) == "2006-06-21", SPEC
        assert str(run_.signal.days[first_return].date()) == "2006-06-22", SPEC

    def test_no_kept_row_sits_exactly_on_a_band(self, result: ExampleThreeTwo) -> None:
        """So no figure here can tell a strict comparison from an inclusive one, and only
        ``TestTheBandOnASignal::test_a_z_score_on_a_band_edge_trades_as_the_script_does``
        reaches the edges through the rule."""
        z = result.zscore
        assert int(np.isnan(z).sum()) == LOOKBACK - 1, SPEC
        assert not np.isin(z, [-1.0, 0.0, 1.0]).any(), SPEC


class TestTheClaim:
    """Location 1559: "quite an improvement from the linear mean reversal strategy".

    The criterion, written on issue 341 after the first transcription ran: the APR and
    the Sharpe ratio are both above Example 3.1's price spread, 0.108335 and 0.589651.
    """

    def test_both_figures_are_above_the_linear_rules(self, result: ExampleThreeTwo) -> None:
        linear = result.linear
        assert (f"{linear.apr:f}", f"{linear.sharpe:f}") == SCRIPT_PRICE_SPREAD, SPEC
        assert result.bollinger.apr > linear.apr, SPEC
        assert result.bollinger.sharpe > linear.sharpe, SPEC

    def test_the_band_leads_by_0_069915_and_0_375022(self, result: ExampleThreeTwo) -> None:
        """The criterion asks for no margin. These gaps are what a margin would have faced."""
        apr_gap = result.bollinger.apr - result.linear.apr
        sharpe_gap = result.bollinger.sharpe - result.linear.sharpe
        assert (f"{apr_gap:+f}", f"{sharpe_gap:+f}") == ("+0.069915", "+0.375022"), SPEC


class TestTheDrawdowns:
    """``calculateMaxDD`` on each rule's ``cumprod(1 + ret) − 1``, with where each one falls.

    The book prints neither rule's. ``blog/bollinger-band-lessons.md`` sets them beside the
    two figures location 1559 compares, as a second view of the same claim. Both rules'
    longest spells start the day after one high, 2008-12-05, and each trough falls
    inside its own spell.
    """

    @pytest.mark.parametrize(
        ("rule", "deepest", "percent", "trough", "longest", "spell"),
        [
            (
                "bollinger",
                -0.21831770065726175,
                "-21.83",
                "2009-05-21",
                252,
                ("2008-12-05", "2008-12-08", "2009-12-07"),
            ),
            (
                "linear",
                -0.34239469001295364,
                "-34.24",
                "2009-01-06",
                640,
                ("2008-12-05", "2008-12-08", "2011-06-22"),
            ),
        ],
    )
    def test_the_deepest_drawdown_and_the_longest_spell_below_a_high(
        self, result: ExampleThreeTwo, rule, deepest, percent, trough, longest, spell
    ) -> None:
        run_ = getattr(result, rule)
        days = run_.signal.days
        cumret = np.cumprod(1 + run_.daily) - 1
        found, rows = calculate_max_dd(cumret)
        assert found == pytest.approx(deepest, abs=1e-10), SPEC
        assert f"{100 * found:.2f}" == percent, SPEC
        assert rows == longest, SPEC
        _, drawdown, duration = drawdown_path(cumret)
        bottom = int(np.argmin(drawdown))
        assert drawdown[bottom] == found
        assert str(days[bottom].date()) == trough, SPEC
        last = int(np.argmax(duration))
        first = last - rows + 1
        assert drawdown[first - 1] == 0 and drawdown[first] < 0
        assert tuple(str(days[row].date()) for row in (first - 1, first, last)) == spell, SPEC
        assert first <= bottom <= last

    def test_the_band_falls_less_far_and_regains_its_high_in_under_half_the_time(
        self, result: ExampleThreeTwo
    ) -> None:
        band, linear = (
            calculate_max_dd(np.cumprod(1 + run_.daily) - 1)
            for run_ in (result.bollinger, result.linear)
        )
        assert band[0] > linear[0] and 2 * band[1] < linear[1], SPEC


class TestTheDivisor:
    """``smartMovingStd`` divides by n where ``movingStd`` divides by n − 1.

    Example 3.1's linear rule cannot see the difference, because a constant on every
    unit cancels out of profit over gross dollars. This rule compares the z-score with a
    fixed threshold, so the scale decides which days trade. ``bollinger.m`` calls
    ``movingStd``, so n − 1 is the transcription and n is a diagnostic.
    """

    def test_dividing_by_n_gives_0_183306_and_0_984872(self, by_n: ExampleThreeTwo) -> None:
        """Rounded as the book rounds, that is 18.3 percent and 0.98, against 17.8 and 0.96."""
        assert by_n.bollinger.apr == pytest.approx(0.18330633, abs=5e-9), SPEC
        assert by_n.bollinger.sharpe == pytest.approx(0.98487233, abs=5e-9), SPEC
        assert (f"{by_n.bollinger.apr:f}", f"{by_n.bollinger.sharpe:f}") != SCRIPT_BOLLINGER
        assert (round(100 * by_n.bollinger.apr, 1), round(by_n.bollinger.sharpe, 2)) == (
            18.3,
            0.98,
        ), SPEC

    def test_dividing_by_n_moves_the_apr_by_0_005057_and_the_sharpe_ratio_by_0_020199(
        self, result: ExampleThreeTwo, by_n: ExampleThreeTwo
    ) -> None:
        apr_gap = by_n.bollinger.apr - result.bollinger.apr
        sharpe_gap = by_n.bollinger.sharpe - result.bollinger.sharpe
        assert (f"{apr_gap:+f}", f"{sharpe_gap:+f}") == ("+0.005057", "+0.020199"), SPEC

    def test_dividing_by_n_scales_every_z_score_by_the_root_of_20_over_19(
        self, result: ExampleThreeTwo, by_n: ExampleThreeTwo
    ) -> None:
        """A 20-row deviation over n is the one over n − 1 times √(19/20), so every z-score
        grows by √(20/19), about 1.0260, and none changes sign."""
        finite = np.isfinite(result.zscore)
        np.testing.assert_array_equal(np.isfinite(by_n.zscore), finite)
        np.testing.assert_allclose(
            by_n.zscore[finite], result.zscore[finite] * np.sqrt(20 / 19), rtol=1e-12, atol=0
        )
        assert f"{np.sqrt(20 / 19):.4f}" == "1.0260"

    def test_dividing_by_n_puts_21_more_days_beyond_the_band_and_moves_15_days_units(
        self, result: ExampleThreeTwo, by_n: ExampleThreeTwo
    ) -> None:
        """Of the 1,461 days with a z-score, 756 sit beyond ±1 under n − 1 and 777 under n.
        The units differ on 15 of the 1,480 days, which is all it takes to move both
        figures."""

        def beyond(z: np.ndarray) -> int:
            return int((np.abs(z[np.isfinite(z)]) > ENTRY_ZSCORE).sum())

        assert int(np.isfinite(result.zscore).sum()) == 1461, SPEC
        assert (beyond(result.zscore), beyond(by_n.zscore)) == (756, 777), SPEC
        assert int((result.bollinger.units != by_n.bollinger.units).sum()) == 15, SPEC

    def test_the_exit_test_passes_on_the_same_days_but_one_more_exit_happens(
        self, result: ExampleThreeTwo, by_n: ExampleThreeTwo
    ) -> None:
        """A positive factor keeps every z-score's sign, so ``z > 0`` and ``z < 0`` hold on
        the same rows under either divisor. A position has to be open to close, though.
        All 76 exits under n − 1 fall on the same rows under n, and the run divided by n
        has a 77th on 2007-06-07. It closes a short entered on 2007-05-29 that the n − 1
        run never opened."""
        with np.errstate(invalid="ignore"):
            for test in (np.greater, np.less):
                np.testing.assert_array_equal(
                    test(by_n.zscore, EXIT_ZSCORE), test(result.zscore, EXIT_ZSCORE)
                )

        def exits(units: np.ndarray) -> set[int]:
            return set((np.flatnonzero((units[:-1] != 0) & (units[1:] == 0)) + 1).tolist())

        under_n_less_1, under_n = exits(result.bollinger.units), exits(by_n.bollinger.units)
        assert (len(under_n_less_1), len(under_n)) == (76, 77), SPEC
        assert under_n_less_1 < under_n, SPEC
        (extra,) = under_n - under_n_less_1
        days = result.bollinger.signal.days
        assert str(days[extra].date()) == "2007-06-07", SPEC
        held = by_n.bollinger.units[:extra]
        entered = int(np.flatnonzero(held != -1)[-1]) + 1
        assert str(days[entered].date()) == "2007-05-29", SPEC
        assert held[entered - 1] == 0, SPEC
        assert not result.bollinger.units[entered:extra].any(), SPEC

    def test_swapping_the_average_too_moves_nothing_further(
        self, sources, by_n: ExampleThreeTwo
    ) -> None:
        _, closes = sources
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(price_spread, "moving_std", smart_moving_std)
            patch.setattr(price_spread, "moving_avg", smart_moving_avg)
            both = example_three_two(closes)
        np.testing.assert_array_equal(both.bollinger.daily, by_n.bollinger.daily)
        # smartMovingAvg differs from movingAvg only by skipping what is not finite, and
        # the spread on the kept rows has nothing for it to skip.
        assert np.isfinite(by_n.bollinger.signal.value).all(), SPEC


class TestWhatMovesNothing:
    def test_lag_padding_with_0_or_nan_gives_the_same_returns(self, sources, result) -> None:
        """Neither mirror holds ``lag.m``. A NaN pad makes the first row's return NaN, and
        a zero pad divides by a price of 0, so the first row's profit is NaN over zero gross
        dollars. Either NaN is set to 0."""
        _, closes = sources
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(price_spread, "lag1", _zero_padded_lag)
            zero_padded = example_three_two(closes)
        np.testing.assert_array_equal(zero_padded.bollinger.daily, result.bollinger.daily)


class TestTheRun:
    def test_it_prints_each_figure_beside_chans(self, sources, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "read_sources", lambda *_a, **_k: sources)
        run()
        out = capsys.readouterr().out
        for line, figures in (
            ("Bollinger band, APR", ("0.178249", "0.178249", "17.8%")),
            ("Bollinger band, Sharpe ratio", ("0.964673", "0.964673", "0.96")),
            ("Linear rule, Example 3.1, APR", ("0.108335", "0.108335", "10.9%")),
            ("Linear rule, Example 3.1, Sharpe ratio", ("0.589651", "0.589651", "0.59")),
        ):
            row = next(r for r in out.splitlines() if r.strip().startswith(line + " "))
            assert row.split()[-3:] == list(figures), row
        lines = [r.strip() for r in out.splitlines()]
        header = lines.index(next(r for r in lines if r.startswith("Figure ")))
        assert lines[header].split() == ["Figure", "Computed", "Script", "Book"]
        assert lines[header + 1].startswith("Bollinger band, APR ")
        assert "inputdata_etf/gld.csv" in out and "inputdata_etf/uso.csv" in out
        assert out.count("lifted from inputData_ETF.mat") == 2
        assert "2006-05-24 to 2012-04-09, 1480 trading days after the first 20 are dropped" in out
        assert "z-score beyond 1 and exited at 0" in out
        assert "Exploratory" in out and "docs/replication-log.md carries the verdicts" in out


# --- the band on synthetic arrays ------------------------------------------------


def _bools(*rows: int, n: int = 6) -> np.ndarray:
    flags = np.zeros(n, dtype=bool)
    flags[list(rows)] = True
    return flags


NONE = _bools()


class TestBandUnits:
    """``band_units`` on arrays no real row reaches, for the rule and for issue 342."""

    def test_a_long_is_held_from_its_entry_until_its_exit(self) -> None:
        units = band_units(_bools(1), _bools(4), NONE, NONE)
        assert list(units) == [0, 1, 1, 1, 0, 0]

    def test_a_short_is_the_mirror_at_minus_1(self) -> None:
        units = band_units(NONE, NONE, _bools(2), _bools(3))
        assert list(units) == [0, 0, -1, 0, 0, 0]

    def test_a_row_with_no_signal_holds_yesterdays_units(self) -> None:
        """``fillMissingData``: a repeated entry changes nothing, and nothing decays."""
        units = band_units(_bools(1, 3), NONE, NONE, NONE)
        assert list(units) == [0, 1, 1, 1, 1, 1]

    def test_an_exit_with_nothing_held_holds_nothing(self) -> None:
        units = band_units(NONE, _bools(0, 2), NONE, _bools(1))
        assert list(units) == [0, 0, 0, 0, 0, 0]

    def test_an_exit_wins_a_row_that_also_enters(self) -> None:
        """``bollinger.m`` sets the entry and then the exit, so the exit is written last."""
        units = band_units(_bools(1, 3), _bools(3), NONE, NONE)
        assert list(units) == [0, 1, 1, 0, 0, 0]

    def test_an_entry_on_the_first_row_overwrites_its_0(self) -> None:
        """Row 1 is set to 0 before the entries are written, so an entry there stands."""
        assert band_units(_bools(0), NONE, NONE, NONE)[0] == 1
        assert band_units(NONE, NONE, _bools(0), NONE)[0] == -1

    def test_a_long_becomes_a_short_in_one_day(self) -> None:
        """At these thresholds a z-score above 1 also clears 0, so the long's exit and the
        short's entry fall on one row."""
        z = np.array([np.nan, -1.5, -0.5, 1.5, 0.5, -0.5])
        units = band_units(z < -1, z > 0, z > 1, z < 0)
        assert list(units) == [0, 1, 1, -1, -1, 0]

    def test_a_long_and_a_short_held_together_net_to_0(self) -> None:
        """Bands whose exits sit beyond the other side's entry can hold both at once."""
        units = band_units(_bools(1), NONE, _bools(2), NONE)
        assert list(units) == [0, 1, 0, 0, 0, 0]

    def test_a_z_score_of_exactly_minus_1_or_1_enters_nothing(self) -> None:
        z = np.array([0.5, -1.0, 1.0, -1.0, 1.0, 0.5])
        units = band_units(z < -1, z > 0, z > 1, z < 0)
        assert list(units) == [0, 0, 0, 0, 0, 0]

    def test_a_z_score_of_exactly_0_exits_nothing(self) -> None:
        z = np.array([0.5, -1.5, 0.0, 0.0, 1.5, 0.0])
        units = band_units(z < -1, z > 0, z > 1, z < 0)
        assert list(units) == [0, 1, 1, 1, -1, -1]

    def test_a_nan_z_score_holds_yesterdays_units(self) -> None:
        """A NaN compares false on all four, so a NaN row signals nothing."""
        z = np.array([np.nan, -1.5, np.nan, np.nan, 0.5, np.nan])
        with np.errstate(invalid="ignore"):
            units = band_units(z < -1, z > 0, z > 1, z < 0)
        assert list(units) == [0, 1, 1, 1, 0, 0]

    def test_the_kalman_filters_exits_on_the_entry_band(self) -> None:
        """``KF_beta_EWA_EWC.m`` exits a long at ``e > -sqrt(Q)``, its own entry band."""
        e = np.array([0.0, -2.0, -1.5, -0.5, 2.0, 0.5])
        root_q = np.ones(6)
        units = band_units(e < -root_q, e > -root_q, e > root_q, e < root_q)
        assert list(units) == [0, 1, 1, 0, -1, 0]

    def test_four_arrays_of_another_length_are_refused(self) -> None:
        with pytest.raises(ValueError, match="one length"):
            band_units(_bools(), _bools(), _bools(), _bools(n=5))

    def test_a_two_dimensional_array_is_refused(self) -> None:
        flags = np.zeros((3, 2), dtype=bool)
        with pytest.raises(ValueError, match="one-dimensional"):
            band_units(flags, flags, flags, flags)

    @pytest.mark.parametrize("slot", range(4))
    @pytest.mark.parametrize("dtype", [int, float])
    def test_an_array_of_0s_and_1s_in_place_of_a_boolean_is_refused(self, slot, dtype) -> None:
        """An integer array indexes by position, so ``[0, 1, 0, 0, 0, 0]`` would set rows 0
        and 1 rather than row 1, silently. Every slot is checked, entries and exits both."""
        arrays = [NONE, NONE, NONE, NONE]
        arrays[slot] = _bools(1).astype(dtype)
        with pytest.raises(ValueError, match="four boolean arrays"):
            band_units(*arrays)


DAYS = pd.bdate_range("2020-01-01", periods=8)


class TestTheBandOnASignal:
    def test_the_thresholds_reach_the_comparisons(self) -> None:
        """Every real-data pin runs at 1 and 0, so a band that dropped either would hide."""
        x = np.arange(1.0, 9.0)
        signal = price_spread.price_spread(
            DAYS, x, 3.0 * x + np.array([0.1, -0.2, 0.3, 0.0, -0.1, 0.2, -0.3, 0.1]), 3
        )
        z = zscore(signal.value, 3)
        with np.errstate(invalid="ignore"):
            for entry, exit_ in ((1, 0), (0.5, 0), (0.5, -0.5), (2, 1)):
                run_, traded = bollinger_band(signal, 3, entry, exit_)
                np.testing.assert_array_equal(traded, z)
                np.testing.assert_array_equal(
                    run_.units, band_units(z < -entry, z > -exit_, z > entry, z < exit_)
                )
                np.testing.assert_array_equal(
                    run_.positions, run_.units[:, None] * signal.unit_dollars
                )

    @pytest.mark.parametrize(
        ("z", "units"),
        [
            ([np.nan, -1.0, 1.0, -1.0, 1.0], [0, 0, 0, 0, 0]),
            ([np.nan, -1.5, 0.0, 1.5, 0.0], [0, 1, 1, -1, -1]),
        ],
    )
    def test_a_z_score_on_a_band_edge_trades_as_the_script_does(
        self, monkeypatch, z, units
    ) -> None:
        """``bollinger.m`` compares strictly, so exactly −1 or 1 enters nothing and exactly
        0 exits nothing. No real row lands on an edge, so the z-score is planted."""
        x = np.arange(1.0, 9.0)
        signal = price_spread.price_spread(DAYS, x, 3.0 * x + 0.1 * (-1.0) ** x, 3)
        monkeypatch.setattr(module, "zscore", lambda *_a, **_k: np.array(z))
        run_, _ = bollinger_band(signal, 3)
        assert list(run_.units) == units

    def test_another_lookback_reaches_the_z_score_and_the_linear_rule(self, sources) -> None:
        _, closes = sources
        result = example_three_two(closes, lookback=10)
        assert len(result.bollinger.daily) == 1490
        assert np.flatnonzero(np.isfinite(result.zscore))[0] == 9
        np.testing.assert_array_equal(
            result.linear.daily,
            price_spread.linear_mean_reversion(result.bollinger.signal, 10).daily,
        )


class TestTheRefusals:
    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "read_sources", fail)
        monkeypatch.setattr("sys.argv", ["bollinger"])
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputData_ETF.mat"),
            WindowCrossesScaleBreak("inputdata_etf/uso.csv changes scale on 2009-01-02"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "read_sources", refuse)
        monkeypatch.setattr("sys.argv", ["bollinger"])
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
