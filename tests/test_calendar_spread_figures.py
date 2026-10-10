"""The pins for the calendar-spreads post's one figure.

``tests/test_stationary_candidates.py`` holds what the two batches compute.
This file holds that the figure draws those numbers, so a generator that drew
a bar from the wrong null, put the real count on the wrong side of a bar or
binned the null sets off by a pair fails even when the batches are right. Some
numbers repeat here on purpose, because a figure's labels are prose and the
suite is the authority for every number prose quotes. No test compares bytes,
for the reason ``tests/test_regime_figure.py`` gives.

The vintages are EIA's NYMEX settlements for the nearest four contracts,
downloaded 2026-10-02 on the raw basis: ``RNGC1`` to ``RNGC4`` for natural gas
and ``EER-EPMRR-PE1-Y35NY-DPG`` to ``PE4`` for RBOB gasoline. The
specification is Entry 15's six numbered items in ``docs/replication-log.md``,
which :mod:`chan.stationary_candidates` implements. Like the result it draws,
the figure is exploratory.
"""

from __future__ import annotations

import numpy as np
import pytest
from matplotlib.colors import same_color, to_rgba

import chan.calendar_spread_figures as figures
from chan.calendar_spread_figures import (
    CORRECTED_COLOUR,
    DECLARED_COLOUR,
    DOWNLOADED,
    NULLS_FIGURE,
    make_nulls_figure,
    spreads,
)
from chan.futures import settlements
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.stationary_candidates import SPREAD_PRODUCTS
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def results():
    return spreads()


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("calendar_spread_figures") / NULLS_FIGURE


@pytest.fixture(scope="module")
def figure(results, out):
    return make_nulls_figure(results, out=out)


def _by_gid(figure) -> dict:
    found: dict = {}
    for ax in figure.axes:
        for artist in [*ax.lines, *ax.texts, *ax.patches]:
            gid = artist.get_gid()
            if gid and gid.endswith("-bin"):
                found.setdefault(gid, []).append(artist)
            elif gid:
                found[gid] = artist
    return found


#: Each panel's name, which batch it draws, and how many pairs that batch holds.
PANELS = (("gas", 0, 360), ("rbob", 1, 220))


class TestTheBars:
    @pytest.mark.parametrize(("name", "declared", "corrected"), [("gas", 19, 47), ("rbob", 13, 31)])
    def test_each_bar_sits_at_the_pinned_975th_null_share(
        self, figure, name, declared, corrected
    ) -> None:
        """The bars ``TestTheCalendarSpreadVerdicts`` asserts, as whole pairs."""
        drawn = _by_gid(figure)
        assert set(drawn[f"{name}-declared-bar"].get_xdata()) == {declared}
        assert set(drawn[f"{name}-corrected-bar"].get_xdata()) == {corrected}

    @pytest.mark.parametrize(("name", "which", "n"), PANELS)
    def test_each_bar_is_its_own_null_s_cut(self, figure, results, name, which, n) -> None:
        drawn = _by_gid(figure)
        r = results[which]
        assert set(drawn[f"{name}-declared-bar"].get_xdata()) == {round(r.declared_cut * n)}
        assert set(drawn[f"{name}-corrected-bar"].get_xdata()) == {round(r.cut * n)}

    @pytest.mark.parametrize(("name", "declared", "corrected"), [("gas", 19, 47), ("rbob", 13, 31)])
    def test_each_bar_is_labelled_with_its_null_and_its_count(
        self, figure, name, declared, corrected
    ) -> None:
        drawn = _by_gid(figure)
        assert drawn[f"{name}-declared-label"].get_text() == f"declared null's bar: {declared}"
        assert drawn[f"{name}-corrected-label"].get_text() == f"corrected null's bar: {corrected}"
        assert drawn[f"{name}-declared-label"].xy == (declared, 1.0)
        assert drawn[f"{name}-corrected-label"].xy == (corrected, 1.0)

    def test_each_bar_is_dashed_and_its_label_hangs_left_at_its_own_height(self, figure) -> None:
        """Dashed so a bar never reads as the real count's solid line, and each label
        to the left at its own height, because RBOB's 14 sits one pair from its 13."""
        drawn = _by_gid(figure)
        for name, _, _ in PANELS:
            assert drawn[f"{name}-real-line"].get_linestyle() == "-"
            for key in ("declared", "corrected"):
                assert drawn[f"{name}-{key}-bar"].get_linestyle() == "--"
                assert drawn[f"{name}-{key}-label"].get_ha() == "right"
            heights = {drawn[f"{name}-{key}-label"].xyann[1] for key in ("declared", "corrected")}
            assert len(heights) == 2

    def test_each_bar_and_its_label_take_its_null_s_colour(self, figure) -> None:
        drawn = _by_gid(figure)
        for name, _, _ in PANELS:
            for key, colour in (("declared", DECLARED_COLOUR), ("corrected", CORRECTED_COLOUR)):
                assert to_rgba(drawn[f"{name}-{key}-bar"].get_color()) == to_rgba(colour)
                assert to_rgba(drawn[f"{name}-{key}-label"].get_color()) == to_rgba(colour)


