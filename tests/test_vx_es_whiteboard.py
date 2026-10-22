"""The pins for the two whiteboard GIFs in the VX against ES post.

One sketches Lesson 2's point that one shift slides a fit without tilting it,
and one Lesson 3's two exits. Both are schematic: their dots, shifts and path
are made up, so no test here reads a figure off them. What is pinned is what a
reader takes from them, and that the facts they draw hold on the run.

1. The shift sketch draws one save's falling dots and their fit, the same dots
   moved right by one amount with a fit of the same slope, and the same dots
   moved by uneven amounts with a fit whose slope differs by about a quarter,
   exaggerated so the eye can see it. Each line is the least-squares fit of its own dots.
   test_one_constant_on_every_vx_close_moves_only_the_intercept holds the fact
   behind it on the 2012-05-07 save: the hedge, the deviation and the z-score
   do not move.
2. The exits sketch draws a z-score path against the band and two strips
   beneath it. What is pinned is that each strip holds what
   :func:`chan.vx_es.opposite_band_units` and :func:`chan.vx_es.mean_exit_units`
   hold along the drawn path, that each flat stretch starts where the path
   crosses zero and ends where it reaches the next band, and that the flat
   stretches are short beside the held ones, as the mean exit starts 77 of the
   run's 449 test days with no position.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, both
sketches' slower pace, that two draws give the same bytes, and that each
committed GIF is a fresh draw, a comparison that runs only on macOS arm64
with Comic Sans MS, as ``tests/test_usdcad_tests_whiteboard.py`` explains.
The check that ``docs/figures`` holds exactly the GIFs the modules draw lives
in ``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS`
from here.
"""

from __future__ import annotations

import hashlib
import math
import platform
import re

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import usdcad_tests_whiteboard as whiteboard
from chan import vx_es
from chan import vx_es_whiteboard as sketches
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
from chan.vx_es_whiteboard import (
    CROSSINGS,
    KNOTS,
    ORIGIN,
    PATH_X,
    SAME,
    SAVE_X,
    SAVE_Y,
    UNEVEN,
    fit,
    gif_name,
    main,
    make_vx_es_whiteboards,
    scenes,
    sketch_timeline,
    z_y,
)

POST = REPO_ROOT / "blog" / "vx-es-lessons.md"

#: Every GIF in the order :func:`make_vx_es_whiteboards` writes them.
GIFS = ["vx_es_sketch_one_shift.gif", "vx_es_sketch_two_exits.gif"]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "[The post on GLD and GDX]",
    "Chan’s script for Example 3.2, `bollinger.m`, closes each position",
)

SHIFT_LABELS = [
    "1000·VX",
    "50·ES",
    "one save",
    "every close + the same amount: same slope",
    "uneven shifts: a different slope",
]

