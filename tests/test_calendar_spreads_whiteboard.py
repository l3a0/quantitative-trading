"""The pins for the two whiteboard GIFs in the calendar spreads post.

The first sketch, in Lesson 2, draws natural gas's null counts in each
orientation alone and in both, as circles whose areas and overlap are to
scale. Its figures are :data:`PINNED`, and
``test_the_whiteboard_draws_these_figures`` in
``tests/test_stationary_candidates.py`` holds that the run gives them: the
eight EIA files downloaded 2026-10-02, 1,000 null sets from seed 20261003,
Engle-Granger at one lag on levels against the 10% bar of -3.04. So the tests
here run without the nulls, which take about half a minute.

The second sketch, in Lesson 4, draws the June 2018 natural gas pair's window,
read here through :meth:`OneWindow.read` from the same calendar and files the
run reads. ``tests/test_stationary_candidates.py`` already pins that pair's
window and dropped days.

What is pinned for each:

1. Its words, the exact labels in order, and that each prints its figure.
2. Its inks: black for the circles and lanes, brass for what both
   orientations share and for each closing line, grey for axes and notes, and
   red for the dropped days.
3. Its geometry. Each circle's area and the two circles' shared area stand to
   one scale for their counts, and other figures move them. Each expiry tick,
   lane stretch, dot and cross stands at its trading day.
4. That no label touches a line, leaves the frame or touches another label,
   in the installed hand font and in the wider fallback.
5. Each file's size, frame count, loop and timing, and that it sits in the
   post right after the passage it draws, with alt text quoting its labels.

Two draws on one machine give the same bytes. Whether a committed GIF equals a
fresh draw depends on the font, as ``tests/test_usdcad_tests_whiteboard.py``
explains, so that comparison runs only on macOS arm64 with Comic Sans MS.
"""

from __future__ import annotations

import hashlib
import math
import platform
import re
from datetime import date
from types import SimpleNamespace

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import calendar_spreads_whiteboard as sketches
from chan import stationary_candidates as sc
from chan import usdcad_tests_whiteboard as whiteboard
from chan.calendar_spreads_whiteboard import (
    AREA_PER_PAIR,
    AXIS_Y,
    CIRCLES_Y,
    CROSS,
    FAR_Y,
    KEPT_Y,
    NEAR_Y,
    TICK,
    WINDOW_Y,
    BothOrientations,
    OneWindow,
    Stretch,
    apart,
    day_x,
    gif_name,
    lens_area,
    main,
    make_calendar_spreads_whiteboards,
    radius,
    scenes,
)
from chan.futures import NATURAL_GAS_CONTRACTS, contract_number, month_step, next_trading_day
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    HOLD_MS,
    TITLE_MS,
    WIDTH,
    Frame,
    Label,
    clearances,
    hand_font,
    timeline,
)

POST = REPO_ROOT / "blog" / "calendar-spreads-lessons.md"

#: Every GIF in the order :func:`make_calendar_spreads_whiteboards` writes them.
GIFS = ["calendar_spreads_both_orientations.gif", "calendar_spreads_one_window.gif"]

#: Natural gas's figures, as ``TestTheNullInEachOrientation`` and
#: ``TestTheCalendarSpreadVerdicts`` in ``tests/test_stationary_candidates.py``
#: pin them, on the eight EIA files downloaded 2026-10-02, 1,000 null sets from
#: seed 20261003, both orientations at one lag against the 10% bar of -3.04.
PINNED = BothOrientations(
    pairs=360,
    sets=1000,
    independent_near=38.0,
    independent_far=38.0,
    independent_both=12.0,
    correlated_near=38.0,
    correlated_far=38.0,
    correlated_both=35.0,
    files_near=62,
    files_far=62,
    files_both=57,
)

#: Made-up figures with unequal circles and a half, so a label or a size that
#: should follow the data does. The near circle is the larger in the first
#: panel and the far one in the second.
OTHER = BothOrientations(
    pairs=220,
    sets=500,
    independent_near=30.0,
    independent_far=20.0,
    independent_both=6.5,
    correlated_near=25.0,
    correlated_far=28.0,
    correlated_both=21.5,
    files_near=17,
    files_far=16,
    files_both=14,
)

TITLES = ["What requiring both orientations removes", "One window, four expiries"]

