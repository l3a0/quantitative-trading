"""The pins for the Khandani-Lo reversal on the 2012 panel, *Algorithmic Trading*'s 4.3 and 4.4.

This file is the single authority for every number a prose surface quotes
about these two examples and about the two bridge rows that set them beside
the first book's Examples 3.7 and 3.8. ``docs/replication-log.md`` Entry 19
carries the verdicts and points here row by row, and
``blog/khandani-lo-reversal-lessons.md`` quotes the same figures and the
yearly APRs, the annual mean and deviation, the bridge differences and the
average day that this file pins for it.

Every pin on the committed panel reads one vintage and one specification, so
both are stated once here.

- **Vintage.** ``inputdataohlcdaily_stocks_20120424/``, the 497 stocks lifted
  from Chan's ``inputDataOHLCDaily_stocks_20120424.mat``, saved 2012-04-25,
  read for the close and the open through ``chan.series.load_panel``. Its
  identity is that file's row of ``LIFTED_SOURCES`` in
  ``tests/support/committed_vintages.py``. The stocks are the index as Chan
  held it on 2012-04-24, so every figure is a figure about survivors.
- **Specification.** *Algorithmic Trading*'s ``andrewlo_2007_2012.m`` at the
  mirror commits the module names. Both price frames are cut to 2007-01-03
  through 2011-12-30, 1,260 trading days, before any return is taken. Each
  day's weights are minus the signal against the equal-weighted market, scaled
  to a gross of 1. Example 4.3's signal is the close-to-close return and its
  weights are held to the next close. Example 4.4's signal is the gap from
  yesterday's close to today's open and its weights are held from the open to
  the same day's close. No cost is charged. The APR is
  ``prod(1 + r)^(252 / n) − 1`` and the Sharpe ratio is ``√252 · mean / std``
  over all 1,260 days, with no risk-free rate and the deviation over n − 1.

Each of the eight published figures is held twice: at six decimals of the
computed value, which is what lets the log quote it, and at the precision Chan
printed, through ``matches``. The two yearly APRs apply the script's APR line
to one calendar year of the full run's series, because the script prints no
yearly figure.

Exploratory. Reproducing Chan's figures spends the 2007 to 2011 sample on a
rule somebody else chose. Both examples first ran on 2026-10-04.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
import pytest

from chan import khandani_lo, paths
from chan.khandani_lo import daily_book, notebook_reversal, reversal
from chan.khandani_lo_book_two import (
    BOOK_43_APR_PERCENT,
    BOOK_43_SHARPE,
    BOOK_44_APR_PERCENT,
    BOOK_44_SHARPE,
    BOOK_YEAR_APR_PERCENT,
    SCRIPT_44_APR,
    SCRIPT_44_SHARPE,
    SOURCE_FILE,
    WINDOW_END,
    WINDOW_START,
    BookTwo,
    _verdict,
    book_two,
    close_to_close,
    compounded_apr,
    gap,
    gross_weights,
    held_intraday,
    held_overnight,
    main,
    matches,
    open_to_close,
    run,
    window,
)
from chan.series import (
    WindowCrossesScaleBreak,
    load_panel,
    refuse_window_crossing_a_break,
    scale_breaks,
)
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES
from tests.test_scale_breaks import FLAGGED_IN_CHANS_MAT_FILES

#: Each calendar year's APR in percent, at six decimals, for both examples.
YEARLY_APR_PERCENT = {
    "4.3": {
        2007: -3.046588,
        2008: 30.164676,
        2009: 33.449527,
        2010: 1.818140,
        2011: 10.577823,
    },
    "4.4": {
        2007: 97.169153,
        2008: 161.091599,
        2009: 91.868495,
        2010: 36.844862,
        2011: 15.035091,
    },
}


# --- the committed files -------------------------------------------------------


@pytest.fixture(scope="module")
def closes_panel():
    return load_panel(SOURCE_FILE)


@pytest.fixture(scope="module")
def opens_panel():
    return load_panel(SOURCE_FILE, field="Open")


@pytest.fixture(scope="module")
def first_file():
    _, frame = load_panel(khandani_lo.SOURCE_FILE)
    return frame


@pytest.fixture(scope="module")
def result(closes_panel, opens_panel, first_file) -> BookTwo:
    return book_two(opens_panel[1], closes_panel[1], first_file)


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.khandani_lo_book_two"])


class TestTheVintage:
    """The members are the ``LIFTED_SOURCES`` row, and the window is the script's."""

    def test_the_members_are_the_pinned_source(self, closes_panel, opens_panel) -> None:
        members, closes = closes_panel
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert {m.path.split("/")[0] for m in members} == {folder}
        assert len(members) == count == 497 == closes.shape[1] == opens_panel[1].shape[1]

    def test_the_window_is_1260_days_from_2007_01_03(self, result: BookTwo) -> None:
        """The book's "January 2, 2007" was a market holiday, so no row carries it."""
        for each in (result.close_to_close, result.open_to_close):
            assert len(each.days) == len(each.daily) == 1260
            assert str(each.days[0].date()) == WINDOW_START == "2007-01-03"
            assert str(each.days[-1].date()) == WINDOW_END == "2011-12-30"
        assert pd.Timestamp("2007-01-02") not in result.close_to_close.days

    def test_the_two_years_the_book_names_hold_253_and_252_days(self, result: BookTwo) -> None:
        days = result.close_to_close.days
        assert (days.year == 2008).sum() == 253
        assert (days.year == 2011).sum() == 252

    def test_opens_and_closes_are_missing_on_the_same_cells(
        self, closes_panel, opens_panel
    ) -> None:
        """So no stock in Example 4.4 holds a weight without a same-day return."""
        closes = window(closes_panel[1], WINDOW_START, WINDOW_END).to_numpy()
        opens = window(opens_panel[1], WINDOW_START, WINDOW_END).to_numpy()
        assert (np.isfinite(closes) == np.isfinite(opens)).all()
        assert np.isfinite(closes).sum() == 618_554
        assert (closes[np.isfinite(closes)] > 0).all()
        assert (opens[np.isfinite(opens)] > 0).all()


