"""The pins for post-earnings announcement drift, *Algorithmic Trading*'s Example 7.2.

This file is the single authority for every number any prose surface quotes
about Example 7.2. ``docs/replication-log.md`` Entry 12 carries the verdicts and
points here row by row.

Every pin on the committed files reads two vintages and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintages.** ``inputdataohlcdaily_stocks_20120424/``, the 497 stocks lifted
  from Chan's ``inputDataOHLCDaily_stocks_20120424.mat``, read for the Open and
  Close columns, and ``earnannfile/``, the 497 flag series lifted from his
  ``earnannFile.mat``, read for the Flag column. Their identities are the two
  rows of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``, which
  ``TestTheVintages`` holds the members to. The price file is the S&P 500 as
  Chan held it on 2012-04-24, so every figure is a figure about survivors.
- **Specification.** ``pead.m`` at the mirror commit :mod:`chan.pead` names.
  The prices are cut to the flag file's 330 days before the close-to-open gap
  is taken. The moving standard deviation is book two's ``smartMovingStd``
  over a 90-day lookback. A stock enters on an announcement day whose gap is
  at least 0.5 of that, long or short by its sign, and each day's summed
  return is divided by 30. Every annualisation uses 252 days.

Each of Chan's figures is pinned twice. Once at the precision that is real,
six decimals for the returns and the drawdown and four for the Sharpe ratio,
which is what the log quotes. And once as ``pead.m``'s ``fprintf`` formats it,
against the string the script's own comment lines print, which is the pin
``docs/design.md``'s ``### What an experiment pins`` asks for. The book's two
figures are pinned at the book's precision beside them.

``TestTheHelperMovesADigit`` holds the one thing a port is most likely to get
wrong. The first edition's ``smartstd`` carries the same MATLAB name, and with
it the arithmetic return prints as 0.0668 rather than 0.0667.

Exploratory. Reproducing Chan's figures spends the 2011 and 2012 sample on a
rule he chose. It first ran here on 2026-10-03.
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from chan import matlab_helpers, pead
from chan.matlab_helpers import smart_moving_std, smartstd_first_edition
from chan.pead import (
    BOOK_APR_PERCENT,
    BOOK_LEVERAGE,
    BOOK_LEVERED_PERCENT,
    BOOK_SHARPE,
    DENOMINATOR,
    ENTRY,
    FLAG_FILE,
    LOOKBACK,
    PRICE_FILE,
    SCRIPT_APR,
    SCRIPT_ARITHMETIC,
    SCRIPT_MAX_DD,
    SCRIPT_MAX_DDD,
    SCRIPT_SHARPE,
    TRADING_DAYS,
    Drift,
    close_to_open,
    daily_returns,
    drift_positions,
    main,
    read_sources,
    refuse_scale_breaks,
    run,
)
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "inputdataohlcdaily_stocks_20120424/ Open and Close against earnannfile/ Flag, "
    "cut to the flag file's 330 days, 90-day lookback, entry at 0.5 moving std, "
    "each day's return over 30"
)

# --- the committed files -------------------------------------------------------


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def drift(sources) -> Drift:
    _, _, opens, closes, flags = sources
    return pead.pead(opens, closes, flags)


@pytest.fixture(scope="module")
def first_edition(sources) -> Drift:
    """The same run with the first edition's ``smartstd`` in both places it is called."""
    _, _, opens, closes, flags = sources
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(matlab_helpers, "smartstd_book_two", smartstd_first_edition)
        patch.setattr(pead, "smartstd_book_two", smartstd_first_edition)
        return pead.pead(opens, closes, flags)


class TestTheSpecification:
    def test_the_rule_is_pead_m(self) -> None:
        assert (LOOKBACK, ENTRY, DENOMINATOR, TRADING_DAYS) == (90, 0.5, 30, 252)

    def test_the_sources_are_chans_two_files(self) -> None:
        assert PRICE_FILE == "inputDataOHLCDaily_stocks_20120424.mat"
        assert FLAG_FILE == "earnannFile.mat"


