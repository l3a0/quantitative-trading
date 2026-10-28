"""The pins for VIX futures calendar spreads on the ratio of back to front, *Algorithmic Trading*.

This file is the single authority for every number a prose surface quotes
about the VX calendar spread at Kindle location 2502 and the rows beside it.
``docs/replication-log.md`` Entry 35 carries the verdicts and points here row
by row. The rows are the ones
[issue 349](https://github.com/l3a0/quantitative-trading/issues/349) declared
on 2026-10-05 at ``f107b1f``, before any figure on VX was computed.

Every pin on the committed file reads one strip and one of five
specifications, so they are stated once here and carried in every figure's
failure message.

- **Vintage.** ``data/inputdatadaily_vx_20120507/``, vendor chan-mat, basis
  raw, saved 2012-05-08, lifted from ``inputDataDaily_VX_20120507.mat``. It is
  one vintage per contract, 72 of them from VX-2007F to VX-2012Z, with no spot
  column, read through ``chan.roll_returns.load_strip``. The strip's identity
  is its row of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``.
- **S, the specification.** ``calendarSpdsMeanReversion.m`` at EpchanPreview
  ``e4bc46f``, as :mod:`chan.calendar_spread_reversion` transcribes it, with
  five edits: the VX strip, ``spreadMonth=1``, the signal the second-nearest
  priced contract over the nearest where the two are adjacent columns and
  forward-filled, ``lookback=15``, and the window from 2008-10-27 to the
  file's last row, 2012-05-07, 889 rows. Each pair is held for at least 63 days, the
  spread is reversed where z is above 0, and the figures are annualised over
  252 days with no risk-free rate and no cost.
- **B1.** S with the signal the far contract over the near one for the pair
  the schedule holds, forward-filled across the rows nothing is held.
- **B2.** S with ``holddays=0``.
- **B3.** B1's signal built on B2's schedule, and run with ``holddays=0``.
- **B4.** S measured to 2012-04-23, the book's end date, 879 rows.

Two measurements were taken after seeing the five rows, and their pins say so:
B3 on the book's window, and each of S, B1, B2 and B3 from the first row its
flipped positions hold anything to 2008-10-24. The write-up measured three
more after the run, in ``TestWhichPairTheSignalReads``, and their pins say so
too.

Each computed figure is held at six decimals, so a change cannot move it
inside the published rounding unnoticed, and each published figure at the
precision Chan printed, through ``matches``.

``blog/vx-calendar-spread-lessons.md`` quotes most of these figures, so a
change to any of them moves that post too, and ``TestWhatThePostQuotes`` reads
one copy of each. ``TestWhichPairTheSignalReads`` holds
the numbers the post added, and ``tests/test_vx_calendar_spread_figures.py``
holds what its figure draws. ``blog/crude-oil-calendar-spread-lessons.md``
also quotes one of the class's numbers, the 126 of 847 held days whose near
leg is the front contract.

Exploratory. Reproducing Chan's figures spends his 2006 to 2012 strip on a rule
he chose, S is a reading of the book's text, and B3 was picked out after the
run among five rows. The experiment first ran here on 2026-10-10.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import ou_half_life

from chan import paths
from chan import vx_calendar_spread as module
from chan.calendar_spread_reversion import HOLDDAYS, NUM_DAYS_END, calendar_schedule
from chan.calendar_spread_reversion import SPREAD_MONTH as SHIPPED_SPREAD_MONTH
from chan.khandani_lo_book_two import gap, matches
from chan.roll_returns import MONTH_LETTERS, SOURCE_FILES, Strip, contract_month, load_strip
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.vx_calendar_spread import (
    BEFORE_END,
    BOOK_APR_PERCENT,
    BOOK_END,
    BOOK_SHARPE,
    EACH_IN_TURN,
    LOOKBACK,
    ROWS,
    SPREAD_MONTH,
    START,
    VxCalendarSpread,
    held_pair_ratio,
    main,
    near_leg_rank,
    nearest_two_ratio,
    report,
    run,
    vx_calendar_spread,
)
from tests.support.committed_vintages import LIFTED_SOURCES
from tests.support.post_tables import CELL, either_way, not_found_once, tables

VINTAGE = (
    "inputdatadaily_vx_20120507/ chan-mat raw saved 2012-05-08, from "
    "inputDataDaily_VX_20120507.mat, one vintage per contract VX-2007F to VX-2012Z, no spot"
)
S_SPEC = (
    f"{VINTAGE}; S: calendarSpdsMeanReversion.m with spreadMonth=1, the nearest two priced "
    "contracts' ratio forward-filled, lookback 15, held at least 63 days, "
    "from 2008-10-27 to 2012-05-07"
)
SPECS = {
    "S": S_SPEC,
    "B1": f"{VINTAGE}; B1: S with the held pair's ratio, filled across unheld rows",
    "B2": f"{VINTAGE}; B2: S with holddays=0",
    "B3": f"{VINTAGE}; B3: the held pair's ratio under holddays=0, run with holddays=0",
    "B4": f"{VINTAGE}; B4: S measured to 2012-04-23",
}
AFTER_THE_RUN = "measured after seeing the five rows, so it carries no verdict"

# --- the committed strip -------------------------------------------------------


@pytest.fixture(scope="module")
def strip() -> Strip:
    return load_strip("VX")


@pytest.fixture(scope="module")
def result(strip) -> VxCalendarSpread:
    return vx_calendar_spread(strip.contracts)


class TestTheSpecification:
    def test_the_five_edits_constants(self) -> None:
        assert (START, BOOK_END, BEFORE_END) == (
            pd.Timestamp("2008-10-27"),
            pd.Timestamp("2012-04-23"),
            pd.Timestamp("2008-10-24"),
        )
        assert (LOOKBACK, SPREAD_MONTH, HOLDDAYS, EACH_IN_TURN) == (15, 1, 63, 0)
        assert ROWS == ("S", "B1", "B2", "B3", "B4")

    def test_the_printed_figures_are_ascii_strings_float_can_read(self) -> None:
        assert (BOOK_APR_PERCENT, BOOK_SHARPE) == ("17.7", "1.5")
        assert BOOK_APR_PERCENT.isascii() and BOOK_SHARPE.isascii()
        assert float(BOOK_APR_PERCENT) and float(BOOK_SHARPE)


class TestTheVintage:
    def test_the_strip_is_the_pinned_source(self, strip) -> None:
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SOURCE_FILES["VX"]]
        assert (vendor, basis, saved, folder, count) == (
            "chan-mat",
            "raw",
            "2012-05-08",
            "inputdatadaily_vx_20120507",
            72,
        )
        assert {(m.vendor, m.price_basis, m.obtained) for m in strip.members} == {
            (vendor, basis, saved)
        }
        assert {m.path.split("/")[0] for m in strip.members} == {folder}

    def test_72_contracts_each_a_month_after_the_last_and_no_spot(self, strip) -> None:
        """So ``spreadMonth=1`` pairs each contract with the next month's."""
        columns = list(strip.contracts.columns)
        assert (len(columns), columns[0], columns[-1]) == (72, "VX-2007F", "VX-2012Z"), VINTAGE
        months = np.array([contract_month(symbol) for symbol in columns])
        assert (np.diff(months) == 1).all(), VINTAGE
        assert strip.spot is None, VINTAGE

    def test_the_strip_runs_from_2006_03_23_to_2012_05_07(self, strip) -> None:
        index = strip.contracts.index
        assert (len(index), str(index[0].date()), str(index[-1].date())) == (
            1543,
            "2006-03-23",
            "2012-05-07",
        ), VINTAGE