class TestTheFigures:
    """Each published figure at six decimals, then at the precision Chan printed."""

    @pytest.mark.parametrize(
        ("figure", "computed", "printed"),
        [
            ("4.3 APR percent", 13.677582, BOOK_43_APR_PERCENT),
            ("4.3 Sharpe", 1.259478, BOOK_43_SHARPE),
            ("4.3 APR percent in 2008", 30.164676, BOOK_YEAR_APR_PERCENT[2008]),
            ("4.3 APR percent in 2011", 10.577823, BOOK_YEAR_APR_PERCENT[2011]),
            ("4.4 APR percent", 73.155250, BOOK_44_APR_PERCENT),
            ("4.4 Sharpe", 4.713284, BOOK_44_SHARPE),
            ("4.4 APR", 0.731553, SCRIPT_44_APR),
            ("4.4 Sharpe as printed", 4.713284, SCRIPT_44_SHARPE),
        ],
    )
    def test_each_figure_reproduces(self, result: BookTwo, figure, computed, printed) -> None:
        a, b = result.close_to_close, result.open_to_close
        value = {
            "4.3 APR percent": 100 * a.apr,
            "4.3 Sharpe": a.sharpe,
            "4.3 APR percent in 2008": 100 * a.year_apr(2008),
            "4.3 APR percent in 2011": 100 * a.year_apr(2011),
            "4.4 APR percent": 100 * b.apr,
            "4.4 Sharpe": b.sharpe,
            "4.4 APR": b.apr,
            "4.4 Sharpe as printed": b.sharpe,
        }[figure]
        assert value == pytest.approx(computed, abs=5e-7)
        assert matches(value, printed)

    def test_two_book_figures_sit_close_to_their_rounding_points(self, result: BookTwo) -> None:
        """Row 2's 1.2595 is 0.0095 above 1.25, and row 4's 10.58 is 0.08 above 10.5."""
        a = result.close_to_close
        assert a.sharpe - 1.25 == pytest.approx(0.0095, abs=5e-5)
        assert 100 * a.year_apr(2011) - 10.5 == pytest.approx(0.08, abs=5e-3)

    def test_the_printed_apr_sits_just_above_its_rounding_point(self, result: BookTwo) -> None:
        """0.7315525 would round the sixth decimal either way, and the run is 1.6e-9 above it."""
        assert result.open_to_close.apr - 0.7315525 == pytest.approx(1.6e-9, abs=5e-11)

    def test_the_published_figures_are_the_books_and_the_scripts(self) -> None:
        """Locations 2110 and 2135, and the script's printed comment for Example 4.4."""
        assert (BOOK_43_APR_PERCENT, BOOK_43_SHARPE) == ("13.7", "1.3")
        assert BOOK_YEAR_APR_PERCENT == {2008: "30", 2011: "11"}
        assert (BOOK_44_APR_PERCENT, BOOK_44_SHARPE) == ("73", "4.7")
        assert (SCRIPT_44_APR, SCRIPT_44_SHARPE) == ("0.731553", "4.713284")

    def test_a_year_rerun_on_its_own_would_be_a_different_figure(
        self, closes_panel, result: BookTwo
    ) -> None:
        """Rerunning 2008 alone zeroes its first two days, so it is not the series sliced."""
        alone = close_to_close(closes_panel[1], start="2008-01-01", end="2008-12-31")
        assert alone.daily[:2].tolist() == [0.0, 0.0]
        assert alone.apr != pytest.approx(result.close_to_close.year_apr(2008), abs=1e-6)


