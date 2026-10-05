"""The pins for cross-sectional momentum, *Algorithmic Trading*'s Example 6.2.

This file is the single authority for every number any prose surface quotes
about Example 6.2. ``docs/replication-log.md`` Entry 17 carries the verdicts and
points here row by row.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** ``inputdataohlcdaily_stocks_20120424/``, the 497 stocks lifted
  from Chan's ``inputDataOHLCDaily_stocks_20120424.mat``, saved 2012-04-25,
  read for the Close column. Its identity is the row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py`` that ``TestTheVintage`` holds the
  members to. The file is the S&P 500 as Chan held it on 2012-04-24, so every
  figure is a figure about survivors.
- **Specification.** ``kentdaniel.m`` at the mirror commit
  :mod:`chan.cross_sectional_momentum` names, with ``lag`` read as a one-row
  shift. A 252-row ranking return, the 50 highest long and the 50 lowest
  short, each row's marks held 25 rows, each day's summed return over
  2 · 50 · 25. Book two's ``smartstd`` and ``calculateMaxDD``. Every
  annualisation uses 252 days, with no risk-free rate and no cost. A reading
  pin also names the one thing its reading changes.

The script's figures are pinned at the precision that is real, six decimals
for the returns and the drawdown and four for the Sharpe ratio, and again as
``kentdaniel.m``'s ``fprintf`` formats them, against the strings its comment
lines print. The readings are pinned at four decimals, which
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297) declared
before any of them was computed, alongside the rule deciding whether one lands.

Exploratory. Reproducing Chan's figures spends the 2007 to 2012 sample on a
rule he chose. It first ran here on 2026-10-04.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan import cross_sectional_momentum as module
from chan.cross_sectional_momentum import (
    BOOK_APR_PERCENT,
    BOOK_CRISIS_APR_PERCENT,
    BOOK_SHARPE,
    HOLD_DAYS,
    LOOKBACK,
    PRICE_FILE,
    READINGS,
    SCRIPT_APR,
    SCRIPT_ARITHMETIC,
    SCRIPT_MAX_DD,
    SCRIPT_MAX_DDD,
    SCRIPT_SHARPE,
    SKIP,
    TOP_N,
    TRADING_DAYS,
    WINDOWS,
    Figures,
    cohorts_held,
    daily_returns,
    formations,
    lagged_ranking_returns,
    lands_the_book,
    lands_the_crisis,
    main,
    momentum,
    one_cohort_positions,
    overlapping_positions,
    ranking_returns,
    read_closes,
    report,
    run,
    script_as_printed,
    stabilised,
    window_figures,
)
from chan.matlab_helpers import round_half_away, smartstd_first_edition
from chan.series import (
    WindowCrossesScaleBreak,
    refuse_window_crossing_a_break,
    scale_breaks,
)
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "inputdataohlcdaily_stocks_20120424/ Close, kentdaniel.m as printed: 252-row ranking "
    "return, top and bottom 50, marks held 25 rows, each day over 2 * 50 * 25"
)

# --- the committed file --------------------------------------------------------


@pytest.fixture(scope="module")
def source():
    return read_closes()


@pytest.fixture(scope="module")
def closes(source) -> pd.DataFrame:
    return source[1]


@pytest.fixture(scope="module")
def results(closes) -> dict[str, dict[str, Figures]]:
    return momentum(closes)


@pytest.fixture(scope="module")
def script(results) -> Figures:
    return results["R0"]["2007"]


class TestTheSpecification:
    def test_the_rule_is_kentdaniel_m(self) -> None:
        assert (LOOKBACK, HOLD_DAYS, TOP_N, TRADING_DAYS) == (252, 25, 50, 252)
        assert SKIP == 21

    def test_the_source_is_chans_2012_file(self) -> None:
        assert PRICE_FILE == "inputDataOHLCDaily_stocks_20120424.mat"

    def test_the_readings_are_the_five_the_issue_declared(self) -> None:
        """A sixth reading is an edit to this list, which shows in a diff."""
        assert list(READINGS) == ["R0", "R1", "R2", "R3", "R4"]

    def test_the_windows_are_the_scripts_three(self) -> None:
        """Lines 11 and 12 are active, and lines 13, 14, 9 and 10 commented out."""
        assert WINDOWS == {
            "2007": ("2007-05-15", "2007-12-31"),
            "2008-2009": ("2008-01-02", "2009-12-31"),
            "2010-2012": ("2010-01-04", "2012-04-24"),
        }

    def test_the_book_and_the_script(self) -> None:
        """Location 2800 and the comment lines that close ``kentdaniel.m``."""
        assert (BOOK_APR_PERCENT, BOOK_SHARPE, BOOK_CRISIS_APR_PERCENT) == (37, 4.1, -30)
        assert (SCRIPT_ARITHMETIC, SCRIPT_SHARPE, SCRIPT_APR) == ("0.0315", "0.40", "0.0288")
        assert (SCRIPT_MAX_DD, SCRIPT_MAX_DDD) == ("-0.066923", 182)


class TestTheVintage:
    def test_the_members_are_the_pinned_source(self, source) -> None:
        members, closes = source
        vendor, basis, saved, folder, count = LIFTED_SOURCES[PRICE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert {m.path.split("/")[0] for m in members} == {folder}
        assert len(members) == count == 497
        assert closes.shape == (1500, 497)

    def test_every_stock_survives_to_the_last_day(self, closes) -> None:
        """None stops before 2012-04-24, and 23 start after 2006-05-11."""
        assert str(closes.index[0].date()) == "2006-05-11"
        assert str(closes.index[-1].date()) == "2012-04-24"
        assert closes.iloc[-1].notna().all()
        assert int(closes.iloc[0].isna().sum()) == 23

    def test_no_close_is_zero_and_no_stock_has_a_gap(self, closes) -> None:
        """So no ranking return divides by 0 or reaches across a missing price."""
        assert (closes.to_numpy()[np.isfinite(closes.to_numpy())] > 0).all()
        for symbol in closes.columns:
            column = closes[symbol]
            assert column.loc[column.first_valid_index() :].notna().all(), symbol


class TestTheWindows:
    def test_each_windows_rows(self, closes, results) -> None:
        """Rows counted from 0. Each window starts and ends on a day the file holds."""
        for window, first, count in (
            ("2007", 253, 160),
            ("2008-2009", 413, 505),
            ("2010-2012", 918, 582),
        ):
            days = results["R0"][window].days
            assert days[0] == closes.index[first], window
            assert len(days) == count, window
            assert str(days[0].date()) == WINDOWS[window][0], window
            assert str(days[-1].date()) == WINDOWS[window][1], window

    def test_the_2007_window_opens_the_day_after_the_first_marks(self, closes) -> None:
        longs, shorts = formations(ranking_returns(closes.to_numpy()))
        first = int(np.flatnonzero(longs.any(axis=1))[0])
        assert first == LOOKBACK == 252
        assert str(closes.index[first].date()) == "2007-05-14"
        assert str(closes.index[first + 1].date()) == WINDOWS["2007"][0]
        assert (longs.sum(axis=1)[first:] == TOP_N).all()
        assert (shorts.sum(axis=1)[first:] == TOP_N).all()

    def test_the_first_24_days_of_2007_hold_fewer_than_25_cohorts(self, closes) -> None:
        held = cohorts_held(len(closes))
        assert list(held[253:279]) == list(range(1, 26)) + [25]


class TestTheScript:
    """``kentdaniel.m`` as printed, over 2007, beside its comment and the book."""

    def test_the_arithmetic_annual_return(self, script: Figures) -> None:
        assert script.arithmetic_annual == pytest.approx(0.319989, abs=5e-7), SPEC

    def test_the_sharpe_ratio(self, script: Figures) -> None:
        assert script.sharpe == pytest.approx(4.0657, abs=5e-5), SPEC

    def test_the_compounded_apr(self, script: Figures) -> None:
        assert script.compounded_apr == pytest.approx(0.372577, abs=5e-7), SPEC

    def test_the_maximum_drawdown_and_its_duration(self, script: Figures) -> None:
        assert script.max_drawdown == pytest.approx(-0.033870, abs=5e-7), SPEC
        assert script.max_drawdown_days == 23, SPEC

    def test_none_of_the_five_prints_what_the_comment_says(self, script: Figures) -> None:
        """The comment lines print a Sharpe ratio of 0.40. The code prints 4.07."""
        assert f"{script.arithmetic_annual:7.4f}".strip() == "0.3200" != SCRIPT_ARITHMETIC
        assert f"{script.sharpe:4.2f}" == "4.07" != SCRIPT_SHARPE
        assert f"{script.compounded_apr:10.4f}".strip() == "0.3726" != SCRIPT_APR
        assert f"{script.max_drawdown:f}" == "-0.033870" != SCRIPT_MAX_DD
        assert script.max_drawdown_days == 23 != SCRIPT_MAX_DDD


class TestASecondImplementation:
    """The same rule written again in pandas, sharing no code with the module.

    A rank in place of MATLAB's sort, a rolling sum in place of 25 shifts, and
    ``pct_change`` in place of ``lag``. It shares the transcription's reading
    of the script, a one-row ``lag`` and MATLAB's tie order among it, so its
    agreement rules out a slip in the numpy code and not a misreading of the
    MATLAB.
    """

    def test_it_agrees_with_the_transcription_on_every_day(self, closes) -> None:
        ranking = closes / closes.shift(LOOKBACK) - 1
        ascending = ranking.rank(axis=1, method="first")
        finite = ranking.notna().sum(axis=1)
        longs = ascending.gt(finite - TOP_N, axis=0) & ranking.notna()
        shorts = ascending.le(TOP_N) & ranking.notna()
        marks = longs.astype(float) - shorts.astype(float)
        marks.iloc[:LOOKBACK] = 0.0
        positions = marks.rolling(HOLD_DAYS, min_periods=1).sum()
        earned = (positions.shift(1) * closes.pct_change(fill_method=None)).sum(axis=1, min_count=1)
        daily = (earned / (2 * TOP_N) / HOLD_DAYS).fillna(0.0).to_numpy()
        assert np.abs(daily - script_as_printed(closes.to_numpy())).max() < 1e-15


class TestTheBook:
    """The book's figures under the rule issue 297 declared before any run."""

    def test_no_reading_lands_37_percent_and_4_1(self, results) -> None:
        for name in READINGS:
            assert not lands_the_book(results[name]["2007"]), name

    def test_the_arithmetic_return_misses_37_percent_on_every_reading(self, results) -> None:
        rounded = {
            name: int(round_half_away(100 * results[name]["2007"].arithmetic_annual))
            for name in READINGS
        }
        assert rounded == {"R0": 32, "R1": 32, "R2": 29, "R3": 34, "R4": 32}
        assert BOOK_APR_PERCENT not in rounded.values()

    def test_two_readings_land_4_1_alone(self, results) -> None:
        """A partial landing, which the declared rule says is not a landing."""
        landed = [
            name for name in READINGS if round_half_away(10 * results[name]["2007"].sharpe) == 41
        ]
        assert landed == ["R0", "R4"]

    def test_the_script_misses_minus_30_percent_on_the_arithmetic_return(self, results) -> None:
        crisis = results["R0"]["2008-2009"]
        assert round_half_away(100 * crisis.arithmetic_annual) == -32
        assert not lands_the_crisis(crisis)

    def test_the_compounded_aprs_round_to_both_of_the_books(self, results) -> None:
        """Found after the rule was fixed, so reported and deciding nothing.

        The declared rule set the book's APR against the arithmetic return,
        following Example 7.2. Here the compounded figure is the one that
        rounds to the book's, in both windows.
        """
        assert round_half_away(100 * results["R0"]["2007"].compounded_apr) == BOOK_APR_PERCENT
        crisis = results["R0"]["2008-2009"].compounded_apr
        assert crisis == pytest.approx(-0.298789, abs=5e-7), SPEC
        assert round_half_away(100 * crisis) == BOOK_CRISIS_APR_PERCENT

    def test_the_return_after_2009_stabilised_below_2007(self, results) -> None:
        later = results["R0"]["2010-2012"]
        assert later.arithmetic_annual == pytest.approx(0.016244, abs=5e-7), SPEC
        assert stabilised(later, results["R0"]["2007"])


