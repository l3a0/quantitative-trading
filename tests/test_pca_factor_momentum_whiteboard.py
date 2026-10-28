"""The pins for the two whiteboard GIFs in the PCA factor momentum post.

One sketches Lesson 1's point that tomorrow's weights are fitted on a window
that already holds today's return, and one Lesson 5's point that PMC takes
PC1, so the factor that is usually PC1 lands in PC2. Neither is schematic in
its figures.

Both draw figures from Example 7.4's factor momentum run on Chan's S&P 600
file, which takes about a minute. So the figures are pinned here as
:data:`PINNED_WINDOW` and :data:`PINNED_RANK_SHIFT`, every test here runs
without the run, and ``test_the_whiteboard_draws_this_runs_figures`` in
``tests/test_pca_factor_momentum.py`` holds that the run gives them, reading
the fixtures that file already computes.

What is pinned for each sketch:

1. Its words, the exact labels in the order they are drawn.
2. Its colours: day t's weights and the pair in black, tomorrow's own weights
   in red, the weights that leave today out and the box that is mostly PMC in
   brass, the two days in red and the notes and axes in grey.
3. Its geometry: each bracket over the rows ``decompose`` reads for it, each
   box in its slot, and each bar at its share of PC2's squared products, to
   one scale.
4. Its numbers, read from the pins, a made-up second set of figures that
   moves the words and the bars with it, and figures the words would
   misdescribe, which are refused.
5. Its place in the post, right after the paragraph it draws, keyed on that
   paragraph's opening words.
6. Its alt text, which quotes the title and every label in drawing order.

The shared rules hold for both: every label clears every line by 10 pixels in
the installed hand font and in the fallback, sits inside the board and stays
clear of the other labels. Two draws on one machine give the same bytes.
Whether a committed GIF equals a fresh draw depends on the font, as
``tests/test_usdcad_tests_whiteboard.py`` explains, so that comparison runs
only on macOS arm64 with Comic Sans MS. The check that ``docs/figures`` holds
exactly the GIFs the modules draw lives in
``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS` from
here.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import platform
import re
from types import SimpleNamespace

import matplotlib
import numpy as np
import pandas as pd
import pytest
from PIL import Image

from chan import pca_factor_momentum
from chan import pca_factor_momentum_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.pca_factor import LOOKBACK, SPLICED
from chan.pca_factor_momentum import decompose
from chan.pca_factor_momentum_whiteboard import (
    BAR_X,
    BARS_BASE,
    BRACKET_Y,
    BRACKETS,
    DAY_AXIS_Y,
    DAY_X,
    SHARE_SCALE,
    SLOT_Y,
    WITH_X,
    WITHOUT_X,
    RankShift,
    Window,
    gif_name,
    main,
    make_pca_factor_momentum_whiteboards,
    scenes,
    sketch_timeline,
)
from chan.regime_figure import ACCENT, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    TITLE_MS,
    WIDTH,
    Frame,
    Label,
    clearances,
    hand_font,
)

POST = REPO_ROOT / "blog" / "pca-factor-momentum-lessons.md"

#: Every GIF in the order :func:`make_pca_factor_momentum_whiteboards` writes
#: them, which is the order the post places them.
GIFS = [
    "pca_factor_momentum_sketch_window.gif",
    "pca_factor_momentum_sketch_rank_shift.gif",
]

#: The paragraph each GIF follows, by its opening words, and the paragraph
#: after it.
FOLLOWS = (
    ("The window closes that gap.", "The pair fixes all three at once."),
    (
        "A return that size dominates any window that holds it.",
        "Dropping PMC and running everything again moves every factor.",
    ),
)

#: PC2's figures in the window sketch, unrounded. The vintage is
#: ``ijr_20080114/``, Chan's ``IJR_20080114.mat`` read for the Close column,
#: and the specification is ``tests/test_pca_factor_momentum.py``'s ``SPEC``.
#: ``test_with_sign_and_rank_matched``,
#: ``test_with_tomorrows_weights_fitted_on_251_days_that_leave_today_out``,
#: ``test_a_251_day_window_that_holds_today_reads_like_the_matched_row`` and
#: ``TestTheFigures`` there pin them at four decimals, and a re-pin there
#: moves these.
PINNED_WINDOW = Window(
    matched=-0.016058469436349466,
    left_out=0.07762279316139081,
    shortened=-0.0158275679151743,
    paired=0.0777633726394293,
)

#: The rank shift sketch's figures, on the same vintage and specification.
#: ``test_pmc_takes_pc1_through_2007_08_10_and_pc2_from_2007_08_13``,
#: ``test_two_days_carry_97_percent_of_pc2s_squared_products``,
#: ``test_without_pmc_the_same_two_days_carry_pc1`` and ``TestWithoutPMC``
#: there pin them, and a re-pin there moves these.
PINNED_RANK_SHIFT = RankShift(
    weights=(0.9144463092160766, 0.9223410361220626),
    span=("2007-08-02", "2007-08-10"),
    days=("2007-08-09", "2007-08-10"),
    shares=(0.20816937430403865, 0.7622407152883922),
    others=750,
    without_share=0.9460556165871636,
    paired=0.0777633726394293,
    without=-0.015207825928129547,
)

WINDOW_LABELS = [
    "t − 252",
    "t − 251",
    "t − 1",
    "t",
    "t + 1",
    "…",
    "today",
    "tomorrow",
    "day t’s weights: 252 days to t − 1",
    "day t+1’s weights: 252 days to t",
    "already holds",
    "today’s return",
    "tomorrow’s weights, 251 days, today left out",
    "PC2: tomorrow’s own weights, matched −0.0161",
    "→ today left out 0.0776",
    "≈ the pair 0.0778",
    "251 days that hold today: −0.0158",
]

RANK_SHIFT_LABELS = [
    "PC1",
    "PC2",
    "PC3",
    "usual PC1",
    "without PMC",
    "mostly PMC",
    "weight 0.9144 to 0.9223",
    "with PMC: days 2007-08-02 to 08-10",
    "usual PC1",
    "750 other days",
    "08-09",
    "08-10",
    "97.04% of PC2’s",
    "squared products",
    "without PMC: the same two days, 94.61% of PC1’s",
    "PC2: 0.0778 with PMC → −0.0152 without",
]

#: Each label's ink, in drawing order.
WINDOW_COLOURS = [MUTED] * 6 + [INK, INK, INK, LOST, LOST, LOST, ACCENT, LOST, ACCENT, INK, MUTED]
RANK_SHIFT_COLOURS = [INK, INK, INK, INK, MUTED, ACCENT, ACCENT, INK, INK, MUTED, LOST, LOST]
RANK_SHIFT_COLOURS += [LOST, LOST, MUTED, INK]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def every():
    return scenes(PINNED_WINDOW, PINNED_RANK_SHIFT)


@pytest.fixture(scope="module")
def frames(every):
    return [sketch_timeline(scene) for scene in every]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_pca_factor_momentum_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), figures=(PINNED_WINDOW, PINNED_RANK_SHIFT)
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


def _ends(stroke) -> tuple[float, float]:
    return float(stroke.x.min()), float(stroke.x.max())


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, every) -> None:
        assert [scene.title for scene in every] == [
            "Tomorrow’s own weights have seen today’s return",
            "PMC takes PC1, so the usual PC1 lands in PC2",
        ]

    def test_each_has_its_own_gif_named_for_it(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

    def test_each_says_what_it_should(self, every) -> None:
        assert [scene.labels for scene in every] == [WINDOW_LABELS, RANK_SHIFT_LABELS]

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
        """Neither sketch draws a tint. One that does would need the green
        edge the equity seasonals module's ``_tinted`` draws, since the tint
        alone stands 1.29 to 1 against the board."""
        assert [fill for scene in every for fill in scene.fills] == []

    def test_they_draw_in_the_shared_inks_as_the_posts_chart_does(self, every) -> None:
        """The post's chart has not moved to ``chan.palette``, so neither has
        any sketch here."""
        inks = {INK, MUTED, ACCENT, LOST}
        for scene in every:
            assert {s.color for s in scene.steps} <= inks, scene.slug


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

    def test_handed_figures_never_run_the_decompositions(self, monkeypatch, tmp_path) -> None:
        """Every draw here is handed the pins, so a draw handed them must not
        run the minute of decompositions, or this file stops being quick."""

        def refuse(*args, **kwargs):
            raise AssertionError("the run was read although figures were handed in")

        monkeypatch.setattr(sketches, "run_figures", refuse)
        paths = make_pca_factor_momentum_whiteboards(
            out_dir=tmp_path, figures=(PINNED_WINDOW, PINNED_RANK_SHIFT)
        )
        assert [path.name for path in paths] == GIFS

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
        """Both carry more than a reader takes in at the USD.CAD post's pace,
        so both hold each label for 0.9 seconds and their drawing for twelve,
        the equity seasonals post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert sketches.PACED == tuple(scene.slug for scene in every)
        assert (
            (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS)
            == (
                equity.PACED_LABEL_MS,
                equity.PACED_HOLD_MS,
            )
            == (900, 12000)
        )
        for scene, steps in zip(every, frames, strict=True):
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            assert steps[-1].ms == sketches.PACED_HOLD_MS, scene.slug
            labels = [
                f
                for f in steps[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            assert {f.ms for f in labels} == {sketches.PACED_LABEL_MS}, scene.slug
            assert [(f.done, f.partial) for f in steps] == [
                (f.done, f.partial) for f in whiteboard.timeline(scene)
            ]

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_pca_factor_momentum_whiteboards(
            out_dir=tmp_path, figures=(PINNED_WINDOW, PINNED_RANK_SHIFT)
        )
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_every_other_figure(self) -> None:
        """The post's chart, ``pca_factor_momentum.png``, starts like the
        prefix up to its last word, and no file but these GIFs starts with all
        of it."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert "pca_factor_momentum.png" in names

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
            ), f"{path.name}: redraw with: uv run python -m chan.pca_factor_momentum_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        """It draws into a scratch folder, because a draw into the figures
        folder would overwrite the committed GIFs that the byte test compares."""
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(sketches, "run_figures", lambda: (PINNED_WINDOW, PINNED_RANK_SHIFT))
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]

    def test_a_redraw_reads_both_sketches_figures_from_one_run(self, monkeypatch) -> None:
        """``run_figures`` loads the S&P 600 file's closes, runs the
        decompositions once, and hands the same objects to both readers."""
        seen = {}

        def record(name, value):
            def step(*args, **kwargs):
                seen[name] = (args, kwargs)
                return value

            return step

        closes = object()
        monkeypatch.setattr(sketches, "load_panel", record("load_panel", (None, closes)))
        monkeypatch.setattr(sketches, "file_returns", record("file_returns", "returns"))
        monkeypatch.setattr(sketches, "daily_components", record("daily_components", "parts"))
        monkeypatch.setattr(sketches, "compute_both", record("compute_both", "results"))
        monkeypatch.setattr(sketches, "weight_statistics", record("weight_statistics", "weights"))
        monkeypatch.setattr(Window, "from_run", record("window", PINNED_WINDOW))
        monkeypatch.setattr(RankShift, "from_run", record("rank_shift", PINNED_RANK_SHIFT))
        assert sketches.run_figures() == (PINNED_WINDOW, PINNED_RANK_SHIFT)
        assert seen["load_panel"] == ((sketches.SMALL_CAPS,), {"field": "Close"})
        assert seen["file_returns"] == ((closes,), {})
        assert seen["daily_components"] == (("returns",), {})
        assert seen["compute_both"] == ((closes,), {})
        assert seen["weight_statistics"] == (("returns", "parts"), {})
        assert seen["window"] == (("results", "weights"), {})
        assert seen["rank_shift"] == ((closes, "parts", "results"), {})


class TestThePost:
    @staticmethod
    def _paragraphs() -> list[str]:
        return [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]

    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        """Lesson 1's right after the paragraph on the window that closes the
        gap, and Lesson 5's right after the paragraph on PMC's weight."""
        paragraphs = self._paragraphs()
        for (opening, then), name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name
            assert paragraphs[index + 2].startswith(then), name

    def test_the_window_sits_in_lesson_1_and_the_rank_shift_in_lesson_5(self) -> None:
        text = POST.read_text(encoding="utf-8")
        window, shift = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lesson_1, lesson_2 = text.index("## Lesson 1:"), text.index("## Lesson 2:")
        lesson_5 = text.index("## Lesson 5:")
        cannot = text.index("## What this replication cannot say")
        assert lesson_1 < window < lesson_2 < lesson_5 < shift < cannot

    def test_each_sketch_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """A label drawn twice, such as the rank shift's "usual PC1", is quoted
        each time, after the one drawn before it."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_it_is_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "drawn slowly, that holds its finished drawing for twelve seconds" in alt

    def test_the_window_alt_text_says_where_each_bracket_runs(self, every) -> None:
        """Each phrase states a fact a test in ``TestTheWindowSketch`` holds."""
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        for words in (
            "so it is not to scale",
            "Black dots on the axis at t and t + 1",
            "from the top down",
            "Three brackets follow above the axis",
            "Under the axis, red words",
            "A black bracket from t − 252 to t − 1",
            "A red bracket from t − 251 to t, its right end over today’s dot",
            "A brass bracket runs from the red bracket’s left end to the black bracket’s right end",
            "red words read “PC2: tomorrow’s own weights",
            "brass words “→ today left out",
            "black words “≈ the pair",
            "grey words “251 days",
        ):
            assert words in alt, words

    def test_the_rank_shift_alt_text_says_where_each_box_and_bar_stands(self, every) -> None:
        """Each phrase states a fact a test in ``TestTheRankShiftSketch`` holds."""
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        for words in (
            "Three grey shelves mark three slots",
            "named “PC1”, “PC2” and “PC3” from the top",
            "To the right, three bars",
            "In the left column, a black box marked “usual PC1” sits in the first slot",
            "In the right column, a brass box marked “mostly PMC”",
            "takes the first slot",
            "An arrow runs from the left column’s box down to a second black box",
            "in the right column’s second slot",
            "The third slot stays empty in both columns",
            "all to one scale",
            "a short grey bar marked “750 other days” for the other days together",
            "two red bars marked “08-09” and “08-10”, the second more than three times as tall",
            "Red words beside them",
            "grey words read “without PMC",
            "black words “PC2:",
        ):
            assert words in alt, words
        first, second = PINNED_RANK_SHIFT.shares
        assert 3 < second / first < 4

    def test_the_module_says_neither_is_schematic_and_which_parts_are(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "Neither is schematic in its figures" in doc
        assert "is not to scale" in doc
        assert "the slots carry no figure of their own" in doc

    def test_the_footer_links_the_module_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        assert f"[the whiteboard sketches]({base}src/chan/pca_factor_momentum_whiteboard.py)" in (
            footer
        )
        assert f"[what the sketches draw]({base}tests/test_pca_factor_momentum_whiteboard.py)" in (
            footer
        )


# --- Lesson 1: tomorrow's weights have already seen today's return ------------


class TestTheWindowSketch:
    def test_its_figures_print_as_the_run_pins_them(self) -> None:
        """At the four decimals ``tests/test_pca_factor_momentum.py`` pins and
        the post's table prints."""
        w = PINNED_WINDOW
        assert [f"{v:.4f}" for v in (w.matched, w.left_out, w.shortened, w.paired)] == [
            "-0.0161",
            "0.0776",
            "-0.0158",
            "0.0778",
        ]
        assert abs(w.left_out - w.paired) < sketches.CLOSE < abs(w.matched - w.paired)

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert [s.color for s in scene.steps if isinstance(s, Label)] == WINDOW_COLOURS
        assert _stroke(scene, "axis").color == MUTED
        assert _stroke(scene, "today").color == INK
        assert _stroke(scene, "tomorrow").color == LOST
        assert _stroke(scene, "left-out").color == ACCENT
        assert _stroke(scene, "today-return").color == INK
        assert _stroke(scene, "tomorrow-return").color == INK

    def test_each_bracket_covers_the_rows_decompose_reads_for_it(self, monkeypatch) -> None:
        """Day t's weights read the 252 rows before row t, day t+1's own the
        252 rows to row t, and the weights that leave today out the 251 rows
        before row t, as ``weight_statistics`` asks for them."""
        rows = []

        def components(window):
            rows.append((int(window[0, 0]), int(window[0, -1])))
            return np.zeros((window.shape[0], 1)), np.zeros(1)

        monkeypatch.setattr(pca_factor_momentum, "revised_matlab_components", components)
        returns = np.repeat(np.arange(400.0)[:, None], 3, axis=1)
        t = 300
        decompose(returns, t)
        decompose(returns, t + 1)
        decompose(returns, t, LOOKBACK - 1)
        assert rows == [
            (t + first, t + last)
            for first, last in (BRACKETS["today"], BRACKETS["tomorrow"], BRACKETS["left-out"])
        ]
        assert BRACKETS == {
            "today": (-252, -1),
            "tomorrow": (-251, 0),
            "left-out": (-251, -1),
        }

    def test_weight_statistics_fits_the_left_out_weights_on_the_251_rows_before_today(
        self, monkeypatch
    ) -> None:
        """Every short window it fits is ``LOOKBACK - 1`` rows long and ends
        before row t, which leaves today out, or at row t, which keeps it in."""
        rng = np.random.default_rng(11)
        returns = rng.normal(0, 0.02, size=(LOOKBACK + 4, 12))
        components = pca_factor_momentum.daily_components(returns)
        asked, real = [], pca_factor_momentum.decompose

        def record(returns, t, lookback=LOOKBACK):
            asked.append((t, lookback))
            return real(returns, t, lookback)

        monkeypatch.setattr(pca_factor_momentum, "decompose", record)
        pca_factor_momentum.weight_statistics(returns, components)
        days = [d.end for d in components[:-1]]
        assert asked == [call for t in days for call in ((t, LOOKBACK - 1), (t + 1, LOOKBACK - 1))]

    def test_each_bracket_spans_its_days_on_the_axis_top_to_bottom(self, every) -> None:
        scene = every[0]
        for gid, (first, last) in BRACKETS.items():
            bracket = _stroke(scene, gid)
            assert _ends(bracket) == pytest.approx((DAY_X[first], DAY_X[last])), gid
            assert np.median(bracket.y) == pytest.approx(BRACKET_Y[gid]), gid
        heights = [BRACKET_Y[gid] for gid in ("today", "tomorrow", "left-out")]
        assert heights == sorted(heights, reverse=True)
        assert min(heights) > DAY_AXIS_Y

    def test_the_red_bracket_ends_over_todays_return_and_the_brass_under_both(self, every) -> None:
        scene = every[0]
        today, tomorrow, left_out = (_stroke(scene, g) for g in ("today", "tomorrow", "left-out"))
        dot = _stroke(scene, "today-return")
        assert _ends(tomorrow)[1] == pytest.approx(float(dot.x[0]))
        assert _ends(left_out) == pytest.approx((_ends(tomorrow)[0], _ends(today)[1]))
        assert _ends(today)[1] < float(dot.x[0])

    def test_each_bracket_is_named_above_its_left_end(self, every) -> None:
        scene = every[0]
        for gid in BRACKETS:
            words = next(s for s in scene.steps if isinstance(s, Label) and s.names == gid)
            assert words.x == pytest.approx(_ends(_stroke(scene, gid))[0]), gid
            assert words.y > BRACKET_Y[gid], gid
        notes = [_label(scene, "already holds"), _label(scene, "today’s return")]
        right = _ends(_stroke(scene, "tomorrow"))[1]
        for note in notes:
            assert note.x > right
        assert notes[0].y > BRACKET_Y["tomorrow"] > notes[1].y

    def test_the_axis_marks_each_day_and_both_returns(self, every) -> None:
        scene = every[0]
        axis = _stroke(scene, "axis")
        for offset, x in DAY_X.items():
            tick = _label(scene, sketches._day(offset))
            assert tick.x == pytest.approx(x)
            assert tick.y < DAY_AXIS_Y
            assert np.isclose(axis.x, x).any(), offset
        assert sorted(DAY_X) == [-LOOKBACK, -(LOOKBACK - 1), -1, 0, 1]
        xs = [DAY_X[offset] for offset in sorted(DAY_X)]
        assert xs == sorted(xs) and len(set(xs)) == len(xs)
        skip = _label(scene, "…")
        assert DAY_X[-(LOOKBACK - 1)] < skip.x < DAY_X[-1]
        for gid, offset, word in (("today-return", 0, "today"), ("tomorrow-return", 1, "tomorrow")):
            dot = _stroke(scene, gid)
            assert (float(dot.x[0]), float(dot.y[0])) == (DAY_X[offset], DAY_AXIS_Y)
            assert (_label(scene, word).x, _label(scene, word).y > DAY_AXIS_Y) == (
                DAY_X[offset],
                True,
            )

    def test_the_foot_sits_under_the_axis(self, every) -> None:
        scene = every[0]
        for text in WINDOW_LABELS[13:]:
            assert _label(scene, text).y < DAY_AXIS_Y - sketches.TICK_WORDS_BELOW, text

    def test_other_figures_move_the_words(self, every) -> None:
        moved = Window(matched=-0.2, left_out=0.031, shortened=0.05, paired=0.03)
        scene = sketches._window(moved)
        assert scene.labels == [
            *WINDOW_LABELS[:13],
            "PC2: tomorrow’s own weights, matched −0.2000",
            "→ today left out 0.0310",
            "≈ the pair 0.0300",
            "251 days that hold today: 0.0500",
        ]

    @pytest.mark.parametrize("left_out", [0.0828, 0.0727, -0.0161])
    def test_a_left_out_figure_far_from_the_pair_is_refused(self, left_out) -> None:
        """The sketch prints "≈" between the two, so a gap of 0.005 or more is refused."""
        with pytest.raises(ValueError):
            sketches._window(dataclasses.replace(PINNED_WINDOW, left_out=left_out))


# --- Lesson 5: PMC takes PC1, so the usual PC1 lands in PC2 -------------------


def _box_of(scene, gid) -> tuple[float, float, float, float]:
    box = _stroke(scene, gid)
    return float(box.x.min()), float(box.y.min()), float(box.x.max()), float(box.y.max())


class TestTheRankShiftSketch:
    def test_its_figures_print_as_the_run_pins_them(self) -> None:
        r = PINNED_RANK_SHIFT
        assert [f"{v:.4f}" for v in r.weights] == ["0.9144", "0.9223"]
        assert r.span == ("2007-08-02", "2007-08-10")
        assert r.days == ("2007-08-09", "2007-08-10")
        assert (f"{r.share:.4f}", f"{r.without_share:.4f}") == ("0.9704", "0.9461")
        assert r.others == 752 - 2
        assert (f"{r.paired:.4f}", f"{r.without:.4f}") == ("0.0778", "-0.0152")

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert [s.color for s in scene.steps if isinstance(s, Label)] == RANK_SHIFT_COLOURS
        for k in range(3):
            assert _stroke(scene, f"shelf-{k}").color == MUTED
        assert _stroke(scene, "usual-without").color == INK
        assert _stroke(scene, "usual-with").color == INK
        assert _stroke(scene, "push").color == INK
        assert _stroke(scene, "pmc").color == ACCENT
        assert _stroke(scene, "baseline").color == MUTED
        assert [_stroke(scene, f"bar-{k}").color for k in range(3)] == [MUTED, LOST, LOST]

    def test_each_slot_is_named_beside_its_shelf(self, every) -> None:
        scene = every[1]
        for k, (name, y) in enumerate(zip(("PC1", "PC2", "PC3"), SLOT_Y, strict=True)):
            shelf = _stroke(scene, f"shelf-{k}")
            assert _label(scene, name).y == pytest.approx(y)
            assert float(shelf.y.max()) < y
            assert _ends(shelf)[0] < WITHOUT_X[0] and _ends(shelf)[1] > WITH_X[1]
        assert list(SLOT_Y) == sorted(SLOT_Y, reverse=True)

    def test_the_usual_pc1_sits_first_without_pmc_and_second_with_it(self, every) -> None:
        scene = every[1]
        x0, y0, x1, y1 = _box_of(scene, "usual-without")
        assert (x0, x1) == pytest.approx(WITHOUT_X)
        assert y0 < SLOT_Y[0] < y1
        x0, y0, x1, y1 = _box_of(scene, "usual-with")
        assert WITH_X[0] == pytest.approx(x0) and x1 < WITH_X[1]
        assert y0 < SLOT_Y[1] < y1
        x0, y0, x1, y1 = _box_of(scene, "pmc")
        assert (x0, x1) == pytest.approx(WITH_X)
        assert y0 < SLOT_Y[0] < y1
        assert _label(scene, "without PMC").y > _box_of(scene, "usual-without")[3]
        header = _label(scene, "with PMC: days 2007-08-02 to 08-10")
        assert header.y > _box_of(scene, "pmc")[3]
        assert header.x == pytest.approx(WITH_X[0])

    def test_the_third_slot_stays_empty(self, every) -> None:
        """Every mark over the slots but the shelves sits above the second
        shelf, so nothing stands in PC3's slot."""
        scene = every[1]
        for stroke in scene.strokes:
            if stroke.gid.startswith("shelf-") or float(stroke.x.min()) > WITH_X[1]:
                continue
            assert float(stroke.y.min()) > sketches.SHELF_Y[1], stroke.gid

    def test_the_arrow_runs_from_the_usual_pc1_down_to_its_second_place(self, every) -> None:
        scene = every[1]
        arrow = _stroke(scene, "push")
        lowest = int(np.argmin(arrow.y))
        start, tip = (arrow.x[0], arrow.y[0]), (arrow.x[lowest], arrow.y[lowest])
        without, with_ = _box_of(scene, "usual-without"), _box_of(scene, "usual-with")
        assert start[0] >= without[2] and start[1] <= without[1]
        assert tip[0] <= with_[0] and with_[1] < tip[1] < with_[3]
        assert tip[1] < start[1]

    def test_each_bar_stands_at_its_share_to_one_scale(self, every) -> None:
        scene = every[1]
        r = PINNED_RANK_SHIFT
        for k, (x, share) in enumerate(zip(BAR_X, (1 - r.share, *r.shares), strict=True)):
            bar = _stroke(scene, f"bar-{k}")
            assert set(bar.x) == {x}, k
            assert (float(bar.y[0]), float(bar.y[-1])) == pytest.approx(
                (BARS_BASE, BARS_BASE + SHARE_SCALE * share)
            ), k
        base = _stroke(scene, "baseline")
        assert set(np.round(base.y, 12)) == {BARS_BASE}
        assert _ends(base)[0] < min(BAR_X) and _ends(base)[1] > max(BAR_X)
        assert min(BAR_X) > WITH_X[1]

    def test_each_bar_is_named_under_the_baseline(self, every) -> None:
        scene = every[1]
        for k, text in enumerate(("750 other days", "08-09", "08-10")):
            label = _label(scene, text)
            assert (label.x, label.names) == (BAR_X[k], f"bar-{k}")
            assert label.y < BARS_BASE

    def test_the_share_sits_beside_the_tallest_bar(self, every) -> None:
        scene = every[1]
        tallest = _stroke(scene, "bar-2")
        for text in ("97.04% of PC2’s", "squared products"):
            label = _label(scene, text)
            assert label.x < BAR_X[2] and label.y < float(tallest.y.max())

    def test_other_figures_move_the_words_and_the_bars(self) -> None:
        moved = RankShift(
            weights=(0.81, 0.88),
            span=("2009-03-02", "2009-03-13"),
            days=("2009-03-05", "2009-03-06"),
            shares=(0.5, 0.25),
            others=600,
            without_share=0.7,
            paired=0.0412,
            without=0.0105,
        )
        scene = sketches._rank_shift(moved)
        assert scene.labels == [
            *RANK_SHIFT_LABELS[:6],
            "weight 0.8100 to 0.8800",
            "with PMC: days 2009-03-02 to 03-13",
            "usual PC1",
            "600 other days",
            "03-05",
            "03-06",
            "75.00% of PC2’s",
            "squared products",
            "without PMC: the same two days, 70.00% of PC1’s",
            "PC2: 0.0412 with PMC → 0.0105 without",
        ]
        heights = [float(_stroke(scene, f"bar-{k}").y[-1]) - BARS_BASE for k in range(3)]
        assert heights == pytest.approx([SHARE_SCALE * s for s in (0.25, 0.5, 0.25)])

    @pytest.mark.parametrize(
        "changes",
        [
            {"days": ("2007-08-09", "2007-08-13")},
            {"days": ("2007-08-01", "2007-08-02")},
            {"span": ("2007-08-02", "2008-01-10"), "days": ("2007-08-09", "2008-01-09")},
        ],
        ids=["a day after PMC leaves PC1", "a day before it arrives", "a second year"],
    )
    def test_figures_the_words_would_misdescribe_are_refused(self, changes) -> None:
        with pytest.raises(ValueError):
            sketches._rank_shift(dataclasses.replace(PINNED_RANK_SHIFT, **changes))


#: Nine made-up trading days for :class:`TestTheRankShiftReader`.
READER_DAYS = pd.bdate_range("2007-07-30", periods=9)


def _pairs(column: int, large: tuple[int, int]) -> SimpleNamespace:
    """Six pair days whose products on ``column`` are large on the two ``large`` days."""
    tomorrow = np.full((6, 5), 0.1)
    tomorrow[list(large), column] = (3.0, 4.0)
    return SimpleNamespace(today=np.ones((6, 5)), tomorrow=tomorrow, days=READER_DAYS[2:8])


def _from_run(monkeypatch, carriers: list[int], without: tuple[int, int]) -> RankShift:
    """PMC's return on row 1, held by one window per carrier, each ending a day later."""
    closes = pd.DataFrame(1.0, index=READER_DAYS, columns=[SPLICED, "X"])
    returns = np.zeros((len(READER_DAYS), 2))
    returns[1, 0] = 1.0
    holding = [SimpleNamespace(end=2 + k) for k in range(len(carriers))]
    monkeypatch.setattr(sketches, "file_returns", lambda _: returns)
    monkeypatch.setattr(sketches, "windows_holding", lambda _, row: holding if row == 1 else [])
    monkeypatch.setattr(
        sketches, "largest_loading", lambda d, column: (0.9 + d.end / 100, carriers[d.end - 2])
    )
    results = SimpleNamespace(
        spliced=SimpleNamespace(
            pairs=_pairs(sketches.FACTOR, (1, 2)), comparison=SimpleNamespace(factors=[0.0] * 5)
        ),
        unspliced=SimpleNamespace(
            pairs=_pairs(0, without), comparison=SimpleNamespace(factors=[0.0] * 5)
        ),
    )
    return RankShift.from_run(closes, [None] * 7, results)


class TestTheRankShiftReader:
    """:meth:`RankShift.from_run` on a made-up run of nine days, so its
    refusals are reached without the decompositions."""

    def test_it_reads_the_days_pmc_carries_pc1_and_the_two_large_days(self, monkeypatch) -> None:
        found = _from_run(monkeypatch, [0, 0, 0, 1, 1, 2], without=(1, 2))
        assert found.span == ("2007-08-01", "2007-08-03")
        assert found.weights == pytest.approx((0.92, 0.94))
        assert found.days == ("2007-08-02", "2007-08-03")
        assert found.others == 4

    @pytest.mark.parametrize(
        "carriers",
        [[1, 1, 0], [0, 1, 0], [0, 0, 1, 0]],
        ids=["PMC not on PC1 first", "PC1 again after a gap", "PC1 again at the end"],
    )
    def test_pmc_off_pc1_on_its_first_days_or_back_on_it_later_is_refused(
        self, monkeypatch, carriers
    ) -> None:
        with pytest.raises(ValueError, match="first days"):
            _from_run(monkeypatch, carriers, without=(1, 2))

    def test_two_other_days_carrying_pc1_without_pmc_is_refused(self, monkeypatch) -> None:
        with pytest.raises(ValueError, match="same two days"):
            _from_run(monkeypatch, [0, 0, 1], without=(3, 4))