class TestTheSignalsOnVx:
    def test_ss_signal_is_missing_only_on_its_first_148_rows(self, strip) -> None:
        """The nearest two priced columns skip a contract only before 2006-10-23, so the
        forward fill changes nothing inside the window, and the ADF test and the half-life
        read the other 1,395 rows."""
        signal = nearest_two_ratio(strip.contracts)
        missing = signal.index[signal.isna().to_numpy()]
        assert len(missing) == 148, S_SPEC
        assert int(signal.notna().sum()) == 1395, S_SPEC
        assert str(signal.first_valid_index().date()) == "2006-10-23", S_SPEC
        assert missing.equals(signal.index[:148]), S_SPEC

    def test_b1s_fill_moves_its_half_life_from_15_to_20(self, strip, result) -> None:
        """The half-life reads the filled signal, so the unheld rows count, and on the held
        rows alone it is 15.106686."""
        schedule = calendar_schedule(strip.contracts, spread_month=SPREAD_MONTH)
        signal = held_pair_ratio(strip.contracts, schedule)
        held = (schedule != 0).any(axis=1).to_numpy()
        unfilled = signal[held].dropna().to_numpy()
        assert f"{ou_half_life(unfilled):.6f}" == "15.106686", SPECS["B1"]
        assert f"{result.rows['B1'].half_life:.6f}" == "20.509824", SPECS["B1"]

    def test_holddays_0_holds_64_of_vxs_71_pairs(self, strip) -> None:
        """The first pair's window is one row, and six pairs whose near contract still
        trades on 2012-05-07 are skipped once VX-2012K's pair has taken the rows to the end."""
        schedule = calendar_schedule(
            strip.contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN
        )
        near = (schedule == -1).any(axis=0).to_numpy()[:-1]
        unheld = list(strip.contracts.columns[:-1][~near])
        assert (int(near.sum()), len(near)) == (64, 71), SPECS["B2"]
        assert unheld == [
            "VX-2007F",
            "VX-2012M",
            "VX-2012N",
            "VX-2012Q",
            "VX-2012U",
            "VX-2012V",
            "VX-2012X",
        ], SPECS["B2"]
        last_near = schedule.columns[(schedule.iloc[-1] == -1).to_numpy()]
        assert list(last_near) == [], SPECS["B2"]
        assert schedule["VX-2012K"].iloc[-11] == -1 and strip.contracts["VX-2012K"].iloc[-1] > 0

    def test_holddays_0_ends_its_last_pair_on_the_books_end_date(self, strip) -> None:
        """VX-2012K still trades on the file's last row, 2012-05-07, so the schedule reads
        that row as its expiry, and its pair ends 10 rows earlier, on 2012-04-23. B2 and B3
        share the schedule, so the date does not tell them apart."""
        schedule = calendar_schedule(
            strip.contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN
        )
        assert str(schedule.index[-11].date()) == "2012-04-23", SPECS["B2"]
        assert (schedule.iloc[-10:] == 0).all().all(), SPECS["B2"]
        last_priced = strip.contracts["VX-2012K"].last_valid_index()
        assert str(last_priced.date()) == "2012-05-07", VINTAGE

    def test_from_2008_10_27_b3_holds_43_pairs_and_enters_42(self, strip) -> None:
        """Each pair is held in turn from VX-2008X's to VX-2012K's, and only VX-2008X's
        pair was entered before the window starts. The count the entry's cost sentence
        quotes."""
        schedule = calendar_schedule(
            strip.contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN
        )
        near = schedule.columns[(schedule.loc[START:] == -1).any(axis=0).to_numpy()]
        assert (len(near), near[0], near[-1]) == (43, "VX-2008X", "VX-2012K"), SPECS["B3"]
        months = np.array([contract_month(symbol) for symbol in near])
        assert (np.diff(months) == 1).all(), SPECS["B3"]
        entered = [schedule.index[(schedule[c] == -1).to_numpy()][0] for c in near]
        assert sum(day >= START for day in entered) == 42, SPECS["B3"]

    def test_from_2008_10_27_b3s_rolls_trade_two_or_four_and_its_reversals_most(
        self, strip, result
    ) -> None:
        """What the entry's cost sentence counts. Each new pair's near contract is the old
        pair's far one, so a roll trades two contracts where that contract keeps its side
        and four where it switches. Between rolls B3 reverses both legs, and those
        reversals are most of the 554 contracts it trades. Measured after the run."""
        schedule = calendar_schedule(
            strip.contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN
        )
        short = schedule.eq(-1)
        near = short.idxmax(axis=1).where(short.any(axis=1))
        before = near.shift()
        roll = ((near != before) & near.notna() & before.notna()).loc[START:]
        leaves = (near.isna() & before.notna()).loc[START:]
        positions = result.rows["B3"].positions
        traded = positions.diff().abs().sum(axis=1).loc[START:]
        reversal = (traded > 0) & ~roll & ~leaves
        assert sorted(traded[roll].value_counts().items()) == [(2.0, 26), (4.0, 16)], (
            f"{SPECS['B3']}; {AFTER_THE_RUN}"
        )
        assert traded[reversal].value_counts().to_dict() == {4.0: 109}, (
            f"{SPECS['B3']}; {AFTER_THE_RUN}"
        )
        now, then = positions.loc[START:][reversal], positions.shift().loc[START:][reversal]
        assert (now == -then).all().all(), f"{SPECS['B3']}; {AFTER_THE_RUN}"
        assert (traded.sum(), traded[reversal].sum()) == (554.0, 436.0), (
            f"{SPECS['B3']}; {AFTER_THE_RUN}"
        )

    def test_the_shipped_spread_month_of_12_holds_the_near_contract_alone(self, strip) -> None:
        """Why S edits ``spreadMonth``. The strip lists 2 to 10 contracts a day, so pairing
        contract c with c + 12 leaves the far leg unpriced on most held days, and the
        script's ``smartsum`` then holds the near contract alone."""
        contracts = strip.contracts
        priced = np.isfinite(contracts.to_numpy())
        counts = priced.sum(axis=1)
        assert (counts.min(), float(np.median(counts)), counts.max()) == (2, 8.0, 10), VINTAGE
        schedule = calendar_schedule(contracts).to_numpy()
        held = (schedule != 0).any(axis=1)
        near = ((schedule == -1) & priced).any(axis=1)
        far = ((schedule == 1) & priced).any(axis=1)
        assert (
            int(held.sum()),
            int((held & near & far).sum()),
            int((held & near & ~far).sum()),
            int((held & ~near & ~far).sum()),
        ) == (1284, 84, 1183, 17), f"{VINTAGE}; the script as shipped, spreadMonth=12"