class TestTheDistances:
    """Each reading's distance from the book, which issue 297 asked for beside the landing."""

    @pytest.mark.parametrize(
        ("name", "from_37", "from_4_1", "from_minus_30"),
        [
            ("R0", -0.0500, -0.0343, -0.0232),
            ("R1", -0.0478, -0.1862, -0.0130),
            ("R2", -0.0807, -0.2768, -0.0053),
            ("R3", -0.0329, 0.1779, 0.0077),
            ("R4", -0.0485, -0.0469, -0.0232),
        ],
    )
    def test_the_distance(self, results, name, from_37, from_4_1, from_minus_30) -> None:
        first, crisis = results[name]["2007"], results[name]["2008-2009"]
        assert first.arithmetic_annual - BOOK_APR_PERCENT / 100 == pytest.approx(
            from_37, abs=5e-5
        ), SPEC
        assert first.sharpe - BOOK_SHARPE == pytest.approx(from_4_1, abs=5e-5), SPEC
        assert crisis.arithmetic_annual - BOOK_CRISIS_APR_PERCENT / 100 == pytest.approx(
            from_minus_30, abs=5e-5
        ), SPEC


class TestTheScriptOverTheOtherWindows:
    def test_2008_and_2009(self, results) -> None:
        f = results["R0"]["2008-2009"]
        assert f.arithmetic_annual == pytest.approx(-0.323195, abs=5e-7), SPEC
        assert f.sharpe == pytest.approx(-1.2930, abs=5e-5), SPEC
        assert f.max_drawdown == pytest.approx(-0.606634, abs=5e-7), SPEC
        assert f.max_drawdown_days == 371, SPEC

    def test_2010_to_2012(self, results) -> None:
        f = results["R0"]["2010-2012"]
        assert f.sharpe == pytest.approx(0.2004, abs=5e-5), SPEC
        assert f.compounded_apr == pytest.approx(0.013043, abs=5e-7), SPEC
        assert f.max_drawdown == pytest.approx(-0.095556, abs=5e-7), SPEC
        assert f.max_drawdown_days == 190, SPEC


