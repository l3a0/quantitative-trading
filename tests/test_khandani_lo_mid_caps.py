"""The pins for Khandani and Lo's reversal on the S&P 400, between Chan's S&P 500 and S&P 600.

This file is the single authority for every number a prose surface quotes
about [issue 303](https://github.com/l3a0/quantitative-trading/issues/303)'s
run. ``docs/replication-log.md`` Entry 50 reports it and points here row by
row. The S&P 500 and S&P 600 figures it reads against are pinned in
``tests/test_khandani_lo.py`` and ``tests/test_khandani_lo_small_caps.py``,
and ``TestChansTwoFiles`` holds that this module's runs land on those same
pins rather than retyping them as new ones.

Every pin reads the same vintages and one specification, so they are stated
once here.

- **The S&P 400 vintage.** ``research/filings/ijh/members.csv``, IJH's 401
  holdings in iShares Trust's N-Q for 2007-12-31, accession
  ``0001193125-08-043324``, at the sha256
  ``tests/test_sp400_panel.py``'s ``MEMBERS_SHA256`` holds. A run holds the
  285 that pass the price check and have a 2006 row before the vendor's
  2006-12-28 cut-off. Their prices are the ``sp400`` cross-section in
  ``data/archive_vintages.jsonl``, Alpha Vantage's
  ``TIME_SERIES_DAILY_ADJUSTED`` downloaded on 2026-10-11.
- **The control's vintage.** ``research/filings/ijr/members_2007-12-31.csv``,
  IJR's 602 holdings in the same N-Q, of which a run holds 385 by the same
  rule. Their prices are the ``sp600`` cross-section, downloaded on
  2026-10-05 for the 509 rows IJR's members file shares and on 2026-10-05 or
  2026-10-11 for the 93 others.
- **Chan's two files.** ``spx_20071123/``, the S&P 500 as it stood on
  2007-11-23, and ``ijr_20080114/``, the S&P 600 as it stood on 2008-01-14,
  read through ``chan.series.load_panel`` for the close and with
  ``field="Open"`` for the open.
- **The price basis.** On the archive panels a close is ``adjusted_close``
  and an open is ``open × adjusted_close / close`` on the same day. Chan's
  files are his vendor's adjusted prices.
- **The specification.** Rule B, ``chan.khandani_lo.reversal`` unchanged, on
  frames cut to 2005-12-01 to 2006-12-31 for the archive panels and whole for
  Chan's files. Every run is read over 2006-01-03 to 2006-12-29, 251 trading
  days in all four. The cost is 5 basis points on each side of a change in
  weight, and the Sharpe ratio is ``√252 · mean / std`` with no risk-free
  rate. Each run gives the three figures ``chan.khandani_lo.Reversal``
  carries: before costs, after costs with Chan's two quirks kept, and after
  costs with the first day charged.
- **The exclusions.** The control's returns on CORSQ's 2006-05-19 and ZD's
  2006-05-25 are NaN, and MAG's price on 2006-01-10 is NaN, on both prices.
  The control is pinned with them, which is primary, and without them.

Every figure is pinned at four decimals, at ``abs=5e-5``, which is what lets
the log quote it at four. A gap and its standard error are Memmel's (2003)
test on two before-cost daily series, as
``chan.khandani_lo_small_caps.sharpe_gap`` computes it, and they rest on its
assumption that the daily profits are independent and normal.

The archive pins skip where no archive is configured or ``QT_ARCHIVE_RUN`` is
not 1, the way ``tests/conftest.py``'s ``archive_skip_reason`` decides. The
readings and the exclusions are also tested on frames built by hand, which
run everywhere.

EXPLORATORY. The run applies a rule Chan published, unchanged, to stocks from
the S&P 400 and S&P 600, the two universes his exercise names, and Chan prints
no figure for either
universe, so no figure carries a verdict. Every reading was declared on issue
303 before any figure was computed. It first ran on 2026-10-11.
"""

from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import io
import math

import numpy as np
import pandas as pd
import pytest

from chan import archive, khandani_lo, khandani_lo_small_caps, paths, sp400_panel
from chan import khandani_lo_mid_caps as mid_caps
from chan.fund_panel import numbered_members
from chan.khandani_lo import daily_returns, reversal, reversal_weights
from chan.khandani_lo_mid_caps import (
    BAD_PRINTS,
    HOLDS,
    KEPT_FLAGGED_DAYS,
    NOT_SEPARABLE,
    PARTIAL,
    REVERSED,
    SPLIT_DAYS,
    MidCapComparison,
    exclude,
    nearer_step,
    order,
    pair_directions,
    reading,
    separable,
    split_at,
    split_column,
    without_bad_prints,
)
from chan.khandani_lo_small_caps import MIXED, POINTING_AGAINST, POINTING_CHANS_WAY
from tests.conftest import archive_skip_reason
from tests.test_sp400_panel import MEMBERS_SHA256

START, END = pd.Timestamp("2006-01-03"), pd.Timestamp("2006-12-29")
PRICES = ("closes", "opens")