class TestTheRows:
    """The five rows issue 349 declared, at six decimals."""

    @pytest.mark.parametrize(
        ("key", "rows", "adf", "half_life", "apr", "sharpe", "max_dd", "days", "last_held"),
        [
            ("S", 889, "-5.568107", "13.036829", "-0.040454", "-0.563912", "-0.255618", 871,
             "2012-03-07"),
            ("B1", 889, "-4.010034", "20.509824", "0.033430", "0.510861", "-0.161533", 628,
             "2012-03-07"),
            ("B2", 889, "-5.568107", "13.036829", "-0.113153", "-0.990744", "-0.404239", 870,
             "2012-04-23"),
            ("B3", 889, "-4.839517", "16.273041", "0.173462", "1.457009", "-0.107287", 166,
             "2012-04-23"),
            ("B4", 879, "-5.568107", "13.036829", "-0.040905", "-0.567112", "-0.255618", 861,
             "2012-03-07"),
        ],
    )  # fmt: skip
    def test_each_rows_figures(
        self, result, key, rows, adf, half_life, apr, sharpe, max_dd, days, last_held
    ) -> None:
        found, spec = result.rows[key], SPECS[key]
        assert len(found.returns) == rows, spec
        assert (f"{found.adf.statistic:.6f}", f"{found.half_life:.6f}") == (adf, half_life), spec
        assert (f"{found.apr:.6f}", f"{found.sharpe:.6f}") == (apr, sharpe), spec
        assert (f"{found.max_dd:.6f}", found.max_dd_days) == (max_dd, days), spec
        assert str(found.last_held.date()) == last_held, spec
        assert found.lookback == LOOKBACK, spec

    @pytest.mark.parametrize("key", ROWS)
    def test_each_window_starts_on_2008_10_27(self, result, key) -> None:
        index = result.rows[key].returns.index
        last = "2012-04-23" if key == "B4" else "2012-05-07"
        assert (str(index[0].date()), str(index[-1].date())) == ("2008-10-27", last), SPECS[key]

    @pytest.mark.parametrize("key", ROWS)
    def test_the_1_percent_critical_value_is_minus_3_4583(self, result, key) -> None:
        assert result.rows[key].adf.critical[0] == -3.4583, SPECS[key]


class TestTheClaims:
    """S against location 2502's three figures, the verdicts Entry 35 carries."""

    def test_ss_adf_statistic_clears_the_1_percent_critical_value(self, result) -> None:
        adf = result.rows["S"].adf
        assert adf.statistic < adf.critical[0], S_SPEC
        assert f"{adf.critical[0] - adf.statistic:.6f}" == "2.109807", S_SPEC

    def test_s_misses_the_apr_and_sharpe_ratio_with_the_wrong_sign(self, result) -> None:
        s = result.rows["S"]
        assert not matches(100 * s.apr, BOOK_APR_PERCENT), S_SPEC
        assert not matches(s.sharpe, BOOK_SHARPE), S_SPEC
        assert (gap(100 * s.apr, BOOK_APR_PERCENT), gap(s.sharpe, BOOK_SHARPE)) == (-21.7, -2.1)
        assert s.apr < 0 and s.sharpe < 0, S_SPEC

    def test_b4_misses_the_same_way_on_the_books_end_date(self, result) -> None:
        """Cutting S's last 10 rows lowers its APR and Sharpe ratio a little, keeps its
        drawdown, and shortens that drawdown by the 10 rows cut."""
        s, b4 = result.rows["S"], result.rows["B4"]
        assert b4.apr < 0 and b4.sharpe < 0, SPECS["B4"]
        assert (f"{s.apr - b4.apr:.6f}", f"{s.sharpe - b4.sharpe:.6f}") == (
            "0.000451",
            "0.003199",
        ), SPECS["B4"]
        assert (s.max_dd == b4.max_dd, s.max_dd_days - b4.max_dd_days) == (True, 10), SPECS["B4"]

    def test_b3_rounds_to_the_sharpe_ratio_but_not_the_apr_to_the_files_end(self, result) -> None:
        """No verdict. B3 is a row beside the specification."""
        b3 = result.rows["B3"]
        assert matches(b3.sharpe, BOOK_SHARPE), SPECS["B3"]
        assert not matches(100 * b3.apr, BOOK_APR_PERCENT), SPECS["B3"]
        assert gap(100 * b3.apr, BOOK_APR_PERCENT) == -0.4, SPECS["B3"]

    def test_only_b2_and_b3_hold_a_pair_on_the_books_end_date(self, result) -> None:
        """Both run ``holddays=0``, so the date does not separate B3 from B2."""
        held_to_end = [key for key in ROWS if result.rows[key].last_held == BOOK_END]
        assert held_to_end == ["B2", "B3"], f"{SPECS['B2']}; {SPECS['B3']}"