class TestEachYear:
    """Each calendar year's APR for both examples, the labels the figure draws.

    Location 2110 names 2008 and 2011 for Example 4.3, and ``TestTheFigures``
    holds those two against the book. The post quotes the other three years
    and every year of Example 4.4, which the book does not print, so they are
    pinned here, in ``YEARLY_APR_PERCENT``, at six decimals of a percent.
    """

    @pytest.mark.parametrize("example", ["4.3", "4.4"])
    def test_each_years_apr(self, result: BookTwo, example) -> None:
        run = result.close_to_close if example == "4.3" else result.open_to_close
        assert sorted(set(run.days.year)) == sorted(YEARLY_APR_PERCENT[example])
        for year, percent in YEARLY_APR_PERCENT[example].items():
            assert 100 * run.year_apr(year) == pytest.approx(percent, abs=5e-7), (example, year)

    def test_example_4_4_earns_less_every_year_after_2008(self, result: BookTwo) -> None:
        run = result.open_to_close
        later = [run.year_apr(year) for year in range(2008, 2012)]
        assert all(a > b for a, b in zip(later, later[1:], strict=False))


class TestTheMeanAndTheDeviation:
    """Why 4.7 is so far above 1.3: the deviations are close and the means are not.

    The annual mean is ``252 · mean`` and the annual deviation ``√252 · std``
    with n − 1, so their ratio is each example's pinned Sharpe ratio.
    """

    @pytest.mark.parametrize(
        ("example", "mean", "deviation"),
        [("4.3", 0.1338, 0.1063), ("4.4", 0.5565, 0.1181)],
    )
    def test_each_examples_annual_mean_and_deviation(
        self, result: BookTwo, example, mean, deviation
    ) -> None:
        run = result.close_to_close if example == "4.3" else result.open_to_close
        annual_mean = 252 * run.daily.mean()
        annual_deviation = np.sqrt(252) * run.daily.std(ddof=1)
        assert annual_mean == pytest.approx(mean, abs=5e-5)
        assert annual_deviation == pytest.approx(deviation, abs=5e-5)
        assert annual_mean / annual_deviation == pytest.approx(run.sharpe, abs=1e-12)