class TestTheReadings:
    """Each reading's arithmetic annual return and Sharpe ratio, at four decimals."""

    @pytest.mark.parametrize(
        ("name", "window", "arithmetic", "sharpe"),
        [
            ("R1", "2007", 0.3222, 3.9138),
            ("R1", "2008-2009", -0.3130, -1.2586),
            ("R1", "2010-2012", 0.0104, 0.1277),
            ("R2", "2007", 0.2893, 3.8232),
            ("R2", "2008-2009", -0.3053, -1.2821),
            ("R2", "2010-2012", 0.0176, 0.2262),
            ("R3", "2007", 0.3371, 4.2779),
            ("R3", "2008-2009", -0.2923, -1.1695),
            ("R3", "2010-2012", 0.0332, 0.4093),
            ("R4", "2007", 0.3215, 4.0531),
        ],
    )
    def test_the_reading(self, results, name, window, arithmetic, sharpe) -> None:
        f = results[name][window]
        changed = READINGS[name][0]
        assert f.arithmetic_annual == pytest.approx(arithmetic, abs=5e-5), f"{SPEC}, {changed}"
        assert f.sharpe == pytest.approx(sharpe, abs=5e-5), f"{SPEC}, {changed}"

    def test_r4_is_the_script_once_25_cohorts_are_held(self, closes) -> None:
        """Only the 2007 window's first 24 days change, so R4's later windows are R0's."""
        values = closes.to_numpy()
        r0 = script_as_printed(values)
        r4 = READINGS["R4"][1](values)
        full = cohorts_held(len(values)) == HOLD_DAYS
        assert np.array_equal(r4[full], r0[full])
        assert not np.array_equal(r4[253:277], r0[253:277])

    def test_the_opposite_sign_negates_every_day(self, closes) -> None:
        """Long losers and short winners. Declared on the issue and settled by this."""
        values = closes.to_numpy()
        longs, shorts = formations(ranking_returns(values))
        positions = overlapping_positions(longs, shorts)
        divisor = 2 * TOP_N * HOLD_DAYS
        assert np.array_equal(
            daily_returns(-positions, values, divisor), -daily_returns(positions, values, divisor)
        )