class TestTheRealCount:
    @pytest.mark.parametrize(("name", "real"), [("gas", 57), ("rbob", 14)])
    def test_the_marker_and_line_sit_at_the_pinned_count(self, figure, name, real) -> None:
        """The counts ``test_natural_gas_reproduces`` and ``test_rbob_does_not_reproduce`` pin."""
        drawn = _by_gid(figure)
        assert list(drawn[f"{name}-real"].get_xdata()) == [real]
        assert list(drawn[f"{name}-real"].get_ydata()) == [0]
        assert set(drawn[f"{name}-real-line"].get_xdata()) == {real}
        assert drawn[f"{name}-real"].get_clip_on() is False, "half the marker would be cut off"
        bins = [*drawn[f"{name}-declared-bin"], *drawn[f"{name}-corrected-bin"]]
        assert drawn[f"{name}-real-line"].get_zorder() > max(b.get_zorder() for b in bins)

    def test_the_line_and_marker_wear_neither_null_s_colour(self, figure) -> None:
        """In grey or brass the real count would read as one of the nulls."""
        drawn = _by_gid(figure)
        for name, _, _ in PANELS:
            line, marker = drawn[f"{name}-real-line"], drawn[f"{name}-real"]
            assert same_color(line.get_color(), INK)
            assert same_color(marker.get_markerfacecolor(), INK)
            for null in (DECLARED_COLOUR, CORRECTED_COLOUR):
                assert not same_color(line.get_color(), null)
                assert not same_color(marker.get_markerfacecolor(), null)

    def test_natural_gas_sits_past_both_bars_and_rbob_between_them(self, figure) -> None:
        """The picture of the two verdicts: the correction moves RBOB's and not natural gas's."""
        drawn = _by_gid(figure)

        def x(gid: str) -> float:
            return float(np.asarray(drawn[gid].get_xdata())[0])

        assert x("gas-declared-bar") < x("gas-corrected-bar") < x("gas-real")
        assert x("rbob-declared-bar") < x("rbob-real") < x("rbob-corrected-bar")

    def test_each_panel_title_gives_the_count(self, figure) -> None:
        top, bottom = figure.axes
        assert top.get_title(loc="left") == (
            "Natural gas: 57 of 360 pairs reject in both orientations"
        )
        assert bottom.get_title(loc="left") == (
            "RBOB gasoline: 14 of 220 pairs reject in both orientations"
        )


class TestTheHistograms:
    @pytest.mark.parametrize(("name", "which", "n"), PANELS)
    @pytest.mark.parametrize("key", ["declared", "corrected"])
    def test_each_bin_counts_the_null_sets_at_its_whole_pair(
        self, figure, results, name, which, n, key
    ) -> None:
        """One bin per whole pair, centred on it, holding every one of the 1,000 sets."""
        drawn = _by_gid(figure)
        null = results[which].declared_null if key == "declared" else results[which].null
        pairs = np.rint(null * n).astype(int)
        bins = drawn[f"{name}-{key}-bin"]
        heights = {round(b.get_x() + b.get_width() / 2): b.get_height() for b in bins}
        assert all(b.get_width() == pytest.approx(1.0) for b in bins)
        assert sum(heights.values()) == 1000
        for count in range(pairs.max() + 1):
            assert heights[count] == (pairs == count).sum(), count

    @pytest.mark.parametrize(("name", "which", "n"), PANELS)
    def test_the_axis_reaches_past_every_count_drawn(self, figure, results, name, which, n):
        ax = figure.axes[which]
        r = results[which]
        largest = max(
            round(r.share * n), np.rint(r.null * n).max(), np.rint(r.declared_null * n).max()
        )
        assert ax.get_xlim()[0] == -0.5
        assert ax.get_xlim()[1] >= largest + 2, "the rightmost line would sit on the frame"

    @pytest.mark.parametrize(("name", "which", "n"), PANELS)
    def test_the_labels_have_headroom_above_the_tallest_bin(self, figure, name, which, n):
        """The bar labels hang from the top of the axes, so they need room above the bins."""
        ax = figure.axes[which]
        bins = [*_by_gid(figure)[f"{name}-declared-bin"], *_by_gid(figure)[f"{name}-corrected-bin"]]
        assert ax.get_ylim()[1] >= 1.3 * max(b.get_height() for b in bins)

    def test_the_note_s_grey_and_brass_are_the_nulls_colours(self) -> None:
        """The note names the declared null grey and the corrected one brass."""
        assert (DECLARED_COLOUR, CORRECTED_COLOUR) == (MUTED, ACCENT)

    def test_the_two_nulls_wear_different_colours(self) -> None:
        """Colour is the only key to which histogram is which null."""
        assert not same_color(DECLARED_COLOUR, CORRECTED_COLOUR)

    @pytest.mark.parametrize(("name", "which", "n"), PANELS)
    @pytest.mark.parametrize(
        ("key", "colour"), [("declared", DECLARED_COLOUR), ("corrected", CORRECTED_COLOUR)]
    )
    def test_each_histogram_wears_its_null_s_colour_and_shows_the_other_through_it(
        self, figure, name, which, n, key, colour
    ) -> None:
        for patch in _by_gid(figure)[f"{name}-{key}-bin"]:
            assert to_rgba(patch.get_facecolor(), 1.0) == to_rgba(colour, 1.0)
            assert patch.get_alpha() < 1

    def test_nothing_wears_a_verdict_colour(self, figure) -> None:
        verdicts = {to_rgba(GOOD), to_rgba(LOST)}
        for ax in figure.axes:
            for patch in ax.patches:
                assert to_rgba(patch.get_facecolor(), 1.0) not in verdicts
            for line in ax.lines:
                assert to_rgba(line.get_color()) not in verdicts
            for text in [*ax.texts, ax.title, ax.xaxis.label, ax.yaxis.label]:
                assert to_rgba(text.get_color()) not in verdicts
        for text in figure.texts:
            assert to_rgba(text.get_color()) not in verdicts