class TestTheVintages:
    """The members are the two ``LIFTED_SOURCES`` rows, and the window is Chan's."""

    def test_the_members_are_the_pinned_sources(self, sources) -> None:
        prices, announcements, opens, closes, flags = sources
        for members, source, frames in (
            (prices, PRICE_FILE, (opens, closes)),
            (announcements, FLAG_FILE, (flags,)),
        ):
            vendor, basis, saved, folder, count = LIFTED_SOURCES[source]
            assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {
                (vendor, basis, saved)
            }
            assert {m.path.split("/")[0] for m in members} == {folder}
            assert len(members) == count == 497
            assert all(frame.shape[1] == count for frame in frames)

    def test_both_sources_name_the_same_stocks_in_one_order(self, sources) -> None:
        prices, announcements, opens, closes, flags = sources
        assert [m.symbol for m in prices] == [m.symbol for m in announcements]
        assert list(opens.columns) == list(closes.columns) == list(flags.columns)

    def test_the_window_is_the_flag_files_days(self, sources, drift: Drift) -> None:
        """Location 3024's "January 3, 2011, to April 24, 2012", 330 days of 1,500."""
        _, _, opens, _, flags = sources
        assert len(opens) == 1500
        assert drift.days.equals(flags.index)
        assert len(drift.days) == 330
        assert str(drift.days[0].date()) == "2011-01-03"
        assert str(drift.days[-1].date()) == "2012-04-24"

    def test_the_first_days_gap_is_nan_because_the_cut_comes_first(self, sources) -> None:
        """Taking the gap before the cut would give 2011-01-03 a gap from 2010-12-31."""
        _, _, opens, closes, flags = sources
        days = flags.index
        gaps = close_to_open(opens.loc[days].to_numpy(), closes.loc[days].to_numpy())
        assert np.isnan(gaps[0]).all()
        assert np.isfinite(close_to_open(opens.to_numpy(), closes.to_numpy())[1250]).sum() > 400


class TestTheFigures:
    """Each of ``pead.m``'s five figures beside what the script and the book print."""

    def test_the_arithmetic_annual_return_is_the_books_apr(self, drift: Drift) -> None:
        """``252 · mean``. ``pead.m`` prints 0.0667 and the book says 6.7 percent."""
        assert drift.arithmetic_annual == pytest.approx(0.066743, abs=5e-7), SPEC
        assert f"{drift.arithmetic_annual:7.4f}".strip() == SCRIPT_ARITHMETIC == "0.0667", SPEC
        assert round(100 * drift.arithmetic_annual, 1) == BOOK_APR_PERCENT == 6.7, SPEC

    def test_the_sharpe_ratio(self, drift: Drift) -> None:
        """``√252 · mean / smartstd``. ``pead.m`` prints 1.49 and the book 1.5."""
        assert drift.sharpe == pytest.approx(1.4909, abs=5e-5), SPEC
        assert f"{drift.sharpe:4.2f}" == SCRIPT_SHARPE == "1.49", SPEC
        assert round(drift.sharpe, 1) == BOOK_SHARPE == 1.5, SPEC

    def test_levered_four_times_it_is_close_to_27_percent(self, drift: Drift) -> None:
        """Location 3024: levered "at least four times", "close to 27 percent"."""
        assert drift.levered == pytest.approx(0.266970, abs=5e-7), SPEC
        assert BOOK_LEVERAGE == 4, SPEC
        assert round(100 * drift.levered) == BOOK_LEVERED_PERCENT == 27, SPEC

    def test_the_compounded_apr(self, drift: Drift) -> None:
        """``prod(1 + ret)^(252/330) − 1``. ``pead.m`` prints 0.0680 and the book nothing."""
        assert drift.compounded_apr == pytest.approx(0.067952, abs=5e-7), SPEC
        assert f"{drift.compounded_apr:10.4f}".strip() == SCRIPT_APR == "0.0680", SPEC

    def test_the_books_apr_is_not_the_compounded_one(self, drift: Drift) -> None:
        """The compounded figure is 6.8 percent at the book's precision, so a pin
        setting 6.7 against it would match the wrong number."""
        assert round(100 * drift.compounded_apr, 1) == 6.8 != BOOK_APR_PERCENT, SPEC

    def test_the_maximum_drawdown_and_its_duration(self, drift: Drift) -> None:
        """``calculateMaxDD`` on the compounded cumulative return. ``pead.m`` prints
        −0.026052 over 109 days, and the book neither."""
        assert drift.max_drawdown == pytest.approx(-0.026052, abs=5e-7), SPEC
        assert f"{drift.max_drawdown:f}" == SCRIPT_MAX_DD == "-0.026052", SPEC
        assert drift.max_drawdown_days == SCRIPT_MAX_DDD == 109, SPEC

    def test_the_busiest_day_holds_chans_denominator(self, drift: Drift) -> None:
        """Location 3024: "there is a maximum of 30 positions in one day"."""
        assert drift.most_held == DENOMINATOR == 30, SPEC
        assert drift.trades == 1072, SPEC

    def test_no_stock_trades_before_its_window_fills(self, drift: Drift) -> None:
        """The first 89 rows have no spread, so they hold no position and earn 0."""
        assert not drift.positions[: LOOKBACK - 1].any(), SPEC
        assert (drift.daily[: LOOKBACK - 1] == 0).all(), SPEC
        assert np.isfinite(drift.daily).all(), SPEC