class TestTheHelperMovesADigit:
    """The first edition's ``smartstd`` in place of book two's, everything else kept."""

    def test_the_first_editions_helper_prints_4_05_rather_than_4_07(
        self, closes, script: Figures
    ) -> None:
        """Line 48 leaves no NaN, so the two differ only by the square root of 159/160."""
        daily = script_as_printed(closes.to_numpy())
        first = window_figures(
            daily, pd.DatetimeIndex(closes.index), "2007", smartstd=smartstd_first_edition
        )
        assert first.sharpe == pytest.approx(4.0530, abs=5e-5), SPEC
        assert first.sharpe == pytest.approx(script.sharpe * np.sqrt(159 / 160), rel=1e-12)
        assert f"{first.sharpe:4.2f}" == "4.05" != f"{script.sharpe:4.2f}"
        assert first.arithmetic_annual == script.arithmetic_annual


class TestTheScaleBreakDecision:
    """Why the module does not call the guard, run rather than asserted.

    The guard read from each stock's first price, the way :mod:`chan.pead`
    calls it, refuses the 2007 window and the 2008 and 2009 window, and passes
    the last.
    """

    def test_the_flagged_days_fall_one_in_2007_and_29_in_2008_and_2009(self, closes) -> None:
        flagged = [
            day for symbol in closes.columns for day in scale_breaks(closes[symbol].dropna())
        ]
        counts = {
            window: sum(pd.Timestamp(start) <= day <= pd.Timestamp(end) for day in flagged)
            for window, (start, end) in WINDOWS.items()
        }
        assert len(flagged) == 30
        assert counts == {"2007": 1, "2008-2009": 29, "2010-2012": 0}

    def test_the_2007_day_is_etfcs_and_the_strategy_held_it_short_at_full_weight(
        self, closes
    ) -> None:
        """ETFC's close fell from 85.9 to 35.5 into 2007-11-12.

        ``daily_returns`` multiplies the position one row back by the day's
        return, so the row that earns the flagged close is 2007-11-09, where
        all 25 cohorts held ETFC short.
        """
        flagged = [
            (symbol, day)
            for symbol in closes.columns
            for day in scale_breaks(closes[symbol].dropna())
            if pd.Timestamp(WINDOWS["2007"][0]) <= day <= pd.Timestamp(WINDOWS["2007"][1])
        ]
        assert flagged == [("ETFC", pd.Timestamp("2007-11-12"))], SPEC
        etfc = closes["ETFC"]
        assert (etfc.loc["2007-11-09"], etfc.loc["2007-11-12"]) == (85.9, 35.5), SPEC
        values = closes.to_numpy()
        positions = overlapping_positions(*formations(ranking_returns(values)))
        held = pd.Series(positions[:, list(closes.columns).index("ETFC")], index=closes.index)
        assert held.loc["2007-11-09"] == -HOLD_DAYS, SPEC

    def test_the_guard_refuses_the_two_windows_the_book_prints(self, source) -> None:
        members, closes = source
        legs = [(m, closes[m.symbol].dropna()) for m in members]
        for window in ("2007", "2008-2009"):
            start, end = (pd.Timestamp(each) for each in WINDOWS[window])
            with pytest.raises(WindowCrossesScaleBreak):
                refuse_window_crossing_a_break(legs, start=start, end=end)
        start, end = (pd.Timestamp(each) for each in WINDOWS["2010-2012"])
        refuse_window_crossing_a_break(legs, start=start, end=end)

    def test_the_module_does_not_call_it(self) -> None:
        assert not hasattr(module, "refuse_window_crossing_a_break")