class TestTheMeasurementsAfterTheRun:
    """Taken after seeing the five rows. None carries a verdict."""

    def test_b3_on_the_books_window(self, result) -> None:
        b3 = result.b3_book_window
        days = b3.returns.index
        assert (len(days), str(days[0].date()), str(days[-1].date())) == (
            879,
            "2008-10-27",
            "2012-04-23",
        ), AFTER_THE_RUN
        assert (f"{b3.apr:.6f}", f"{b3.sharpe:.6f}") == ("0.176952", "1.475658"), AFTER_THE_RUN
        assert (f"{b3.max_dd:.6f}", b3.max_dd_days) == ("-0.107287", 166), AFTER_THE_RUN
        assert str(b3.last_held.date()) == "2012-04-23", AFTER_THE_RUN

    def test_b3_on_the_books_window_rounds_to_both_printed_figures(self, result) -> None:
        b3 = result.b3_book_window
        assert matches(100 * b3.apr, BOOK_APR_PERCENT), AFTER_THE_RUN
        assert matches(b3.sharpe, BOOK_SHARPE), AFTER_THE_RUN

    @pytest.mark.parametrize(
        ("key", "first", "rows", "apr", "sharpe"),
        [
            ("S", "2006-11-10", 492, "-0.027638", "-0.291914"),
            ("B1", "2006-11-10", 492, "0.204377", "2.279855"),
            ("B2", "2006-12-29", 459, "-0.018707", "-0.091522"),
            ("B3", "2007-01-23", 445, "-0.074173", "-0.562291"),
        ],
    )
    def test_each_row_before_october_2008(self, result, key, first, rows, apr, sharpe) -> None:
        found = result.before[key]
        days = found.returns.index
        spec = f"{SPECS[key]}, from its first held row to 2008-10-24, {AFTER_THE_RUN}"
        assert (str(days[0].date()), str(days[-1].date()), len(days)) == (
            first,
            "2008-10-24",
            rows,
        ), spec
        assert (f"{found.apr:.6f}", f"{found.sharpe:.6f}") == (apr, sharpe), spec

    def test_each_before_window_starts_on_the_first_flipped_row_holding_anything(
        self, result
    ) -> None:
        for key, found in result.before.items():
            positions = result.rows[key].positions
            holding = positions.index[(positions != 0).any(axis=1).to_numpy()]
            assert found.returns.index[0] == holding[0], key

    def test_only_b3_does_worse_before_october_2008_than_after(self, result) -> None:
        worse = [
            key
            for key, before in result.before.items()
            if before.apr < result.rows[key].apr and before.sharpe < result.rows[key].sharpe
        ]
        assert worse == ["B3"], AFTER_THE_RUN

    def test_the_rows_before_october_2008_are_s_and_b1_to_b3(self, result) -> None:
        """B4 differs from S only in its end, so before October 2008 it would repeat S."""
        assert list(result.before) == ["S", "B1", "B2", "B3"], AFTER_THE_RUN


class TestWhichPairTheSignalReads:
    """Numbers the post on Entry 35 quotes about which pair each row trades, none a
    published figure. The write-up measured them after the run, so they are as
    exploratory as the rest."""

    def test_ss_near_leg_is_the_front_contract_on_126_of_its_847_held_rows(self, strip) -> None:
        """S holds each pair from at least 73 rows before its near contract's expiry, and VX
        expires monthly, so its near leg is usually two to five contracts out while its
        signal reads the front two."""
        schedule = calendar_schedule(strip.contracts, spread_month=SPREAD_MONTH)
        rank = near_leg_rank(strip.contracts, schedule).loc[START:].dropna()
        assert len(rank) == 847, f"{S_SPEC}; {AFTER_THE_RUN}"
        assert rank.value_counts().sort_index().to_dict() == {
            1.0: 126,
            2.0: 229,
            3.0: 221,
            4.0: 201,
            5.0: 70,
        }, f"{S_SPEC}; {AFTER_THE_RUN}"
        near = schedule.columns[(schedule.loc[START:] == -1).any(axis=0).to_numpy()]
        assert (len(near), near[0], near[-1]) == (11, "VX-2009G", "VX-2012H"), (
            f"{S_SPEC}; {AFTER_THE_RUN}"
        )

    def test_under_holddays_0_the_near_leg_is_the_front_or_the_second(self, strip) -> None:
        """Each pair starts the row after the last one ended, 10 rows before the old near
        contract's expiry, so for those rows the old near contract is still the front."""
        schedule = calendar_schedule(
            strip.contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN
        )
        rank = near_leg_rank(strip.contracts, schedule).loc[START:].dropna()
        assert len(rank) == 879, f"{SPECS['B2']}; {AFTER_THE_RUN}"
        assert rank.value_counts().sort_index().to_dict() == {1.0: 459, 2.0: 420}, (
            f"{SPECS['B2']}; {AFTER_THE_RUN}"
        )

    def test_b1_and_b3_earn_and_s_and_b2_lose(self, result) -> None:
        """B1 and B3 read the held pair's own ratio and S and B2 the front pair's. Four
        rows chosen in advance show the pattern, which is not a cause, and B2 reads its
        held pair more often than S and still loses more."""
        earns = {key: result.rows[key].apr > 0 for key in ("S", "B1", "B2", "B3")}
        assert earns == {"S": False, "B1": True, "B2": False, "B3": True}, (
            f"{VINTAGE}; S and B1 to B3 to 2012-05-07; {AFTER_THE_RUN}"
        )


POST = paths.REPO_ROOT / "blog" / "vx-calendar-spread-lessons.md"
#: Chan's "99 percent", which the module prints inside its report and holds as no constant.
BOOK_PROBABILITY = "99"
#: The readings that run to the file's last day, the four the post's last table sets side by side.
READINGS = tuple(key for key in ROWS if key != "B4")
_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven")


def _minus(x: float, places: int) -> str:
    """A figure in prose, with the post's typographic minus sign."""
    return f"{x:.{places}f}".replace("-", "−")


def _month(contract: str) -> str:
    """``VX-2007F`` as the post names it, January 2007."""
    year, letter = contract[-5:-1], contract[-1]
    return f"{pd.Timestamp(int(year), MONTH_LETTERS.index(letter) + 1, 1):%B %Y}"


def _reading(key: str) -> str:
    """A reading's name as :func:`tables` reads its cell, so ``B1`` as ``1`` and ``S`` as ``S``."""
    return (CELL.findall(key) or [key])[0]


def _rolls(schedule: pd.DataFrame) -> pd.Series:
    """The days from :data:`START` on which the held pair changes from one pair to the next."""
    short = schedule.eq(-1)
    near = short.idxmax(axis=1).where(short.any(axis=1))
    before = near.shift()
    return ((near != before) & near.notna() & before.notna()).loc[START:]