def approx(value: float) -> object:
    return pytest.approx(value, abs=5e-5)


# --- the readings, on figures written by hand ----------------------------------


class TestTheOrder:
    """One price's three figures, S&P 500 first, read as issue 303 declared."""

    @pytest.mark.parametrize(
        ("figures", "word"),
        [
            ((0.25, 2.03, 3.41), HOLDS),
            ((3.41, 2.03, 0.25), REVERSED),
            ((4.42, 3.45, 5.31), PARTIAL),
            ((0.25, 3.41, 2.03), PARTIAL),
            ((0.25, 0.25, 3.41), PARTIAL),
            ((3.41, 2.03, 2.03), PARTIAL),
        ],
    )
    def test_holds_fully_reversed_or_partial(self, figures, word) -> None:
        assert order(figures) == word

    def test_the_three_words(self) -> None:
        assert (HOLDS, REVERSED, PARTIAL) == ("holds", "fully reversed", "partial")

    @pytest.mark.parametrize(
        ("figures", "steps"),
        [
            ((0.25, 2.03, 3.41), (True, True)),
            ((4.42, 3.45, 5.31), (False, True)),
            ((0.25, 3.41, 2.03), (True, False)),
            ((3.41, 2.03, 0.25), (False, False)),
            ((1.0, 1.0, 2.0), (False, True)),
        ],
    )
    def test_each_adjacent_pair_largest_first(self, figures, steps) -> None:
        assert pair_directions(figures) == steps

    def test_one_universe_has_no_pair(self) -> None:
        with pytest.raises(ValueError, match="at least two universes"):
            pair_directions([1.0])


class TestTheReading:
    @pytest.mark.parametrize(
        ("closes", "opens", "word"),
        [
            ((0.25, 2.03, 3.41), (4.42, 4.9, 5.31), POINTING_CHANS_WAY),
            ((3.41, 2.03, 0.25), (5.31, 4.9, 4.42), POINTING_AGAINST),
            ((0.25, 2.03, 3.41), (4.42, 3.45, 5.31), MIXED),
            ((0.25, 2.03, 3.41), (5.31, 4.9, 4.42), MIXED),
            ((3.41, 2.03, 0.25), (4.42, 3.45, 5.31), MIXED),
            ((4.42, 3.45, 5.31), (4.42, 3.45, 5.31), MIXED),
        ],
    )
    def test_both_prices_read_together(self, closes, opens, word) -> None:
        assert reading(closes, opens) == word

    def test_the_words_are_issue_249s(self) -> None:
        assert (POINTING_CHANS_WAY, MIXED, POINTING_AGAINST) == (
            "pointing the way Chan says",
            "mixed",
            "pointing against it",
        )


class TestTheControlRule:
    @pytest.mark.parametrize(
        ("figures", "step"),
        [
            ((0.25, 2.03, 3.41), 1.38),
            ((4.42, 3.45, 5.31), 0.97),
            ((1.0, 5.0, 5.5), 0.5),
            ((1.0, 5.0, 4.5), 0.5),
        ],
    )
    def test_the_nearer_step(self, figures, step) -> None:
        """A distance, so the S&P 600 below the S&P 400 counts the same as above it."""
        assert nearer_step(figures) == pytest.approx(step)

    @pytest.mark.parametrize(
        ("gaps", "steps", "held"),
        [
            ((0.1, -0.7), (1.4, 0.97), True),
            ((0.1, -1.0), (1.4, 0.97), False),
            ((1.5, 0.0), (1.4, 0.97), False),
            ((-1.4, 0.97), (1.4, 0.97), True),
        ],
    )
    def test_a_gap_wider_than_the_step_at_either_price_is_not_separable(
        self, gaps, steps, held
    ) -> None:
        assert separable(gaps, steps) is held

    def test_one_gap_per_price(self) -> None:
        with pytest.raises(ValueError, match="one control gap per price"):
            separable([0.1], [1.0, 1.0])

    def test_a_comparison_that_is_not_separable_reads_no_direction(self) -> None:
        """Stand-in ladders whose order holds at both prices, with a control too wide."""

        def stand_in(figures, control_gap):
            large, mid, small = figures
            return mid_caps.Ladder(
                large=_figure(large),
                mid=_figure(mid),
                small=_figure(small),
                control=None,
                control_unexcluded=None,
                mid_gap=None,
                small_gap=None,
                control_gap=_gap(control_gap),
                control_gap_unexcluded=_gap(control_gap),
            )

        holding = MidCapComparison(
            closes=stand_in((0.25, 2.03, 3.41), 0.1), opens=stand_in((4.0, 4.5, 5.3), 0.4)
        )
        assert holding.reading == POINTING_CHANS_WAY
        too_wide = MidCapComparison(
            closes=stand_in((0.25, 2.03, 3.41), 0.1), opens=stand_in((4.0, 4.5, 5.3), -0.6)
        )
        assert not too_wide.separable
        assert too_wide.reading == NOT_SEPARABLE == "not separable from how the panel was built"


def _figure(before_costs: float):
    return type("Run", (), {"before_costs": before_costs})()