class TestTheRun:
    def test_it_prints_the_script_beside_chans_and_every_reading(
        self, source, results, capsys
    ) -> None:
        members, _ = source
        report(members, results)
        out = capsys.readouterr().out
        assert "497 members lifted from inputDataOHLCDaily_stocks_20120424.mat" in out
        assert "2007-05-15 to 2007-12-31, 160 trading days" in out
        for line, figures in (
            ("Arithmetic annual return", ["0.319989", "0.3200", "0.0315", "37", "percent"]),
            ("Sharpe ratio, sqrt", ["4.0657", "4.07", "0.40", "4.1"]),
            ("Compounded APR", ["0.372577", "0.3726", "0.0288"]),
            ("Maximum drawdown  ", ["-0.033870", "-0.066923"]),
            ("Maximum drawdown duration", ["23", "182"]),
        ):
            (row,) = [each for each in out.splitlines() if line in each]
            assert all(figure in row.split() for figure in figures), row
        for name in READINGS:
            (row,) = [each for each in out.splitlines() if each.strip().startswith(name)]
            assert row.split()[-3] == "no", row
        assert "landing 37 percent and 4.1 together: none." in out
        assert "rounds to -30 percent: no." in out
        assert "stabilised below its 2007 level: yes." in out
        assert "about survivors" in out
        assert "Exploratory." in out
        assert "Entry 17 carries the verdicts" in out
        (r0,) = [each for each in out.splitlines() if each.strip().startswith("R0")]
        assert r0.split()[-2:] == ["-0.0500", "-0.0343"], r0

    def test_run_reads_the_committed_file(self, source, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "read_closes", lambda data_dir=None: source)
        results = run()
        assert set(results) == set(READINGS)
        assert "Cross-sectional momentum" in capsys.readouterr().out

    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable(f"no committed vintage is lifted from {PRICE_FILE}")

        monkeypatch.setattr(module, "run", refuse)
        monkeypatch.setattr("sys.argv", ["cross_sectional_momentum"])
        with pytest.raises(SystemExit, match="no committed vintage is lifted from inputData"):
            main()


