"""The pins for post-earnings announcement drift, *Algorithmic Trading*'s Example 7.2.

This file is the single authority for every number any prose surface quotes
about Example 7.2's run on Chan's files. ``blog/post-earnings-drift-lessons.md``
also quotes figures that five other files pin.

1. ``tests/test_pead_figures.py`` pins the dates of the longest spell below
   the high, of the high it falls from and of the deepest drawdown inside it.
2. ``tests/test_series.py`` pins the flag file's 1,885 flags, Apple's three
   flagged days and the 29 stocks with none, as facts about the committed
   flags.
3. ``tests/test_pead_rerun.py`` pins what the rerun's calendar shares with
   Chan's flags and the two Apple mornings his file misses, and
   ``tests/test_earnings_filings.py`` when each of Apple's filings was
   accepted.
4. ``tests/test_equity_seasonals.py`` pins Example 7.7's two Sharpe ratios,
   which Lesson 4 recalls.

``TestWhatThePostQuotes`` reads the post itself. It checks one copy of each
figure the post quotes against the run, at the precision the post prints, and
that includes the figures the first three files pin, read here from the same
committed files. It does not read Example 7.7's two figures or any second
copy of a figure, and its docstring names the runs it reads. README lists what
the post says that nothing pins. ``docs/replication-log.md`` Entry 12 carries
the verdicts and points here row by row.

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
it the arithmetic return prints as 0.0668 rather than 0.0667. It also names
the one position the swap drops, PNW's long on 2012-02-24, which Lesson 4 and
its sketch in ``chan.pead_whiteboard`` draw.

Exploratory. Reproducing Chan's figures spends the 2011 and 2012 sample on a
rule he chose. It first ran here on 2026-10-03.
"""

from __future__ import annotations

from datetime import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from chan import matlab_helpers, pead, pead_rerun
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
from chan.pead_figures import cumulative_return, longest_spell
from chan.pead_rerun import r1_day
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

    def test_157_of_the_330_days_hold_a_position_from_2011_05_11(self, drift: Drift) -> None:
        """Fewer than half the days hold a position, whatever the divisor.

        The first 89 cannot, because the 90-day deviation has not filled. After
        that a day holds one only when a flagged stock clears half a deviation.
        """
        held = np.count_nonzero(drift.positions, axis=1) > 0
        assert int(held.sum()) == 157, SPEC
        assert str(drift.days[held][0].date()) == "2011-05-11", SPEC
        assert drift.days[held][0] == drift.days[LOOKBACK - 1], SPEC

    def test_1279_announcements_fall_where_the_deviation_can_be_finite(
        self, sources, drift: Drift
    ) -> None:
        """Row 89 is the first whose 90-day window can hold a finite deviation.
        Of the 1,279 flagged stock-days from there on, 1,072 clear half a deviation."""
        _, _, _, _, flags = sources
        announced = flags.loc[drift.days].to_numpy() != 0
        assert int(announced[LOOKBACK - 1 :].sum()) == 1279, SPEC
        assert int(np.count_nonzero(drift.positions[announced])) == drift.trades == 1072, SPEC


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

    def test_the_one_position_that_moves_is_pnws_long_on_2012_02_24(
        self, sources, drift: Drift, first_edition: Drift
    ) -> None:
        """Lesson 4's one position. PNW's gap of 0.4212 percent clears half book
        two's deviation, 0.4189 percent, and misses half the first edition's,
        0.4213 percent. All 90 gaps in its window are finite, so the first
        edition's zero-fill plays no part, and its n − 1 divisor alone widens the
        deviation, by √(90/89). That long lost 0.36 percent on the day, and no
        other day's return moves."""
        _, _, opens, closes, _ = sources
        differ = np.argwhere(drift.positions != first_edition.positions)
        assert len(differ) == 1, SPEC
        ((row, column),) = differ
        assert (opens.columns[column], str(drift.days[row].date())) == ("PNW", "2012-02-24")
        assert (drift.positions[row, column], first_edition.positions[row, column]) == (1, 0)
        op = opens.loc[drift.days].to_numpy(dtype=float)[:, column]
        cl = closes.loc[drift.days].to_numpy(dtype=float)[:, column]
        gaps = close_to_open(op[:, None], cl[:, None])[:, 0]
        window = gaps[row - LOOKBACK + 1 : row + 1]
        assert int(np.isfinite(window).sum()) == len(window) == LOOKBACK == 90, SPEC
        gap = gaps[row]
        half_two = ENTRY * float(matlab_helpers.smartstd_book_two(window))
        half_first = ENTRY * float(smartstd_first_edition(window))
        assert half_two <= gap < half_first, SPEC
        assert [f"{100 * v:.4f}" for v in (gap, half_two, half_first)] == [
            "0.4212",
            "0.4189",
            "0.4213",
        ], SPEC
        assert half_first / half_two == pytest.approx(np.sqrt(90 / 89), rel=1e-12), SPEC
        day_return = (cl[row] - op[row]) / op[row]
        assert f"{100 * day_return:.2f}" == "-0.36", SPEC
        assert np.flatnonzero(drift.daily != first_edition.daily).tolist() == [row], SPEC
        assert drift.daily[row] - first_edition.daily[row] == pytest.approx(
            day_return / DENOMINATOR, abs=1e-15
        ), SPEC


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