def _gap(gap: float):
    return type("Gap", (), {"gap": gap})()


# --- the exclusions, on frames written by hand --------------------------------------

DAYS = pd.bdate_range("2006-01-02", periods=8)
NAN = math.nan


def _frame() -> pd.DataFrame:
    """Three members over eight days. BBB halves on day 4, and CCC prints low on day 2."""
    return pd.DataFrame(
        {
            "AAA": [10.0, 10.5, 10.2, 10.4, 10.1, 10.3, 10.6, 10.5],
            "BBB": [40.0, 41.0, 40.0, 42.0, 21.5, 21.0, 21.8, 22.0],
            "CCC": [5.0, 5.2, 2.0, 5.1, 5.3, 5.2, 5.0, 5.1],
        },
        index=DAYS,
    )


def _returns(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        daily_returns(frame.to_numpy(dtype=float)), index=frame.index, columns=frame.columns
    )


def _rejoined(returns: pd.DataFrame, splits) -> pd.DataFrame:
    """Each split member's two columns read back as one, its returns side by side."""
    out = returns.copy()
    for symbol, day in splits.items():
        out[symbol] = out[symbol].combine_first(out[split_column(symbol, day)])
        out = out.drop(columns=split_column(symbol, day))
    return out


def _changed(before: pd.DataFrame, after: pd.DataFrame) -> list[tuple[str, str]]:
    same = (before == after) | (before.isna() & after.isna())
    return [
        (symbol, day.date().isoformat())
        for symbol in before.columns
        for day in before.index[~same[symbol]]
    ]


class TestTheExclusions:
    SPLIT = {"BBB": DAYS[4].date().isoformat()}
    PRINT = {"CCC": DAYS[2].date().isoformat()}

    def test_a_bad_print_is_one_price_and_the_two_returns_touching_it(self) -> None:
        frame = _frame()
        out = without_bad_prints(frame, self.PRINT)
        assert _changed(frame, out) == [("CCC", self.PRINT["CCC"])]
        assert _changed(_returns(frame), _returns(out)) == [
            ("CCC", DAYS[2].date().isoformat()),
            ("CCC", DAYS[3].date().isoformat()),
        ]
        assert _returns(out).loc[DAYS[2:4], "CCC"].isna().all()

    def test_a_split_is_one_return_and_keeps_every_price(self) -> None:
        frame = _frame()
        out = split_at(frame, self.SPLIT)
        assert list(out.columns) == ["AAA", "BBB", "BBB from 2006-01-06", "CCC"]
        assert out[["AAA", "CCC"]].equals(frame[["AAA", "CCC"]])
        assert out["BBB"].loc[: DAYS[3]].equals(frame["BBB"].loc[: DAYS[3]])
        assert out["BBB"].loc[DAYS[4] :].isna().all()
        assert out["BBB from 2006-01-06"].loc[: DAYS[3]].isna().all()
        assert out["BBB"].combine_first(out["BBB from 2006-01-06"]).equals(frame["BBB"])
        assert _changed(_returns(frame), _rejoined(_returns(out), self.SPLIT)) == [
            ("BBB", "2006-01-06")
        ]

    def test_a_split_keeps_each_days_count_of_priced_members(self) -> None:
        frame = _frame()
        out = split_at(frame, self.SPLIT)
        assert (out.notna().sum(axis=1) == frame.notna().sum(axis=1)).all()

    def test_a_split_weights_the_member_at_0_on_its_day_and_nowhere_else(self) -> None:
        frame = _frame()
        out = split_at(frame, self.SPLIT)
        weights = pd.DataFrame(
            reversal_weights(out.to_numpy(dtype=float)), index=out.index, columns=out.columns
        )
        both = weights["BBB"] + weights["BBB from 2006-01-06"]
        assert both.iloc[4] == 0.0
        assert (both.iloc[2:4] != 0.0).all() and (both.iloc[5:] != 0.0).all()
        unsplit = reversal_weights(frame.to_numpy(dtype=float))
        assert weights["AAA"].iloc[[1, 2, 3, 5, 6, 7]].to_numpy() == pytest.approx(
            unsplit[[1, 2, 3, 5, 6, 7], 0]
        )

    def test_the_profit_is_the_unexcluded_profit_less_the_split_days_term(self) -> None:
        """Before costs, the only day that moves is the split day, by the member's own term."""
        frame = _frame()
        window = {"start": str(DAYS[1].date()), "end": str(DAYS[-1].date())}
        whole = reversal(frame, **window)
        split = reversal(split_at(frame, self.SPLIT), **window)
        weights = reversal_weights(frame.to_numpy(dtype=float))
        returns = daily_returns(frame.to_numpy(dtype=float))
        # The window starts on day 1, so the split day, day 4, is position 3.
        moved = np.flatnonzero(~np.isclose(whole.pnl, split.pnl))
        assert list(moved) == [3, 4]
        assert split.pnl[3] == pytest.approx(whole.pnl[3] - weights[3, 1] * returns[4, 1])

    def test_the_declared_cells(self) -> None:
        assert SPLIT_DAYS == {"CORSQ": "2006-05-19", "ZD": "2006-05-25"}
        assert BAD_PRINTS == {"MAG": "2006-01-10"}
        assert KEPT_FLAGGED_DAYS == {"KCI": "2006-08-04"}
        assert "KCI" not in SPLIT_DAYS and "KCI" not in BAD_PRINTS

    def test_exclude_makes_exactly_the_declared_returns_nan(self) -> None:
        """On a stand-in control frame of 2006 business days, every price 1 plus a drift."""
        days = pd.bdate_range("2006-01-02", "2006-06-30")
        drift = np.linspace(1.0, 2.0, len(days))
        frame = pd.DataFrame(
            {symbol: drift * (k + 1) for k, symbol in enumerate(("AAA", "CORSQ", "MAG", "ZD"))},
            index=days,
        )
        changed = _changed(_returns(frame), _rejoined(_returns(exclude(frame)), SPLIT_DAYS))
        assert changed == [
            ("CORSQ", "2006-05-19"),
            ("MAG", "2006-01-10"),
            ("MAG", "2006-01-11"),
            ("ZD", "2006-05-25"),
        ]

    @pytest.mark.parametrize(
        ("prints", "said"),
        [({"DDD": "2006-01-04"}, "DDD has no price"), ({"CCC": "2006-03-01"}, "CCC has no price")],
    )
    def test_a_bad_print_the_frame_does_not_hold_is_refused(self, prints, said) -> None:
        with pytest.raises(ValueError, match=said):
            without_bad_prints(_frame(), prints)

    def test_a_bad_print_already_missing_is_refused(self) -> None:
        frame = _frame()
        frame.iloc[2, 2] = NAN
        with pytest.raises(ValueError, match="CCC has no price"):
            without_bad_prints(frame, self.PRINT)

    @pytest.mark.parametrize(
        "splits", [{"DDD": "2006-01-06"}, {"BBB": "2006-03-01"}, {"BBB": "2006-01-02"}]
    )
    def test_a_split_with_no_return_to_exclude_is_refused(self, splits) -> None:
        with pytest.raises(ValueError, match="BBB|DDD"):
            split_at(_frame(), splits)

    def test_a_split_on_a_day_with_no_price_is_refused(self) -> None:
        """With no price on the day there is no return to exclude, only one already missing."""
        frame = _frame()
        frame.iloc[4, 1] = NAN
        with pytest.raises(ValueError, match="BBB has no return on 2006-01-06"):
            split_at(frame, self.SPLIT)


