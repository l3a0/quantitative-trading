"""The pins for the two whiteboard GIFs in the Conditional Parameter Optimization post.

One sketches the strategy's entry and exit rule on a made-up z-score path, and
one Lesson 2's claim that Chan's annual returns cannot reach his cumulative
ones, read as compounded or as arithmetic. What is pinned is what a reader
takes from each.

1. The rule sketch is schematic. Its exit lines sit at
   :data:`chan.cpo.EXIT_FRACTION` times the entry, which a test pins at −0.6
   directly. Its position strip is :func:`chan.cpo.positions` run on the
   drawn path, which a test holds against a literal loop over the rules, and
   each of its four events sits where the path crosses the line that fires
   it, with each exit before 0. Its closing line reads the grid's lowest entry
   from :data:`chan.cpo.ENTRY_THRESHOLDS`, never typed here.
2. The annual returns sketch reads Chan's printed figures from
   :data:`chan.cpo.BOOK_UNCONDITIONAL` and :data:`chan.cpo.BOOK_CONDITIONAL`
   and computes the compounded figure and the arithmetic ceiling from them.
   The tests derive both again with the formulas
   ``tests/test_cpo.py`` uses, hold every height to one affine scale of a
   dollar's growth, and draw a made-up arm to show the words follow the
   figures.

Neither sketch needs the owner's archive of minute bars, so every test here
runs on a clone.

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

from chan import cpo
from chan import cpo_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.cpo_whiteboard import (
    DOLLAR_Y,
    LEVEL_X,
    PER_DOLLAR,
    PER_Z,
    STRIP_Y,
    YEARS,
    ZERO_Y,
    Arm,
    arithmetic_ceiling,
    compounded,
    events,
    fixed_arm,
    gif_name,
    growth_y,
    held,
    main,
    make_cpo_whiteboards,
    rechosen_arm,
    scenes,
    sketch_timeline,
    year_x,
    z_path,
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

POST = REPO_ROOT / "blog" / "conditional-parameter-optimization-lessons.md"

#: Every GIF in the order :func:`make_cpo_whiteboards` writes them.
GIFS = [
    "cpo_sketch_rule.gif",
    "cpo_sketch_annual_returns.gif",
]

#: The paragraph each GIF follows, by its opening words: the numbered list of
#: the strategy, the grid and the bars, and Lesson 2's paragraph on the
#: arithmetic annual return.
FOLLOWS = (
    "1. **The spread.**",
    "The other common definition of an annual return is arithmetic",
)

#: The grid's lowest entry threshold, read from the grid and never typed.
LOWEST = min(cpo.ENTRY_THRESHOLDS)

RULE_LABELS = [
    "0",
    "+entry",
    "−entry",
    "+0.6 × entry",
    "−0.6 × entry",
    "z-score",
    "flat",
    "position",
    "buy GLD",
    "long",
    "exit long",
    "flat",
    "short GLD",
    "short",
    "exit short",
    "flat",
    "each exit comes before the z-score reaches 0",
    f"lowest entry {LOWEST:g}: lines at ±{LOWEST:g}, ±{0.6 * LOWEST:g}",
]

ANNUAL_LABELS = [
    "$1",
    "year 1",
    "year 2",
    "year 3",
    "61.4%: 17.29% compounded",
    "at most 68.0%: 17.29% arithmetic",
    "73% printed",
    "68.0% still short of 73%",
    "re-chosen arm, 19.77% a year:",
    "71.8% compounded, at most 81.0% arithmetic,",
    "83% printed",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def every():
    return scenes()


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_cpo_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels(scene) -> list[Label]:
    return [s for s in scene.steps if isinstance(s, Label)]


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


def _paragraphs() -> list[str]:
    return [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]


def _alt(scene) -> str:
    text = POST.read_text(encoding="utf-8")
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


def _literal_rule(z: np.ndarray, entry: float) -> list[int]:
    """The book's four rules read one minute at a time, exits before entries:
    a long exits once the z-score is above −0.6 times the entry, a short once
    it is below +0.6 times it, and below −entry buys and above +entry shorts."""
    held_now, found = 0, []
    for value in z:
        if held_now == 1 and value > -0.6 * entry:
            held_now = 0
        if held_now == -1 and value < 0.6 * entry:
            held_now = 0
        if value < -entry:
            held_now = 1
        elif value > entry:
            held_now = -1
        found.append(held_now)
    return found


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

    def test_neither_draws_a_tint(self, every) -> None:
        """No pale tint, so none needs the green edge the shared rules ask of one."""
        assert not [fill for scene in every for fill in scene.fills]


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
            frames = sketch_timeline(scene)
            assert (frames[0].done, frames[0].ms) == (0, TITLE_MS)
            assert frames[-1].ms == sketches.PACED_HOLD_MS
        assert sketches.PACED_HOLD_MS > HOLD_MS

    def test_both_sketches_build_slowly_and_hold_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace, in both sketches."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("rule", "annual_returns")
        for scene in every:
            frames = sketch_timeline(scene)
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            assert labels, scene.slug
            assert {f.ms for f in labels} == {sketches.PACED_LABEL_MS}, scene.slug
            assert [(f.done, f.partial) for f in frames] == [
                (f.done, f.partial) for f in timeline(scene)
            ], scene.slug
            assert frames != timeline(scene), scene.slug

    def test_an_unpaced_scene_keeps_the_usual_pace(self, every, monkeypatch) -> None:
        monkeypatch.setattr(sketches, "PACED", ())
        for scene in every:
            assert sketch_timeline(scene) == timeline(scene)

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_cpo_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "cpo_cells.png").exists()

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
            ), f"{path.name}: redraw with: uv run python -m chan.cpo_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_the_footer_links_the_sketch_code_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        code = f"[the whiteboard sketches]({base}src/chan/cpo_whiteboard.py)"
        tests = f"[what the sketches draw]({base}tests/test_cpo_whiteboard.py)"
        assert code in footer and tests in footer

    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = _paragraphs()
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_the_rule_sketch_sits_after_the_bars_and_before_the_unstated_choices(self) -> None:
        """The list it follows ends on the bars, and the paragraph after its
        caption opens on what the book leaves unstated."""
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(FOLLOWS[0])]
        assert "\n8. **The bars.**" in paragraphs[index]
        assert paragraphs[index + 3].startswith(
            "The book does not say how to line up the two funds’ bars"
        )

    def test_each_is_followed_by_a_one_sentence_italic_caption(self) -> None:
        """The post captions its chart, so each sketch gets a caption too."""
        paragraphs = _paragraphs()
        for name in GIFS:
            (index,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{name})" in p]
            caption = paragraphs[index + 1]
            assert re.fullmatch(r"\*[^*\n]+\.\*", caption), name
            assert caption.count(". ") == 0, name

    def test_each_sits_in_its_section(self) -> None:
        text = POST.read_text(encoding="utf-8")
        rule, annual = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        strategy = text.index("## The strategy, the grid and the bars")
        lesson_1 = text.index("## Lesson 1:")
        lesson_2 = text.index("## Lesson 2:")
        lesson_3 = text.index("## Lesson 3:")
        assert strategy < rule < lesson_1
        assert lesson_2 < annual < lesson_3

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        for scene in every:
            alt, at = _alt(scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_names_its_pace(self, every) -> None:
        for scene in every:
            alt = _alt(scene)
            assert "drawn slowly" in alt and "twelve seconds" in alt, scene.slug

    def test_the_rule_is_schematic_and_says_so(self, every) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "The first sketch is schematic and carries no figures from the run." in doc
        assert "The second sketch is not schematic" in doc
        assert "It is schematic and carries no figures from the run." in _alt(every[0])
        assert "drawn to one scale of a dollar’s growth" in _alt(every[1])


# --- The strategy, the grid and the bars: the entry and exit rule -------------


class TestTheRuleSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "The entry and exit rule"
        assert every[0].labels == RULE_LABELS

    def test_the_exit_is_minus_0_6_times_the_entry(self) -> None:
        """The book's exit_threshold = −0.6 × entry_threshold, pp. 140 to 141."""
        assert cpo.EXIT_FRACTION == -0.6

    def test_the_grids_lowest_entry_is_its_first(self) -> None:
        assert LOWEST == cpo.ENTRY_THRESHOLDS[0]
        assert list(cpo.ENTRY_THRESHOLDS) == sorted(cpo.ENTRY_THRESHOLDS)

    def test_each_line_sits_at_its_multiple_of_the_entry(self, every) -> None:
        scene = every[0]
        heights = {
            "zero": 0.0,
            "entry-high": 1.0,
            "entry-low": -1.0,
            "exit-high": 0.6,
            "exit-low": -0.6,
        }
        for gid, z in heights.items():
            stroke = _stroke(scene, gid)
            assert np.allclose(stroke.y, ZERO_Y + z * PER_Z), gid
            assert (stroke.x[0], stroke.x[-1]) == LEVEL_X, gid
            assert stroke.dashed == bool(z), gid

    def test_the_path_is_drawn_on_the_lines_scale(self, every) -> None:
        x, z = z_path()
        stroke = _stroke(every[0], "z")
        assert np.array_equal(stroke.x, x)
        assert np.allclose(stroke.y, ZERO_Y + z * PER_Z)

    def test_the_strip_is_the_codes_rule_on_the_path(self) -> None:
        _, z = z_path()
        assert held(z).tolist() == _literal_rule(z, 1.0)

    def test_it_buys_exits_shorts_and_exits_in_that_order(self) -> None:
        _, z = z_path()
        found = events(held(z))
        assert [(e.before, e.after) for e in found] == [(0, 1), (1, 0), (0, -1), (-1, 0)]
        assert [e.name for e in found] == ["buy GLD", "exit long", "short GLD", "exit short"]

    def test_each_event_is_where_the_path_crosses_its_line(self) -> None:
        _, z = z_path()
        buy, exit_long, short, exit_short = events(held(z))
        assert z[buy.at - 1] >= -1.0 > z[buy.at]
        assert z[exit_long.at - 1] <= -0.6 < z[exit_long.at]
        assert z[short.at - 1] <= 1.0 < z[short.at]
        assert z[exit_short.at - 1] >= 0.6 > z[exit_short.at]

    def test_each_exit_comes_before_0(self) -> None:
        """The long exits while the z-score is still below 0 and the short
        while it is still above, and neither crosses 0 before its exit."""
        _, z = z_path()
        buy, exit_long, short, exit_short = events(held(z))
        assert (z[buy.at : exit_long.at + 1] < 0).all()
        assert (z[short.at : exit_short.at + 1] > 0).all()

    def test_each_dot_sits_on_the_path_and_its_guide_drops_to_the_strip(self, every) -> None:
        scene = every[0]
        x, z = z_path()
        for k, event in enumerate(events(held(z))):
            dot, guide = _stroke(scene, f"event-{k}"), _stroke(scene, f"guide-{k}")
            assert (dot.x[0], dot.y[0]) == (x[event.at], ZERO_Y + z[event.at] * PER_Z)
            assert np.allclose(guide.x, x[event.at])
            assert guide.y[0] == dot.y[0] and guide.y[-1] > STRIP_Y

    def test_each_stretch_of_the_strip_runs_between_its_events(self, every) -> None:
        scene = every[0]
        x, z = z_path()
        position = held(z)
        bounds = [0, *(e.at for e in events(position)), len(x) - 1]
        for k, (a, b) in enumerate(zip(bounds, bounds[1:], strict=False)):
            stretch = _stroke(scene, f"held-{k}")
            assert (stretch.x[0], stretch.x[-1]) == (x[a], x[b]), k
            assert np.allclose(stretch.y, STRIP_Y), k
            held_here = int(position[a])
            assert stretch.color == {1: GOOD, -1: LOST, 0: MUTED}[held_here], k
            assert stretch.width == (2.2 if held_here == 0 else 7.0), k

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert {s.gid: s.color for s in scene.strokes} == {
            "zero": MUTED,
            "entry-high": INK,
            "entry-low": INK,
            "exit-high": ACCENT,
            "exit-low": ACCENT,
            "z": INK,
            "held-0": MUTED,
            "event-0": GOOD,
            "guide-0": MUTED,
            "held-1": GOOD,
            "event-1": ACCENT,
            "guide-1": MUTED,
            "held-2": MUTED,
            "event-2": LOST,
            "guide-2": MUTED,
            "held-3": LOST,
            "event-3": ACCENT,
            "guide-3": MUTED,
            "held-4": MUTED,
        }
        assert [label.color for label in _labels(scene)] == [
            MUTED,
            INK,
            INK,
            ACCENT,
            ACCENT,
            INK,
            MUTED,
            MUTED,
            GOOD,
            GOOD,
            ACCENT,
            MUTED,
            LOST,
            LOST,
            ACCENT,
            MUTED,
            ACCENT,
            MUTED,
        ]

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[0])
        for phrase in (
            "A green dot where the path falls below −entry",
            "A brass dot where the path rises back above −0.6 times the entry",
            "A red dot where the path rises above +entry",
            "A brass dot where the path falls back below +0.6 times the entry",
            "each dropping a grey dashed guide to the strip",
        ):
            assert phrase in alt, phrase

    def test_each_word_of_the_strip_sits_under_its_stretch(self, every) -> None:
        scene = every[0]
        for word in _labels(scene):
            if not word.names.startswith("held-") or word.text == "position":
                continue
            stretch = _stroke(scene, word.names)
            assert word.x == pytest.approx((stretch.x[0] + stretch.x[-1]) / 2), word.names
            assert word.y < STRIP_Y, word.names

    def test_each_guide_is_dashed(self, every) -> None:
        for k in range(4):
            assert _stroke(every[0], f"guide-{k}").dashed, k