# --- the verdict rules, on figures made up to sit on their edges ---------------


def _figures(arithmetic: float, sharpe: float = 0.0) -> Figures:
    return Figures(
        days=pd.DatetimeIndex([]),
        arithmetic_annual=arithmetic,
        sharpe=sharpe,
        compounded_apr=0.0,
        max_drawdown=0.0,
        max_drawdown_days=0,
    )


class TestTheVerdictRules:
    """The rules issue 297 declared, held on their edges, since the file reaches none."""

    def test_37_percent_and_4_1_together_land(self) -> None:
        assert lands_the_book(_figures(0.37, 4.1))

    def test_37_percent_alone_does_not_land(self) -> None:
        assert not lands_the_book(_figures(0.37, 3.9))
        assert not lands_the_book(_figures(0.36, 4.1))

    def test_a_half_rounds_away_from_zero_as_matlab_does(self) -> None:
        """36.5 percent rounds to 37 in MATLAB and to 36 in Python's ``round``."""
        assert 100 * 0.365 == 36.5
        assert lands_the_book(_figures(0.365, 4.05))

    def test_minus_30_percent_lands_the_crisis_and_minus_31_does_not(self) -> None:
        assert lands_the_crisis(_figures(-0.30))
        assert lands_the_crisis(_figures(-0.295))
        assert not lands_the_crisis(_figures(-0.31))

    def test_stabilised_holds_from_0_up_to_below_the_first_window(self) -> None:
        first = _figures(0.32)
        assert stabilised(_figures(0.0), first)
        assert stabilised(_figures(0.31), first)
        assert not stabilised(_figures(-0.01), first)
        assert not stabilised(_figures(0.32), first)