class TestTheHelperMovesADigit:
    """The first edition's ``smartstd`` in place of book two's, everything else kept."""

    def test_the_first_editions_helper_misses_chans_printed_digit(
        self, drift: Drift, first_edition: Drift
    ) -> None:
        """0.066833 prints as 0.0668, one unit off what ``pead.m`` prints."""
        assert first_edition.arithmetic_annual == pytest.approx(0.066833, abs=5e-7), SPEC
        printed = f"{first_edition.arithmetic_annual:7.4f}".strip()
        assert printed == "0.0668" != SCRIPT_ARITHMETIC, SPEC
        assert first_edition.trades == drift.trades - 1 == 1071, SPEC

    def test_the_other_printed_figures_survive_the_swap(self, first_edition: Drift) -> None:
        """Only the arithmetic return moves at the precision ``pead.m`` prints."""
        assert f"{first_edition.sharpe:4.2f}" == SCRIPT_SHARPE, SPEC
        assert f"{first_edition.compounded_apr:10.4f}".strip() == SCRIPT_APR, SPEC
        assert f"{first_edition.max_drawdown:f}" == SCRIPT_MAX_DD, SPEC
        assert first_edition.max_drawdown_days == SCRIPT_MAX_DDD, SPEC


class TestTheRun:
    @pytest.fixture()
    def guarded(self, sources, monkeypatch) -> list:
        """The committed sources, read once, and every window the guard is asked about."""
        asked = []
        monkeypatch.setattr(pead, "read_sources", lambda data_dir=None: sources)
        monkeypatch.setattr(pead, "refuse_scale_breaks", lambda *args: asked.append(args[3]))
        return asked

    def test_it_runs_the_scale_break_guard_over_the_flag_files_days(
        self, guarded: list, sources
    ) -> None:
        run()
        (days,) = guarded
        assert days.equals(sources[4].index)

    def test_it_prints_each_figure_beside_chans(self, guarded: list, capsys) -> None:
        drift = run()
        out = capsys.readouterr().out
        assert "2011-01-03 to 2012-04-24, 330 trading days, 497 stocks" in out
        assert f"held {drift.most_held} positions, and {drift.trades} were taken" in out
        for line, figures in (
            ("Arithmetic annual return", ["0.066743", "0.0667", "6.7", "percent"]),
            ("Sharpe ratio", ["1.4909", "1.49", "1.5"]),
            ("Compounded APR", ["0.067952", "0.0680"]),
            ("Levered 4 times", ["0.266970", "27", "percent"]),
            ("Maximum drawdown  ", ["-0.026052"]),
            ("Maximum drawdown duration", ["109"]),
        ):
            (row,) = [each for each in out.splitlines() if line in each]
            assert all(figure in row.split() for figure in figures), row
        assert "about survivors" in out
        assert "Exploratory." in out


# --- the rule, on frames small enough to read ----------------------------------


def _frames(
    rows: int, gap: float, flag_day: int, spikes: dict[int, float] | None = None
) -> tuple[pd.DataFrame, ...]:
    """Two stocks whose close-to-open gap alternates ±1 percent, then one day of ``gap``.

    The alternating gaps give a moving spread of exactly 0.01, so the threshold
    on ``flag_day`` sits at 0.005. Each day closes 2 percent above its open.
    ``spikes`` sets the gap on other days.
    """
    days = pd.bdate_range("2011-01-03", periods=rows)
    gaps = np.where(np.arange(rows) % 2 == 0, 0.01, -0.01)
    gaps[flag_day] = gap
    for day, spike in (spikes or {}).items():
        gaps[day] = spike
    opens, closes = np.empty(rows), np.empty(rows)
    previous = 100.0
    for t in range(rows):
        opens[t] = previous * (1 + gaps[t])
        closes[t] = previous = opens[t] * 1.02
    columns = ["AAA", "BBB"]
    flags = np.zeros((rows, 2))
    flags[flag_day, 0] = 1.0
    as_frame = lambda values: pd.DataFrame(  # noqa: E731
        np.column_stack([values, values]), index=days, columns=columns
    )
    return as_frame(opens), as_frame(closes), pd.DataFrame(flags, index=days, columns=columns)