# --- Lesson 2: the annual returns against the cumulative ones -----------------


class TestTheBooksFigures:
    def test_the_arms_are_the_books(self) -> None:
        assert fixed_arm() == Arm(
            cpo.BOOK_UNCONDITIONAL["annual"], cpo.BOOK_UNCONDITIONAL["cumulative"]
        )
        assert rechosen_arm() == Arm(
            cpo.BOOK_CONDITIONAL["annual"], cpo.BOOK_CONDITIONAL["cumulative"]
        )

    def test_its_figures(self) -> None:
        """The figures ``tests/test_cpo.py`` pins, from the same formulas."""
        assert YEARS == 3
        for arm, compound, ceiling in ((fixed_arm(), 0.614, 0.680), (rechosen_arm(), 0.718, 0.810)):
            assert arm.compounded == (1 + arm.annual) ** 3 - 1
            assert arm.ceiling == math.exp(3 * arm.annual) - 1
            assert arm.compounded == pytest.approx(compound, abs=5e-4)
            assert arm.ceiling == pytest.approx(ceiling, abs=5e-4)

    def test_both_readings_fall_short_of_the_printed_figure(self) -> None:
        for arm in (fixed_arm(), rechosen_arm()):
            assert arm.compounded < arm.ceiling < arm.printed

    def test_the_ceiling_bounds_every_path_of_daily_returns(self) -> None:
        """Any daily returns averaging the annual figure over 252 days a year
        compound to no more than the ceiling, which is what makes it one."""
        annual = fixed_arm().annual
        days = 252 * YEARS
        rng = np.random.default_rng(0)
        for spread in (0.0, 0.005, 0.02):
            r = rng.normal(0.0, spread, days)
            r = r - r.mean() + annual / 252
            assert np.prod(1 + r) - 1 <= arithmetic_ceiling(annual) + 1e-12, spread

    def test_the_formulas(self) -> None:
        assert compounded(0.1, 2) == pytest.approx(0.21)
        assert arithmetic_ceiling(0.1, 2) == pytest.approx(math.exp(0.2) - 1)


class TestTheAnnualReturnsSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Fixed arm at 17.29% a year"
        assert every[1].labels == ANNUAL_LABELS

    def test_every_height_is_one_scale_of_a_dollars_growth(self, every) -> None:
        scene, arm = every[1], fixed_arm()
        assert growth_y(0.0) == DOLLAR_Y
        assert growth_y(1.0) - growth_y(0.0) == pytest.approx(PER_DOLLAR)
        assert np.allclose(_stroke(scene, "ceiling").y, DOLLAR_Y + arm.ceiling * PER_DOLLAR)
        assert np.allclose(_stroke(scene, "printed").y, DOLLAR_Y + arm.printed * PER_DOLLAR)
        bracket = _stroke(scene, "short").y
        assert (bracket.min(), bracket.max()) == pytest.approx(
            (growth_y(arm.ceiling), growth_y(arm.printed))
        )

    def test_the_staircase_steps_at_each_years_end(self, every) -> None:
        stairs = _stroke(every[1], "stairs")
        annual = fixed_arm().annual
        for year in range(YEARS):
            level = DOLLAR_Y + ((1 + annual) ** year - 1) * PER_DOLLAR
            on_step = (stairs.x > year_x(year) + 1e-9) & (stairs.x < year_x(year + 1) - 1e-9)
            assert on_step.any(), year
            assert np.allclose(stairs.y[on_step], level), year
        top = DOLLAR_Y + fixed_arm().compounded * PER_DOLLAR
        assert stairs.y[-1] == pytest.approx(top)
        assert stairs.x[0] == year_x(0) and stairs.y[0] == DOLLAR_Y

    def test_the_marks_stack_in_the_order_of_their_figures(self, every) -> None:
        scene = every[1]
        top = _stroke(scene, "stairs").y[-1]
        ceiling = _stroke(scene, "ceiling").y[0]
        printed = _stroke(scene, "printed").y[0]
        assert top < ceiling < printed

    def test_the_words_sit_by_the_marks_they_name(self, every) -> None:
        scene, arm = every[1], fixed_arm()
        assert _label(scene, "61.4%: 17.29% compounded").y == growth_y(arm.compounded)
        still = _label(scene, "68.0% still short of 73%").y
        assert growth_y(arm.ceiling) < still < growth_y(arm.printed) + 0.1
        assert _label(scene, "73% printed").y > growth_y(arm.printed)
        for year in (1, 2, 3):
            assert _label(scene, f"year {year}").x == year_x(year)

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert {s.gid: s.color for s in scene.strokes} == {
            "stairs": INK,
            "ceiling": ACCENT,
            "printed": LOST,
            "short": LOST,
        }
        assert _stroke(scene, "ceiling").dashed
        assert [label.color for label in _labels(scene)] == [
            INK,
            MUTED,
            MUTED,
            MUTED,
            INK,
            ACCENT,
            LOST,
            LOST,
            MUTED,
            MUTED,
            MUTED,
        ]

    def test_its_words_follow_the_figures(self) -> None:
        made_up = scenes(fixed=Arm(0.1, 0.5), rechosen=Arm(0.2, 0.9))[1]
        assert made_up.title == "Fixed arm at 10.00% a year"
        assert made_up.labels == [
            "$1",
            "year 1",
            "year 2",
            "year 3",
            "33.1%: 10.00% compounded",
            "at most 35.0%: 10.00% arithmetic",
            "50% printed",
            "35.0% still short of 50%",
            "re-chosen arm, 20.00% a year:",
            "72.8% compounded, at most 82.2% arithmetic,",
            "90% printed",
        ]

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[1])
        assert "the most three years of daily returns averaging an arithmetic 17.29%" in alt
        assert "A red mark above both" in alt
        assert "A dashed brass ceiling above it" in alt
        assert "a red bracket from the ceiling up to the mark" in alt

    def test_the_bracket_stands_right_of_the_marks_it_joins(self, every) -> None:
        scene = every[1]
        bracket = _stroke(scene, "short").x
        right = max(_stroke(scene, gid).x.max() for gid in ("ceiling", "printed"))
        assert np.allclose(bracket, bracket[0]) and bracket[0] > right