class TestWhatThePostQuotes:
    """One copy of each run figure ``blog/vx-calendar-spread-lessons.md`` quotes.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built from the run at the precision the post prints
    it, and looked for in a short fragment holding the number and the few
    words that name one place in the post. Each fragment must occur exactly
    once, so it cannot match a second copy. A typo in a copy that is read, or
    a re-pin that leaves the post behind, fails here, while rewording the
    prose between two figures does not. A figure the post rounds from a
    pinned one, such as −4.0 percent, 17.3 percent or 0.0451 percentage
    points, is rounded here from the run. The post's three tables are each
    read whole, as the grid of its cells with its row labels and column
    heads, through :func:`tests.support.post_tables.tables`, so a cell
    changed, added, dropped or moved fails, and so does a label or head
    swapped, while the same table turned on its side still passes.

    Four things stay unread.

    1. Second copies of a figure. The post states several figures more than
       once, and only one copy of each is read. The copies left unread
       include the opening's −4.0 and 17.7 percent, the 2 to 10 contracts a
       day in "What changes from crude oil", the 459 of 879 days in Lesson
       2's last paragraph, the 1,183 days after Lesson 4's counts, and the
       126 of 847 in the closing list.
    2. The figures in the chart's alt text.
       ``tests/test_vx_calendar_spread_figures.py`` reads its eight bar figures
       against the chart's labels, and its readings of the curves are
       approximate.
    3. Chan's words and their Kindle locations, the script's name and
       commit, and the references.
    4. The numbers the two sketches print and their alt texts quote, which
       ``tests/test_vx_calendar_spread_whiteboard.py`` derives from the
       schedules.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    def test_the_post_holds_three_tables(self, text) -> None:
        assert len(tables(text)) == 3

    def test_the_file_and_the_readings(self, strip, result, text) -> None:
        contracts = strip.contracts
        columns, index = contracts.columns, contracts.index
        (saved,) = {m.obtained for m in strip.members}
        s, b4 = result.rows["S"], result.rows["B4"]
        fragments = [
            f"It is `{SOURCE_FILES[module.ROOT]}`, the file the commented-out line names, "
            f"saved {saved}",
            f"It holds {len(columns)} contracts, one for each month from {_month(columns[0])} "
            f"to {_month(columns[-1])}, over {len(index):,} days from {index[0].date()} to "
            f"{index[-1].date()}.",
            f"The crude oil script pairs each contract with the one expiring "
            f"{SHIPPED_SPREAD_MONTH} months later.",
            f"The script holds each pair for at least {HOLDDAYS} days, its own minimum",
            f"The window from {s.returns.index[0].date()} to the file’s last day, "
            f"{s.returns.index[-1].date()}, which is {len(s.returns):,} days.",
            f"**B4** is S measured to {b4.returns.index[-1].date()}, the book’s end date, "
            f"{len(b4.returns):,} days.",
        ]
        assert not_found_once(text, fragments) == [], S_SPEC

    def test_lesson_1(self, strip, result, text) -> None:
        s, b4 = result.rows["S"], result.rows["B4"]
        adf = s.adf
        critical = adf.critical[0]
        ratio = nearest_two_ratio(strip.contracts).dropna()
        assert s.apr < 0 and s.sharpe < 0, "both miss with the wrong sign"
        fragments = [
            f"The ADF statistic of S’s ratio is {_minus(adf.statistic, 6)}, against a 1 percent "
            f"critical value of {_minus(critical, 4)},",
            f"with a margin of {critical - adf.statistic:.6f}.",
            f"The test reads all {len(ratio):,} days on which the ratio can be computed, from "
            f"{ratio.index[0].date()}.",
            f"so {_minus(s.apr, 6)} in the table below is {_minus(100 * s.apr, 1)} percent.",
            f"The book gives the lookback as {LOOKBACK} days,",
            f"the half-life rounded, which here would be {round(s.half_life)} days.",
            f"The APR is {_minus(100 * s.apr, 1)} percent and the Sharpe ratio is "
            f"{_minus(s.sharpe, 2)},",
            f"lowers the APR by {s.apr - b4.apr:.6f}, which is {100 * (s.apr - b4.apr):.4f} "
            f"percentage points, and the Sharpe ratio by {s.sharpe - b4.sharpe:.6f}.",
        ]
        assert not_found_once(text, fragments) == [], S_SPEC
        table = [
            ["Figure", "S", "Book"],
            ["ADF statistic", f"{adf.statistic:.6f}", BOOK_PROBABILITY],
            ["Half-life, days", f"{s.half_life:.6f}", "none printed"],
            ["APR", f"{s.apr:.6f}", BOOK_APR_PERCENT],
            ["Sharpe ratio", f"{s.sharpe:.6f}", BOOK_SHARPE],
            ["Maximum drawdown", f"{s.max_dd:.6f}", "none"],
        ]
        assert tables(text)[0] in either_way(table), S_SPEC

    def test_lesson_2(self, strip, result, text) -> None:
        contracts = strip.contracts
        schedule = calendar_schedule(contracts, spread_month=SPREAD_MONTH)
        rank = near_leg_rank(contracts, schedule).loc[START:].dropna()
        front = int((rank == 1).sum())
        near = schedule.columns[(schedule.loc[START:] == -1).any(axis=0).to_numpy()]
        sevenths = round(7 * (len(rank) - front) / len(rank))
        each = calendar_schedule(contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN)
        each_rank = near_leg_rank(contracts, each).loc[START:].dropna()
        rolls = _rolls(each)
        second = each_rank.index[(each_rank == 2).to_numpy()]
        after_rolls = sorted(
            contracts.index[contracts.index.get_loc(day) + k]
            for day in rolls.index[rolls.to_numpy()]
            for k in range(NUM_DAYS_END)
        )
        assert list(second) == after_rolls, f"{SPECS['B2']}; the first days after each roll"
        fragments = [
            f"The script holds each pair for at least {HOLDDAYS} days and lets it go "
            f"{NUM_DAYS_END} days before its near contract’s last trading day, so it opens each "
            f"pair at least {HOLDDAYS + NUM_DAYS_END} days before that day.",
            f"On the {len(rank):,} days from {START.date()} on which S holds a pair, its near leg "
            f"is the front contract on {front}.",
            f"S holds {len(near)} pairs in that time. The near leg of the first is {near[0]}, "
            f"the {_month(near[0])} contract. The near leg of the last is {near[-1]}, the "
            f"{_month(near[-1])} one.",
            f"So on {_WORDS[sevenths]} days in seven,",
            f"Its near leg is the front contract on {int((each_rank == 1).sum())} of its "
            f"{len(each_rank):,} held days and the second on the other {len(second)}.",
            f"Those {len(second)} are the first {NUM_DAYS_END} days after each of its "
            f"{int(rolls.sum())} rolls in that time,",
            f"against S’s {front} of {len(rank):,},",
        ]
        assert not_found_once(text, fragments) == [], f"{S_SPEC}; {SPECS['B2']}"
        places = [
            ["Near leg's place", "Days held by S"],
            *(
                [f"{place:.0f}", str(days)]
                for place, days in rank.value_counts().sort_index().items()
            ),
        ]
        assert tables(text)[1] in either_way(places), f"{S_SPEC}; {AFTER_THE_RUN}"
        signal = {"S": "front pair", "B1": "held pair", "B2": "front pair", "B3": "held pair"}
        readings = [
            ["Reading", "Signal", "APR", "Sharpe"],
            *(
                [
                    _reading(key),
                    signal[key],
                    f"{result.rows[key].apr:.6f}",
                    f"{result.rows[key].sharpe:.6f}",
                ]
                for key in READINGS
            ),
        ]
        assert tables(text)[2] in either_way(readings), "; ".join(SPECS[k] for k in READINGS)

    def test_lesson_3(self, strip, result, text) -> None:
        b3, book, early = result.rows["B3"], result.b3_book_window, result.before["B3"]
        each = calendar_schedule(strip.contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN)
        (last_near,) = each.columns[(each.loc[b3.last_held] == -1).to_numpy()]
        fragments = [
            f"Measured to {book.returns.index[-1].date()}, the book’s end date, its APR is "
            f"{book.apr:.6f} and its Sharpe ratio {book.sharpe:.6f}, which round to the printed "
            f"{BOOK_APR_PERCENT} percent and {BOOK_SHARPE}.",
            f"Measured to the file’s last day, they are {b3.apr:.6f} and {b3.sharpe:.6f}.",
            f"That APR is {100 * b3.apr:.1f} percent, which misses {BOOK_APR_PERCENT} percent by "
            f"{-gap(100 * b3.apr, BOOK_APR_PERCENT)} percentage points",
            f"From its first held day, {early.returns.index[0].date()}, to "
            f"{early.returns.index[-1].date()}, its APR is {_minus(early.apr, 6)} and its "
            f"Sharpe ratio {_minus(early.sharpe, 6)}.",
            f"B3’s last held day is {b3.last_held.date()}, the book’s printed end date",
            f"{last_near} is the {_month(last_near)} contract.",
            f"so it reads {strip.contracts.index[-1].date()} as {last_near}’s expiry and lets go "
            f"of the pair {NUM_DAYS_END} days earlier, on {b3.last_held.date()}.",
        ]
        assert not_found_once(text, fragments) == [], f"{SPECS['B3']}; {AFTER_THE_RUN}"

    def test_lesson_4(self, strip, text) -> None:
        contracts = strip.contracts
        priced = np.isfinite(contracts.to_numpy())
        counts = priced.sum(axis=1)
        median = float(np.median(counts))
        assert median.is_integer(), VINTAGE
        schedule = calendar_schedule(contracts).to_numpy()
        held = (schedule != 0).any(axis=1)
        near = ((schedule == -1) & priced).any(axis=1)
        far = ((schedule == 1) & priced).any(axis=1)
        fragments = [
            f"loads a file that prices at most {counts.max()} contracts on any day.",
            f"its schedule holds a pair on {int(held.sum()):,} days. Both legs have a price on "
            f"{int((held & near & far).sum()):,} of them. On {int((held & near & ~far).sum()):,} "
            f"only the near leg is priced, and on {int((held & ~near & ~far).sum()):,} neither is.",
            f"which prices {counts.min()} to {counts.max()} contracts a day with a median of "
            f"{median:.0f}.",
        ]
        assert not_found_once(text, fragments) == [], (
            f"{VINTAGE}; the script as shipped, spreadMonth={SHIPPED_SPREAD_MONTH}"
        )

    def test_what_it_cannot_say_about_costs(self, strip, result, text) -> None:
        each = calendar_schedule(strip.contracts, spread_month=SPREAD_MONTH, holddays=EACH_IN_TURN)
        near = each.columns[(each.loc[START:] == -1).any(axis=0).to_numpy()]
        entered = sum(each.index[(each[c] == -1).to_numpy()][0] >= START for c in near)
        short = each.eq(-1)
        held = short.idxmax(axis=1).where(short.any(axis=1))
        leaves = (held.isna() & held.shift().notna()).loc[START:]
        rolls = _rolls(each)
        traded = result.rows["B3"].positions.diff().abs().sum(axis=1).loc[START:]
        reversals = int(((traded > 0) & ~rolls & ~leaves).sum())
        low, high = sorted(int(n) for n in traded[rolls].unique())
        fragments = [
            f"From {START.date()}, B3 holds {len(near)} pairs and enters {entered} of them,",
            f"a roll trades {_WORDS[low]} contracts when that contract keeps its side and "
            f"{_WORDS[high]} when it switches.",
            f"B3 also reverses both legs on {reversals} days between rolls,",
        ]
        assert not_found_once(text, fragments) == [], f"{SPECS['B3']}; {AFTER_THE_RUN}"


# --- the rules on synthetic frames ---------------------------------------------

DAYS = pd.bdate_range("2020-01-01", periods=6)


def _frame(rows: list[list[float]]) -> pd.DataFrame:
    """A strip of three contracts, one row per day, NaN where a contract is not priced."""
    return pd.DataFrame(rows, index=DAYS[: len(rows)], columns=["X0", "X1", "X2"])


NAN = np.nan


class TestTheNearestTwoRatio:
    def test_it_is_the_second_nearest_over_the_nearest(self) -> None:
        ratio = nearest_two_ratio(_frame([[20.0, 25.0, 30.0]]))
        assert ratio.tolist() == [1.25]

    def test_a_row_whose_nearest_two_priced_columns_skip_is_nan(self) -> None:
        """X0 and X2 are the nearest two priced, and they are not adjacent columns."""
        ratio = nearest_two_ratio(_frame([[20.0, NAN, 30.0], [20.0, 25.0, 30.0]]))
        assert np.isnan(ratio.iloc[0])
        assert ratio.iloc[1] == 1.25

    def test_a_row_starting_on_a_later_column_still_fits(self) -> None:
        ratio = nearest_two_ratio(_frame([[NAN, 25.0, 30.0]]))
        assert ratio.tolist() == [1.2]

    def test_a_row_with_one_priced_contract_is_nan(self) -> None:
        assert nearest_two_ratio(_frame([[NAN, NAN, 30.0]])).isna().all()

    def test_it_is_on_the_contracts_index(self) -> None:
        contracts = _frame([[20.0, 25.0, 30.0], [20.0, NAN, 30.0]])
        assert nearest_two_ratio(contracts).index.equals(contracts.index)

    def test_a_skipping_row_after_a_priced_one_stays_nan(self) -> None:
        """The function fills nothing forward, which :func:`run_spread` does for every signal."""
        ratio = nearest_two_ratio(_frame([[20.0, 25.0, 30.0], [20.0, NAN, 30.0]]))
        assert ratio.iloc[0] == 1.25
        assert np.isnan(ratio.iloc[1])


def _schedule(rows: list[list[float]]) -> pd.DataFrame:
    return _frame(rows)


class TestTheHeldPairRatio:
    def test_the_held_pair_across_a_roll(self) -> None:
        """X1 over X0 while the first pair is held, then X2 over X1 from the roll."""
        contracts = _frame([[10.0, 12.0, 18.0]] * 4)
        schedule = _schedule(
            [[-1.0, 1.0, 0.0], [-1.0, 1.0, 0.0], [0.0, -1.0, 1.0], [0.0, -1.0, 1.0]]
        )
        assert held_pair_ratio(contracts, schedule).tolist() == [1.2, 1.2, 1.5, 1.5]

    def test_it_is_filled_forward_across_unheld_days(self) -> None:
        """Nothing is held on rows 2 and 3, so they carry row 1's ratio, and the next pair
        sets its own on row 4. The prices on the unheld rows do not reach the signal."""
        contracts = _frame(
            [[10.0, 12.0, 18.0], [10.0, 13.0, 18.0], [10.0, 99.0, 99.0], [10.0, 99.0, 99.0],
             [10.0, 12.0, 18.0]]
        )  # fmt: skip
        schedule = _schedule(
            [[-1.0, 1.0, 0.0], [-1.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0],
             [0.0, -1.0, 1.0]]
        )  # fmt: skip
        assert held_pair_ratio(contracts, schedule).tolist() == [1.2, 1.3, 1.3, 1.3, 1.5]

    def test_it_is_nan_before_the_first_held_row(self) -> None:
        contracts = _frame([[10.0, 12.0, 18.0]] * 3)
        schedule = _schedule([[0.0, 0.0, 0.0], [-1.0, 1.0, 0.0], [-1.0, 1.0, 0.0]])
        ratio = held_pair_ratio(contracts, schedule)
        assert np.isnan(ratio.iloc[0]) and ratio.iloc[1:].tolist() == [1.2, 1.2]

    def test_it_reads_the_far_column_over_the_near_one_wherever_they_sit(self) -> None:
        """The far contract is the schedule's +1 column, not the column after the near."""
        contracts = _frame([[10.0, 12.0, 18.0]])
        assert held_pair_ratio(contracts, _schedule([[-1.0, 0.0, 1.0]])).tolist() == [1.8]

    def test_a_schedule_on_other_days_or_columns_is_refused(self) -> None:
        contracts = _frame([[10.0, 12.0, 18.0]] * 2)
        shifted = _schedule([[-1.0, 1.0, 0.0]] * 2).set_axis(DAYS[1:3])
        renamed = _schedule([[-1.0, 1.0, 0.0]] * 2).set_axis(["A", "B", "C"], axis=1)
        for schedule in (shifted, renamed):
            with pytest.raises(ValueError, match="on their own days and columns"):
                held_pair_ratio(contracts, schedule)