class TestTheFirstDays:
    """The cut comes before the returns, so the first days earn nothing."""

    def test_close_to_close_earns_nothing_on_its_first_two_days(self, result: BookTwo) -> None:
        daily = result.close_to_close.daily
        assert np.flatnonzero(daily == 0).tolist() == [0, 1]
        assert np.isnan(result.close_to_close.weights[0]).all()

    def test_open_to_close_earns_nothing_on_its_first_day(self, result: BookTwo) -> None:
        daily = result.open_to_close.daily
        assert np.flatnonzero(daily == 0).tolist() == [0]
        assert np.isnan(result.open_to_close.weights[0]).all()

    def test_a_lag_padded_with_zeros_gives_the_same_series(
        self, closes_panel, result: BookTwo
    ) -> None:
        """Neither mirror holds ``lag.m``. LeSage's pads with 0, so row 0 is a price over 0."""
        prices = window(closes_panel[1], WINDOW_START, WINDOW_END).to_numpy(dtype=float)
        padded = np.vstack([np.zeros((1, prices.shape[1])), prices[:-1]])
        with np.errstate(divide="ignore", invalid="ignore"):
            returns = (prices - padded) / padded
        assert np.isinf(returns[0]).sum() == 480
        assert np.isnan(returns[0]).sum() == 17
        assert np.array_equal(
            held_overnight(gross_weights(returns), returns), result.close_to_close.daily
        )


class TestTheWeights:
    def test_every_day_with_a_return_holds_a_gross_of_one(self, result: BookTwo) -> None:
        for each in (result.close_to_close, result.open_to_close):
            gross = np.nansum(np.abs(each.weights), axis=1)
            assert gross[0] == 0.0
            assert gross[1:] == pytest.approx(1.0, abs=1e-12)

    def test_the_weights_sum_to_zero_every_day(self, result: BookTwo) -> None:
        """Location 2110's "almost perfectly dollar neutral" holds exactly, up to rounding."""
        for each in (result.close_to_close, result.open_to_close):
            assert np.nansum(each.weights, axis=1) == pytest.approx(0.0, abs=1e-12)

    def test_the_notebook_without_its_fill_computes_the_same_profit(
        self, closes_panel, result: BookTwo
    ) -> None:
        """Rule A of Example 3.8 scales to a gross of 1 and skips a NaN the same way.

        Its window has to be passed, because it defaults to the first book's 2006.
        """
        cut = window(closes_panel[1], WINDOW_START, WINDOW_END)
        notebook = notebook_reversal(cut, start=WINDOW_START, end=WINDOW_END, fill=False)
        assert notebook.pnl == pytest.approx(result.close_to_close.daily, abs=1e-12)


