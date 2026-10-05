"""The pins for the Conditional Parameter Optimization post's one figure.

``tests/test_cpo.py`` holds what Example 7.1 computes. This file holds that the
figure draws those numbers, so a generator that plotted the wrong array, put
Chan's line at the wrong height or labelled the wrong cell fails even when the
run is right. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads a run of Example 7.1, and the real run needs the owner's
archive of minute bars, so the file splits in two.

1. **The drawing**, on a synthetic :class:`chan.cpo.Result` of 400 cells built
   here, runs on every clone. Its vintages come from
   ``data/archive_vintages.jsonl`` through
   :func:`chan.archive.read_archive_manifest`, which needs no archive.
2. **The labels on the real run** read the session's one run from
   ``tests/conftest.py``, so they skip where ``tests/test_cpo.py``'s pins skip.
   The vintages are the archive's ``gld_intraday_1min.csv.gz``, sha256
   ``3611a8f7…0de7a``, and ``gdx_intraday_1min.csv.gz``, sha256
   ``c47f5890…711c``, and the specification is the 19 readings declared on
   issue 23 before any return was computed.

Like Entry 16's row 10, which it draws, the figure was added after the result
was seen and is exploratory.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import chan.cpo_figures as figures
from chan import cpo
from chan.archive import ArchiveRefused, ArchiveUnavailable, read_archive_manifest
from chan.cpo_figures import CELLS_FIGURE, labelled_cells, make_cells_figure
from chan.paths import FIGURES_DIR

#: Where the synthetic run puts the three cells the figure must find, and a
#: decoy that would be nearest if the line were measured against 1.95.
CHOSEN, HIGHEST, NEAREST, DECOY = 42, 123, 250, 300

#: The words each label must carry, so swapping two labels' roles fails.
ROLES = {
    "chosen": "chosen on the training years",
    "highest": "highest test Sharpe ratio",
    "nearest": "nearest Chan's 1.947",
}


def synthetic_result() -> cpo.Result:
    """A run of 400 cells whose three labelled cells sit where the test put them.

    Every other cell's Sharpe ratio stays outside 1.6 to 2.3 and below 5.5, so
    only the cells placed here compete. ``NEAREST`` sits at 1.946 and
    ``DECOY`` at 1.949, so a figure measuring against 1.95 rather than 1.947
    labels the decoy. ``CHOSEN`` is not the highest, as on the real run, so a
    figure that labelled the argmax as the chosen cell fails. The re-chosen
    arm's cells never include ``CHOSEN``, so a figure that read the chosen cell
    from them fails too.
    """
    rng = np.random.default_rng(20261004)
    n = len(cpo.cells())
    sharpes = rng.choice(
        np.concatenate([rng.uniform(0.5, 1.6, n), rng.uniform(2.3, 5.5, n)]), n, replace=False
    )
    sharpes[HIGHEST] = 6.0
    sharpes[NEAREST] = 1.946
    sharpes[DECOY] = 1.949
    trips = rng.uniform(0.5, 60.0, n)
    by_symbol = {entry.symbol: entry for entry in read_archive_manifest()}
    days = pd.bdate_range(end="2020-12-31", periods=20)
    return cpo.Result(
        vintages=(by_symbol["GLD"], by_symbol["GDX"]),
        days=days,
        n_train=16,
        unconditional=cpo.cells()[CHOSEN],
        unconditional_returns=np.zeros(4),
        unconditional_trips=np.zeros(4, dtype=np.int64),
        conditional_cells=np.array([7, 8, 9, 10]),
        conditional_returns=np.zeros(4),
        conditional_trips=np.zeros(4, dtype=np.int64),
        cell_sharpes=sharpes,
        cell_trips=trips,
    )


@pytest.fixture(scope="module")
def result() -> cpo.Result:
    return synthetic_result()


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("cpo_figures") / CELLS_FIGURE


@pytest.fixture(scope="module")
def figure(result, out):
    return make_cells_figure(result, out=out)


def _by_gid(figure) -> dict:
    ax = figure.axes[0]
    return {
        artist.get_gid(): artist
        for artist in [*ax.lines, *ax.texts, *ax.collections]
        if artist.get_gid()
    }


class TestWhatItDraws:
    def test_each_point_is_a_cell_s_round_trips_against_its_sharpe_ratio_in_grid_order(
        self, figure, result
    ) -> None:
        drawn = _by_gid(figure)["cells"].get_offsets()
        assert len(drawn) == len(cpo.cells())
        assert np.array_equal(drawn[:, 0], result.cell_trips)
        assert np.array_equal(drawn[:, 1], result.cell_sharpes)

    def test_the_round_trip_axis_is_logarithmic(self, figure) -> None:
        assert figure.axes[0].get_xscale() == "log"

    def test_the_line_sits_at_chan_s_1_947(self, figure) -> None:
        assert set(_by_gid(figure)["book-line"].get_ydata()) == {1.947}
        assert cpo.BOOK_UNCONDITIONAL["sharpe"] == 1.947

    def test_the_line_s_label_names_1_947_and_sits_on_the_line(self, figure) -> None:
        label = _by_gid(figure)["book-label"]
        assert label.get_text() == "Chan's Sharpe ratio, 1.947"
        assert label.xy[1] == 1.947

    def test_every_cell_is_inside_the_axes(self, figure, result) -> None:
        low, high = figure.axes[0].get_ylim()
        assert low < min(result.cell_sharpes.min(), 1.947)
        assert high > result.cell_sharpes.max()


class TestTheThreeLabels:
    def test_the_module_finds_the_chosen_the_highest_and_the_nearest_cell(self, result) -> None:
        assert labelled_cells(result) == {"chosen": CHOSEN, "highest": HIGHEST, "nearest": NEAREST}

    @pytest.mark.parametrize(
        ("key", "at"), [("chosen", CHOSEN), ("highest", HIGHEST), ("nearest", NEAREST)]
    )
    def test_each_mark_sits_on_its_cell_and_names_it(self, figure, result, key, at) -> None:
        drawn = _by_gid(figure)
        mark = drawn[key]
        assert mark.get_xdata()[0] == result.cell_trips[at]
        assert mark.get_ydata()[0] == result.cell_sharpes[at]
        anchor = drawn[f"{key}-label"]
        assert anchor.xy == (result.cell_trips[at], result.cell_sharpes[at])
        label = anchor.get_text()
        assert label.startswith(f"{cpo.cells()[at].label}, {ROLES[key]}\n")
        assert f"Sharpe ratio {result.cell_sharpes[at]:.3f}" in label
        assert f"{result.cell_trips[at]:.3g} round trips a day" in label


class TestTheLabelling:
    def test_the_title_says_exploratory_and_added_after_the_result_was_seen(self, figure) -> None:
        title = figure._suptitle.get_text()
        assert title.startswith("Exploratory")
        assert "added after the result was seen" in title

    def test_the_note_names_both_vintages_by_hash_and_says_no_cost_is_charged(
        self, figure, result
    ) -> None:
        note = figure.texts[-1].get_text()
        for entry in result.vintages:
            assert (
                f"{entry.symbol}: {entry.path}, sha256 {entry.sha256[:8]}…, "
                f"downloaded {entry.download_date}"
            ) in note
        assert "Nothing is charged for costs." in note
        assert "weight_lookback_entry" in note

    def test_the_note_names_the_test_days_it_draws(self, figure, result) -> None:
        note = figure.texts[-1].get_text()
        days = result.test_days
        assert f"{len(days)} test days from {days[0].date()} to {days[-1].date()}" in note


class TestWritingIt:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / CELLS_FIGURE).is_file()

    def test_main_draws_the_run_it_reads(self, monkeypatch, result) -> None:
        drawn = []
        monkeypatch.setattr(figures.cpo, "run", lambda: result)
        monkeypatch.setattr(figures, "make_cells_figure", lambda run: drawn.append(run))
        figures.main()
        assert drawn == [result]

    @pytest.mark.parametrize("refusal", [ArchiveUnavailable, ArchiveRefused])
    def test_main_with_no_archive_exits_with_one_line(self, monkeypatch, refusal) -> None:
        def refuse() -> cpo.Result:
            raise refusal("no archive here, set QT_ARCHIVE_DIR")

        monkeypatch.setattr(figures.cpo, "run", refuse)
        with pytest.raises(SystemExit) as stopped:
            figures.main()
        assert str(stopped.value) == "no archive here, set QT_ARCHIVE_DIR"


class TestOnTheArchive:
    """The labels on the real run, which skip unless the archive pins run."""

    def test_the_three_labels_are_the_cells_entry_16_names(self, cpo_result) -> None:
        names = {key: cpo.cells()[at].label for key, at in labelled_cells(cpo_result).items()}
        assert names == {"chosen": "2_30_0.2", "highest": "2.5_30_0.2", "nearest": "3_60_2.5"}

    def test_it_draws_nothing_after_2020_12_31(self, cpo_result) -> None:
        assert cpo_result.test_days[-1] == pd.Timestamp("2020-12-31")