class TestTheWords:
    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Chan's calendar spreads against two nulls, an exploratory result"
        )

    def test_the_axes_count_pairs_and_null_sets(self, figure) -> None:
        top, bottom = figure.axes
        assert bottom.get_xlabel() == "pairs rejecting in both orientations at 10%"
        assert top.get_ylabel() == bottom.get_ylabel() == "null sets of 1,000"

    def test_the_note_names_the_eight_files_and_their_download_date(self, figure) -> None:
        note = figure.texts[-1].get_text()
        for product in SPREAD_PRODUCTS:
            assert f"{product.name}: {', '.join(product.symbols)}" in note
            for symbol in product.symbols:
                assert settlements(symbol)[0].download_date == DOWNLOADED
        assert note.startswith(f"EIA's NYMEX settlements, downloaded {DOWNLOADED}:\n")
        assert note.replace("\n", " ").endswith(
            "Each histogram is 1,000 sets of simulated contracts that do not cointegrate, "
            "read on the days the real pairs keep. The grey null makes every contract an "
            "independent walk, as declared before any statistic. The brass null correlates "
            "them at the files' own median, the correction made after the result was seen."
        )

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for text in [*figure.axes[0].texts, *figure.axes[1].texts, *figure.texts]:
            assert text.get_parse_math() is False


def test_drawing_writes_the_file_it_is_given(figure, out) -> None:
    assert out.is_file()


def test_drawing_reads_only_the_batches_it_is_given(results, monkeypatch, tmp_path) -> None:
    def refuse(*_args, **_kwargs):
        raise AssertionError("the figure read the vintages instead of the batches it was given")

    monkeypatch.setattr(figures, "calendar_spread", refuse)
    drawn = _by_gid(make_nulls_figure(results, out=tmp_path / NULLS_FIGURE))
    assert list(drawn["gas-real"].get_xdata()) == [57]


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / NULLS_FIGURE).is_file()


def test_the_command_reads_the_vintages_once_and_draws(monkeypatch, capsys) -> None:
    pair, drawn, reads = object(), [], []
    monkeypatch.setattr(figures, "spreads", lambda: reads.append(1) or pair)
    monkeypatch.setattr(figures, "make_nulls_figure", lambda r: drawn.append(r))
    figures.main()
    assert reads == [1]
    assert drawn == [pair]
    assert NULLS_FIGURE in capsys.readouterr().out


def test_a_missing_vintage_reaches_the_operator_as_one_line(monkeypatch) -> None:
    def refuse():
        raise VintageUnavailable("no committed eia vintage for RNGC4")

    monkeypatch.setattr(figures, "spreads", refuse)
    with pytest.raises(SystemExit, match="no committed eia vintage for RNGC4"):
        figures.main()


def test_any_other_failure_still_ends_in_a_traceback(monkeypatch) -> None:
    """Only a refused vintage becomes one line, so a real bug is not hidden."""

    def broken():
        raise ValueError("a bug, not a refusal")

    monkeypatch.setattr(figures, "spreads", broken)
    with pytest.raises(ValueError, match="a bug, not a refusal"):
        figures.main()