class TestBesideTheFirstBook:
    """The two bridge rows. No book prints either, so neither carries a verdict."""

    def test_book_twos_rule_on_the_first_books_file_and_year(self, result: BookTwo) -> None:
        """Against Example 3.7's 0.2510 on the same file and the same 251 days."""
        bridge = result.rule_on_first_file
        assert len(bridge.days) == 251
        assert str(bridge.days[0].date()) == "2006-01-03"
        assert bridge.sharpe == pytest.approx(0.5484, abs=5e-5)

    def test_on_one_year_the_two_days_the_cut_zeroes_move_the_figure_by_a_third(
        self, first_file, result: BookTwo
    ) -> None:
        """Entry 10's row 12 is the same rule taking returns before the cut.

        Rule A without its fill weights the same way and skips a NaN the same
        way, so the two series part only on 2006-01-03 and 2006-01-04, which
        lose 0.48 and 0.14 percent there and earn 0 here. Over 251 days that
        is 0.4170 against 0.5484, with the deviation over n − 1 in both.
        """
        bridge = result.rule_on_first_file
        notebook = notebook_reversal(first_file, fill=False)
        parts = np.flatnonzero(np.abs(notebook.pnl - bridge.daily) > 1e-12)
        assert parts.tolist() == [0, 1]
        assert notebook.pnl[:2] == pytest.approx([-0.0048, -0.0014], abs=5e-5)
        assert khandani_lo.plain_sharpe(notebook.pnl) == pytest.approx(0.4170, abs=5e-5)

    def test_the_differences_the_post_quotes_round_from_the_unrounded_figures(
        self, first_file, result: BookTwo
    ) -> None:
        """0.2974 for the rule, 0.1313 of it for the two days, and 0.7111 still to go.

        Entry 19 once printed the second as 0.1314, which is 0.5484 − 0.4170 on
        the rounded figures. The unrounded difference is 0.131331.
        """
        first_book = reversal(first_file).before_costs
        rule = result.rule_on_first_file.sharpe
        returns_first = khandani_lo.plain_sharpe(notebook_reversal(first_file, fill=False).pnl)
        assert round(rule - first_book, 4) == 0.2974
        assert round(rule - returns_first, 4) == 0.1313
        assert round((rule - returns_first) / (rule - first_book), 2) == 0.44
        assert round(result.close_to_close.sharpe - rule, 4) == 0.7111

    def test_the_first_books_rule_on_this_panel_and_window(self, result: BookTwo) -> None:
        bridge = result.first_rule_on_panel
        assert len(bridge.days) == 1260
        assert str(bridge.days[0].date()) == WINDOW_START
        assert bridge.before_costs == pytest.approx(1.2219, abs=5e-5)
        assert bridge.after_costs_charged == pytest.approx(0.3797, abs=5e-5)

    def test_left_to_its_default_the_first_books_rule_stops_on_the_wrong_months(
        self, closes_panel
    ) -> None:
        """Why every call passes the window: the panel starts inside the first book's 2006.

        The default window opens on the panel's first day, 2006-05-11, which has
        no earlier weights to charge a cost against, so the charged figure is
        NaN there and ``plain_sharpe`` refuses it. The refusal names the NaN
        rather than the window, which is why the call passes the window rather
        than relying on the refusal.
        """
        with pytest.raises(ValueError, match="every day finite"):
            reversal(closes_panel[1])


class TestWhatAnAverageDayCostsOnThePanel:
    """The first book's rule on this panel, as ``TestWhatAnAverageDayCosts`` reads 2006.

    That class, in ``tests/test_khandani_lo.py``, pins 2006's average day: a
    profit of 0.5276 basis points of the rule's average gross position, a
    cost of 7.2525, 13.7453 times
    the profit, and a turnover of 1.4505. On the panel the turnover and the
    cost barely move and the profit is about twenty times larger.
    """

    def test_the_day_earns_ten_basis_points_and_pays_seven(self, result: BookTwo) -> None:
        day = daily_book(result.first_rule_on_panel)
        assert day.profit * 1e4 == pytest.approx(10.5234, abs=5e-5)
        assert day.cost * 1e4 == pytest.approx(7.2868, abs=5e-5)
        assert day.cost_per_profit == pytest.approx(0.6924, abs=5e-5)
        assert day.turnover == pytest.approx(1.4574, abs=5e-5)

    def test_the_profit_is_about_twenty_times_2006s(self, first_file, result: BookTwo) -> None:
        panel = daily_book(result.first_rule_on_panel)
        year = daily_book(reversal(first_file))
        assert panel.profit / year.profit == pytest.approx(19.94, abs=5e-3)