LABELS = [
    [
        "independent walks",
        "near on far: 38",
        "far on near: 38",
        "both: 12",
        "walks correlated as the files are",
        "near on far: 38",
        "far on near: 38",
        "both: 35",
        "medians of 1,000 null sets of 360 natural gas pairs",
        "the files: 62 and 62 alone, 57 both",
    ],
    [
        "Mar expires 26 Feb",
        "Apr expires 27 Mar",
        "May expires 26 Apr",
        "Jun expires 29 May",
        "the window: 64 trading days",
        "June, near",
        "file 3",
        "file 2",
        "file 1",
        "July, far",
        "file 4",
        "file 3",
        "file 2",
        "58 kept",
        "a rule a day off misreads only the crossed days",
    ],
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def window() -> OneWindow:
    return OneWindow.read()


@pytest.fixture(scope="module")
def drawn(window):
    return scenes(PINNED, window)


@pytest.fixture(scope="module")
def frames(drawn):
    return [timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, window):
    return make_calendar_spreads_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), orientations=PINNED, window=window
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _labelled(scene, text, names: str | None = None) -> Label:
    """The one label reading ``text``, naming ``names`` where two read the same."""
    (label,) = [
        s
        for s in scene.steps
        if isinstance(s, Label) and s.text == text and names in (None, s.names)
    ]
    return label


def _circle(stroke) -> tuple[float, float, float]:
    """The centre and radius of a closed circle drawn through equally spaced
    points, from the points less the one that closes it."""
    x, y = stroke.x[:-1], stroke.y[:-1]
    cx, cy = float(x.mean()), float(y.mean())
    return cx, cy, float(np.hypot(x - cx, y - cy).mean())


def _centre(stroke) -> tuple[float, float]:
    """The middle of a stroke's extent, the centre of a circle it traces."""
    return (stroke.x.max() + stroke.x.min()) / 2, (stroke.y.max() + stroke.y.min()) / 2


def _area(stroke) -> float:
    """The area a closed stroke encloses, by the shoelace formula."""
    x, y = stroke.x, stroke.y
    return abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))) / 2


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
    def test_there_are_two_in_the_order_the_post_reads_them(self, drawn) -> None:
        assert [scene.title for scene in drawn] == TITLES

    def test_each_has_its_own_gif_named_for_it(self, drawn) -> None:
        assert [gif_name(scene) for scene in drawn] == GIFS

    def test_each_says_what_it_should(self, drawn) -> None:
        assert [scene.labels for scene in drawn] == LABELS

    def test_every_label_names_a_stroke_drawn_before_it(self, drawn) -> None:
        for scene in drawn:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if not isinstance(s, Label)]
                    assert step.names in earlier, (scene.title, step.text)

    def test_no_label_is_parsed_as_math(self, drawn) -> None:
        assert not [s.text for scene in drawn for s in scene.steps if getattr(s, "math", 0)]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, drawn) -> None:
        for scene in drawn:
            for stroke in scene.strokes:
                assert stroke.points >= stroke.frames, (scene.title, stroke.gid)