class TestTheReportsVerdictLines:
    """What the report prints when a verdict goes the other way, which the file never does."""

    def test_a_landing_reading_prints_yes_and_is_named(
        self, source, results, monkeypatch, capsys
    ) -> None:
        monkeypatch.setattr(
            module, "lands_the_book", lambda figures: figures is results["R3"]["2007"]
        )
        report(source[0], results)
        out = capsys.readouterr().out
        (r3,) = [each for each in out.splitlines() if each.strip().startswith("R3")]
        assert r3.split()[-3] == "yes", r3
        assert "landing 37 percent and 4.1 together: R3." in out

    def test_the_crisis_line_reads_2008_and_2009(
        self, source, results, monkeypatch, capsys
    ) -> None:
        asked = []
        monkeypatch.setattr(
            module, "lands_the_crisis", lambda figures: asked.append(figures) or True
        )
        report(source[0], results)
        assert asked == [results["R0"]["2008-2009"]]
        assert "rounds to -30 percent: yes." in capsys.readouterr().out


# --- the rule, on frames small enough to read ----------------------------------

STOCKS = 2 * TOP_N + 20


def _prices(rows: int = LOOKBACK + 3) -> np.ndarray:
    """Every stock at 100 until row LOOKBACK, then stock j at 100 + j, so higher j ranks higher."""
    prices = np.full((rows, STOCKS), 100.0)
    prices[LOOKBACK:] += np.arange(STOCKS)
    return prices