EXITS_LABELS = [
    "+1",
    "0",
    "−1",
    "hold until the opposite band (this run)",
    "long",
    "short",
    "long",
    "close at the mean (bollinger.m)",
    "long",
    "flat",
    "short",
    "flat",
    "long",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def every():
    return scenes()


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_vx_es_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels_of(scene, gid):
    return [s for s in scene.steps if isinstance(s, Label) and s.names == gid]


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

    def test_both_sketches_build_slowly_and_hold_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("one_shift", "two_exits")
        for scene in every:
            frames = sketch_timeline(scene)
            paced = scene.slug in sketches.PACED
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            assert labels, scene.slug
            assert {f.ms for f in labels} == {
                sketches.PACED_LABEL_MS if paced else whiteboard.LABEL_MS
            }, scene.slug
            assert frames[-1].ms == (sketches.PACED_HOLD_MS if paced else HOLD_MS)
            assert [(f.done, f.partial) for f in frames] == [
                (f.done, f.partial) for f in timeline(scene)
            ]

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_vx_es_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_charts_and_the_roll_return_post(self) -> None:
        """No chart or sibling GIF starts like these, so the prefix checks above
        and in the equity seasonals tests read only this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert not "vx_es_roll_return".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.vx_es_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_the_shift_sketch_sits_in_lesson_2_and_the_exits_in_lesson_3(self) -> None:
        text = POST.read_text(encoding="utf-8")
        shift, exits = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lesson_2 = text.index("## Lesson 2:")
        script = text.index("### The script Chan published")
        lesson_3 = text.index("## Lesson 3:")
        lesson_4 = text.index("## Lesson 4:")
        assert lesson_2 < shift < script < lesson_3 < exits < lesson_4

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Each label is quoted after the one drawn before it, and a label drawn
        more than once, such as the exits sketch's "long", is quoted each time."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_it_is_schematic_and_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "schematic and carries no figures from the run" in alt, scene.slug
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_the_module_says_both_are_schematic(self) -> None:
        assert "Both sketches are schematic and carry no figures from the run" in (
            sketches.__doc__ or ""
        )


# --- Lesson 2: one shift slides, it does not tilt ------------------------------


class TestTheShiftSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "One shift slides, it does not tilt"
        assert every[0].labels == SHIFT_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        for gid, ink in (
            ("x-axis", MUTED),
            ("y-axis", MUTED),
            ("save", INK),
            ("save-fit", INK),
            ("same", ACCENT),
            ("same-fit", ACCENT),
            ("uneven", LOST),
            ("uneven-fit", LOST),
        ):
            assert _stroke(scene, gid).color == ink, gid
            for label in _labels_of(scene, gid):
                assert label.color == ink, label.text

    def test_the_dots_are_dots_and_the_fits_are_lines(self, every) -> None:
        """Colour is never the only cue: each cloud and its line carry their own
        words, and the clouds stand apart from left to right."""
        scene = every[0]
        for cloud in ("save", "same", "uneven"):
            assert _stroke(scene, cloud).dots > 0, cloud
            assert _stroke(scene, f"{cloud}-fit").dots == 0, cloud
        save, same, uneven = (_stroke(scene, c) for c in ("save", "same", "uneven"))
        assert save.x.max() < same.x.min() and same.x.max() < uneven.x.min()

    def test_the_dots_fall(self) -> None:
        assert fit(SAVE_X, SAVE_Y)[1] < 0

    def test_each_axis_is_named_at_its_own_end(self, every) -> None:
        """1000·VX runs across and 50·ES up, the way the regression puts them."""
        scene = every[0]
        across, up = _stroke(scene, "x-axis"), _stroke(scene, "y-axis")
        vx, es = _label(scene, "1000·VX"), _label(scene, "50·ES")
        assert set(across.y) == {ORIGIN[1]} and set(up.x) == {ORIGIN[0]}
        assert vx.names == "x-axis" and es.names == "y-axis"
        assert vx.x == pytest.approx(across.x.max()) and vx.y < ORIGIN[1]
        assert es.y == pytest.approx(up.y.max()) and es.x > ORIGIN[0]

    def test_each_cloud_is_drawn_before_its_fit(self, every) -> None:
        gids = [s.gid for s in every[0].strokes]
        for cloud in ("save", "same", "uneven"):
            assert gids.index(cloud) + 1 == gids.index(f"{cloud}-fit"), cloud

    def test_the_brass_copy_moves_every_dot_right_by_one_amount(self, every) -> None:
        scene = every[0]
        save, same = _stroke(scene, "save"), _stroke(scene, "same")
        assert same.y == pytest.approx(save.y)
        assert same.x - save.x == pytest.approx([SAME] * save.points)
        assert SAME > 0

    def test_the_red_copy_moves_the_dots_by_uneven_amounts(self, every) -> None:
        scene = every[0]
        save, uneven = _stroke(scene, "save"), _stroke(scene, "uneven")
        assert uneven.y == pytest.approx(save.y)
        shifts = uneven.x - save.x
        assert shifts == pytest.approx(UNEVEN)
        assert len(set(np.round(shifts, 9))) > save.points // 2

    def test_each_line_is_the_least_squares_fit_of_its_dots(self, every) -> None:
        scene = every[0]
        for cloud in ("save", "same", "uneven"):
            dots, line = _stroke(scene, cloud), _stroke(scene, f"{cloud}-fit")
            intercept, slope = fit(dots.x, dots.y)
            assert line.y == pytest.approx(intercept + slope * line.x), cloud
            assert line.x.min() < dots.x.min() and line.x.max() > dots.x.max(), cloud

    def test_the_brass_fit_is_parallel_to_the_black_and_sits_elsewhere(self, every) -> None:
        scene = every[0]
        black, brass = (_stroke(scene, gid) for gid in ("save-fit", "same-fit"))
        black_slope = np.polyfit(black.x, black.y, 1)[0]
        brass_slope = np.polyfit(brass.x, brass.y, 1)[0]
        assert brass_slope == pytest.approx(black_slope, abs=1e-9)
        assert fit(SAVE_X + SAME, SAVE_Y)[0] != pytest.approx(fit(SAVE_X, SAVE_Y)[0])

    def test_the_red_fit_tilts_enough_to_see(self, every) -> None:
        """A tilt large enough to see on a phone. The sketch is schematic, and the
        run's 3.6 percent would draw as about one degree."""
        scene = every[0]
        black, red = (_stroke(scene, gid) for gid in ("save-fit", "uneven-fit"))
        change = np.polyfit(red.x, red.y, 1)[0] / np.polyfit(black.x, black.y, 1)[0] - 1
        assert 0.15 < abs(change) < 0.35

    def test_one_constant_on_every_vx_close_moves_only_the_intercept(self) -> None:
        """The fact the sketch draws, on the 2012-05-07 save: three points added
        to every VX close leave the hedge, the deviation and every z-score where
        they were, and move the intercept by the hedge times 3,000 dollars."""
        rows = vx_es.anchored(vx_es.read_legs()[1])
        shifted = rows.copy()
        shifted[vx_es.VX] = shifted[vx_es.VX] + 3.0
        before = vx_es.fit_hedge(rows.iloc[: vx_es.TRAINING_DAYS])
        after = vx_es.fit_hedge(shifted.iloc[: vx_es.TRAINING_DAYS])
        assert after.hedge == pytest.approx(before.hedge, abs=1e-12)
        assert after.residual_std == pytest.approx(before.residual_std, rel=1e-12)
        assert vx_es.zscore(shifted, after) == pytest.approx(vx_es.zscore(rows, before), abs=1e-9)
        assert after.intercept - before.intercept == pytest.approx(
            before.hedge * vx_es.VX_POINT_VALUE * 3.0
        )

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "A grey axis across is labelled “1000·VX” and a grey axis up" in alt
        assert "Black dots fall from upper left to lower right" in alt
        assert "each moved right by the same amount" in alt
        assert "parallel to the black one" in alt
        assert "each moved right by a different amount" in alt
        assert "less steep than the other two" in alt

    def test_the_red_fit_is_less_steep_as_the_alt_text_says(self, every) -> None:
        scene = every[0]
        black, red = (_stroke(scene, gid) for gid in ("save-fit", "uneven-fit"))
        assert abs(np.polyfit(red.x, red.y, 1)[0]) < abs(np.polyfit(black.x, black.y, 1)[0])


# --- Lesson 3: two ways to close a position -----------------------------------

#: The word each held unit draws.
WORDS = {1.0: "long", -1.0: "short", 0.0: "flat"}


def _bars(scene, rule: str):
    return [s for s in scene.strokes if s.gid.startswith(f"{rule}-")]


def _word(scene, bar) -> str:
    (word,) = [s for s in _labels_of(scene, bar.gid) if s.text in WORDS.values()]
    return word.text


class TestTheExitsSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Two ways to close a position"
        assert every[1].labels == EXITS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert _stroke(scene, "path").color == INK
        for name in ("+1", "0", "−1"):
            level = _stroke(scene, f"level-{name}")
            assert (level.color, level.dashed) == (MUTED, True)
            assert _label(scene, name).color == MUTED
        for rule in ("opposite", "mean"):
            for bar in _bars(scene, rule):
                word = _word(scene, bar)
                assert bar.color == {"long": GOOD, "short": LOST, "flat": MUTED}[word], bar.gid
                for label in _labels_of(scene, bar.gid):
                    if label.text == word:
                        assert label.color == bar.color, bar.gid
        for name in ("hold until the opposite band (this run)", "close at the mean (bollinger.m)"):
            assert _label(scene, name).color == INK

    def test_flat_is_thin_and_held_is_thick(self, every) -> None:
        """Colour is never the only cue: every stretch carries its word, and a
        flat one is also drawn thin."""
        scene = every[1]
        for rule in ("opposite", "mean"):
            for bar in _bars(scene, rule):
                thin = bar.width < 3
                assert thin == (_word(scene, bar) == "flat"), bar.gid

    def test_the_levels_sit_at_their_z_scores(self, every) -> None:
        scene = every[1]
        for name, z in (("+1", 1), ("0", 0), ("−1", -1)):
            level = _stroke(scene, f"level-{name}")
            assert level.y == pytest.approx([z_y(z)] * level.points)
            assert _label(scene, name).y == pytest.approx(z_y(z))

    def test_the_path_reaches_each_band_at_its_crossing(self, every) -> None:
        """Below −1 at A, up through 0 at B, above +1 at C, down through 0 at D
        and below −1 again at E."""
        scene = every[1]
        line = _stroke(scene, "path")
        z = (line.y - z_y(0)) / (z_y(1) - z_y(0))
        for point, level, before, after in (
            ("A", -1, 1, -1),
            ("B", 0, -1, 1),
            ("C", 1, -1, 1),
            ("D", 0, 1, -1),
            ("E", -1, 1, -1),
        ):
            (k,) = np.flatnonzero(np.isclose(line.x, CROSSINGS[point]))
            assert z[k] == pytest.approx(level), point
            assert np.sign(z[k - 1] - level) == before, point
            assert np.sign(z[k + 1] - level) == after, point

    def test_each_strip_holds_what_the_runs_rule_holds_along_the_path(self, every) -> None:
        """The z-score the path draws, run through the rules ``chan.vx_es``
        trades, gives each stretch's word at every point strictly inside it."""
        scene = every[1]
        line = _stroke(scene, "path")
        z = (line.y - z_y(0)) / (z_y(1) - z_y(0))
        for rule, units in (
            ("opposite", vx_es.opposite_band_units(z)),
            ("mean", vx_es.mean_exit_units(z)),
        ):
            bars = _bars(scene, rule)
            for k, x in enumerate(line.x):
                inside = [b for b in bars if b.x.min() < x < b.x.max()]
                if inside:
                    (bar,) = inside
                    assert WORDS[float(units[k])] == _word(scene, bar), (rule, x)
                elif x > CROSSINGS["A"] and not any(np.isclose(b.x, x).any() for b in bars):
                    pytest.fail(f"{rule} draws nothing at {x}")
            # Before the first dip below −1, neither rule holds anything.
            assert not units[line.x < CROSSINGS["A"]].any(), rule

    def test_the_strips_run_end_to_end_from_a_to_the_paths_end(self, every) -> None:
        scene = every[1]
        for rule in ("opposite", "mean"):
            bars = _bars(scene, rule)
            assert bars[0].x.min() == pytest.approx(CROSSINGS["A"])
            assert bars[-1].x.max() == pytest.approx(PATH_X[1])
            for one, next_ in zip(bars, bars[1:], strict=False):
                assert one.x.max() == pytest.approx(next_.x.min()), (one.gid, next_.gid)

    def test_each_flat_stretch_starts_where_the_path_crosses_zero(self, every) -> None:
        """Closing at the mean leaves the long at B and the short at D, where
        the path crosses 0, and waits flat for the next band, C and then E."""
        scene = every[1]
        flats = [b for b in _bars(scene, "mean") if _word(scene, b) == "flat"]
        assert [(b.x.min(), b.x.max()) for b in flats] == [
            pytest.approx((CROSSINGS["B"], CROSSINGS["C"])),
            pytest.approx((CROSSINGS["D"], CROSSINGS["E"])),
        ]
        line = _stroke(scene, "path")
        z = line.y - z_y(0)
        held = line.x > CROSSINGS["A"]
        crossings = line.x[held][np.flatnonzero(np.isclose(z[held], 0, atol=1e-12))]
        assert crossings == pytest.approx([b.x.min() for b in flats])

    def test_the_opposite_band_changes_side_only_at_a_band(self, every) -> None:
        scene = every[1]
        bars = _bars(scene, "opposite")
        assert [(_word(scene, b), b.x.min()) for b in bars] == [
            ("long", pytest.approx(CROSSINGS["A"])),
            ("short", pytest.approx(CROSSINGS["C"])),
            ("long", pytest.approx(CROSSINGS["E"])),
        ]

    def test_the_flat_stretches_are_short_beside_the_held_ones(self, every) -> None:
        """In the run the mean exit is flat on 77 of the 449 test days, under one
        in five, and the sketch draws its flat stretches shorter still."""
        scene = every[1]
        bars = _bars(scene, "mean")
        lengths = {b.gid: b.x.max() - b.x.min() for b in bars}
        flat = [lengths[b.gid] for b in bars if _word(scene, b) == "flat"]
        held = [lengths[b.gid] for b in bars if _word(scene, b) != "flat"]
        assert max(flat) < min(held)
        assert sum(flat) / sum(lengths.values()) < 77 / 449 < 1 / 5

    def test_the_mean_exit_is_flat_on_77_of_449_test_days(self) -> None:
        """A test day earns the position held at the day before's close, so a
        flat day is one whose day before closed with no position."""
        traded = vx_es.vx_es(vx_es.read_legs()[1]).exit_at_mean
        start = len(traded.days) - len(traded.test_days)
        held_into = traded.units[start - 1 : -1]
        assert (len(held_into), int((held_into == 0).sum())) == (449, 77)

    def test_the_strips_sit_below_the_path_each_named_above_its_bar(self, every) -> None:
        scene = every[1]
        lowest = _stroke(scene, "path").y.min()
        heights = []
        for rule, name in (
            ("opposite", "hold until the opposite band (this run)"),
            ("mean", "close at the mean (bollinger.m)"),
        ):
            bars = _bars(scene, rule)
            (y,) = {float(v) for b in bars for v in b.y}
            heights.append(y)
            assert y < lowest
            assert _label(scene, name).y > y
            for bar in bars:
                (word,) = [s for s in _labels_of(scene, bar.gid) if s.text == _word(scene, bar)]
                assert word.y < y and word.x == pytest.approx((bar.x.min() + bar.x.max()) / 2)
        assert heights[0] > heights[1]

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert (
            "dips below −1, climbs back through 0, rises above +1, falls back through 0 "
            "and dips below −1 again"
        ) in alt
        assert "then turns back up to end just above it" in alt
        assert -1.0 < KNOTS[-1][1] < 0.0
        assert "a green bar marked “long” from the dip below −1 to the rise above +1" in alt
        assert "a red bar marked “short” from there to the next dip below −1" in alt
        assert "a green bar marked “long” from the dip below −1 to the crossing of 0" in alt
        assert "a red bar marked “short” until the path falls back through 0" in alt
        assert alt.count("short thin grey stretch marked “flat”") == 1
        assert alt.count("short grey stretch marked “flat”") == 1