class TestBothOrientations:
    """Circles whose areas stand for the counts, overlapping by what both share."""

    @pytest.mark.parametrize("figures", [PINNED, OTHER], ids=["pinned", "other"])
    def test_its_labels_print_its_figures(self, figures, window) -> None:
        scene = scenes(figures, window)[0]

        def count(value: float) -> str:
            return f"{value:.0f}" if value == int(value) else f"{value:.1f}"

        for key in ("independent", "correlated"):
            near, far, both = (getattr(figures, f"{key}_{o}") for o in ("near", "far", "both"))
            _labelled(scene, f"near on far: {count(near)}", f"{key}-near")
            _labelled(scene, f"far on near: {count(far)}", f"{key}-far")
            _labelled(scene, f"both: {count(both)}", f"{key}-both")
        assert scene.labels[-2:] == [
            f"medians of {figures.sets:,} null sets of {figures.pairs} natural gas pairs",
            f"the files: {figures.files_near} and {figures.files_far} alone,"
            f" {figures.files_both} both",
        ]

    @pytest.mark.parametrize("figures", [PINNED, OTHER], ids=["pinned", "other"])
    def test_each_circle_s_area_is_its_count_to_one_scale(self, figures, window) -> None:
        scene = scenes(figures, window)[0]
        for key in ("independent", "correlated"):
            for o in ("near", "far"):
                want = getattr(figures, f"{key}_{o}") * AREA_PER_PAIR
                assert _area(_stroke(scene, f"{key}-{o}")) == pytest.approx(want, rel=0.01)

    @pytest.mark.parametrize("figures", [PINNED, OTHER], ids=["pinned", "other"])
    def test_the_overlap_is_what_both_share_to_the_same_scale(self, figures, window) -> None:
        """The brass outline encloses the area of the pairs rejecting both
        ways, and so does the geometry of the two circles it is drawn from."""
        scene = scenes(figures, window)[0]
        for key in ("independent", "correlated"):
            near, far, both = (getattr(figures, f"{key}_{o}") for o in ("near", "far", "both"))
            assert _area(_stroke(scene, f"{key}-both")) == pytest.approx(
                both * AREA_PER_PAIR, rel=0.01
            )
            d = apart(near, far, both)
            assert lens_area(radius(near), radius(far), d) == pytest.approx(
                both * AREA_PER_PAIR, rel=1e-9
            )

    def test_correlating_the_walks_pulls_the_circles_together(self, drawn) -> None:
        """The same two circles in each panel, 38 and 38, sit far closer once
        the walks correlate, because they share 35 pairs rather than 12."""
        scene = drawn[0]

        def centres(key: str) -> tuple[tuple[float, float], tuple[float, float]]:
            near, far = (
                _circle(_stroke(scene, f"{key}-near")),
                _circle(_stroke(scene, f"{key}-far")),
            )
            return near[:2], far[:2]

        def centres_apart(key: str) -> float:
            near, far = centres(key)
            return near[1] - far[1]

        assert centres_apart("independent") > 5 * centres_apart("correlated") > 0
        for key in ("independent", "correlated"):
            near, far = centres(key)
            assert near[0] == pytest.approx(far[0])
            assert (near[1] + far[1]) / 2 == pytest.approx(CIRCLES_Y)

    @pytest.mark.parametrize("figures", [PINNED, OTHER], ids=["pinned", "other"])
    def test_the_lens_runs_along_each_circle_between_their_crossings(self, figures, window) -> None:
        """Its first half lies on the near circle and its second on the far
        one, every point inside both, and the two halves meet where the
        circles cross, on both of them."""
        scene = scenes(figures, window)[0]
        for key in ("independent", "correlated"):
            lens = _stroke(scene, f"{key}-both")
            near, far = _stroke(scene, f"{key}-near"), _stroke(scene, f"{key}-far")
            (nx, ny, nr), (fx, fy, fr) = _circle(near), _circle(far)
            to_near = np.hypot(lens.x - nx, lens.y - ny)
            to_far = np.hypot(lens.x - fx, lens.y - fy)
            assert np.all(to_near <= nr + 1e-6) and np.all(to_far <= fr + 1e-6), key
            half = (len(lens.x) - 1) // 2
            assert to_near[:half] == pytest.approx(radius(getattr(figures, f"{key}_near")))
            assert to_far[half:-1] == pytest.approx(radius(getattr(figures, f"{key}_far")))
            for k in (0, half - 1, half, -2):
                assert (to_near[k], to_far[k]) == pytest.approx((nr, fr), rel=1e-3), (key, k)

    @pytest.mark.parametrize("figures", [PINNED, OTHER], ids=["pinned", "other"])
    def test_each_both_label_sits_beside_its_overlap(self, figures, window) -> None:
        """At the circles' waist, clear of whichever circle is wider."""
        scene = scenes(figures, window)[0]
        for key in ("independent", "correlated"):
            both = sketches._count(getattr(figures, f"{key}_both"))
            label, lens = _labelled(scene, f"both: {both}"), _stroke(scene, f"{key}-both")
            widest = max(_stroke(scene, f"{key}-{o}").x.max() for o in ("near", "far"))
            assert label.y == CIRCLES_Y
            assert label.x == pytest.approx(widest + sketches.LABEL_GAP, abs=1e-3)
            assert lens.y.min() < CIRCLES_Y < lens.y.max()

    def test_a_median_between_two_pairs_stays_a_half(self) -> None:
        assert sketches._pairs(6.5 / 220, 220) == 6.5
        assert (sketches._count(21.5), sketches._count(38.0)) == ("21.5", "38")

    def test_read_hands_each_null_to_its_own_field(self, monkeypatch) -> None:
        """Every figure differs here, so a swapped or misrouted null shows,
        which the natural gas figures, 38 in all four single orientations,
        cannot."""
        spread = SimpleNamespace(
            tests=[SimpleNamespace(pair=k) for k in range(100)],
            null=np.full(10, 0.07),
            declared_null=np.full(10, 0.03),
            correlation=0.9,
            near_on_far_share=0.21,
            far_on_near_share=0.19,
            share=0.15,
        )
        shares = {(0.0, "near"): 0.11, (0.0, "far"): 0.12, (0.9, "near"): 0.13, (0.9, "far"): 0.14}

        def null_shares(pairs, *, correlation, orientation):
            return np.full(10, shares[correlation, orientation])

        monkeypatch.setattr(sc, "calendar_spread", lambda product: spread)
        monkeypatch.setattr(sc, "null_shares", null_shares)
        want = BothOrientations(100, 10, 11, 12, 3, 13, 14, 7, 21, 19, 15)
        assert BothOrientations.read() == want

    def test_its_inks(self, drawn) -> None:
        scene = drawn[0]
        for key in ("independent", "correlated"):
            assert _stroke(scene, f"{key}-near").color == INK
            assert _stroke(scene, f"{key}-far").color == INK
            assert _stroke(scene, f"{key}-both").color == ACCENT
        colours = {step.text: step.color for step in scene.steps if isinstance(step, Label)}
        assert colours["both: 12"] == colours["both: 35"] == ACCENT
        assert colours["medians of 1,000 null sets of 360 natural gas pairs"] == MUTED
        assert colours["the files: 62 and 62 alone, 57 both"] == ACCENT
        assert colours["near on far: 38"] == colours["far on near: 38"] == INK


