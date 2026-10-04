"""The pins for the commodity-seasonals post's one figure.

``tests/test_commodity_seasonals.py`` holds what the two trades compute. This
file holds that the figure draws those numbers, so a generator that drew a
missing year as a loss, put a divider on the wrong side of a year or labelled
one side with the other's count fails even when the trades are right. Some
numbers repeat here on purpose, because a figure's labels are prose and the
suite is the authority for every number prose quotes. No test compares bytes,
for the reason ``tests/test_regime_figure.py`` gives.

The vintages are EIA's NYMEX settlements downloaded 2026-10-02: contract 1 of
New York Harbor regular gasoline through 2005 and of RBOB gasoline from 2006,
and contracts 2 to 4 of Henry Hub natural gas. The specification is the rules
issue 19 pinned, which ``chan.commodity_seasonals`` implements. Like the record
it draws, the figure is exploratory and carries no verdict.
"""

from __future__ import annotations

import pytest
from matplotlib.colors import to_rgba

import chan.commodity_seasonals_figures as figures
from chan.commodity_seasonals import settlements
from chan.commodity_seasonals_figures import (
    DOWNLOADED,
    GASOLINE_BOOK_END,
    NG_BOOK_END,
    YEARS_FIGURE,
    make_years_figure,
    year_trades,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import GOOD, LOST
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def trades():
    return year_trades()


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("commodity_seasonals_figures") / YEARS_FIGURE


@pytest.fixture(scope="module")
def figure(trades, out):
    return make_years_figure(trades, out=out)


def _by_gid(figure) -> dict:
    found = {}
    for ax in figure.axes:
        for artist in [*ax.lines, *ax.texts, *ax.patches]:
            if artist.get_gid():
                found[artist.get_gid()] = artist
    return found


PANELS = (("gasoline", 0), ("gas", 1))


class TestTheBars:
    @pytest.mark.parametrize(("name", "which"), PANELS)
    def test_every_readable_year_is_a_bar_at_its_settlement_change(
        self, figure, trades, name, which
    ) -> None:
        drawn = _by_gid(figure)
        for trade in trades[which]:
            if trade.change is None:
                assert f"{name}-bar-{trade.year}" not in drawn
                continue
            bar = drawn[f"{name}-bar-{trade.year}"]
            assert bar.get_x() + bar.get_width() / 2 == pytest.approx(trade.year)
            assert bar.get_y() + bar.get_height() == pytest.approx(float(trade.change))

    def test_the_bars_are_every_year_of_both_records(self, figure) -> None:
        drawn = _by_gid(figure)
        gasoline = sorted(int(g.rsplit("-", 1)[1]) for g in drawn if g.startswith("gasoline-bar-"))
        gas = sorted(int(g.rsplit("-", 1)[1]) for g in drawn if g.startswith("gas-bar-"))
        assert gasoline == [1995, 1996, *range(2000, 2024)]
        assert gas == list(range(1994, 2024))

    def test_the_three_missing_years_are_labelled_slots_and_nothing_else(self, figure) -> None:
        drawn = _by_gid(figure)
        missing = sorted(gid for gid in drawn if "-missing-" in gid)
        assert missing == [
            "gasoline-missing-1997",
            "gasoline-missing-1998",
            "gasoline-missing-1999",
        ]
        for gid in missing:
            assert drawn[gid].get_text() == "no row"
            assert drawn[gid].xy == (int(gid[-4:]), 0)

    @pytest.mark.parametrize(("name", "which"), PANELS)
    def test_the_marks_give_every_readable_year_s_sign(self, figure, trades, name, which) -> None:
        """The small years, natural gas's 2014 at under a cent, show their sign here."""
        drawn = _by_gid(figure)
        for kind, outcome in (("profit", True), ("loss", False)):
            marks = drawn[f"{name}-{kind}-marks"]
            expected = [t.year for t in trades[which] if t.profitable is outcome]
            assert list(marks.get_xdata()) == expected
        assert drawn[f"{name}-profit-marks"].get_marker() == "^"
        assert drawn[f"{name}-loss-marks"].get_marker() == "v"

    def test_nothing_wears_a_verdict_colour(self, figure) -> None:
        """One ink for every bar whatever its sign, and no green or red anywhere."""
        verdicts = {to_rgba(GOOD), to_rgba(LOST)}
        for ax in figure.axes:
            assert not ax.collections
            colours = {to_rgba(bar.get_facecolor()) for bar in ax.patches if bar.get_gid()}
            assert len(colours) == 1
            assert not colours & verdicts
            for line in ax.lines:
                assert to_rgba(line.get_color()) not in verdicts
            for text in [
                *ax.texts,
                ax.title,
                ax.xaxis.label,
                ax.yaxis.label,
                *ax.get_xticklabels(),
                *ax.get_yticklabels(),
            ]:
                assert to_rgba(text.get_color()) not in verdicts
        for text in figure.texts:
            assert to_rgba(text.get_color()) not in verdicts


class TestTheDividers:
    def test_each_divider_sits_after_the_book_s_last_year(self, figure) -> None:
        drawn = _by_gid(figure)
        assert set(drawn["gasoline-divider"].get_xdata()) == {2015.5}
        assert set(drawn["gas-divider"].get_xdata()) == {2008.5}
        assert (GASOLINE_BOOK_END, NG_BOOK_END) == (2015, 2008)

    def test_the_labels_read_the_counts_the_post_quotes(self, figure) -> None:
        """The same counts ``TestTheVerdicts`` asserts, on each side of each divider."""
        drawn = _by_gid(figure)
        assert drawn["gasoline-label-before"].get_text() == (
            "1995 to 2015\n16 of 21 profitable\n3 with no row"
        )
        assert drawn["gasoline-label-after"].get_text() == "2016 to 2023\n3 of 8 profitable"
        assert drawn["gas-label-before"].get_text() == "1994 to 2008\n15 of 15 profitable"
        assert drawn["gas-label-after"].get_text() == "2009 to 2023\n7 of 15 profitable"

    def test_each_label_sits_on_its_own_side(self, figure) -> None:
        drawn = _by_gid(figure)
        for name, end in (("gasoline", 2015.5), ("gas", 2008.5)):
            before, after = drawn[f"{name}-label-before"], drawn[f"{name}-label-after"]
            assert (before.get_ha(), after.get_ha()) == ("right", "left")
            assert before.xyann[0] < 0 < after.xyann[0]
            assert before.xy == after.xy == (end, 1.0)

    def test_the_labels_hang_above_the_tallest_bar(self, figure) -> None:
        for ax in figure.axes:
            tallest = max(bar.get_y() + bar.get_height() for bar in ax.patches if bar.get_gid())
            low, high = ax.get_ylim()
            assert high > tallest + 0.25 * (tallest - low)


class TestTheWords:
    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Chan's two commodity seasonals, year by year, an exploratory record with no verdict"
        )

    def test_each_panel_names_its_trade(self, figure) -> None:
        top, bottom = figure.axes
        assert top.get_title(loc="left") == (
            "Gasoline: the May contract, close of April 13 to close of April 25"
        )
        assert bottom.get_title(loc="left") == (
            "Natural gas: the June contract, close of February 25 to close of April 15"
        )

    def test_the_axes_name_the_files_units_in_words(self, figure) -> None:
        top, bottom = figure.axes
        assert top.get_ylabel() == "settlement change,\ndollars a gallon"
        assert bottom.get_ylabel() == "settlement change,\ndollars per million Btu"

    def test_the_note_names_the_five_files_and_their_download_date(self, figure) -> None:
        note = figure.texts[-1].get_text().replace("\n", " ")
        symbols = [
            "EER-EPMR-PE1-Y35NY-DPG",
            "EER-EPMRR-PE1-Y35NY-DPG",
            "RNGC3",
            "RNGC2",
            "RNGC4",
        ]
        assert note.startswith(
            f"EIA's NYMEX settlements, downloaded 2026-10-02: {', '.join(symbols)}."
        )
        for symbol in symbols:
            assert settlements(symbol)[0].download_date == DOWNLOADED
        assert "Chan chose both trades after looking at this history." in note
        assert note.endswith(
            "2015 for gasoline, and 2008 for natural gas under the reading that both of its "
            "counts were written for the first edition."
        )

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for text in [*figure.axes[0].texts, *figure.axes[1].texts, *figure.texts]:
            assert text.get_parse_math() is False