class TestTheLadderRefusesMismatchedDays:
    """Rule B on stand-in frames of 2005-12-01 to 2006-12-31 business days, six members.

    The prices are a seeded random walk. The one mismatch is 2006-06-01, dropped
    from one frame, so a gap would otherwise pair profits from different days.
    """

    @staticmethod
    def _prices() -> pd.DataFrame:
        days = pd.bdate_range("2005-12-01", "2006-12-31")
        steps = np.random.default_rng(0).normal(0, 0.01, (len(days), 6))
        return pd.DataFrame(
            100 * np.exp(np.cumsum(steps, axis=0)),
            index=days,
            columns=["AAA", "CORSQ", "MAG", "ZD", "EEE", "FFF"],
        )

    @pytest.mark.parametrize("short", ["mid", "control"])
    def test_a_frame_missing_a_day_is_refused(self, short) -> None:
        prices = self._prices()
        frames = dict.fromkeys(("large", "mid", "small", "control"), prices)
        frames[short] = prices.drop(index=pd.Timestamp("2006-06-01"))
        with pytest.raises(ValueError, match="different trading days"):
            mid_caps.ladder(**frames)


# --- the run, on the owner's archive and Chan's files ---------------------------------


@pytest.fixture(scope="module")
def read():
    """Every panel read once, or a skip naming what is missing."""
    reason = archive_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    return mid_caps.read()


@pytest.fixture(scope="module")
def frames(read) -> mid_caps.Frames:
    return read[2]


@pytest.fixture(scope="module")
def result(frames) -> MidCapComparison:
    return mid_caps.comparison(frames)


class TestTheCommittedVintage:
    """The members files the archive pins read, which runs everywhere."""

    @pytest.mark.parametrize("name", ["ijh", "control"])
    def test_the_members_files(self, name) -> None:
        path = sp400_panel.PANELS[name].path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == MEMBERS_SHA256[name]

    def test_the_panels_and_files(self) -> None:
        assert (mid_caps.LARGE_CAP_FILE, mid_caps.SMALL_CAP_FILE) == (
            "SPX_20071123.mat",
            khandani_lo_small_caps.SOURCE_FILE,
        )
        assert (sp400_panel.IJH_PANEL.cross_section, sp400_panel.CONTROL.cross_section) == (
            "sp400",
            "sp600",
        )