# --- what the post quotes ----------------------------------------------------------

POST = Path(__file__).parents[1] / "blog" / "post-earnings-drift-lessons.md"

#: Small counts as the post spells them out, indexed by the count.
SPELLED = ("no", "one", "two", "three", "four", "five", "six", "seven")


def thousands(count: int) -> str:
    """A count with its thousands comma, as the post's prose writes it."""
    return f"{count:,}"


def _minus(x: float, places: int) -> str:
    """A figure at the post's precision, with the post's prose minus sign, U+2212."""
    return f"{x:.{places}f}".replace("-", "−")


def _afternoon(at: time) -> str:
    """A time after noon as the post writes it, such as 4:00 p.m."""
    return f"{at.hour - 12}:{at.minute:02d} p.m."


class TestWhatThePostQuotes:
    """One copy of each figure ``blog/post-earnings-drift-lessons.md`` quotes, read against the run.

    The classes above pin each figure once, and the post copies it by hand.
    Here each figure is built from the run at the precision the post prints
    it, and looked for in one copy: a short fragment holding the number and
    the few words that name one place in the post. A typo in that copy, or a
    re-pin that leaves the post behind, fails here. Lesson 1's table is
    rebuilt whole from the run, so a digit added to a cell fails as well as a
    digit changed. Each comparison the post's words draw on the run, such as
    "more than half the days hold none", is asserted on the run, and one copy
    of its words is read.

    Four runs supply the figures, all on the committed files.

    1. :func:`chan.pead.pead` on Chan's two files, the run the classes above
       pin, for the five printed figures, the 30, the counts of positions and
       days, and the window.
    2. The same run with the first edition's ``smartstd``, for Lesson 4's
       1,071, 0.066833 and PNW's long on 2012-02-24.
    3. :func:`chan.pead_figures.longest_spell` on that run's cumulative
       return, for the spell's 109 days, its dates, the high before it and
       the trough inside it.
    4. :func:`chan.pead_rerun.read_committed` on the same files, for the flag
       file's 1,885 flags, the 29 stocks with none and Apple's flagged days,
       for Apple's six releases and their acceptance times, and for the 488
       stocks and the 1,540, 311 and 914 flags of the rerun's calendar.
       ``tests/test_series.py`` and ``tests/test_pead_rerun.py`` pin the same
       figures, and this class reads the post's copy of them.

    The post states most figures more than once, in a lesson, the table, an
    alt text or the closing lists, and the other copies are not read, so a
    typo in one of them passes. The two sketches' alt texts are read against
    their labels by ``tests/test_pead_whiteboard.py`` instead. Example 7.7's
    two Sharpe ratios, which Lesson 4 recalls, are not read here, because
    their run reads another book's data, and ``tests/test_equity_seasonals.py``
    holds them. Chan's words, the Kindle locations, the mirror's commit and
    the references stay unpinned, as README lists.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def text(cls) -> str:
        return POST.read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    @classmethod
    def rerun(cls, sources) -> pead_rerun.Sources:
        """The rerun's committed sources, with Chan's two files read once for the module."""
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(pead_rerun, "read_sources", lambda data_dir=None: sources)
            return pead_rerun.read_committed()

    @staticmethod
    def missing(text: str, fragments: list[str]) -> list[str]:
        return [fragment for fragment in fragments if fragment not in text]

    def test_the_files_and_the_window(self, sources, drift: Drift, text) -> None:
        prices, announcements, opens, _, flags = sources
        (prices_saved,) = {m.obtained for m in prices}
        (flags_saved,) = {m.obtained for m in announcements}
        days = drift.days
        assert ENTRY == 0.5, "half that deviation"
        fragments = [
            f"on the S&P 500 from {days[0]:%B %Y} to {days[-1]:%B %Y}",
            f"the opens and closes of {opens.shape[1]} stocks, saved on {prices_saved}",
            f"for the same {flags.shape[1]} stocks",
            f"Saved on {flags_saved}, it covers {len(days)} trading days, from "
            f"{days[0].date()} to {days[-1].date()}.",
            f"cuts the prices down to the flag file’s {len(days)} days",
            f"A company that left the index during {days[0].year} is not in the file.",
            f"The price file holds {opens.shape[1]} stocks, Chan’s list of the S&P 500 on "
            f"{opens.index[-1].date()}",
            f"between {_afternoon(pead_rerun.SESSION_CLOSE)} and "
            f"{pead_rerun.SESSION_OPEN.hour}:{pead_rerun.SESSION_OPEN.minute:02d} a.m. Eastern",
            f"the gap’s {LOOKBACK}-day moving standard deviation",
            "A gap of at least half that deviation goes long",
            f"sums each day’s returns across stocks and divides by {DENOMINATOR}",
            f"times {TRADING_DAYS} trading days a year",
        ]
        assert self.missing(text, fragments) == []

    def test_the_opening(self, drift: Drift, text) -> None:
        d = drift
        fragments = [
            f"an annual percentage rate, or APR, of {100 * d.arithmetic_annual:.1f} percent",
            f"“a very respectable {d.sharpe:.1f}”",
            f"is {d.arithmetic_annual:.6f}, the book’s {100 * d.arithmetic_annual:.1f} percent",
            f"The Sharpe ratio is {d.sharpe:.4f}, the book’s {d.sharpe:.1f}.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_1_s_table(self, drift: Drift, text) -> None:
        """Rebuilt whole from the run, each cell at the precision its column prints."""
        d, none = drift, r"\text{none}"
        rows = [
            (
                "Arithmetic",
                f"{d.arithmetic_annual:.6f}",
                f"{d.arithmetic_annual:7.4f}".strip(),
                rf"{100 * d.arithmetic_annual:.1f}\%",
            ),
            ("Sharpe ratio", f"{d.sharpe:.4f}", f"{d.sharpe:4.2f}", f"{d.sharpe:.1f}"),
            ("Compounded", f"{d.compounded_apr:.6f}", f"{d.compounded_apr:10.4f}".strip(), none),
            ("Max drawdown", f"{d.max_drawdown:.6f}", f"{d.max_drawdown:f}", none),
            ("Longest, days", f"{d.max_drawdown_days}", f"{d.max_drawdown_days}", none),
            ("Most positions", f"{d.most_held}", none, f"{d.most_held}"),
            (f"Levered {BOOK_LEVERAGE}x", f"{d.levered:.6f}", none, rf"{round(100 * d.levered)}\%"),
        ]
        table = (
            r"\small\begin{array}{l|r|r|r}" + "\n"
            r"\text{Figure} & \text{Computed} & \texttt{pead.m} & \text{Book} \\ \hline"
            + "\n"
            + " \\\\\n".join(rf"\text{{{name}}} & {a} & {b} & {c}" for name, a, b, c in rows)
            + "\n\\end{array}"
        )
        printed = sum(script != none for _, _, script, _ in rows)
        quoted = sum(script != none and book != none for _, _, script, book in rows)
        stated = sum(script == none and book != none for _, _, script, book in rows)
        fragments = [
            table,
            f"record {SPELLED[printed]} figures the script prints. The book quotes "
            f"{SPELLED[quoted]} of them, rounded, and states {SPELLED[stated]} more numbers in "
            "its text.",
            f"{SPELLED[printed - quoted].capitalize()} more figures the script prints match too, "
            f"and so do {SPELLED[stated]} numbers Chan states in his text. Lesson 1’s table lists "
            f"all {SPELLED[len(rows)]}.",
            f"the book calls close to {round(100 * d.levered)} percent",
        ]
        assert self.missing(text, fragments) == []

    def test_the_two_aprs(self, drift: Drift, text) -> None:
        arithmetic = f"{100 * drift.arithmetic_annual:.1f}"
        compounded = f"{100 * drift.compounded_apr:.1f}"
        assert compounded != arithmetic, SPEC
        fragments = [
            f"the compounded figure reads {compounded} percent, so the book’s {arithmetic} can "
            "only be the arithmetic one",
        ]
        assert self.missing(text, fragments) == []

    def test_the_spell_below_the_high(self, drift: Drift, text) -> None:
        cumret = cumulative_return(drift)
        spell = longest_spell(cumret)
        day = lambda row: drift.days[row].date()  # noqa: E731
        assert spell.rows == drift.max_drawdown_days, SPEC
        assert spell.depth == pytest.approx(drift.max_drawdown, abs=1e-15), SPEC
        assert spell.first <= spell.trough <= spell.last, "on this run they do"
        assert cumret[spell.last + 1] >= cumret[spell.high], "climbs back to the high"
        assert cumret.max() > cumret[spell.high], "rises past it"
        fragments = [
            f"to a high marked on {day(spell.high)}",
            f"The line climbs back to the high in {drift.days[spell.last + 1]:%B %Y}, rises "
            f"past it, and ends near {round(100 * cumret[-1])} percent in "
            f"{drift.days[-1]:%B %Y}.",
            f"The red band runs {spell.rows} trading days, from {day(spell.first)} to "
            f"{day(spell.last)}, and the deepest drawdown, {_minus(spell.depth, 6)}, falls "
            f"inside it on {day(spell.trough)}.",
            "On this run they do.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2_s_gap(self, sources, drift: Drift, text) -> None:
        flags = sources[4]
        announced = flags.loc[drift.days].to_numpy() != 0
        fillable = int(announced[LOOKBACK - 1 :].sum())
        traded = int(np.count_nonzero(drift.positions[announced]))
        assert traded == drift.trades, SPEC
        assert traded > fillable / 2, "most flagged announcements get traded"
        fragments = [
            f"{thousands(fillable)} announcements fall on or after the first day the "
            f"{LOOKBACK}-day deviation can be computed, and {thousands(traded)} of them clear "
            "the bar and are traded. So most flagged announcements get traded",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_2_s_flags(self, rerun, text) -> None:
        flags, window = rerun.flags, rerun.window
        unflagged = int((flags.to_numpy() == 0).all(axis=0).sum())
        apple = [str(day.date()) for day in flags.index[flags["AAPL"] != 0]]
        releases = [
            pd.Timestamp(r.accepted)
            for r in rerun.releases
            if r.ticker == "AAPL"
            and window[0] <= pd.Timestamp(r.accepted).normalize() <= window[-1]
        ]
        mornings = [r1_day(at, rerun.days) for at in releases]
        inside = [day for day in mornings if day is not None and day in window]
        missed = [str(day.date()) for day in inside if flags.at[day, "AAPL"] == 0]
        (about,) = {at.round("30min").time() for at in releases}
        assert all(at.time() > pead_rerun.SESSION_CLOSE for at in releases), "after the close"
        assert set(np.unique(flags.to_numpy())) == {0.0, 1.0}, "a 1 or a 0"
        assert releases[-1].normalize() == window[-1], "the last came on its final day"
        derived = rerun.calendar_flags("R1")["AAPL"]
        assert [str(d.date()) for d in derived.index[(derived == 1) & (flags["AAPL"] == 0)]] == (
            missed
        )
        fragments = [
            "a 1 on each day the stock announced between the previous close and the open, "
            "and a 0 otherwise",
            f"The file holds {thousands(int(flags.to_numpy().sum()))} flags across its "
            f"{flags.shape[1]} stocks, and {unflagged} of the stocks carry none at all",
            f"Apple is flagged on {SPELLED[len(apple)]} days: {apple[0]}, {apple[1]} and "
            f"{apple[2]}.",
            f"Apple released earnings {SPELLED[len(releases)]} times inside the window. The last "
            f"came on its final day, {window[-1].date()}, so only {SPELLED[len(inside)]} have a "
            f"next morning inside it, and {SPELLED[len(missed)]} of those "
            f"{SPELLED[len(inside)]} mornings carry no flag.",
            f"That calendar flags {missed[0]} and {missed[1]}, the mornings after the "
            f"{SPELLED[len(missed)]} Apple releases Chan’s file misses.",
            f"all {SPELLED[len(releases)]} of Apple’s filings inside the window were accepted "
            f"at about {_afternoon(about)} Eastern, after the close",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_3(self, drift: Drift, text) -> None:
        held = np.count_nonzero(drift.positions, axis=1) > 0
        first = drift.days[held][0]
        assert first == drift.days[LOOKBACK - 1], "the first day one could"
        assert held.sum() < len(held) / 2, "more than half the days hold none"
        fragments = [
            f"The busiest day of the run holds {drift.most_held} positions",
            f"No position is possible in the first {LOOKBACK - 1} days, because the deviation "
            f"needs {LOOKBACK} days in its window",
            f"The first position comes on the first day one could, {first.date()}.",
            f"Across the whole window, {int(held.sum())} of the {len(held)} days hold any "
            "position at all, so more than half the days hold none.",
            f"At exactly {SPELLED[BOOK_LEVERAGE]}, the figure is {drift.levered:.6f}, which "
            f"rounds to his {round(100 * drift.levered)}.",
        ]
        assert self.missing(text, fragments) == []

    def test_lesson_4(self, sources, drift: Drift, first_edition: Drift, text) -> None:
        d, f = drift, first_edition
        assert round(f.arithmetic_annual - d.arithmetic_annual, 4) == 0.0001, "one unit off"
        script = lambda r: (  # noqa: E731
            f"{r.arithmetic_annual:7.4f}".strip(),
            f"{r.sharpe:4.2f}",
            f"{r.compounded_apr:10.4f}".strip(),
            f"{r.max_drawdown:f}",
            r.max_drawdown_days,
        )
        kept = sum(a == b for a, b in zip(script(d), script(f), strict=True))
        ((row, column),) = np.argwhere(d.positions != f.positions)
        _, _, opens, closes, _ = sources
        op = opens.loc[d.days].to_numpy(dtype=float)[:, column]
        cl = closes.loc[d.days].to_numpy(dtype=float)[:, column]
        gaps = close_to_open(op[:, None], cl[:, None])[:, 0]
        window = gaps[row - LOOKBACK + 1 : row + 1]
        finite = int(np.isfinite(window).sum())
        half_two = ENTRY * float(matlab_helpers.smartstd_book_two(window))
        half_first = ENTRY * float(smartstd_first_edition(window))
        loss = (cl[row] - op[row]) / op[row]
        assert d.positions[row, column] == 1 and f.positions[row, column] == 0, "long, then not"
        assert half_two <= gaps[row] < half_first, SPEC
        assert loss < 0 and f.arithmetic_annual > d.arithmetic_annual, "raises the return"
        fragments = [
            f"the strategy takes {thousands(f.trades)} positions rather than "
            f"{thousands(d.trades)}, and the arithmetic annual return becomes "
            f"{f.arithmetic_annual:.6f}. That prints as {script(f)[0]}, one unit off the "
            f"script’s {script(d)[0]}.",
            f"The one position that changes is {opens.columns[column]} on "
            f"{d.days[row].date()}. Its gap was {100 * gaps[row]:.4f} percent. Half the "
            f"*Algorithmic Trading* helper’s deviation was {100 * half_two:.4f} percent, so it "
            f"went long. Half the first edition’s was {100 * half_first:.4f} percent",
            f"has a gap on all {finite} days of its window",
            f"the divisor, {finite - 1} rather than {finite}, and that alone widens",
            f"That long lost {-100 * loss:.2f} percent on the day, so dropping it raises the "
            "return.",
            f"would match {SPELLED[kept]} of the {SPELLED[len(script(d))]} printed figures and "
            "miss the fifth by one digit",
        ]
        assert finite == LOOKBACK, "a gap on all of them"
        assert self.missing(text, fragments) == []

    def test_what_the_rerun_s_calendar_shares_with_chan_s(self, rerun, text) -> None:
        counts = pead_rerun.agreement(rerun.calendar_flags("R1"), rerun.flags)
        fragments = [
            f"Over the {len(rerun.universe('CAL'))} stocks it could match to a filer, that "
            f"calendar and Chan’s share {thousands(counts.both)} flags. Chan’s file holds "
            f"{counts.chan_only} that the rule does not give, and the rule gives "
            f"{counts.derived_only} that his file lacks.",
        ]
        assert self.missing(text, fragments) == []


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