class TestTheRule:
    def test_a_gap_up_on_an_announcement_goes_long_and_earns_the_day(self) -> None:
        opens, closes, flags = _frames(LOOKBACK + 5, 0.03, LOOKBACK + 2)
        result = pead.pead(opens, closes, flags)
        assert result.positions[LOOKBACK + 2].tolist() == [1.0, 0.0]
        assert result.trades == 1
        assert result.daily[LOOKBACK + 2] == pytest.approx(0.02 / DENOMINATOR, abs=1e-15)

    def test_a_gap_down_goes_short(self) -> None:
        opens, closes, flags = _frames(LOOKBACK + 5, -0.03, LOOKBACK + 2)
        result = pead.pead(opens, closes, flags)
        assert result.positions[LOOKBACK + 2].tolist() == [-1.0, 0.0]
        assert result.daily[LOOKBACK + 2] == pytest.approx(-0.02 / DENOMINATOR, abs=1e-15)

    def test_the_same_gap_without_an_announcement_is_not_traded(self) -> None:
        """BBB carries the same prices as AAA and no flag."""
        opens, closes, flags = _frames(LOOKBACK + 5, 0.03, LOOKBACK + 2)
        assert pead.pead(opens, closes, flags).positions[:, 1].sum() == 0

    def test_a_gap_below_half_a_spread_is_not_traded(self) -> None:
        opens, closes, flags = _frames(LOOKBACK + 5, 0.004, LOOKBACK + 2)
        assert pead.pead(opens, closes, flags).trades == 0

    def test_a_gap_of_exactly_half_a_spread_is_traded(self) -> None:
        """``>=`` rather than ``>``, on a gap equal to the threshold by construction."""
        gaps = np.array([[0.5]])
        assert drift_positions(gaps, np.array([[1.0]]), np.array([[1.0]])).tolist() == [[1.0]]
        assert drift_positions(-gaps, np.array([[1.0]]), np.array([[1.0]])).tolist() == [[-1.0]]

    def test_a_stock_meeting_both_tests_ends_short(self) -> None:
        """A spread of 0 and a gap of 0 clear both, and ``pead.m`` sets shorts last."""
        assert drift_positions(np.zeros((1, 1)), np.zeros((1, 1)), np.ones((1, 1))) == -1.0

    def test_a_nan_spread_clears_nothing(self) -> None:
        nan = np.array([[np.nan]])
        assert drift_positions(np.array([[0.5]]), nan, np.array([[1.0]])) == 0.0
        assert drift_positions(nan, np.array([[1.0]]), np.array([[1.0]])) == 0.0

    def test_a_nan_flag_is_refused(self) -> None:
        with pytest.raises(ValueError, match="hold a NaN"):
            drift_positions(np.zeros((1, 1)), np.ones((1, 1)), np.array([[np.nan]]))

    def test_any_flag_other_than_zero_is_an_announcement(self) -> None:
        """MATLAB's ``&`` reads every number but 0 as true, infinity included."""
        flags = np.array([[2.0, -1.0, np.inf, 0.0]])
        positions = drift_positions(np.ones((1, 4)), np.ones((1, 4)), flags)
        assert positions.tolist() == [[1.0, 1.0, 1.0, 0.0]]

    def test_the_spread_is_book_twos_over_the_lookback(self) -> None:
        opens, closes, _ = _frames(LOOKBACK + 5, 0.03, LOOKBACK + 2)
        gaps = close_to_open(opens.to_numpy(), closes.to_numpy())
        spread = smart_moving_std(gaps, LOOKBACK)
        assert np.isnan(spread[: LOOKBACK - 1]).all()
        assert spread[LOOKBACK + 1, 0] == pytest.approx(0.01, abs=1e-12)

    def test_the_prices_are_cut_to_the_days_every_frame_shares(self) -> None:
        opens, closes, flags = _frames(LOOKBACK + 5, 0.03, LOOKBACK + 2)
        result = pead.pead(opens, closes, flags.iloc[3:])
        assert result.days.equals(flags.index[3:])
        assert result.positions.shape == (LOOKBACK + 2, 2)

    def test_the_first_kept_day_has_no_gap_because_the_cut_comes_first(self) -> None:
        """Row 1 gaps 100 percent from row 0's close, and the flags start on row 1.

        The flagged day is the 90th kept row, so its window starts on row 1.
        Cut first, as ``pead.m`` does, and row 1's gap is NaN, the spread on the
        flagged day stays near 0.01, and its 3 percent gap trades. Take the gap
        before the cut and the spike enters the window, the spread grows past
        0.1, and the same day does not trade.
        """
        opens, closes, flags = _frames(LOOKBACK + 5, 0.03, LOOKBACK, spikes={1: 1.0})
        result = pead.pead(opens, closes, flags.iloc[1:])
        assert result.positions[LOOKBACK - 1].tolist() == [1.0, 0.0]

    def test_a_day_with_nothing_finite_to_sum_is_nan_rather_than_zero(self) -> None:
        """``smartsum`` of a row with no finite product is NaN, where ``nansum`` gives 0."""
        positions = np.array([[1.0, 0.0], [1.0, 0.0]])
        opens = np.array([[10.0, 10.0], [np.nan, np.nan]])
        closes = np.array([[11.0, 10.0], [11.0, 10.0]])
        daily = daily_returns(positions, opens, closes)
        assert daily[0] == pytest.approx(0.1 / DENOMINATOR, abs=1e-15)
        assert np.isnan(daily[1])

    def test_frames_holding_different_stocks_are_refused(self) -> None:
        opens, closes, flags = _frames(LOOKBACK + 5, 0.03, LOOKBACK + 2)
        with pytest.raises(ValueError, match="same stocks in one order"):
            pead.pead(opens, closes, flags[["BBB", "AAA"]])


