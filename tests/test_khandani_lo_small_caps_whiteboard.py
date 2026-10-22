"""The pins for the two whiteboard GIFs in the post on the reversal on Chan's S&P 600 file.

One sketches Lesson 3's narrowing of the closes' standard error by the two
books' correlation, and one Lesson 6's order of the three indexes at the
closes and the opens. Neither is schematic.

The narrowing sketch draws :class:`Narrowing`, read from
:func:`chan.khandani_lo_small_caps.compare` on the two committed files, so its
test reads the run itself. The size-order sketch draws that run's S&P 500 and
S&P 600 figures beside the S&P 400's, which need the owner's archive. Those
are pinned here as :data:`PINNED_MID`, so every test here runs without the
archive, and ``test_the_whiteboard_draws_this_runs_figures`` in
``tests/test_khandani_lo_mid_caps.py`` holds that the run gives them.

What is pinned for each sketch:

1. Its words, the exact labels in the order they are drawn.
2. Its colours: each step coloured by what it says about the predicted order,
   each band green, the gap brass and the notes grey.
3. Its geometry: each dot, band edge and the gap line at an affine function of
   its unrounded figure.
4. Its numbers, read from the run, and a made-up second set of figures that
   moves the words, the marks and the colours with it, and figures the words
   would misdescribe, which are refused.
5. Its place in the post, right after the paragraph it draws, keyed on that
   paragraph's opening words.
6. Its alt text, which quotes the title and every label in drawing order.

The shared rules hold for both: every label clears every line by 10 pixels in
the installed hand font and in the fallback, sits inside the board and stays
clear of the other labels, and every pale tint has a green edge. Two draws on
one machine give the same bytes. Whether a committed GIF equals a fresh draw
depends on the font, as ``tests/test_usdcad_tests_whiteboard.py`` explains, so
that comparison runs only on macOS arm64 with Comic Sans MS.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import platform
import re

import matplotlib
import pytest
from PIL import Image

from chan import khandani_lo_mid_caps as mid_caps
from chan import khandani_lo_small_caps as small_caps
from chan import khandani_lo_small_caps_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.archive import ArchiveUnavailable
from chan.fund_panel import PanelRefused
from chan.khandani_lo_small_caps_whiteboard import (
    INDEX_X,
    MidCaps,
    Narrowing,
    SizeOrder,
    _on_gap,
    _size_y,
    gif_name,
    main,
    make_khandani_lo_small_caps_whiteboards,
    sketch_timeline,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    TITLE_MS,
    WIDTH,
    Frame,
    Label,
    clearances,
    hand_font,
)

POST = REPO_ROOT / "blog" / "khandani-lo-small-caps-lessons.md"

#: Every GIF in the order :func:`make_khandani_lo_small_caps_whiteboards`
#: writes them, which is the order the post places them.
GIFS = [
    "khandani_lo_small_caps_correlation_narrows.gif",
    "khandani_lo_small_caps_size_order.gif",
]
#: The GIF a redraw cannot write without the owner's archive.
ARCHIVE_GIFS = {"khandani_lo_small_caps_size_order.gif"}

#: The S&P 400's figures, as ``TestTheMidCapFigures`` and
#: ``TestTheGapsToBothNeighbours`` in ``tests/test_khandani_lo_mid_caps.py``
#: pin them at four decimals. The vintage is the ``sp400`` cross-section in
#: the owner's archive, Alpha Vantage's ``TIME_SERIES_DAILY_ADJUSTED`` for the
#: 285 IJH holdings a run keeps, downloaded on 2026-10-11, and the S&P 500 is
#: Chan's ``SPX_20071123.mat`` and the S&P 600 his ``IJR_20080114.mat``. The
#: specification is rule B before costs over 2006-01-03 to 2006-12-29, 251
#: days, and each step's z is Memmel's test, the smaller index less the
#: larger. A re-pin there moves these figures.
PINNED_MID = MidCaps(
    closes=2.0337991700794444,
    opens=3.453316770324929,
    closes_up_z=2.1973049054236578,
    closes_down_z=1.3593448748395631,
    opens_up_z=-1.0777487158812218,
    opens_down_z=1.550006388641198,
)

NARROWING_LABELS = [
    "−2",
    "0",
    "+2",
    "gap in Sharpe ratio",
    "unrelated, ρ = 0: standard error 1.4252",
    "2 standard errors each way",
    "measured ρ = 0.5258: standard error 0.9872",
    "gap +3.1576",
    "z 2.2155, barely past 2",
    "z 3.1987",
    "closes, before costs, 251 days",
]

SIZE_ORDER_LABELS = [
    "S&P 500",
    "S&P 400",
    "S&P 600",
    "predicted: rises as the companies get smaller",
    "0.2510",
    "2.1973 standard errors",
    "2.0338",
    "3.4086",
    "closes",
    "4.4202",
    "breaks the order, about one standard error",
    "3.4533",
    "5.3052",
    "opens",
    "S&P 400: Alpha Vantage files downloaded in 2026",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def result() -> small_caps.Comparison:
    """The comparison on the two committed files, which needs no archive."""
    return small_caps.compare()


@pytest.fixture(scope="module")
def narrowing(result) -> Narrowing:
    return Narrowing.from_comparison(result)


@pytest.fixture(scope="module")
def order(result) -> SizeOrder:
    return SizeOrder.from_runs(result, PINNED_MID)


@pytest.fixture(scope="module")
def every(narrowing, order):
    """Both scenes in the order their GIFs are written."""
    return (sketches._correlation_narrows(narrowing), sketches._size_order(order))


@pytest.fixture(scope="module")
def frames(every):
    return [sketch_timeline(scene) for scene in every]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, result):
    return make_khandani_lo_small_caps_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), comparison=result, mid=PINNED_MID
    )


def _stroke(scene, gid):
    (found,) = [s for s in scene.strokes if s.gid == gid]
    return found


def _label(scene, text) -> Label:
    (found,) = [s for s in scene.steps if isinstance(s, Label) and s.text == text]
    return found


def _font(monkeypatch, fallback: bool) -> None:
    if fallback:
        monkeypatch.setattr(whiteboard, "hand_font", lambda: whiteboard.FALLBACK_FONT)


def _boxes(scene):
    with matplotlib.rc_context(whiteboard._style()):
        canvas, artists = whiteboard._board(scene)
        whiteboard._show(scene, artists, Frame(len(scene.steps), 0, 0))
        canvas.draw()
        renderer = canvas.get_renderer()
        return [
            (artist.get_text(), artist.get_window_extent(renderer))
            for artist in artists
            if hasattr(artist, "get_text") and artist.get_visible()
        ]


def _durations(path) -> list[int]:
    with Image.open(path) as image:
        found = []
        for index in range(image.n_frames):
            image.seek(index)
            found.append(image.info["duration"])
        return found


def _alt(text: str, scene) -> str:
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, every) -> None:
        assert [scene.title for scene in every] == [
            "The correlation narrows the standard error",
            "The size order: mixed",
        ]

    def test_each_has_its_own_gif_named_for_it(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

    def test_each_says_what_it_should(self, every) -> None:
        assert [scene.labels for scene in every] == [NARROWING_LABELS, SIZE_ORDER_LABELS]

    def test_every_label_names_a_stroke_drawn_before_it(self, every) -> None:
        for scene in every:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if not isinstance(s, Label)]
                    assert step.names in earlier, (scene.title, step.text)

    def test_no_label_is_parsed_as_math(self, every) -> None:
        assert not [s.text for scene in every for s in scene.steps if getattr(s, "math", 0)]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, every) -> None:
        for scene in every:
            for stroke in scene.strokes:
                assert stroke.points >= stroke.frames, (scene.title, stroke.gid)

    def test_every_pale_tint_has_a_green_edge(self, every) -> None:
        """The tint alone stands 1.29 to 1 against the white board, under WCAG
        2.1's 3 to 1 for a graphical object, so every tinted region gets a
        green edge that runs round it."""
        assert sketches.TINT_EDGE >= 1.0
        tints = 0
        for scene in every:
            for fill in scene.fills:
                assert fill.color == whiteboard.TINT
                tints += 1
                edges = [
                    s
                    for s in scene.strokes
                    if s.color == GOOD
                    and s.width == sketches.TINT_EDGE
                    and s.x.min() == pytest.approx(fill.x0)
                    and s.x.max() == pytest.approx(fill.x1)
                    and s.y.min() == pytest.approx(fill.y0)
                    and s.y.max() == pytest.approx(fill.y1)
                ]
                assert edges, (scene.slug, fill.gid)
        assert tints == 2


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, every, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in every:
            found = clearances(scene)
            assert set(found) == {*scene.labels, scene.title}
            for text, pixels in found.items():
                assert pixels >= CLEAR_PX, (scene.title, text, round(pixels, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_sits_inside_the_board(
        self, every, monkeypatch, fallback
    ) -> None:
        _font(monkeypatch, fallback)
        for scene in every:
            for text, box in _boxes(scene):
                inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                assert inside >= INSIDE_PX, (scene.title, text, round(inside, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_no_two_labels_touch(self, every, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in every:
            boxes = _boxes(scene)
            for k, (one, a) in enumerate(boxes):
                for other, b in boxes[k + 1 :]:
                    gap = math.hypot(
                        max(a.x0 - b.x1, b.x0 - a.x1, 0.0), max(a.y0 - b.y1, b.y0 - a.y1, 0.0)
                    )
                    assert gap >= APART_LABELS_PX, (scene.title, one, other, round(gap, 1))


class TestTheNarrowing:
    """Lesson 3's sketch draws the closes' gap against two standard errors each
    way, with the two books treated as unrelated and at their measured
    correlation."""

    def test_its_figures_are_the_runs(self, narrowing, result) -> None:
        """The run's own gap, correlation and error, and the error at ρ = 0 as
        ``test_without_the_correlation_the_closes_standard_error_would_be_1_4252``
        computes it."""
        gap = result.closes_gap
        assert (narrowing.gap, narrowing.correlation, narrowing.standard_error) == (
            gap.gap,
            gap.correlation,
            gap.standard_error,
        )
        assert narrowing.days == 251
        assert narrowing.z == gap.z
        assert (f"{narrowing.unrelated_error:.4f}", f"{narrowing.unrelated_z:.4f}") == (
            "1.4252",
            "2.2155",
        )

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert _stroke(scene, "axis").color == MUTED
        assert _stroke(scene, "gap").color == ACCENT
        for gid in ("unrelated", "measured"):
            assert _stroke(scene, f"{gid}-edge").color == GOOD
        colours = {step.text: step.color for step in scene.steps if isinstance(step, Label)}
        assert colours == {
            "−2": MUTED,
            "0": MUTED,
            "+2": MUTED,
            "gap in Sharpe ratio": MUTED,
            "unrelated, ρ = 0: standard error 1.4252": INK,
            "2 standard errors each way": GOOD,
            "measured ρ = 0.5258: standard error 0.9872": INK,
            "gap +3.1576": ACCENT,
            "z 2.2155, barely past 2": INK,
            "z 3.1987": INK,
            "closes, before costs, 251 days": MUTED,
        }

    def test_each_band_runs_two_unrounded_standard_errors_each_way_of_0(
        self, every, narrowing
    ) -> None:
        scene = every[0]
        for fill, error in zip(
            scene.fills, (narrowing.unrelated_error, narrowing.standard_error), strict=True
        ):
            assert (fill.x0, fill.x1) == (_on_gap(-2 * error), _on_gap(2 * error))
            assert (fill.x0 + fill.x1) / 2 == pytest.approx(_on_gap(0.0))
        assert scene.fills[0].y0 > scene.fills[1].y1

    def test_the_gap_crosses_both_rows_past_both_bands(self, every, narrowing) -> None:
        scene = every[0]
        gap = _stroke(scene, "gap")
        assert set(gap.x) == {_on_gap(narrowing.gap)}
        assert gap.y.min() == pytest.approx(sketches.NARROW_AXIS_Y)
        assert gap.y.max() > max(f.y1 for f in scene.fills)
        assert all(gap.x[0] > f.x1 for f in scene.fills)

    def test_the_axis_is_to_scale(self) -> None:
        """Each tick stands at an affine function of its value, so equal gaps
        stand equally far apart."""
        lo, hi = sketches.NARROW_RANGE
        assert (_on_gap(lo), _on_gap(hi)) == pytest.approx(sketches.NARROW_X)
        assert _on_gap(2.0) - _on_gap(0.0) == pytest.approx(_on_gap(0.0) - _on_gap(-2.0))

    def test_each_row_and_its_z_share_a_height(self, every) -> None:
        scene = every[0]
        for fill, text in zip(scene.fills, NARROWING_LABELS[8:10], strict=True):
            assert _label(scene, text).y == pytest.approx((fill.y0 + fill.y1) / 2)
            assert _label(scene, text).x > _stroke(scene, "gap").x[0]

    def test_other_figures_move_the_labels_and_the_marks(self) -> None:
        moved = Narrowing(
            gap=2.5, correlation=0.7, standard_error=0.8, unrelated_error=1.15, days=250
        )
        scene = sketches._correlation_narrows(moved)
        assert scene.labels == [
            *NARROWING_LABELS[:4],
            "unrelated, ρ = 0: standard error 1.1500",
            "2 standard errors each way",
            "measured ρ = 0.7000: standard error 0.8000",
            "gap +2.5000",
            "z 2.1739, barely past 2",
            "z 3.1250",
            "closes, before costs, 250 days",
        ]
        assert set(_stroke(scene, "gap").x) == {_on_gap(2.5)}
        assert scene.fills[1].x1 == _on_gap(1.6)

    @pytest.mark.parametrize(
        "changes",
        [
            {"standard_error": 1.5},
            {"unrelated_error": 1.6},
            {"unrelated_error": 1.2},
            {"gap": 4.0, "unrelated_error": 1.9, "standard_error": 1.0},
        ],
        ids=[
            "the correlation widens the error",
            "the unrelated gap inside 2",
            "the unrelated gap far past 2",
            "off the axis",
        ],
    )
    def test_figures_the_words_would_misdescribe_are_refused(self, narrowing, changes) -> None:
        with pytest.raises(ValueError):
            sketches._correlation_narrows(dataclasses.replace(narrowing, **changes))


#: A made-up run in which the order holds at both prices and the closes' step
#: from the S&P 400 to the S&P 600 is the one beyond one year's noise.
HOLDS = SizeOrder(
    closes=(0.5, 1.5, 4.0), opens=(2.0, 3.0, 3.5), closes_z=(1.2, 2.6), opens_z=(1.1, 0.4)
)


class TestTheSizeOrder:
    """Lesson 6's sketch draws each price's three Sharpe ratios to one scale,
    and colours each step by what it says about the order Chan predicts."""

    def test_its_figures_are_the_runs(self, order, result) -> None:
        assert order.closes == (
            result.large_closes.before_costs,
            PINNED_MID.closes,
            result.small_closes.before_costs,
        )
        assert order.opens == (
            result.large_opens.before_costs,
            PINNED_MID.opens,
            result.small_opens.before_costs,
        )
        assert order.closes_z == (PINNED_MID.closes_up_z, PINNED_MID.closes_down_z)
        assert order.opens_z == (PINNED_MID.opens_up_z, PINNED_MID.opens_down_z)

    def test_the_pinned_s_and_p_400_figures_print_as_the_post_does(self) -> None:
        assert [
            f"{v:.4f}"
            for v in (
                PINNED_MID.closes,
                PINNED_MID.opens,
                PINNED_MID.closes_up_z,
                PINNED_MID.closes_down_z,
                PINNED_MID.opens_up_z,
                PINNED_MID.opens_down_z,
            )
        ] == ["2.0338", "3.4533", "2.1973", "1.3593", "-1.0777", "1.5500"]

    def test_it_reads_mixed_as_the_run_does(self, order) -> None:
        assert order.reading == small_caps.MIXED

    def test_each_dot_stands_at_its_figure_over_its_index(self, every, order) -> None:
        scene = every[1]
        for price, figures in (("closes", order.closes), ("opens", order.opens)):
            for k, (x, figure) in enumerate(zip(INDEX_X, figures, strict=True)):
                dot = _stroke(scene, f"{price}-{k}")
                assert (dot.x[0], dot.y[0]) == (x, _size_y(figure))
                assert dot.color == INK
                value = _label(scene, f"{figure:.4f}")
                assert value.names == dot.gid
                assert math.hypot(value.x - x, value.y - dot.y[0]) < 0.5

    def test_the_scale_is_affine_and_starts_at_0_above_the_axis(self) -> None:
        assert _size_y(2.0) - _size_y(1.0) == pytest.approx(_size_y(1.0) - _size_y(0.0))
        assert _size_y(0.0) > sketches.SIZE_AXIS_Y
        assert _size_y(sketches.SIZE_TOP) < whiteboard.YLIM[1]

    def test_each_step_joins_two_dots(self, every, order) -> None:
        scene = every[1]
        for price, figures in (("closes", order.closes), ("opens", order.opens)):
            for k in (1, 2):
                step = _stroke(scene, f"{price}-step-{k}")
                assert (step.x[0], step.y[0]) == (INDEX_X[k - 1], _size_y(figures[k - 1]))
                assert (step.x[-1], step.y[-1]) == pytest.approx((INDEX_X[k], _size_y(figures[k])))

    def test_each_step_takes_the_colour_of_what_it_says(self, every) -> None:
        """The closes' first step rises beyond the noise, the opens' first
        falls, and both second steps rise inside the noise."""
        scene = every[1]
        assert {
            gid: _stroke(scene, gid).color
            for gid in ("closes-step-1", "closes-step-2", "opens-step-1", "opens-step-2")
        } == {
            "closes-step-1": GOOD,
            "closes-step-2": INK,
            "opens-step-1": LOST,
            "opens-step-2": INK,
        }

    def test_colour_is_never_the_only_cue(self, every) -> None:
        """Each coloured step carries words in its own colour, and each line its name."""
        scene = every[1]
        for text, gid, colour in (
            ("2.1973 standard errors", "closes-step-1", GOOD),
            ("breaks the order, about one standard error", "opens-step-1", LOST),
        ):
            label = _label(scene, text)
            assert (label.names, label.color) == (gid, colour)
        for price in ("closes", "opens"):
            assert _label(scene, price).names == f"{price}-2"

    def test_the_notes_are_grey(self, every) -> None:
        scene = every[1]
        assert _stroke(scene, "axis").color == _stroke(scene, "predicted").color == MUTED
        for text in (
            *SIZE_ORDER_LABELS[:4],
            "S&P 400: Alpha Vantage files downloaded in 2026",
        ):
            assert _label(scene, text).color == MUTED, text

    def test_the_predicted_arrow_points_up_and_right(self, every) -> None:
        arrow = _stroke(every[1], "predicted")
        assert arrow.x[-1] > arrow.x[0] and arrow.y[-1] > arrow.y[0]

    def test_other_figures_move_the_title_the_marks_and_the_colours(self) -> None:
        scene = sketches._size_order(HOLDS)
        assert scene.title == "The size order: pointing the way Chan says"
        assert scene.labels == [
            *SIZE_ORDER_LABELS[:4],
            "0.5000",
            "1.5000",
            "2.6000 standard errors",
            "4.0000",
            "closes",
            "2.0000",
            "3.0000",
            "3.5000",
            "opens",
            SIZE_ORDER_LABELS[-1],
        ]
        assert [
            _stroke(scene, gid).color
            for gid in ("closes-step-1", "closes-step-2", "opens-step-1", "opens-step-2")
        ] == [INK, GOOD, INK, INK]
        assert _stroke(scene, "closes-2").y[0] == _size_y(4.0)

    def test_a_falling_step_names_its_standard_errors_in_words(self, order) -> None:
        moved = dataclasses.replace(order, opens_z=(-1.6, order.opens_z[1]))
        assert "breaks the order, about two standard errors" in sketches._size_order(moved).labels

    @pytest.mark.parametrize(
        "changes",
        [
            {"opens_z": (-2.4, 1.55)},
            {"opens_z": (-0.3, 1.55)},
            {"opens_z": (1.08, 1.55)},
            {"closes": (0.25, 2.03, 6.0)},
            {"opens": (-0.1, 3.45, 5.31)},
        ],
        ids=[
            "a fall beyond the noise",
            "a fall of under half a standard error",
            "a z whose sign is not the step's",
            "off the top",
            "below 0",
        ],
    )
    def test_figures_the_words_would_misdescribe_are_refused(self, order, changes) -> None:
        with pytest.raises(ValueError):
            sketches._size_order(dataclasses.replace(order, **changes))


class TestTheGifs:
    def test_there_is_one_named_for_each_scene(self, gifs) -> None:
        assert [path.name for path in gifs] == GIFS

    def test_each_is_680_by_320_and_loops_forever(self, gifs, frames) -> None:
        for path, steps in zip(gifs, frames, strict=True):
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(path) == [f.ms for f in steps], path.name

    def test_each_opens_on_its_title_and_holds_its_drawing_slowly(self, every, frames) -> None:
        assert sketches.PACED == tuple(scene.slug for scene in every)
        for scene, steps in zip(every, frames, strict=True):
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            assert steps[-1].ms == sketches.PACED_HOLD_MS, scene.slug
            shown = [f.ms for f in steps if f.partial == 0 and 0 < f.done < len(scene.steps)]
            assert set(shown) <= {sketches.PACED_LABEL_MS, whiteboard.FRAME_MS}

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, result) -> None:
        again = make_khandani_lo_small_caps_whiteboards(
            out_dir=tmp_path, comparison=result, mid=PINNED_MID
        )
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, frames) -> None:
        for name, steps in zip(GIFS, frames, strict=True):
            committed = FIGURES_DIR / name
            with Image.open(committed) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(committed) == [f.ms for f in steps], name

    def test_each_is_a_fresh_draw_byte_for_byte(self, gifs) -> None:
        system, machine, font = platform.system(), platform.machine(), hand_font()
        if (system, machine, font) != ("Darwin", "arm64", "Comic Sans MS"):
            pytest.skip(
                f"the committed GIFs were drawn on Darwin arm64 in Comic Sans MS, and this is "
                f"{system} {machine} drawing in {font}"
            )
        for path in gifs:
            committed = (FIGURES_DIR / path.name).read_bytes()
            assert (
                hashlib.sha256(path.read_bytes()).hexdigest()
                == hashlib.sha256(committed).hexdigest()
            ), f"{path.name}: redraw with: uv run python -m chan.khandani_lo_small_caps_whiteboard"


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        """Lesson 3's right after the paragraph that sets the correlation to 0,
        and Lesson 6's right after the paragraph on the S&P 400's figures."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "On the closes, had the two books been unrelated",
                "Before costs the S&P 400",
            ),
            GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_sketch_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            quoted = [f"“{w}”" for w in scene.labels]
            places = [alt.find(w) for w in quoted]
            assert -1 not in places, [w for w, at in zip(quoted, places, strict=True) if at < 0]
            assert places == sorted(places), scene.slug
            assert alt.endswith("which holds for twelve seconds."), scene.slug

    def test_the_narrowing_alt_text_says_where_the_gap_stands(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "just past the upper band’s right end and well past the lower band’s" in alt

    def test_the_size_order_alt_text_names_each_steps_colour(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        for words in (
            "climbs in green, labelled “2.1973 standard errors”",
            "falls in red, labelled “breaks the order, about one standard error”",
            "then in black to a dot labelled “3.4086”",
            "then climbs in black to a dot labelled “5.3052”",
        ):
            assert words in alt, words


class TestTheCommand:
    def test_it_writes_every_committed_path(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            sketches,
            "make_khandani_lo_small_caps_whiteboards",
            lambda: [FIGURES_DIR / name for name in GIFS],
        )
        main()
        assert capsys.readouterr().out.splitlines() == [
            f"wrote {FIGURES_DIR / name}" for name in GIFS
        ]

    @pytest.mark.parametrize(
        "refusal",
        [ArchiveUnavailable("no archive here"), PanelRefused("a member is missing")],
        ids=["no archive", "panel refused"],
    )
    def test_without_the_archive_it_names_the_gif_it_left(
        self, monkeypatch, refusal, tmp_path
    ) -> None:
        """It draws into a scratch folder, because a draw into the figures
        folder would overwrite the committed GIFs that the byte test compares."""

        def refuse(*args, **kwargs):
            raise refusal

        before = {path.name: path.read_bytes() for path in FIGURES_DIR.glob("*.gif")}
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(mid_caps, "read", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == (
            f"khandani_lo_small_caps_size_order.gif was not redrawn: {refusal}"
        )
        assert sorted(p.name for p in tmp_path.glob("*.gif")) == sorted(set(GIFS) - ARCHIVE_GIFS)
        assert {path.name: path.read_bytes() for path in FIGURES_DIR.glob("*.gif")} == before

    def test_the_archive_slugs_are_the_archive_gifs(self) -> None:
        assert {f"{sketches.GIF_PREFIX}{slug}.gif" for slug in sketches.ARCHIVE_SLUGS} == (
            ARCHIVE_GIFS
        )