def test_drawing_writes_the_file_it_is_given(figure, out) -> None:
    assert out.is_file()


def test_drawing_reads_only_the_trades_it_is_given(trades, monkeypatch, tmp_path) -> None:
    """Short records draw short panels, and nothing reads the vintages again."""

    def refuse(*_args, **_kwargs):
        raise AssertionError("the figure read the vintages instead of the trades it was given")

    monkeypatch.setattr(figures, "gasoline_trades", refuse)
    monkeypatch.setattr(figures, "natural_gas_trades", refuse)
    gasoline, gas = trades
    short = make_years_figure((gasoline[:25], gas[:22]), out=tmp_path / YEARS_FIGURE)
    drawn = _by_gid(short)
    assert max(int(g.rsplit("-", 1)[1]) for g in drawn if g.startswith("gasoline-bar-")) == 2019
    assert drawn["gasoline-label-after"].get_text() == "2016 to 2019\n2 of 4 profitable"
    assert max(int(g.rsplit("-", 1)[1]) for g in drawn if g.startswith("gas-bar-")) == 2015
    assert short.axes[1].get_xlim()[1] == pytest.approx(2019.7)


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / YEARS_FIGURE).is_file()


def test_the_command_reads_the_vintages_once_and_draws(monkeypatch, capsys) -> None:
    pair, drawn, reads = object(), [], []
    monkeypatch.setattr(figures, "year_trades", lambda: reads.append(1) or pair)
    monkeypatch.setattr(figures, "make_years_figure", lambda t: drawn.append(t))
    figures.main()
    assert reads == [1]
    assert drawn == [pair]
    assert YEARS_FIGURE in capsys.readouterr().out


def test_a_missing_vintage_reaches_the_operator_as_one_line(monkeypatch) -> None:
    def refuse():
        raise VintageUnavailable("no committed eia vintage for RNGC4")

    monkeypatch.setattr(figures, "year_trades", refuse)
    with pytest.raises(SystemExit, match="no committed eia vintage for RNGC4"):
        figures.main()


def test_any_other_failure_still_ends_in_a_traceback(monkeypatch) -> None:
    """Only a refused vintage becomes one line, so a real bug is not hidden."""

    def broken():
        raise ValueError("a bug, not a refusal")

    monkeypatch.setattr(figures, "year_trades", broken)
    with pytest.raises(ValueError, match="a bug, not a refusal"):
        figures.main()
