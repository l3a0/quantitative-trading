"""The pins for the commodity-seasonals post's chart.

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

import itertools
import math

import pytest
from matplotlib.colors import to_rgba

import chan.commodity_seasonals_figures as figures
from chan import regime_figure
from chan.commodity_seasonals import profitable_count, settlements
from chan.commodity_seasonals_figures import (
    ACCENT,
    DOWNLOADED,
    GASOLINE_BOOK_END,
    GOOD,
    LOST,
    NG_BOOK_END,
    YEARS_FIGURE,
    make_years_figure,
    year_trades,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import SURFACE
from chan.usdcad_tests_whiteboard import BOARD
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

    def test_each_panel_draws_its_zero_line(self, figure) -> None:
        drawn = _by_gid(figure)
        for name, _ in PANELS:
            assert set(drawn[f"{name}-zero"].get_ydata()) == {0}

    def test_the_marks_sit_along_each_panel_s_foot(self, figure) -> None:
        """In axes units, so a mark stays at the foot whatever the panel's dollar range."""
        drawn = _by_gid(figure)
        for (name, _), ax in zip(PANELS, figure.axes, strict=True):
            for kind in ("profit", "loss"):
                marks = drawn[f"{name}-{kind}-marks"]
                assert set(marks.get_ydata()) == {0.035}
                assert marks.get_transform() == ax.get_xaxis_transform()

    def test_the_panels_share_one_year_axis_from_1994_to_2023(self, figure) -> None:
        top, bottom = figure.axes
        assert top.get_xlim() == bottom.get_xlim()
        assert bottom.get_xlim() == pytest.approx((1993.3, 2023.7))
        assert bottom.get_xlabel() == "year of the trade"

    def test_the_lowest_bar_sits_clear_of_the_panel_s_foot_marks(self, figure) -> None:
        for ax in figure.axes:
            heights = [bar.get_y() + bar.get_height() for bar in ax.patches if bar.get_gid()]
            lowest, highest = min(heights), max(heights)
            assert ax.get_ylim()[0] < lowest - 0.1 * (highest - lowest)

    def test_nothing_wears_a_verdict_colour(self, figure) -> None:
        """One ink for every bar whatever its sign, and no green or red anywhere."""
        verdicts = {to_rgba(GOOD), to_rgba(LOST)}
        for ax in figure.axes:
            assert not ax.collections
            colours = {to_rgba(bar.get_facecolor()) for bar in ax.patches if bar.get_gid()}
            assert len(colours) == 1
            assert not colours & verdicts
            for line in ax.lines:
                for colour in (
                    line.get_color(),
                    line.get_markerfacecolor(),
                    line.get_markeredgecolor(),
                ):
                    assert to_rgba(colour) not in verdicts
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

    @pytest.mark.parametrize(("name", "which", "end"), [("gasoline", 0, 2015), ("gas", 1, 2008)])
    def test_each_label_counts_its_own_side_of_the_trades(
        self, figure, trades, name, which, end
    ) -> None:
        drawn = _by_gid(figure)
        for side, years in (
            ("before", [t for t in trades[which] if t.year <= end]),
            ("after", [t for t in trades[which] if t.year > end]),
        ):
            missing = sum(1 for t in years if t.profitable is None)
            expected = (
                f"{years[0].year} to {years[-1].year}\n"
                f"{profitable_count(years)} of {len(years)} profitable"
            ) + (f"\n{missing} with no row" if missing else "")
            assert drawn[f"{name}-label-{side}"].get_text() == expected

    def test_each_label_sits_on_its_own_side(self, figure) -> None:
        drawn = _by_gid(figure)
        for name, end in (("gasoline", 2015.5), ("gas", 2008.5)):
            before, after = drawn[f"{name}-label-before"], drawn[f"{name}-label-after"]
            assert (before.get_ha(), after.get_ha()) == ("right", "left")
            assert before.xyann[0] < 0 < after.xyann[0]
            assert before.xy == after.xy == (end, 1.0)
            assert before.get_va() == after.get_va() == "top"

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
        assert note == (
            f"EIA's NYMEX settlements, downloaded 2026-10-02: {', '.join(symbols)}. "
            "One contract a year with no costs, so a bar above zero is a profitable year, "
            "and the marks along each foot point up for a profit and down for a loss. "
            "The dashed line is where the book's years end: 2015 for gasoline, and 2008 for "
            "natural gas under the reading that both of its counts were written for the "
            "first edition. Chan chose both trades after looking at years before the line."
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


# --- The post's colours -------------------------------------------------------
#
# Contrast is WCAG's. The colour-blind separation simulates protanopia,
# deuteranopia and tritanopia with Machado, Oliveira and Fernandes (2009) at
# full severity, then measures the distance in OKLab times 100. 8 is the
# separation a reader can rely on, and 15 the floor for normal vision, the
# thresholds the dataviz guidance this repo's charts follow sets.

_MACHADO = {
    "protan": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deutan": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritan": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


def _linear(colour: str) -> tuple[float, float, float]:
    r, g, b, _ = to_rgba(colour)
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b))


def _contrast(one: str, two: str) -> float:
    lum = [
        sum(w * c for w, c in zip((0.2126, 0.7152, 0.0722), _linear(x), strict=True))
        for x in (one, two)
    ]
    return (max(lum) + 0.05) / (min(lum) + 0.05)


def _oklab(rgb) -> tuple[float, float, float]:
    r, g, b = rgb
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)  # noqa: E741
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def _apart(one: str, two: str, kind: str | None = None) -> float:
    def seen(colour):
        rgb = _linear(colour)
        if kind is None:
            return _oklab(rgb)
        return _oklab(
            [
                min(1.0, max(0.0, sum(k * c for k, c in zip(row, rgb, strict=True))))
                for row in _MACHADO[kind]
            ]
        )

    return 100 * math.dist(seen(one), seen(two))


class TestThePostsColours:
    INKS = {"accent": ACCENT, "good": GOOD, "lost": LOST}

    @pytest.mark.parametrize("name", ["accent", "good", "lost"])
    def test_each_reads_as_text_on_the_board_and_the_ground(self, name) -> None:
        for ground in (BOARD, SURFACE):
            assert _contrast(self.INKS[name], ground) >= 4.5, (name, ground)

    def test_every_pair_stays_apart_with_and_without_colour_blindness(self) -> None:
        pairs = itertools.combinations(self.INKS.values(), 2)
        for one, two in pairs:
            assert _apart(one, two) >= 15, (one, two)
            for kind in _MACHADO:
                assert _apart(one, two, kind) >= 8, (one, two, kind)

    def test_the_shared_colours_they_replace_do_not(self) -> None:
        """The brass and red the other posts draw in sit 3.0 apart under deuteranopia."""
        shared = _apart(regime_figure.ACCENT, regime_figure.LOST, "deutan")
        assert shared == pytest.approx(3.0, abs=0.05)