class TestTheNearLegRank:
    def test_it_counts_the_priced_contracts_up_to_the_near_leg(self) -> None:
        """Row 0 holds the front pair, row 1 the pair one out, and row 2 nothing."""
        contracts = _frame([[10.0, 12.0, 18.0]] * 3)
        schedule = _schedule([[-1.0, 1.0, 0.0], [0.0, -1.0, 1.0], [0.0, 0.0, 0.0]])
        rank = near_leg_rank(contracts, schedule)
        assert rank.iloc[:2].tolist() == [1.0, 2.0] and np.isnan(rank.iloc[2])

    def test_an_expired_contract_before_the_near_leg_does_not_count(self) -> None:
        """X0 has no price, so X1 is the front contract and the near leg ranks first."""
        contracts = _frame([[np.nan, 12.0, 18.0]])
        assert near_leg_rank(contracts, _schedule([[0.0, -1.0, 1.0]])).tolist() == [1.0]

    def test_it_reads_the_near_leg_rather_than_the_far_one(self) -> None:
        contracts = _frame([[10.0, 12.0, 18.0]])
        assert near_leg_rank(contracts, _schedule([[0.0, 1.0, -1.0]])).tolist() == [3.0]

    def test_it_is_on_the_contracts_index(self) -> None:
        contracts = _frame([[10.0, 12.0, 18.0]] * 2)
        rank = near_leg_rank(contracts, _schedule([[-1.0, 1.0, 0.0]] * 2))
        assert rank.index.equals(contracts.index) and rank.name == "near_leg_rank"

    def test_a_schedule_on_other_days_or_columns_is_refused(self) -> None:
        contracts = _frame([[10.0, 12.0, 18.0]] * 2)
        shifted = _schedule([[-1.0, 1.0, 0.0]] * 2).set_axis(DAYS[1:3])
        renamed = _schedule([[-1.0, 1.0, 0.0]] * 2).set_axis(["A", "B", "C"], axis=1)
        for schedule in (shifted, renamed):
            with pytest.raises(ValueError, match="on their own days and columns"):
                near_leg_rank(contracts, schedule)


