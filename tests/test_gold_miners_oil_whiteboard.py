"""The pins for the two whiteboard GIFs in the gold miners and oil post.

One sketches how the Johansen trace test reaches its count on GLD, GDX and
USO over the whole span: the first hypothesis rejected, the second not, and
the count stopping there at one relation. The other sketches Lesson 3's
three pairs and the zero-weight tests: the one relation could be the miners
and oil pair's own by its count, and the weights say it needs gold.

Neither sketch is schematic.

1. The counting sketch's figures come from
   :class:`chan.gold_miners_oil_whiteboard.CountingStop`, which reads the
   triplet's test in :mod:`chan.gold_miners_oil` on the committed vintage.
   What is pinned is each figure it prints, that the two columns and the two
   dashed bars stand at one affine function of their values on one floor,
   that the third slot is drawn as an empty dotted outline whose figure is
   never printed, that a made-up set of figures moves the words with them,
   and that figures which would make its words false are refused.
2. The three-pairs sketch's figures come from
   :class:`chan.gold_miners_oil_whiteboard.PairsAndWeights`, read from the
   same run's control, its two pairs with USO and its zero-weight tests. What
   is pinned is each figure it prints, that each edge joins the two funds it
   names and is dashed red for none or solid green for one, that each weight
   note names its fund's dot, that a made-up set moves the words, and that
   figures which would make its words false are refused. Its triangle's shape
   carries no figure, so no test reads one off it.

The run reads committed vintages, so the tests read it directly rather than a
frozen copy of its figures. ``tests/test_gold_miners_oil.py`` holds the same
statistics on its own derivation.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, both
sketches' slower pace, that two draws give the same bytes, and that each
committed GIF is a fresh draw, a comparison that runs only on macOS arm64 with
Comic Sans MS, as ``tests/test_usdcad_tests_whiteboard.py`` explains. The
check that ``docs/figures`` holds exactly the GIFs the modules draw lives in
``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS` from
here.
"""

from __future__ import annotations