class TestThePanels:
    def test_the_run_holds_285_and_385_members(self, read) -> None:
        _, (mid, control), frames = read
        assert (len(mid), len(control)) == (285, 385)
        assert list(frames.mid_closes.columns) == mid == sorted(mid)
        assert list(frames.control_opens.columns) == control

    @pytest.mark.parametrize(
        ("panel", "index", "count", "value"),
        [(sp400_panel.IJH_PANEL, 0, 0.711, 0.748), (sp400_panel.CONTROL, 1, 0.640, 0.681)],
    )
    def test_the_share_of_each_filing_a_run_holds(self, read, panel, index, count, value) -> None:
        """By count and by the filing's value, at the one decimal of a percentage the log quotes."""
        held = read[1][index]
        rows = sp400_panel.load(panel)
        holdings = dict(numbered_members(panel.fund, sp400_panel.REPORT_DATE))
        row_of = {row.ticker: row.row for row in rows if row.check == "pass"}
        total = sum(int(h.value) for h in holdings.values())
        kept = sum(int(holdings[row_of[ticker]].value) for ticker in held)
        assert round(len(held) / len(rows), 3) == count
        assert round(kept / total, 3) == value

    def test_each_archive_frame_is_the_calendar_over_its_span(self, frames) -> None:
        calendar = sp400_panel.calendar()
        span = calendar[
            (calendar >= pd.Timestamp(mid_caps.FRAME_START))
            & (calendar <= pd.Timestamp(mid_caps.FRAME_END))
        ]
        for frame in (frames.mid_closes, frames.mid_opens, frames.control_closes):
            assert frame.index.equals(span)
        assert (span[0], len(span)) == (pd.Timestamp("2005-12-01"), 272)

    def test_all_four_runs_hold_the_same_251_days_at_both_prices(self, result) -> None:
        for price in PRICES:
            ladder = getattr(result, price)
            for run in (ladder.large, ladder.mid, ladder.small, ladder.control):
                assert run.days.equals(ladder.large.days)
            assert len(ladder.large.days) == 251
            assert (ladder.large.days[0], ladder.large.days[-1]) == (START, END)

    def test_no_day_of_profit_before_costs_is_nan(self, result) -> None:
        for price in PRICES:
            ladder = getattr(result, price)
            for run in (ladder.mid, ladder.control, ladder.control_unexcluded):
                assert np.isfinite(run.pnl).all()


class TestChansTwoFiles:
    """The S&P 500 and S&P 600 runs land on the pins the two earlier test files hold."""

    def test_they_are_the_small_cap_modules_runs_to_the_bit(self, result) -> None:
        earlier = khandani_lo_small_caps.compare()
        for price in PRICES:
            ladder = getattr(result, price)
            for mine, theirs in (
                (ladder.large, getattr(earlier, f"large_{price}")),
                (ladder.small, getattr(earlier, f"small_{price}")),
            ):
                for field in ("before_costs", "after_costs", "after_costs_charged"):
                    assert getattr(mine, field) == getattr(theirs, field)

    @pytest.mark.parametrize(
        ("price", "universe", "figures"),
        [
            ("closes", "large", (0.2510, -3.1884, -3.2337)),
            ("opens", "large", (4.4202, 0.7834, 0.8293)),
            ("closes", "small", (3.4086, -0.3702, -0.3255)),
            ("opens", "small", (5.3052, 2.0147, 2.0257)),
        ],
    )
    def test_the_pinned_figures(self, result, price, universe, figures) -> None:
        run = getattr(getattr(result, price), universe)
        assert (run.before_costs, run.after_costs, run.after_costs_charged) == tuple(
            approx(f) for f in figures
        )


class TestTheMidCapFigures:
    """Rule B on the 285 held IJH members, 2006-01-03 to 2006-12-29, 5 bp a side."""

    def test_closes(self, result) -> None:
        r = result.closes.mid
        assert r.before_costs == approx(2.0338)
        assert r.after_costs == approx(-1.4444)
        assert r.after_costs_charged == approx(-1.4524)

    def test_opens(self, result) -> None:
        r = result.opens.mid
        assert r.before_costs == approx(3.4533)
        assert r.after_costs == approx(0.4589)
        assert r.after_costs_charged == approx(0.4884)