def _expiring(expiries: list[int], rows: int = 120) -> pd.DataFrame:
    """Contract c priced from row 0 to row ``expiries[c]``, both included."""
    prices = np.full((rows, len(expiries)), np.nan)
    for c, last in enumerate(expiries):
        prices[: last + 1, c] = 50.0 + c + 0.1 * np.arange(last + 1)
    return pd.DataFrame(
        prices,
        index=pd.bdate_range("2020-01-01", periods=rows),
        columns=[f"X{c}" for c in range(len(expiries))],
    )


class TestEachInTurn:
    """``holddays=0``, which B2 and B3 run, with its two exceptions."""

    def test_each_pair_is_held_in_turn_but_the_first_and_the_trailing_ones(self) -> None:
        """Pair 0's window is one row. Pairs 3 and 4 both have a near contract priced on the
        last row, and pair 3 takes the rows to 10 before it, so pair 4 is skipped."""
        contracts = _expiring([40, 70, 100, 119, 119, 119])
        schedule = calendar_schedule(contracts, spread_month=1, holddays=EACH_IN_TURN)
        held = [c for c in range(5) if (schedule.iloc[:, c] == -1).any()]
        assert held == [1, 2, 3]
        near = schedule.to_numpy() == -1
        assert np.flatnonzero(near[:, 1]).tolist() == list(range(31, 61))
        assert np.flatnonzero(near[:, 3]).tolist() == list(range(91, 110))

    def test_the_held_pair_ratio_under_it_rolls_on_each_held_pair(self) -> None:
        contracts = _expiring([40, 70, 100, 119, 119, 119])
        schedule = calendar_schedule(contracts, spread_month=1, holddays=EACH_IN_TURN)
        ratio = held_pair_ratio(contracts, schedule)
        prices = contracts.to_numpy()
        assert ratio.iloc[:31].isna().all()
        assert ratio.iloc[31] == prices[31, 2] / prices[31, 1]
        assert ratio.iloc[61] == prices[61, 3] / prices[61, 2]
        assert (ratio.iloc[110:] == prices[109, 4] / prices[109, 3]).all()

    def test_on_cls_strip_it_holds_68_of_77_pairs(self) -> None:
        """The count issue 348 left to this build, on
        ``inputdatadaily_cl_20120813/``, chan-mat, raw, saved 2012-08-14, with
        Example 5.4's ``spreadMonth=12``. The same two exceptions leave out CL-2007F's
        pair and the eight whose near contract still trades on 2012-08-13 after
        CL-2012U's."""
        contracts = load_strip("CL").contracts
        schedule = calendar_schedule(contracts, holddays=EACH_IN_TURN)
        near = (schedule == -1).any(axis=0).to_numpy()[:-12]
        assert (int(near.sum()), len(near)) == (68, 77)
        assert list(contracts.columns[:-12][~near]) == [
            "CL-2007F",
            "CL-2012V",
            "CL-2012X",
            "CL-2012Z",
            "CL-2013F",
            "CL-2013G",
            "CL-2013H",
            "CL-2013J",
            "CL-2013K",
        ]
        assert (schedule["CL-2012U"] == -1).any() and contracts["CL-2012U"].iloc[-1] > 0