import hashlib
import math
import platform
import re
from dataclasses import replace

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import gold_miners_oil
from chan import gold_miners_oil_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.gold_miners_oil_whiteboard import (
    FLOOR,
    FUNDS,
    HALF,
    NOTES_X,
    OUTLINE_TOP,
    SLOTS,
    TRIM,
    CountingStop,
    CountRefused,
    PairsAndWeights,
    PairsRefused,
    gif_name,
    main,
    make_gold_miners_oil_whiteboards,
    scenes,
    sketch_timeline,
    up,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
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

POST = REPO_ROOT / "blog" / "gold-miners-oil-lessons.md"

#: Every GIF in the order :func:`make_gold_miners_oil_whiteboards` writes them.
GIFS = ["gold_miners_oil_sketch_counting.gif", "gold_miners_oil_sketch_three_pairs.gif"]

#: What each GIF follows and what comes after it: Lesson 1's list, keyed on
#: its last item's opening, and Lesson 3's paragraph on gold and oil alone.
TRIPLET_ITEM = "3. **The three funds, exactly one.**"
NEXT_PARAGRAPH = "The nearest call is the first"
PAIRS_PARAGRAPH = "Gold and oil alone find nothing"
WEIGHTS_PARAGRAPH = "The triplet’s weights can."

COUNTING_LABELS = [
    "r ≤ 0",
    "r ≤ 1",
    "r ≤ 2",
    "44.838",
    "99% bar, 35.463",
    "rejected: go on",
    "7.005",
    "99% bar, 19.935",
    "not rejected: stop",
    "short even of the\n90% bar, 13.429",
    "not read:\nthe count stopped",
    "count: 1 relation",
]

PAIRS_LABELS = [
    "GLD",
    "GDX",
    "USO",
    "three funds,\none relation",
    "10.447: none",
    "4.350: none",
    "27.166: one at 99%",
    "pair bar at 99%: 19.935",
    "a count of one cannot\nsay which pair it is",
    "GLD’s weight 0?\n10.015: rejected at 95%",
    "USO’s weight 0?\n0.057: not rejected",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def stop() -> CountingStop:
    return CountingStop.read()


@pytest.fixture(scope="module")
def pairs() -> PairsAndWeights:
    return PairsAndWeights.read()


@pytest.fixture(scope="module")
def every(stop, pairs):
    return scenes(stop, pairs)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_gold_miners_oil_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


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


def _paragraphs() -> list[str]:
    return [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

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
        """Neither sketch draws a tint today. One that does would need the
        green edge the equity seasonals module's ``_tinted`` draws, since the
        tint alone stands 1.29 to 1 against the board."""
        tints = [fill for scene in every for fill in scene.fills if fill.color == whiteboard.TINT]
        assert tints == []


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


class TestTheGifs:
    def test_there_is_one_named_for_each_scene(self, gifs) -> None:
        assert [path.name for path in gifs] == GIFS

    def test_each_is_680_by_320_and_loops_forever(self, gifs, every) -> None:
        for path, scene in zip(gifs, every, strict=True):
            steps = sketch_timeline(scene)
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(path) == [f.ms for f in steps], path.name

    def test_each_opens_on_its_title_and_holds_its_drawing(self, every) -> None:
        for scene in every:
            steps = sketch_timeline(scene)
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            hold = sketches.PACED_HOLD_MS if scene.slug in sketches.PACED else HOLD_MS
            assert steps[-1].ms == hold, scene.slug

    def test_both_build_slowly_and_hold_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("counting", "three_pairs")
        for scene in every:
            frames = sketch_timeline(scene)
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            assert labels, scene.slug
            assert {f.ms for f in labels} == {sketches.PACED_LABEL_MS}, scene.slug
            assert frames[-1].ms == sketches.PACED_HOLD_MS
            assert [(f.done, f.partial) for f in frames] == [
                (f.done, f.partial) for f in timeline(scene)
            ]

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_gold_miners_oil_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        """No chart starts like these, so the prefix check above reads only
        this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert "gold_miners_oil_break.png" in names

    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, every) -> None:
        for name, scene in zip(GIFS, every, strict=True):
            steps = sketch_timeline(scene)
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
            ), f"{path.name}: redraw with: uv run python -m chan.gold_miners_oil_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_it_follows_lesson_1s_list_and_comes_before_the_nearest_call(self) -> None:
        """Right after the list whose last item is the three funds' count, and
        before the paragraph on the nearest call."""
        paragraphs = _paragraphs()
        (index,) = [
            k
            for k, p in enumerate(paragraphs)
            if any(line.startswith(TRIPLET_ITEM) for line in p.splitlines())
        ]
        assert paragraphs[index].splitlines()[-1].startswith(TRIPLET_ITEM)
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", paragraphs[index + 1]
        )
        assert paragraphs[index + 2].startswith(NEXT_PARAGRAPH)

    def test_the_pairs_sketch_follows_gold_and_oil_alone(self) -> None:
        """Right after the paragraph on gold and oil alone, and before the one
        on the triplet's weights."""
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(PAIRS_PARAGRAPH)]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[1])}\)", paragraphs[index + 1]
        )
        assert paragraphs[index + 2].startswith(WEIGHTS_PARAGRAPH)

    def test_the_counting_sketch_sits_in_lesson_1_and_the_pairs_in_lesson_3(self) -> None:
        text = POST.read_text(encoding="utf-8")
        counting, pairs_at = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lesson_1, lesson_2 = text.index("## Lesson 1:"), text.index("## Lesson 2:")
        lesson_3, lesson_4 = text.index("## Lesson 3:"), text.index("## Lesson 4:")
        assert lesson_1 < counting < lesson_2 < lesson_3 < pairs_at < lesson_4

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Each label is quoted after the one drawn before it, with a line
        break in a label read as a space."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                quoted = f"“{label.replace(chr(10), ' ')}”"
                found = alt.find(quoted, at)
                assert found >= 0, (scene.slug, label)
                at = found + len(quoted)

    def test_its_alt_text_says_it_is_slow_and_drawn_to_scale(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "schematic" not in alt
        assert "drawn to one scale from the run" in alt
        assert "drawn slowly" in alt
        assert "twelve seconds" in alt

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "A grey floor runs across the board with three slots under it" in alt
        assert "Over the first slot a tall black column" in alt
        assert "a dashed line crosses it below its top" in alt
        assert "A green check follows" in alt
        assert "A grey arrow leads to the second slot" in alt
        assert "a short black column" in alt and "well under a dashed line" in alt
        assert "Red words say" in alt and "a red note says" in alt
        assert "Over the third slot a grey dotted outline stands empty" in alt
        assert "The closing words, top right, read" in alt
        scene = every[0]
        first, second = _stroke(scene, "column-1"), _stroke(scene, "column-2")
        bar_1, bar_2 = _stroke(scene, "bar-1"), _stroke(scene, "bar-2")
        assert bar_1.y[0] < first.y.max() and second.y.max() < bar_2.y[0]
        assert first.y.max() > 2 * second.y.max() - FLOOR

    def test_the_footer_links_the_sketch_and_its_tests(self) -> None:
        footer = _paragraphs()[-1]
        assert footer.startswith("*Not investment advice.")
        for path in (
            "src/chan/gold_miners_oil_whiteboard.py",
            "tests/test_gold_miners_oil_whiteboard.py",
        ):
            assert f"/blob/main/{path})" in footer, path
        assert "[the whiteboard sketches](" in footer
        assert "[what the sketches draw](" in footer

    def test_the_module_says_it_is_not_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "Neither sketch is schematic" in doc
        assert "Its triangle's shape and the lengths of its edges carry no figure" in doc
        assert (
            "The dotted outline over the third slot is the one mark whose height is not a figure"
            in doc
        )


# --- Counting stops at the first no -------------------------------------------


class TestTheCountingSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "Counting stops at the first no"
        assert every[0].labels == COUNTING_LABELS

    def test_the_run_gives_the_figures_it_prints(self, stop: CountingStop) -> None:
        """The triplet's trace test at 99 percent, the figures
        ``tests/test_gold_miners_oil.py`` pins on its own derivation."""
        assert [f"{v:.3f}" for v in (stop.first, stop.first_bar)] == ["44.838", "35.463"]
        assert [f"{v:.3f}" for v in (stop.second, stop.second_bar)] == ["7.005", "19.935"]
        assert f"{stop.second_bar_90:.3f}" == "13.429"
        assert f"{stop.unread:.3f}" == "0.164"
        assert stop.count == 1

    def test_it_reads_the_triplets_trace_test(self, stop: CountingStop) -> None:
        _, closes = gold_miners_oil.read_sources()
        triplet = gold_miners_oil.gold_miners_oil(closes).triplet
        assert (stop.first, stop.second, stop.unread) == tuple(float(v) for v in triplet.trace)
        assert (stop.first_bar, stop.second_bar) == tuple(
            float(v) for v in triplet.trace_critical[:2, 2]
        )
        assert stop.second_bar_90 == float(triplet.trace_critical[1, 0])
        assert stop.count == triplet.relations("trace", 99)

    def test_its_count_is_the_trace_tests_at_99_percent(self) -> None:
        """On a run where the eigen statistic finds nothing and the 95 percent
        bars cannot be cleared, the count is still the trace test's at 99."""
        _, closes = gold_miners_oil.read_sources()
        result = gold_miners_oil.gold_miners_oil(closes)
        bars = result.triplet.trace_critical.copy()
        bars[:, 1] = 1e9
        triplet = replace(
            result.triplet, eigen=np.zeros_like(result.triplet.eigen), trace_critical=bars
        )
        assert CountingStop.from_run(replace(result, triplet=triplet)).count == 1

    def test_the_unread_statistic_is_never_printed(self, every, stop) -> None:
        """The test computes it, but the count stops before it, so no label
        carries it."""
        for places in (1, 2, 3, 4):
            printed = f"{stop.unread:.{places}f}"
            assert not [t for t in every[0].labels if printed in t], printed

    def test_its_colours(self, every) -> None:
        """Green for the rejection, red for the stop, grey for context, and
        black for the figures."""
        scene = every[0]
        strokes = {
            "floor": MUTED,
            "column-1": INK,
            "bar-1": INK,
            "check": GOOD,
            "on": MUTED,
            "column-2": INK,
            "bar-2": INK,
            "unread": MUTED,
        }
        assert {s.gid: s.color for s in scene.strokes} == strokes
        colours = dict.fromkeys(COUNTING_LABELS[:3], MUTED) | {
            "44.838": INK,
            "99% bar, 35.463": INK,
            "rejected: go on": GOOD,
            "7.005": INK,
            "99% bar, 19.935": INK,
            "not rejected: stop": LOST,
            "short even of the\n90% bar, 13.429": LOST,
            "not read:\nthe count stopped": MUTED,
            "count: 1 relation": INK,
        }
        assert {s.text: s.color for s in scene.steps if isinstance(s, Label)} == colours

    def test_colour_is_never_the_only_cue(self, every) -> None:
        """The green rejection and the red stop each carry their own words,
        and the rejection a check mark too."""
        scene = every[0]
        assert "not" not in _label(scene, "rejected: go on").text
        assert _label(scene, "not rejected: stop").text.startswith("not ")
        check = _stroke(scene, "check")
        assert len(set(np.round(check.y, 6))) > 2

    def test_the_columns_and_bars_stand_to_one_scale(self, every, stop) -> None:
        """Each column's top and each dashed bar's height is one affine
        function of its value, on one floor."""
        scene = every[0]
        heights = np.array(
            [
                _stroke(scene, "column-1").y.max(),
                _stroke(scene, "column-2").y.max(),
                *(set(_stroke(scene, g).y).pop() for g in ("bar-1", "bar-2")),
            ]
        )
        values = np.array([stop.first, stop.second, stop.first_bar, stop.second_bar])
        slope, intercept = np.polyfit(values, heights, 1)
        assert heights == pytest.approx(intercept + slope * values, abs=1e-9)
        assert intercept == pytest.approx(FLOOR) and slope > 0
        for gid in ("bar-1", "bar-2"):
            assert len(set(_stroke(scene, gid).y)) == 1, gid
        for gid in ("column-1", "column-2"):
            assert _stroke(scene, gid).y.min() == pytest.approx(FLOOR), gid
        assert set(_stroke(scene, "floor").y) == {FLOOR}

    def test_each_column_bar_and_figure_sits_over_its_slot(self, every) -> None:
        scene = every[0]
        for k, (column, bar, figure) in enumerate(
            (("column-1", "bar-1", "44.838"), ("column-2", "bar-2", "7.005"))
        ):
            box, line = _stroke(scene, column), _stroke(scene, bar)
            assert (box.x.min(), box.x.max()) == pytest.approx((SLOTS[k] - HALF, SLOTS[k] + HALF))
            assert line.x.min() < box.x.min() and box.x.max() < line.x.max(), bar
            assert _label(scene, figure).x == SLOTS[k], figure
            assert _label(scene, COUNTING_LABELS[k]).x == SLOTS[k]
        assert _label(scene, "r ≤ 2").x == SLOTS[2]
        assert SLOTS[0] < SLOTS[1] < SLOTS[2]

    def test_the_first_figure_sits_inside_its_column_and_the_second_above(self, every) -> None:
        scene = every[0]
        first, second = _stroke(scene, "column-1"), _stroke(scene, "column-2")
        assert FLOOR < _label(scene, "44.838").y < first.y.max()
        assert _label(scene, "7.005").y > second.y.max()

    def test_the_arrow_leads_from_the_first_slot_to_the_second(self, every) -> None:
        scene = every[0]
        arrow = _stroke(scene, "on")
        assert arrow.x[0] > _stroke(scene, "column-1").x.max()
        assert arrow.x.max() < _stroke(scene, "column-2").x.min()
        assert arrow.x.argmax() > 0

    def test_the_third_slot_is_an_empty_dotted_outline(self, every) -> None:
        """Dots with no line, over the third slot, at a height that is not a
        figure, and nothing else drawn there."""
        scene = every[0]
        outline = _stroke(scene, "unread")
        assert outline.dots > 0 and not outline.dashed
        assert (outline.x.min(), outline.x.max()) == pytest.approx(
            (SLOTS[2] - HALF, SLOTS[2] + HALF)
        )
        assert (outline.y.min(), outline.y.max()) == pytest.approx((FLOOR, OUTLINE_TOP))
        over = [
            s.gid
            for s in scene.strokes
            if s.gid != "floor" and (s.x >= SLOTS[2] - HALF - 0.01).any()
        ]
        assert over == ["unread"]

    def test_it_is_drawn_in_the_order_the_count_runs(self, every) -> None:
        order = [s.gid for s in every[0].strokes]
        assert order == ["floor", "column-1", "bar-1", "check", "on", "column-2", "bar-2", "unread"]
        assert every[0].steps[-1].text == "count: 1 relation"

    def test_its_words_follow_made_up_figures(self, stop, pairs) -> None:
        """Other statistics print their own figures and stand at their own
        heights on the same scale."""
        made_up = replace(
            stop,
            first=40.5,
            second=10.25,
            first_bar=30.125,
            second_bar=18.0,
            second_bar_90=12.5,
            unread=1.0,
        )
        scene = scenes(made_up, pairs)[0]
        assert scene.labels == [
            "r ≤ 0",
            "r ≤ 1",
            "r ≤ 2",
            "40.500",
            "99% bar, 30.125",
            "rejected: go on",
            "10.250",
            "99% bar, 18.000",
            "not rejected: stop",
            "short even of the\n90% bar, 12.500",
            "not read:\nthe count stopped",
            "count: 1 relation",
        ]
        assert _stroke(scene, "column-1").y.max() == pytest.approx(up(40.5))
        assert _stroke(scene, "column-2").y.max() == pytest.approx(up(10.25))
        assert set(_stroke(scene, "bar-2").y) == {up(18.0)}

    @pytest.mark.parametrize(
        ("change", "message"),
        [
            ({"first": 30.0}, "does not clear"),
            ({"second": 20.0}, "clears 19"),
            ({"second": 14.0}, "clears its 90% bar"),
            ({"count": 2}, "the count is 2"),
            ({"count": 0}, "the count is 0"),
        ],
        ids=["first not rejected", "second rejected", "second past 90", "two", "none"],
    )
    def test_it_refuses_figures_that_make_its_words_false(self, stop, change, message) -> None:
        with pytest.raises(CountRefused, match=message):
            replace(stop, **change)

    def test_it_reads_the_file_through_the_scale_break_guard(self, monkeypatch) -> None:
        """Not a second read path that skips the guard ``python -m
        chan.gold_miners_oil`` runs."""

        def refuse(*args, **kwargs):
            raise RuntimeError("guard ran")

        monkeypatch.setattr(gold_miners_oil, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(RuntimeError, match="guard ran"):
            CountingStop.read()


# --- Lesson 3: one relation, three pairs ----------------------------------------


class TestThePairsSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "One relation, three pairs"
        assert every[1].labels == PAIRS_LABELS

    def test_the_run_gives_the_figures_it_prints(self, pairs: PairsAndWeights) -> None:
        """The control, the two pairs with USO and the zero-weight tests,
        which ``tests/test_gold_miners_oil.py`` pins on its own derivation."""
        assert [f"{v:.3f}" for v in (pairs.gld_gdx, pairs.gld_uso, pairs.gdx_uso)] == [
            "10.447",
            "4.350",
            "27.166",
        ]
        # GDX and USO reach full rank at 90 percent, the post's first detail
        # in Lesson 3, which is why the edge says "one at 99%" and not "one".
        assert pairs.counts == {"gld_gdx": (0, 0), "gld_uso": (0, 0), "gdx_uso": (2, 1)}
        assert f"{pairs.pair_bar:.3f}" == "19.935"
        assert pairs.triplet_count == 1
        assert [f"{v:.3f}" for v in (pairs.gld_weight, pairs.uso_weight)] == ["10.015", "0.057"]
        assert [f"{v:.3f}" for v in (pairs.weight_bar, pairs.weight_bar_90)] == ["3.841", "2.706"]

    def test_it_reads_each_pair_and_weight_from_the_run(self, pairs: PairsAndWeights) -> None:
        _, closes = gold_miners_oil.read_sources()
        result = gold_miners_oil.gold_miners_oil(closes)
        assert pairs.gld_gdx == float(result.control.trace[0])
        assert pairs.gld_uso == float(result.with_oil["GLD"].trace[0])
        assert pairs.gdx_uso == float(result.with_oil["GDX"].trace[0])
        assert pairs.pair_bar == float(result.control.trace_critical[0, 2])
        assert pairs.gld_weight == result.zero_weight["GLD"]
        assert pairs.uso_weight == result.zero_weight["USO"]
        assert pairs.weight_bar == gold_miners_oil.CHI2_1[95]
        assert pairs.weight_bar_90 == gold_miners_oil.CHI2_1[90]

    def test_it_never_says_rejected_at_99(self, every) -> None:
        """The post reads GLD's rejection at 95 percent, since the large-sample
        bars reject too often on this sample."""
        weights = [t for t in every[1].labels if "weight" in t]
        assert len(weights) == 2
        assert not [t for t in weights if "99" in t]

    def test_its_colours(self, every) -> None:
        """Red dashed for none, green solid for one, black for the funds, grey
        for context and brown for the point."""
        scene = every[1]
        assert {s.gid: (s.color, s.dashed) for s in scene.strokes} == {
            "gld": (INK, False),
            "gdx": (INK, False),
            "uso": (INK, False),
            "gld-gdx": (LOST, True),
            "gld-uso": (LOST, True),
            "gdx-uso": (GOOD, False),
        }
        assert {s.text: s.color for s in scene.steps if isinstance(s, Label)} == {
            "GLD": INK,
            "GDX": INK,
            "USO": INK,
            "three funds,\none relation": MUTED,
            "10.447: none": LOST,
            "4.350: none": LOST,
            "27.166: one at 99%": GOOD,
            "pair bar at 99%: 19.935": MUTED,
            "a count of one cannot\nsay which pair it is": ACCENT,
            "GLD’s weight 0?\n10.015: rejected at 95%": GOOD,
            "USO’s weight 0?\n0.057: not rejected": LOST,
        }

    def test_colour_is_never_the_only_cue(self, every) -> None:
        """Each edge says none or one in words and is dashed or solid, and
        each weight note says rejected or not rejected."""
        scene = every[1]
        for gid in ("gld-gdx", "gld-uso", "gdx-uso"):
            edge = _stroke(scene, gid)
            words = [
                label.text
                for label in scene.steps
                if isinstance(label, Label) and label.names == gid
            ]
            text = words[0]
            assert edge.dashed == text.endswith(": none"), gid
            assert edge.dashed != text.endswith(": one at 99%"), gid
        assert _label(scene, "GLD’s weight 0?\n10.015: rejected at 95%").text.endswith(
            ": rejected at 95%"
        )
        assert _label(scene, "USO’s weight 0?\n0.057: not rejected").text.endswith(": not rejected")

    def test_each_edge_joins_the_funds_it_names(self, every) -> None:
        """An edge runs between its two dots, stopping short of each by the
        same trim."""
        scene = every[1]
        for name in FUNDS:
            dot = _stroke(scene, name)
            assert (dot.x.tolist(), dot.y.tolist()) == ([FUNDS[name][0]], [FUNDS[name][1]]), name
        for gid in ("gld-gdx", "gld-uso", "gdx-uso"):
            one, other = gid.split("-")
            edge = _stroke(scene, gid)
            start, end = np.array([edge.x[0], edge.y[0]]), np.array([edge.x[-1], edge.y[-1]])
            a, b = np.array(FUNDS[one]), np.array(FUNDS[other])
            assert np.linalg.norm(start - a) == pytest.approx(TRIM), gid
            assert np.linalg.norm(end - b) == pytest.approx(TRIM), gid
            direction = (b - a) / np.linalg.norm(b - a)
            for x, y in zip(edge.x, edge.y, strict=True):
                offset = np.array([x, y]) - a
                assert abs(offset[0] * direction[1] - offset[1] * direction[0]) < 1e-9, gid

    def test_gld_sits_at_the_top_and_the_others_below_it(self, every) -> None:
        scene = every[1]
        (gx, gy), (dx, dy), (ux, uy) = FUNDS["gld"], FUNDS["gdx"], FUNDS["uso"]
        assert dy == uy < gy and dx < gx < ux
        assert _label(scene, "GLD").y > gy
        assert _label(scene, "GDX").y < dy and _label(scene, "USO").y < uy
        inside = _label(scene, "three funds,\none relation")
        assert dy < inside.y < gy and dx < inside.x < ux

    def test_each_edge_label_sits_beside_its_edge(self, every) -> None:
        scene = every[1]
        (gx, _), (dx, dy), (ux, _) = FUNDS["gld"], FUNDS["gdx"], FUNDS["uso"]
        assert _label(scene, "10.447: none").x < (gx + dx) / 2
        assert _label(scene, "4.350: none").x > (gx + ux) / 2
        bottom = _label(scene, "27.166: one at 99%")
        assert bottom.y < dy and dx < bottom.x < ux

    def test_each_weight_note_names_its_funds_dot(self, every) -> None:
        scene = every[1]
        assert _label(scene, "GLD’s weight 0?\n10.015: rejected at 95%").names == "gld"
        assert _label(scene, "USO’s weight 0?\n0.057: not rejected").names == "uso"
        notes = [s for s in scene.steps if isinstance(s, Label) and s.x == NOTES_X]
        assert [s.text for s in notes] == PAIRS_LABELS[7:]
        assert NOTES_X > max(x for x, _ in FUNDS.values())

    def test_it_is_drawn_in_the_post_s_order(self, every) -> None:
        """The funds, the two pairs that find none, the pair that finds one,
        then the bar, the point and the weights."""
        assert [s.gid for s in every[1].strokes] == [
            "gld",
            "gdx",
            "uso",
            "gld-gdx",
            "gld-uso",
            "gdx-uso",
        ]
        assert every[1].labels[-2:] == PAIRS_LABELS[-2:]

    def test_its_words_follow_made_up_figures(self, pairs, stop) -> None:
        made_up = replace(
            pairs,
            gld_gdx=8.25,
            gld_uso=3.5,
            gdx_uso=30.125,
            pair_bar=20.5,
            gld_weight=12.75,
            uso_weight=0.5,
        )
        assert scenes(stop, made_up)[1].labels == [
            "GLD",
            "GDX",
            "USO",
            "three funds,\none relation",
            "8.250: none",
            "3.500: none",
            "30.125: one at 99%",
            "pair bar at 99%: 20.500",
            "a count of one cannot\nsay which pair it is",
            "GLD’s weight 0?\n12.750: rejected at 95%",
            "USO’s weight 0?\n0.500: not rejected",
        ]

    @pytest.mark.parametrize(
        ("change", "message"),
        [
            ({"triplet_count": 2}, "the triplet finds 2"),
            ({"counts": {"gld_gdx": (1, 0), "gld_uso": (0, 0), "gdx_uso": (1, 1)}}, "gld_gdx"),
            ({"counts": {"gld_gdx": (0, 0), "gld_uso": (0, 1), "gdx_uso": (1, 1)}}, "gld_uso"),
            ({"counts": {"gld_gdx": (0, 0), "gld_uso": (0, 0), "gdx_uso": (1, 0)}}, "gdx_uso"),
            ({"triplet_count": 0}, "the triplet finds 0"),
            ({"counts": {"gld_gdx": (0, 0), "gld_uso": (0, 0), "gdx_uso": (2, 2)}}, "gdx_uso"),
            ({"gld_weight": 3.0}, "does not clear"),
            ({"uso_weight": 3.0}, "USO's weight"),
        ],
        ids=[
            "two relations",
            "gold and miners",
            "gold and oil",
            "miners and oil",
            "no relation",
            "miners and oil twice",
            "gold",
            "oil",
        ],
    )
    def test_it_refuses_figures_that_make_its_words_false(self, pairs, change, message) -> None:
        with pytest.raises(PairsRefused, match=message):
            replace(pairs, **change)

    def test_it_refuses_pairs_whose_bars_differ(self) -> None:
        _, closes = gold_miners_oil.read_sources()
        result = gold_miners_oil.gold_miners_oil(closes)
        control = replace(result.control, trace_critical=result.control.trace_critical + 1.0)
        with pytest.raises(PairsRefused, match="bars differ"):
            PairsAndWeights.from_run(replace(result, control=control))

    def test_its_counts_are_the_trace_tests(self) -> None:
        """On a run where every pair's eigen statistic finds nothing, the
        counts are still the trace test's."""
        _, closes = gold_miners_oil.read_sources()
        result = gold_miners_oil.gold_miners_oil(closes)
        quiet = {k: replace(t, eigen=np.zeros_like(t.eigen)) for k, t in result.with_oil.items()}
        control = replace(result.control, eigen=np.zeros_like(result.control.eigen))
        found = PairsAndWeights.from_run(replace(result, control=control, with_oil=quiet))
        assert found.counts == {"gld_gdx": (0, 0), "gld_uso": (0, 0), "gdx_uso": (2, 1)}

    def test_the_notes_run_down_the_right_in_drawing_order(self, every) -> None:
        """The alt text reads the bar and the point, then "below them" the
        two weight notes, so each note sits under the one drawn before it."""
        notes = [s for s in every[1].steps if isinstance(s, Label) and s.x == NOTES_X]
        heights = [s.y for s in notes]
        assert heights == sorted(heights, reverse=True)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "“GLD” at the top, “GDX” bottom left and “USO” bottom right" in alt
        assert "with grey words inside" in alt
        assert "On the right a grey note" in alt and "Below them a green note" in alt
        assert "schematic" not in alt
        assert "carrying figures from the run" in alt
        assert "drawn slowly" in alt and "twelve seconds" in alt
        assert "Three black dots form a triangle" in alt
        assert "A red dashed edge joins GLD and GDX" in alt
        assert "a red dashed edge joins GLD and USO" in alt
        assert "A green solid edge joins GDX and USO along the bottom" in alt
        assert "a grey note" in alt and "brown words" in alt
        assert "a green note reads “GLD’s" in alt and "a red note reads “USO’s" in alt

    def test_it_reads_the_file_through_the_scale_break_guard(self, monkeypatch) -> None:
        def refuse(*args, **kwargs):
            raise RuntimeError("guard ran")

        monkeypatch.setattr(gold_miners_oil, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(RuntimeError, match="guard ran"):
            PairsAndWeights.read()