class TestTheScaleBreakDecision:
    """Why the module does not call the guard, run rather than asserted.

    The guard refuses this window on both fields, each stock read from its own
    rows. On the close it names the 17 stocks ``tests/test_scale_breaks.py``
    pins. Chan's script computes across them and his figures need them, which
    CAH shows, so the module computes across them too, as its docstring says.
    """

    START, END = pd.Timestamp(WINDOW_START), pd.Timestamp(WINDOW_END)

    @pytest.mark.parametrize(("field", "stocks"), [("Close", 17), ("Open", 14)])
    def test_handed_each_members_own_rows_it_refuses(
        self, closes_panel, opens_panel, field, stocks
    ) -> None:
        members, frame = closes_panel if field == "Close" else opens_panel
        legs = [(m, frame[m.symbol].dropna()) for m in members]
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(legs, start=self.START, end=self.END)
        said = str(refused.value)
        assert said.count("changes scale") == stocks
        assert "has no readable" not in said

    def test_on_the_close_it_names_the_stocks_the_scale_break_pins_hold(self, closes_panel) -> None:
        members, frame = closes_panel
        legs = [(m, frame[m.symbol].dropna()) for m in members]
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(legs, start=self.START, end=self.END)
        named = set(
            re.findall(r"inputdataohlcdaily_stocks_20120424/[a-z]+\.csv", str(refused.value))
        )
        pinned = {k for k in FLAGGED_IN_CHANS_MAT_FILES if k.startswith("inputdataohlcdaily")}
        assert named == pinned

    def test_three_stocks_are_flagged_on_the_open_only(self, closes_panel, opens_panel) -> None:
        def flagged(frame):
            cut = window(frame, WINDOW_START, WINDOW_END)
            return {s for s in cut.columns if scale_breaks(cut[s].dropna())}

        assert flagged(opens_panel[1]) - flagged(closes_panel[1]) == {"HBAN", "SLM", "ZION"}

    def test_cahs_flag_is_not_a_crash_and_the_figures_need_it(self, closes_panel) -> None:
        """19.96, 14.50, 23.57 on three days, and without CAH neither of 4.3's figures lands."""
        _, frame = closes_panel
        closes = frame["CAH"].loc["2009-08-31":"2009-09-02"].tolist()
        assert closes == [19.96, 14.5, 23.57]
        without = close_to_close(frame.drop(columns=["CAH"]), start=WINDOW_START, end=WINDOW_END)
        assert 100 * without.apr == pytest.approx(13.26, abs=5e-3)
        assert without.sharpe == pytest.approx(1.2267, abs=5e-5)
        assert not matches(100 * without.apr, BOOK_43_APR_PERCENT)
        assert not matches(without.sharpe, BOOK_43_SHARPE)

    def test_aigs_first_flag_is_a_day_the_rule_weights(self, closes_panel, result: BookTwo) -> None:
        """AIG has a finite return on 2008-09-15, so the rule weights the crash."""
        _, frame = closes_panel
        column = frame.columns.get_loc("AIG")
        day = result.close_to_close.days.get_loc(pd.Timestamp("2008-09-15"))
        assert np.isfinite(result.close_to_close.weights[day, column])