class TestTheGapsToBothNeighbours:
    """Memmel's test on each adjacent pair's before-cost profit, the smaller index as ``a``."""

    @pytest.mark.parametrize(
        ("price", "pair", "gap", "error", "correlation", "z", "beyond"),
        [
            ("closes", "mid_gap", 1.7828, 0.8114, 0.6758, 2.1973, True),
            ("closes", "small_gap", 1.3748, 1.0113, 0.5028, 1.3593, False),
            ("opens", "mid_gap", -0.9669, 0.8972, 0.6188, -1.0777, False),
            ("opens", "small_gap", 1.8519, 1.1948, 0.3250, 1.5500, False),
        ],
    )
    def test_the_gap(self, result, price, pair, gap, error, correlation, z, beyond) -> None:
        g = getattr(getattr(result, price), pair)
        assert g.days == 251
        assert (g.gap, g.standard_error, g.correlation, g.z) == (
            approx(gap),
            approx(error),
            approx(correlation),
            approx(z),
        )
        assert g.beyond_noise is beyond

    def test_the_gaps_are_the_runs_own_figures_exactly(self, result) -> None:
        for price in PRICES:
            ladder = getattr(result, price)
            assert ladder.mid_gap.a_sharpe == ladder.mid.before_costs
            assert ladder.mid_gap.b_sharpe == ladder.large.before_costs
            assert ladder.small_gap.a_sharpe == ladder.small.before_costs
            assert ladder.small_gap.b_sharpe == ladder.mid.before_costs

    def test_the_whiteboard_draws_this_runs_figures(self, result) -> None:
        """The size-order sketch in ``tests/test_khandani_lo_small_caps_whiteboard.py``
        draws its ``PINNED_MID`` figures, so it runs without the archive. This
        holds that this run gives them, each within 1e-12 of the figure the sketch
        was drawn from."""
        from chan.khandani_lo_small_caps_whiteboard import MidCaps
        from tests.test_khandani_lo_small_caps_whiteboard import PINNED_MID

        drawn = MidCaps.from_run(result)
        for field in dataclasses.fields(MidCaps):
            name = field.name
            assert getattr(drawn, name) == pytest.approx(getattr(PINNED_MID, name), abs=1e-12), name


class TestTheControl:
    """IJR's 385 held members, built as the S&P 400 panel is, against Chan's S&P 600 file."""

    @pytest.mark.parametrize(
        ("price", "excluded", "unexcluded"),
        [
            ("closes", (3.5194, 0.0655, 0.0575), (1.8962, 0.9858, 0.9798)),
            ("opens", (4.5808, 1.6774, 1.6903), (2.6002, 1.5671, 1.5679)),
        ],
    )
    def test_the_figures_with_and_without_the_exclusions(
        self, result, price, excluded, unexcluded
    ) -> None:
        ladder = getattr(result, price)
        for run, figures in ((ladder.control, excluded), (ladder.control_unexcluded, unexcluded)):
            assert (run.before_costs, run.after_costs, run.after_costs_charged) == tuple(
                approx(f) for f in figures
            )

    @pytest.mark.parametrize(
        ("price", "gap", "error", "correlation", "z", "beyond"),
        [
            ("closes", 0.1108, 0.4943, 0.8836, 0.2241, False),
            ("opens", -0.7244, 0.5768, 0.8484, -1.2559, False),
        ],
    )
    def test_the_gap_to_chans_file(self, result, price, gap, error, correlation, z, beyond) -> None:
        g = getattr(result, price).control_gap
        assert (g.gap, g.standard_error, g.correlation, g.z) == (
            approx(gap),
            approx(error),
            approx(correlation),
            approx(z),
        )
        assert g.beyond_noise is beyond

    @pytest.mark.parametrize(
        ("price", "gap", "error", "correlation", "z", "beyond"),
        [
            ("closes", -1.5124, 1.2979, 0.1758, -1.1653, False),
            ("opens", -2.7050, 1.2882, 0.2070, -2.0998, True),
        ],
    )
    def test_the_gap_without_the_exclusions(
        self, result, price, gap, error, correlation, z, beyond
    ) -> None:
        g = getattr(result, price).control_gap_unexcluded
        assert (g.gap, g.standard_error, g.correlation, g.z) == (
            approx(gap),
            approx(error),
            approx(correlation),
            approx(z),
        )
        assert g.beyond_noise is beyond

    @pytest.mark.parametrize(
        ("price", "figures"),
        [("closes", (3.5194, 0.0657, 0.0577)), ("opens", (4.5808, 1.6775, 1.6904))],
    )
    def test_a_literal_nan_return_on_the_split_days_moves_only_the_after_cost_figures(
        self, frames, monkeypatch, price, figures
    ) -> None:
        """What the split treatment's charge for closing and reopening costs.

        Same vintage and specification as the primary control, with MAG's bad
        print excluded as declared, but each split day's return set to NaN in
        ``chan.khandani_lo.daily_returns`` instead of carrying the member
        under two columns. The member's weight on that day is then NaN rather
        than 0, so the cost charges no close and no reopening. Before costs
        the two treatments agree, and after costs this one sits above the
        primary figures.
        """
        raw = getattr(frames, f"control_{price}")
        primary = reversal(exclude(raw))
        frame = without_bad_prints(raw, BAD_PRINTS)
        cells = [
            (frame.index.get_loc(pd.Timestamp(day)), frame.columns.get_loc(symbol))
            for symbol, day in SPLIT_DAYS.items()
        ]

        def with_nan_returns(prices: np.ndarray) -> np.ndarray:
            returns = daily_returns(prices)
            for row, column in cells:
                returns[row, column] = math.nan
            return returns

        monkeypatch.setattr(khandani_lo, "daily_returns", with_nan_returns)
        run = khandani_lo.reversal(frame)
        assert (run.before_costs, run.after_costs, run.after_costs_charged) == tuple(
            approx(f) for f in figures
        )
        assert run.before_costs == pytest.approx(primary.before_costs, abs=1e-12)
        assert run.after_costs > primary.after_costs
        assert run.after_costs_charged > primary.after_costs_charged

    def test_the_s_and_p_400s_step_to_its_nearer_neighbour(self, result) -> None:
        """On the closes the S&P 600 is nearer, and on the opens the S&P 500 is."""
        assert result.closes.nearer_step == approx(1.3748)
        assert result.closes.nearer_step == result.closes.small_gap.gap
        assert result.opens.nearer_step == approx(0.9669)
        assert result.opens.nearer_step == -result.opens.mid_gap.gap

    def test_the_ordering_is_separable_with_the_exclusions_and_not_without(self, result) -> None:
        assert result.separable
        assert not result.separable_unexcluded

    def test_the_exclusion_changes_the_returns_on_exactly_the_declared_cells(self, frames) -> None:
        for price in PRICES:
            raw = getattr(frames, f"control_{price}")
            out = exclude(raw)
            assert [c for c in out.columns if c not in raw.columns] == [
                "CORSQ from 2006-05-19",
                "ZD from 2006-05-25",
            ]
            changed = _changed(_returns(raw), _rejoined(_returns(out), SPLIT_DAYS))
            assert changed == [
                ("CORSQ", "2006-05-19"),
                ("MAG", "2006-01-10"),
                ("MAG", "2006-01-11"),
                ("ZD", "2006-05-25"),
            ], price

    @pytest.mark.parametrize(
        ("price", "before", "day", "after"),
        [("closes", 32.1999, 12.5599, 32.7818), ("opens", 31.2300, 12.5599, 32.0059)],
    )
    def test_mags_bad_print_shows_on_both_prices(self, frames, price, before, day, after) -> None:
        column = getattr(frames, f"control_{price}")["MAG"]
        assert column.loc["2006-01-09":"2006-01-11"].tolist() == [
            approx(before),
            approx(day),
            approx(after),
        ]