# --- main and the report ----------------------------------------------------------


@pytest.fixture
def no_arguments(monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["vx_calendar_spread"])


class TestMain:
    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputDataDaily_VX_20120507"),
            WindowCrossesScaleBreak("inputdatadaily_vx_20120507/vx-2008x.csv changes scale"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, no_arguments, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "load_strip", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch, no_arguments) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "load_strip", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_main_refuses_an_argument(self, monkeypatch) -> None:
        monkeypatch.setattr("sys.argv", ["vx_calendar_spread", "--start", "2008-01-02"])
        with pytest.raises(SystemExit) as stopped:
            main()
        assert stopped.value.code == 2

    def test_run_reads_vx_and_passes_the_data_directory(
        self, strip, monkeypatch, capsys, tmp_path
    ) -> None:
        asked = []

        def fake_load_strip(root, data_dir=None):
            asked.append((root, data_dir))
            return strip

        monkeypatch.setattr(module, "load_strip", fake_load_strip)
        found, result = run(tmp_path)
        assert asked == [("VX", tmp_path)]
        assert found is strip
        assert list(result.rows) == list(ROWS)
        assert "Exploratory." in capsys.readouterr().out

    def test_main_on_an_empty_data_directory_names_the_file(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setattr("sys.argv", ["vx_calendar_spread"])
        monkeypatch.setattr(
            module, "load_strip", lambda root, data_dir=None: load_strip(root, tmp_path)
        )
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "inputDataDaily_VX_20120507" in str(stopped.value)


@pytest.fixture(scope="module")
def printed(strip, result) -> str:
    out = io.StringIO()
    with redirect_stdout(out):
        report(strip, result)
    return out.getvalue()


def _row(text: str, label: str) -> str:
    return next(r for r in text.splitlines() if r.strip().startswith(label))


class TestTheReport:
    def test_the_adf_row_carries_its_verdict_and_criterion(self, printed) -> None:
        row = _row(printed, "ADF statistic of the ratio")
        assert "-5.568107" in row.split() and "99 percent" in row
        assert "reproduced, criterion below the 1 percent critical value -3.4583" in row

    @pytest.mark.parametrize(
        ("label", "figures", "verdict"),
        [
            ("APR percent", ["-4.045401", "17.7"], "did not reproduce, gap -21.7"),
            ("Sharpe ratio", ["-0.563912", "1.5"], "did not reproduce, gap -2.1"),
        ],
    )
    def test_ss_apr_and_sharpe_ratio_carry_a_verdict(
        self, printed, label, figures, verdict
    ) -> None:
        row = _row(printed, label)
        assert all(figure in row.split() for figure in figures), row
        assert row.rstrip().endswith(verdict), row

    def test_the_rows_beside_and_after_carry_no_verdict(self, printed) -> None:
        beside = printed.split("Beside S, declared with it on issue 349.")[1]
        assert "B3 landing was found after the run" in beside
        b3 = _row(beside, "B3 ")
        assert "0.173462" in b3.split() and "1.457009" in b3.split()
        after = beside.split("Measured after seeing the rows above")[1]
        assert "APR 0.176952, Sharpe 1.475658" in _row(after, "B3 on the book's window")
        assert "APR -0.074173, Sharpe -0.562291" in _row(after, "B3   2007-01-23")
        assert "reproduce" not in beside

    def test_every_declared_row_prints_its_figures(self, printed, result) -> None:
        beside = printed.split("Beside S, declared with it on issue 349.")[1]
        for key in ROWS:
            found = result.rows[key]
            row = _row(beside, f"{key} ").split()
            assert f"{found.apr:.6f}" in row and f"{found.sharpe:.6f}" in row, SPECS[key]

    def test_it_prints_the_vintage_the_window_and_the_label(self, printed) -> None:
        assert "inputdatadaily_vx_20120507/" in _row(printed, "vintage")
        assert _row(printed, "vintage").endswith("no spot")
        assert _row(printed, "window").split()[1:] == [
            "2008-10-27",
            "to",
            "2012-05-07,",
            "889",
            "days",
        ]
        assert "Exploratory. docs/replication-log.md carries the verdicts." in printed