class TestTheReport:
    def test_it_prints_each_figure_beside_chans(self, capsys, no_arguments) -> None:
        main()
        out = capsys.readouterr().out
        assert "497 members lifted from inputDataOHLCDaily_stocks_20120424.mat" in out
        assert "2007-01-03 to 2011-12-30, 1260 trading days" in out
        for line, figures in (
            ("4.3 close to close, APR percent  ", ["13.677582", "13.7", "reproduced"]),
            ("4.3 close to close, Sharpe", ["1.259478", "1.3", "reproduced"]),
            ("in 2008", ["30.164676", "30", "reproduced"]),
            ("in 2011", ["10.577823", "11", "reproduced"]),
            ("4.4 open to close, APR percent", ["73.155250", "73", "reproduced"]),
            ("4.4 open to close, Sharpe  ", ["4.713284", "4.7", "reproduced"]),
            ("APR as the script prints it", ["0.731553", "reproduced"]),
            ("Sharpe as the script prints it", ["4.713284", "reproduced"]),
        ):
            (row,) = [each for each in out.splitlines() if line in each]
            assert all(figure in row.split() for figure in figures), row
        assert "Sharpe 0.5484, where Example 3.7 printed 0.25" in out
        assert "Sharpe 1.2219 before costs and 0.3797 after 5 bp a side" in out
        assert "about survivors" in out
        assert "Exploratory." in out

    def test_a_missing_vintage_reaches_the_reader_as_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "inputDataOHLCDaily_stocks_20120424.mat cannot be" in str(stopped.value)

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputDataOHLCDaily_stocks_20120424.mat"):
            run(tmp_path)

    def test_run_hands_its_directory_to_every_read(self, monkeypatch, tmp_path) -> None:
        """All three reads, the panel's closes and opens and the first book's closes."""
        asked = []

        def recording(source, *, field="Close", data_dir=None):
            asked.append((source, field, data_dir))
            return [], pd.DataFrame()

        monkeypatch.setattr("chan.khandani_lo_book_two.load_panel", recording)
        monkeypatch.setattr("chan.khandani_lo_book_two.book_two", lambda *_: None)
        monkeypatch.setattr("chan.khandani_lo_book_two.report", lambda *_: None)
        run(tmp_path)
        assert asked == [
            (SOURCE_FILE, "Close", tmp_path),
            (SOURCE_FILE, "Open", tmp_path),
            (khandani_lo.SOURCE_FILE, "Close", tmp_path),
        ]

    def test_any_other_failure_keeps_its_traceback(self, monkeypatch, no_arguments) -> None:
        """Only a refusal is turned into one line. A bug still surfaces as itself."""

        def broken(*_args, **_kwargs):
            raise RuntimeError("a bug, not a refusal")

        monkeypatch.setattr("chan.khandani_lo_book_two.load_panel", broken)
        with pytest.raises(RuntimeError, match="a bug, not a refusal"):
            main()


# --- a panel small enough to work by hand ------------------------------------------
#
# Three stocks over four days. C is first priced on day 1, so it has no return
# that day and keeps a NaN weight.
#
#   day   A      B       C
#   0     10     20      NaN
#   1     11     19      5       returns  +0.10  -0.05  NaN    market +0.025
#   2     11     19.95   5.5     returns   0     +0.05  +0.10  market +0.05
#   3     12.1   19.95   5.5     returns  +0.10   0      0     market +0.0333

HAND = np.array(
    [
        [10.0, 20.0, np.nan],
        [11.0, 19.0, 5.0],
        [11.0, 19.95, 5.5],
        [12.1, 19.95, 5.5],
    ]
)
HAND_DAYS = pd.to_datetime(["2006-12-29", "2007-01-03", "2007-01-04", "2007-01-05"])


def _hand_frame(values: np.ndarray = HAND) -> pd.DataFrame:
    return pd.DataFrame(values, index=HAND_DAYS, columns=["A", "B", "C"])