class TestTheRefusals:
    def test_a_stock_one_source_lacks_is_refused_by_symbol(self, monkeypatch) -> None:
        def fake(source, *, field, data_dir=None):
            symbols = ["AAA", "BBB"] if source == PRICE_FILE else ["AAA", "CCC"]
            return [SimpleNamespace(symbol=s) for s in symbols], pd.DataFrame()

        monkeypatch.setattr(pead, "load_panel", fake)
        with pytest.raises(VintageUnavailable, match="BBB priced and not flagged, CCC flagged"):
            read_sources()

    def test_a_scale_break_on_a_stocks_own_rows_is_refused(self) -> None:
        days = pd.bdate_range("2011-01-03", periods=4)
        member = SimpleNamespace(symbol="AAA", path="x/aaa.csv")
        steady = pd.DataFrame({"AAA": [10.0, 10.1, 10.2, 10.3]}, index=days)
        halved = pd.DataFrame({"AAA": [10.0, 10.1, 5.05, 5.1]}, index=days)
        refuse_scale_breaks([member], steady, steady, days)
        with pytest.raises(WindowCrossesScaleBreak, match="x/aaa.csv changes scale on 2011-01-05"):
            refuse_scale_breaks([member], steady, halved, days)

    def test_the_guard_passes_chans_files_over_the_window(self, sources, drift) -> None:
        """The real guard on all 497 stocks, so a refusal would fail here first."""
        prices, _, opens, closes, _ = sources
        refuse_scale_breaks(prices, opens, closes, drift.days)

    def test_a_price_missing_after_the_first_is_still_refused(self) -> None:
        """Reading from the first price is not dropping every NaN."""
        days = pd.bdate_range("2011-01-03", periods=4)
        member = SimpleNamespace(symbol="AAA", path="x/aaa.csv")
        holed = pd.DataFrame({"AAA": [10.0, np.nan, 10.2, 10.3]}, index=days)
        with pytest.raises(WindowCrossesScaleBreak, match="no readable day-over-day move"):
            refuse_scale_breaks([member], holed, holed, days)

    def test_a_stock_listed_inside_the_window_passes_on_its_own_rows(self) -> None:
        """MPC and XYL have no price before their spin-offs, which the panel's columns
        would read as an unreadable day."""
        days = pd.bdate_range("2011-01-03", periods=4)
        member = SimpleNamespace(symbol="AAA", path="x/aaa.csv")
        late = pd.DataFrame({"AAA": [np.nan, np.nan, 10.0, 10.1]}, index=days)
        refuse_scale_breaks([member], late, late, days)

    def test_main_prints_a_refusal_as_one_line(self, monkeypatch) -> None:
        def refuse(data_dir=None):
            raise VintageUnavailable("no committed vintage is lifted from earnannFile.mat")

        monkeypatch.setattr(pead, "run", refuse)
        monkeypatch.setattr("sys.argv", ["pead"])
        with pytest.raises(SystemExit, match="no committed vintage is lifted from earnannFile"):
            main()