class TestOneWindow:
    """The June 2018 natural gas pair, read through the run's own functions."""

    def test_it_reads_the_window_the_run_reads(self, window) -> None:
        assert window.window == sc.spread_window(NATURAL_GAS_CONTRACTS, (2018, 6))
        assert (window.window[0], window.window[-1]) == (date(2018, 2, 27), date(2018, 5, 29))
        assert (len(window.window), len(window.kept)) == (64, 58)
        assert window.kept == sc.spread_pair(NATURAL_GAS_CONTRACTS, (2018, 6)).kept
        assert window.dropped == tuple(sorted(sc.guard_band(NATURAL_GAS_CONTRACTS, (2018, 6))))

    def test_it_rests_on_four_expiries(self, window) -> None:
        assert window.expiries == (
            ((2018, 3), date(2018, 2, 26)),
            ((2018, 4), date(2018, 3, 27)),
            ((2018, 5), date(2018, 4, 26)),
            ((2018, 6), date(2018, 5, 29)),
        )
        assert next_trading_day(window.expiries[0][1]) == window.window[0]
        assert window.expiries[-1][1] == window.window[-1]

    def test_each_leg_moves_up_a_file_the_day_after_each_expiry_inside(self, window) -> None:
        assert window.stretches == (
            Stretch(date(2018, 2, 27), date(2018, 3, 27), 3, 4),
            Stretch(date(2018, 3, 28), date(2018, 4, 26), 2, 3),
            Stretch(date(2018, 4, 27), date(2018, 5, 29), 1, 2),
        )
        inside = [day for _, day in window.expiries[1:3]]
        assert [s.first for s in window.stretches[1:]] == [next_trading_day(d) for d in inside]
        for stretch in window.stretches:
            for day in (stretch.first, stretch.last):
                assert contract_number(day, 2018, 6, NATURAL_GAS_CONTRACTS.last_trade) == (
                    stretch.near_file
                )

    def test_kept_and_dropped_days_split_the_window(self, window) -> None:
        """This pair lacks no file row, so its kept days and its six dropped
        days are the whole window."""
        assert len(window.dropped) == 6
        assert sorted(window.kept + window.dropped) == list(window.window)

    def test_another_pair_moves_the_words(self) -> None:
        other = OneWindow.read(NATURAL_GAS_CONTRACTS, (2023, 6))
        scene = scenes(PINNED, other)[1]
        assert scene.labels[:4] == [
            "Mar expires 24 Feb",
            "Apr expires 29 Mar",
            "May expires 26 Apr",
            "Jun expires 26 May",
        ]
        assert scene.labels[4] == f"the window: {len(other.window)} trading days"
        assert scene.labels[-2] == f"{len(other.kept)} kept"
        assert other.far == month_step(2023, 6, 1)

    def test_each_mark_stands_at_its_trading_day(self, drawn, window) -> None:
        scene = drawn[1]
        for k, (_, day) in enumerate(window.expiries):
            tick = _stroke(scene, f"expiry-{k}")
            assert np.allclose(tick.x, day_x(window, day))
            assert tick.y.min() == AXIS_Y
            assert _labelled(scene, scene.labels[k]).x == pytest.approx(day_x(window, day))
        for leg in ("near", "far"):
            for k, stretch in enumerate(window.stretches):
                lane = _stroke(scene, f"{leg}-{k}")
                assert (lane.x[0], lane.x[-1]) == pytest.approx(
                    (day_x(window, stretch.first), day_x(window, stretch.last))
                )
        kept = _stroke(scene, "kept")
        assert list(kept.x) == pytest.approx([day_x(window, d) for d in window.kept])
        assert np.all(kept.y == KEPT_Y)
        for k, day in enumerate(window.dropped):
            cross = _stroke(scene, f"dropped-{k}")
            assert _centre(cross) == pytest.approx((day_x(window, day), KEPT_Y))
        bracket = _stroke(scene, "window")
        assert (bracket.x.min(), bracket.x.max()) == pytest.approx(
            (day_x(window, window.window[0]), day_x(window, window.window[-1]))
        )

    def test_one_step_a_trading_day(self, window) -> None:
        days = window.window
        steps = np.diff([day_x(window, d) for d in days])
        assert np.allclose(steps, steps[0]) and steps[0] > 0

    def test_each_file_label_sits_over_its_stretch(self, drawn, window) -> None:
        scene = drawn[1]
        files = [s for s in scene.steps if isinstance(s, Label) and s.text.startswith("file ")]
        numbers = [s.near_file for s in window.stretches] + [s.far_file for s in window.stretches]
        assert [f"file {n}" for n in numbers] == [label.text for label in files]
        for label in files:
            lane = _stroke(scene, label.names)
            assert label.x == pytest.approx((lane.x[0] + lane.x[-1]) / 2)
            assert label.y > lane.y[0]

    def test_the_near_lane_sits_above_the_far_one_beside_its_name(self, drawn, window) -> None:
        scene = drawn[1]
        for k in range(len(window.stretches)):
            near, far = _stroke(scene, f"near-{k}"), _stroke(scene, f"far-{k}")
            assert np.all(near.y == NEAR_Y) and np.all(far.y == FAR_Y)
        assert WINDOW_Y > NEAR_Y > FAR_Y > KEPT_Y > AXIS_Y
        assert _labelled(scene, "June, near").y == NEAR_Y
        assert _labelled(scene, "July, far").y == FAR_Y

    def test_each_guide_rises_dashed_from_its_tick_to_the_window(self, drawn, window) -> None:
        scene = drawn[1]
        for k, (_, day) in enumerate(window.expiries):
            guide = _stroke(scene, f"expiry-{k}-guide")
            assert np.allclose(guide.x, day_x(window, day))
            assert guide.dashed
            assert (guide.y.min(), guide.y.max()) == pytest.approx((AXIS_Y + TICK, WINDOW_Y))

    def test_kept_days_are_dots_and_each_cross_has_its_size(self, drawn, window) -> None:
        scene = drawn[1]
        assert _stroke(scene, "kept").dots > 0
        for k in range(len(window.dropped)):
            cross = _stroke(scene, f"dropped-{k}")
            assert cross.x.max() - cross.x.min() == pytest.approx(2 * CROSS)
            assert cross.y.max() - cross.y.min() == pytest.approx(2 * CROSS)

    def test_its_inks(self, drawn, window) -> None:
        scene = drawn[1]
        for label in scene.steps:
            if not isinstance(label, Label) or label.names.startswith("dropped-"):
                continue
            grey = "expires" in label.text or label.text.endswith(" kept")
            assert label.color == (MUTED if grey else INK), label.text
        for stroke in scene.strokes:
            if stroke.gid.startswith("dropped-"):
                assert stroke.color == LOST, stroke.gid
            elif stroke.gid.startswith(("near-", "far-", "window")):
                assert stroke.color == INK, stroke.gid
            else:
                assert stroke.color == MUTED, stroke.gid
        closing = _labelled(scene, "a rule a day off misreads only the crossed days")
        assert closing.color == ACCENT
        assert closing.names == f"dropped-{len(window.dropped) - 1}"
        assert scene.steps[-1] == closing


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, drawn, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            found = clearances(scene)
            assert set(found) == {*scene.labels, scene.title}
            for text, pixels in found.items():
                assert pixels >= CLEAR_PX, (scene.title, text, round(pixels, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_sits_inside_the_board(
        self, drawn, monkeypatch, fallback
    ) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            for text, box in _boxes(scene):
                inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                assert inside >= INSIDE_PX, (scene.title, text, round(inside, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_no_two_labels_touch(self, drawn, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            boxes = _boxes(scene)
            for k, (one, a) in enumerate(boxes):
                for other, b in boxes[k + 1 :]:
                    gap = math.hypot(
                        max(a.x0 - b.x1, b.x0 - a.x1, 0.0), max(a.y0 - b.y1, b.y0 - a.y1, 0.0)
                    )
                    assert gap >= APART_LABELS_PX, (scene.title, one, other, round(gap, 1))


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

    def test_each_opens_on_its_title_and_holds_its_drawing(self, frames) -> None:
        for steps in frames:
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            assert steps[-1].ms == HOLD_MS

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, window) -> None:
        again = make_calendar_spreads_whiteboards(
            out_dir=tmp_path, orientations=PINNED, window=window
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
            ), f"{path.name}: redraw with: uv run python -m chan.calendar_spreads_whiteboard"


class TestThePost:
    def test_the_orientations_sketch_follows_the_figure_s_caption(self) -> None:
        """Right after the histograms' caption and before the lesson's closing
        advice, since it explains the rise those histograms show."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith("*Each histogram is 1,000")]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", paragraphs[index + 1]
        )
        assert paragraphs[index + 2].startswith("Build the null from what the data does")

    def test_the_window_sketch_closes_the_six_days_list(self) -> None:
        """After the two-item list under its heading and before the next heading."""
        text = POST.read_text(encoding="utf-8")
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        (index,) = [
            k for k, p in enumerate(paragraphs) if p == "### The six days each window drops"
        ]
        items = paragraphs[index + 1].splitlines()
        assert [line[:3] for line in items] == ["1. ", "2. "]
        assert items[0].startswith("1. **Each pair rests on four expiries.**")
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[1])}\)", paragraphs[index + 2]
        )
        assert paragraphs[index + 3] == "### The rule checked against the files"

    def test_every_sketch_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, drawn) -> None:
        """A label drawn twice is quoted twice, each after the one before it."""
        text = POST.read_text(encoding="utf-8")
        for scene in drawn:
            alt = _alt(text, scene)
            at = 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + 1

    def test_the_orientations_alt_text_says_what_the_circles_show(self, drawn) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), drawn[0])
        assert "“near on far: 38” above a black circle labelled “far on near: 38”" in alt
        assert round(3 * PINNED.independent_both / PINNED.independent_near) == 1
        assert "about a third of each circle" in alt
        assert "each circle’s area to scale" in alt
        assert "almost on top of each other" in alt

    def test_the_window_alt_text_names_the_crossed_days(self, drawn, window) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), drawn[1])
        words = {3: "three", 4: "Four"}
        start = window.window[0]
        assert f"from late {start:%B} to late" in alt and start.day > 20
        assert f"{words[len(window.expiries)]} grey ticks with dashed guides" in alt
        assert f"breaks into {words[len(window.stretches)]} stretches" in alt
        assert "a new one starting the day after each expiry inside the window" in alt
        assert "Beneath it a lane labelled “July, far”" in alt
        assert f"{ {6: 'six'}[len(window.dropped)] } red crosses" in alt
        assert "on each expiry inside it and the day after" in alt
        assert f"late May {window.window[-1].year}" in alt


class TestTheCommand:
    def test_it_writes_every_committed_path(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            sketches,
            "make_calendar_spreads_whiteboards",
            lambda: [FIGURES_DIR / name for name in GIFS],
        )
        main()
        assert capsys.readouterr().out.splitlines() == [
            f"wrote {FIGURES_DIR / name}" for name in GIFS
        ]

    def test_handed_nothing_it_reads_both_figure_classes(self, monkeypatch, gifs, tmp_path) -> None:
        """A redraw reads the orientations from the run, stood in for here by
        the pinned figures, and the window from the files, and draws what the
        figures handed in draw."""
        read = []

        def orientations(cls):
            read.append(cls)
            return PINNED

        monkeypatch.setattr(BothOrientations, "read", classmethod(orientations))
        paths = make_calendar_spreads_whiteboards(out_dir=tmp_path)
        assert read == [BothOrientations]
        for path, drawn in zip(paths, gifs, strict=True):
            assert path.read_bytes() == drawn.read_bytes(), path.name