class TestTheRule:
    def test_the_ranking_return_spans_252_rows(self) -> None:
        prices = _prices()
        ranking = ranking_returns(prices)
        assert np.isnan(ranking[:LOOKBACK]).all()
        assert ranking[LOOKBACK, 7] == pytest.approx(0.07)

    def test_the_lagged_ranking_return_ends_21_rows_back(self) -> None:
        prices = _prices(LOOKBACK + SKIP + 1)
        ranking = lagged_ranking_returns(prices)
        assert ranking[LOOKBACK, 7] == 0.0
        assert ranking[LOOKBACK + SKIP, 7] == pytest.approx(0.07)

    def test_the_highest_50_go_long_and_the_lowest_50_short(self) -> None:
        longs, shorts = formations(ranking_returns(_prices()))
        assert not longs[:LOOKBACK].any() and not shorts[:LOOKBACK].any()
        assert list(np.flatnonzero(longs[LOOKBACK])) == list(range(STOCKS - TOP_N, STOCKS))
        assert list(np.flatnonzero(shorts[LOOKBACK])) == list(range(TOP_N))

    def test_a_nan_return_is_never_marked(self) -> None:
        prices = _prices()
        prices[0, STOCKS - 1] = np.nan
        prices[0, 0] = np.nan
        longs, shorts = formations(ranking_returns(prices))
        assert not longs[LOOKBACK, STOCKS - 1] and not shorts[LOOKBACK, 0]
        assert longs[LOOKBACK].sum() == shorts[LOOKBACK].sum() == TOP_N
        assert longs[LOOKBACK, STOCKS - TOP_N - 1] and shorts[LOOKBACK, TOP_N]

    def test_ties_keep_their_column_order(self) -> None:
        prices = np.full((LOOKBACK + 1, STOCKS), 100.0)
        longs, shorts = formations(ranking_returns(prices))
        assert list(np.flatnonzero(shorts[LOOKBACK])) == list(range(TOP_N))
        assert list(np.flatnonzero(longs[LOOKBACK])) == list(range(STOCKS - TOP_N, STOCKS))

    def test_a_row_with_exactly_50_returns_is_marked(self) -> None:
        prices = _prices()
        prices[0, TOP_N:] = np.nan
        longs, shorts = formations(ranking_returns(prices))
        assert longs[LOOKBACK].sum() == shorts[LOOKBACK].sum() == TOP_N

    def test_a_row_with_fewer_than_50_returns_is_refused(self) -> None:
        prices = _prices()
        prices[0, TOP_N - 1 :] = np.nan
        with pytest.raises(ValueError, match="fewer than the 50"):
            formations(ranking_returns(prices))

    def test_overlapping_positions_sum_the_last_25_rows(self) -> None:
        longs = np.zeros((30, 2), dtype=bool)
        shorts = np.zeros((30, 2), dtype=bool)
        longs[2:5, 0] = True
        shorts[3, 0] = True
        positions = overlapping_positions(longs, shorts)
        assert list(positions[:6, 0]) == [0, 0, 1, 1, 2, 2]
        assert positions[26, 0] == 2 and positions[27, 0] == 1 and positions[29, 0] == 0

    def test_one_cohort_holds_the_latest_formation_only(self) -> None:
        rows = LOOKBACK + 2 * HOLD_DAYS + 1
        longs = np.zeros((rows, 1), dtype=bool)
        shorts = np.zeros((rows, 1), dtype=bool)
        longs[LOOKBACK] = True
        shorts[LOOKBACK + 1 : LOOKBACK + HOLD_DAYS] = True
        positions = one_cohort_positions(longs, shorts)
        assert not positions[:LOOKBACK].any()
        assert (positions[LOOKBACK : LOOKBACK + HOLD_DAYS] == 1).all()
        assert (positions[LOOKBACK + HOLD_DAYS :] == 0).all()

    def test_the_cohorts_held_rise_from_the_row_after_the_first_marks(self) -> None:
        held = cohorts_held(LOOKBACK + 30)
        assert held[LOOKBACK] == 0 and held[LOOKBACK + 1] == 1
        assert held[LOOKBACK + HOLD_DAYS] == HOLD_DAYS == held[-1]

    def test_yesterdays_position_earns_todays_return(self) -> None:
        closes = np.array([[10.0, 10.0], [11.0, 9.0], [11.0, 9.0]])
        positions = np.array([[1.0, -1.0], [0.0, 0.0], [0.0, 0.0]])
        assert list(daily_returns(positions, closes, 1.0)) == pytest.approx([0.0, 0.2, 0.0])
        assert list(daily_returns(positions, closes, 1.0, lag=0)) == pytest.approx([0.0, 0, 0])

    def test_a_day_with_nothing_finite_or_no_divisor_returns_0(self) -> None:
        closes = np.array([[np.nan], [10.0], [11.0]])
        positions = np.ones((3, 1))
        daily = daily_returns(positions, closes, np.array([1.0, 1.0, 0.0]))
        assert list(daily) == [0.0, 0.0, 0.0]

    def test_the_figures_read_only_the_windows_rows(self) -> None:
        days = pd.bdate_range("2007-05-14", periods=4)
        daily = np.array([0.5, 0.01, -0.01, 0.02])
        figures = window_figures(daily, days, "2007")
        assert len(figures.days) == 3
        assert figures.arithmetic_annual == pytest.approx(TRADING_DAYS * 0.02 / 3)