class TestTheFlaggedDaysRawRows:
    """The raw closes and volumes the classification quoted, which the log quotes too."""

    @pytest.mark.parametrize(
        ("cross_section", "symbol", "start", "closes", "volumes"),
        [
            ("sp400", "KCI", "2006-08-03", [42.58, 24.95], [1_511_000, 13_567_800]),
            ("sp600", "CORSQ", "2006-05-18", [59.21, 30.00], [459_412, 1_301_321]),
            ("sp600", "ZD", "2006-05-24", [51.67, 28.15], [745_600, 1_123_900]),
            ("sp600", "MAG", "2006-01-09", [3.32, 1.295, 3.38], [1_901_000, 56_800, 270_000]),
        ],
    )
    def test_the_rows(self, read, cross_section, symbol, start, closes, volumes) -> None:
        rows = len(closes)
        _, close = archive.read_cross_section(cross_section, column="close", symbols=[symbol])
        _, volume = archive.read_cross_section(cross_section, column="volume", symbols=[symbol])
        assert close[symbol].loc[start:].head(rows).tolist() == closes
        assert volume[symbol].loc[start:].head(rows).tolist() == volumes


class TestTheFlaggedDayKept:
    def test_kcis_return_is_finite_and_weighted_on_both_prices(self, frames) -> None:
        for frame, ratio in ((frames.mid_closes, 0.5860), (frames.mid_opens, 0.5522)):
            prices = frame.to_numpy(dtype=float)
            row = frame.index.get_loc(pd.Timestamp(KEPT_FLAGGED_DAYS["KCI"]))
            column = frame.columns.get_loc("KCI")
            assert prices[row, column] / prices[row - 1, column] == approx(ratio)
            assert np.isfinite(daily_returns(prices)[row, column])
            assert reversal_weights(prices)[row, column] > 0


class TestTheRunsReading:
    def test_the_order_holds_on_the_closes_and_is_partial_on_the_opens(self, result) -> None:
        assert (result.closes.order, result.opens.order) == (HOLDS, PARTIAL)
        assert pair_directions(result.closes.figures) == (True, True)
        assert pair_directions(result.opens.figures) == (False, True)

    def test_it_reads_mixed(self, result) -> None:
        """Declared on issue 303 before any figure was computed."""
        assert result.reading == MIXED