class TestTheRuleByHand:
    def test_the_weights_scale_to_a_gross_of_one_and_leave_nan_in_place(self) -> None:
        """Day 1: deviations −0.075 and +0.075 over a gross of 0.15."""
        returns = np.array([[np.nan] * 3, [0.10, -0.05, np.nan]])
        weights = gross_weights(returns)
        assert np.isnan(weights[0]).all()
        assert weights[1, :2] == pytest.approx([-0.5, 0.5])
        assert np.isnan(weights[1, 2])

    def test_buy_the_loser_and_short_the_winner(self) -> None:
        weights = gross_weights(np.array([[0.02, -0.02, 0.0]]))
        assert weights[0, 0] < 0 < weights[0, 1]
        assert weights[0, 2] == 0.0

    def test_overnight_profit_uses_yesterdays_weights(self) -> None:
        """Day 2 holds day 1's −0.5 and +0.5 into returns of 0 and +0.05."""
        run = close_to_close(_hand_frame(), start="2006-01-01", end="2007-12-31")
        assert run.daily[:2].tolist() == [0.0, 0.0]
        assert run.daily[2] == pytest.approx(-0.5 * 0.0 + 0.5 * 0.05)

    def test_the_window_is_cut_before_the_returns_and_both_bounds_are_inclusive(self) -> None:
        run = close_to_close(_hand_frame(), start="2007-01-03", end="2007-01-05")
        assert [str(d.date()) for d in run.days] == ["2007-01-03", "2007-01-04", "2007-01-05"]
        # 2006-12-29 is cut first, so 2007-01-03 has no return and 2007-01-04
        # holds its NaN weights. Both earn nothing.
        assert run.daily[:2].tolist() == [0.0, 0.0]

    def test_intraday_profit_uses_todays_weights_over_the_gross(self) -> None:
        weights = np.array([[0.5, -0.5]])
        opens = np.array([[10.0, 20.0]])
        closes = np.array([[11.0, 20.0]])
        assert held_intraday(weights, opens, closes).tolist() == [pytest.approx(0.05)]

    def test_intraday_profit_divides_by_a_gross_that_is_not_one(self) -> None:
        """Weights summing to 2 in absolute value, and to 0.5, both give the day's 0.05."""
        opens, closes = np.array([[10.0, 20.0]]), np.array([[11.0, 20.0]])
        for weights in ([[1.0, -1.0]], [[0.25, -0.25]]):
            day = held_intraday(np.array(weights), opens, closes)
            assert day.tolist() == [pytest.approx(0.05)]

    def test_a_day_with_no_weight_earns_zero_rather_than_nan(self) -> None:
        nan = np.full((1, 2), np.nan)
        assert held_intraday(nan, np.ones((1, 2)), np.ones((1, 2))).tolist() == [0.0]
        assert held_overnight(nan, np.ones((1, 2))).tolist() == [0.0]

    def test_open_to_close_signals_on_the_gap_from_yesterdays_close(self) -> None:
        """A gaps down 10 percent at the open and B up 10, so A is bought and B shorted."""
        days = pd.to_datetime(["2007-01-03", "2007-01-04"])
        closes = pd.DataFrame([[10.0, 10.0], [9.9, 10.0]], index=days, columns=["A", "B"])
        opens = pd.DataFrame([[10.0, 10.0], [9.0, 11.0]], index=days, columns=["A", "B"])
        run = open_to_close(opens, closes, start="2007-01-03", end="2007-01-04")
        assert run.weights[1].tolist() == pytest.approx([0.5, -0.5])
        assert run.daily[1] == pytest.approx(0.5 * 0.1 - 0.5 * (10.0 / 11.0 - 1))

    @pytest.mark.parametrize(
        "other",
        [
            lambda frame: frame[["A", "B"]],
            lambda frame: frame.iloc[1:],
            lambda frame: frame[["B", "A", "C"]],
        ],
        ids=["fewer stocks", "fewer days", "stocks reordered"],
    )
    def test_frames_that_do_not_line_up_are_refused(self, other) -> None:
        """A reordered frame would otherwise pair one stock's opens with another's closes."""
        frame = _hand_frame()
        with pytest.raises(ValueError, match="same days and stocks"):
            open_to_close(frame, other(frame), start="2007-01-03", end="2007-01-05")

    def test_the_apr_compounds_and_annualises_over_252(self) -> None:
        assert compounded_apr(np.full(252, 0.001)) == pytest.approx(1.001**252 - 1)
        assert compounded_apr(np.full(126, 0.001)) == pytest.approx(1.001**252 - 1)

    def test_a_figure_that_misses_is_reported_as_missing_with_its_gap(self) -> None:
        """Every committed figure reproduces, so only a case by hand reaches this branch."""
        assert _verdict(13.677582, "13.7") == "reproduced"
        assert _verdict(13.64, "13.7") == "did not reproduce, gap -0.1"

    def test_a_published_figure_matches_at_its_own_decimals(self) -> None:
        assert matches(13.677582, "13.7")
        assert not matches(13.64, "13.7")
        assert matches(30.164676, "30")
        assert matches(0.7315525015859361, "0.731553")
        assert gap(13.64, "13.7") == pytest.approx(-0.1)