@pytest.fixture(scope="module")
def printed(read, result) -> str:
    """The report on the run the other pins read, rather than a second read of every panel."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        mid_caps.report(read[0], read[1], result)
    return out.getvalue()


class TestTheReport:
    def test_the_panels(self, printed) -> None:
        assert "500 members lifted from SPX_20071123.mat" in printed
        assert "600 members lifted from IJR_20080114.mat" in printed
        assert "285 of IJH's 401 holdings on 2007-12-31, sp400 cross-section" in printed
        assert "385 of IJR's 602 holdings on 2007-12-31" in printed
        assert "2006-01-03 to 2006-12-29, 251 trading days" in printed

    @pytest.mark.parametrize(
        ("line", "figures"),
        [
            ("Closes, before costs", ["0.2510", "2.0338", "3.4086", "3.5194", "1.8962"]),
            ("Closes, after 5 bp a side, first day uncharged",
             ["-3.1884", "-1.4444", "-0.3702", "0.0655", "0.9858"]),
            ("Closes, after 5 bp a side, first day charged",
             ["-3.2337", "-1.4524", "-0.3255", "0.0575", "0.9798"]),
            ("Opens, before costs", ["4.4202", "3.4533", "5.3052", "4.5808", "2.6002"]),
            ("Opens, after 5 bp a side, first day uncharged",
             ["0.7834", "0.4589", "2.0147", "1.6774", "1.5671"]),
            ("Opens, after 5 bp a side, first day charged",
             ["0.8293", "0.4884", "2.0257", "1.6903", "1.5679"]),
        ],
    )  # fmt: skip
    def test_each_figure_row(self, printed, line, figures) -> None:
        (row,) = [each for each in printed.splitlines() if line in each]
        assert row.split()[-5:] == figures

    def test_the_gaps_steps_and_reading(self, printed) -> None:
        assert (
            "S&P 400 less S&P 500               gap +1.7828, standard error 0.8114, "
            "correlation 0.6758, z +2.1973, beyond one year's noise" in printed
        )
        assert "control less Chan's S&P 600        gap -0.7244, standard error 0.5768" in printed
        # The step line prints the control's gaps unsigned, as separable reads them.
        assert (
            "S&P 400's step to its nearer neighbour 0.9669, "
            "control's gap 0.7244, 2.7050 unexcluded" in printed
        )
        assert "Closes  order holds, S&P 500 to S&P 400 rises, S&P 400 to S&P 600 rises" in printed
        assert (
            "Opens   order partial, S&P 500 to S&P 400 does not rise, S&P 400 to S&P 600 rises"
            in printed
        )
        assert "Control within the step at both prices: yes, and no without the exclusions." in (
            printed
        )
        assert "Reading, declared before any figure: mixed." in printed
        assert "EXPLORATORY." in printed
        assert "judged against nothing" in printed


class TestTheCommand:
    def test_a_missing_archive_reaches_the_reader_as_one_line(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setattr("sys.argv", ["chan.khandani_lo_mid_caps"])
        monkeypatch.delenv("QT_ARCHIVE_DIR", raising=False)
        monkeypatch.setattr(archive, "ARCHIVE_DIR_CONFIG", tmp_path / "absent")
        with pytest.raises(SystemExit) as stopped:
            mid_caps.main()
        assert str(stopped.value).startswith("no data archive is configured")


# --- what the post quotes ----------------------------------------------------------------

POST = paths.REPO_ROOT / "blog" / "khandani-lo-small-caps-lessons.md"


@pytest.fixture(scope="module")
def post() -> str:
    return POST.read_text(encoding="utf-8")


class TestThePostQuotesTheLadder:
    """Lesson 6 of ``blog/khandani-lo-small-caps-lessons.md`` quotes this run, each figure once.

    Each fragment is built from the run at the precision the post prints, so
    a typo in the post fails here. It needs the archive, so it skips with the
    archive pins above. Its words, such as "about one standard error" and
    "most of the 116", are not asserted, and the size-order sketch's alt text
    is held by ``tests/test_khandani_lo_small_caps_whiteboard.py``.
    """

    def test_the_holdings(self, post, read) -> None:
        _, (mid, _), _ = read
        holdings = len(sp400_panel.load(sp400_panel.IJH_PANEL))
        fragments = [
            f"That run starts from the {holdings} holdings",
            f"Of the {holdings}, {len(mid)} pass both. Most of the {holdings - len(mid)} left out",
        ]
        assert [f for f in fragments if f not in post] == []

    def test_the_ladder_and_the_control(self, post, result) -> None:
        c, o = result.closes, result.opens
        assert c.control_gap.gap > 0 > o.control_gap.gap
        # The post names the nearer neighbour at each price, the S&P 600 on the
        # closes and the S&P 500 on the opens.
        assert c.nearer_step == c.small_gap.gap and o.nearer_step == -o.mid_gap.gap
        fragments = [
            f"Before costs the S&P 400’s Sharpe ratio is {c.mid.before_costs:.4f} on the closes, "
            f"between the S&P 500’s {c.large.before_costs:.4f} and the S&P 600’s "
            f"{c.small.before_costs:.4f}.",
            f"On the opens it is {o.mid.before_costs:.4f}, below both the S&P 500’s "
            f"{o.large.before_costs:.4f} and the S&P 600’s {o.small.before_costs:.4f}.",
            "the step on the closes from the S&P 500 to the S&P 400, "
            f"at {c.mid_gap.z:.4f} standard errors.",
            f"lands {c.control_gap.gap:.4f} above that file’s on the closes and "
            f"{-o.control_gap.gap:.4f} below it on the opens.",
            f"On the closes that neighbour is the S&P 600, {c.nearer_step:.4f} away, "
            f"and on the opens it is the S&P 500, {o.nearer_step:.4f} away.",
        ]
        assert [f for f in fragments if f not in post] == []
