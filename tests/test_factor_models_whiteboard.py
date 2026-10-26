"""The pins for the two whiteboard GIFs in the factor models post.

One sketches Lesson 2's point that the residuals cancel, so the revised
Python ranks on each stock's own returns, and one Lesson 3's point that a sign
flip changes both members of a pair. Both are schematic: their returns, factor
series, weights and ranked stocks are made up, so no test here reads a figure
off them. What is pinned is what a reader takes from them, and that the facts
they draw hold in the code the post's numbers come from.

1. The residuals sketch draws a dozen daily returns as bars, the fitted value
   beside each as a dot, and the gap between them as a tick coloured by its
   sign. What is pinned is that the dots are the least-squares fit of the bars
   on an intercept and five factor series, so the gaps sum to 0 and the two
   totals stand at the same height, that the totals are plain sums rather than
   a compounded return, and that :func:`chan.pca_factor.python_expected` gives
   :func:`chan.pca_factor.summed_returns` on a made-up window, the identity the
   sketch draws.
2. The sign flip sketch draws day t's weights, the pair they give, the same
   weights reversed, the product a series of fresh weights would read, and the
   pair under the flip. What is pinned is that f and g are the weights applied
   to two days of returns, that the reversed weights give −f and −g, that the
   pair's product is the same under the flip and the fresh-weights product is
   its negative, and that :func:`chan.pca_factor_momentum.uncentred` does not
   move when one pair flips, as
   ``test_a_flipped_vector_moves_no_product_and_no_statistic`` in
   ``tests/test_pca_factor_momentum.py`` holds on the run.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, the sign
flip sketch's slower pace, that two draws give the same bytes, and that each
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

from chan import factor_models_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.factor_models_whiteboard import (
    ARROW_Y,
    AXIS_Y,
    DAY_AFTER,
    DAY_T,
    DOT_OFFSET,
    FACTOR_SERIES,
    PANELS,
    PRODUCT_SCALE,
    RANKED,
    RETURN_SCALE,
    RETURNS,
    TOTAL_SCALE,
    TOTALS_BASE,
    VALUE_BASE,
    VALUE_SCALE,
    WEIGHTS,
    day_x,
    fitted,
    gif_name,
    main,
    make_factor_models_whiteboards,
    pair,
    scenes,
    sketch_timeline,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.pca_factor import python_expected, summed_returns
from chan.pca_factor_momentum import uncentred
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

POST = REPO_ROOT / "blog" / "factor-models-lessons.md"

#: Every GIF in the order :func:`make_factor_models_whiteboards` writes them.
GIFS = ["factor_models_residuals_cancel.gif", "factor_models_sign_flip.gif"]

#: The paragraph each GIF follows, by its opening words. The residuals sketch
#: follows the display equation after its paragraph, as the post tests check.
FOLLOWS = (
    "The revised Python regresses each stock’s returns",
    "Each day’s principal component analysis gives each factor",
)

RESIDUALS_LABELS = [
    "one stock’s year (schematic)",
    "daily returns",
    "fitted values",
    "+ return above the fit",
    "− return below the fit",
    "with an intercept, the gaps sum to 0",
    "Σ returns",
    "Σ fitted",
    "=",
    "four stocks, ranked",
    "rank on Σ fitted = rank on Σ returns",
    "momentum, no factors needed",
]

FLIP_LABELS = [
    "day t’s weights",
    "f",
    "g",
    "one pair: day t, day t+1",
    "f·g",
    "+",
    "same direction, sign flipped",
    "f",
    "−g",
    "f·(−g)",
    "−",
    "fresh weights each day:",
    "the flip reads as a reversal",
    "−f",
    "−g",
    "+",
    "(−f)(−g) = fg",
    "a flip changes both members,",
    "so the product stays",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def every():
    return scenes()


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_factor_models_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _labels_of(scene, gid):
    return [s for s in scene.steps if isinstance(s, Label) and s.names == gid]


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


def _height(bar) -> float:
    """A bar's signed length from its first point to its last."""
    return float(bar.y[-1] - bar.y[0])


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

    def test_only_the_sign_flip_sketch_builds_slowly(self, every) -> None:
        """Its labels show alone for 0.9 s and its drawing for 12 s, the equity
        post's slow pace. The residuals sketch keeps the usual pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("sign_flip",)
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
        again = make_factor_models_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_every_other_figure(self) -> None:
        """No chart or sibling GIF starts like these, such as the post's chart
        ``factor_momentum_autocorrelations.png``, so the check above reads only
        this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert "factor_momentum_autocorrelations.png" in names

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
            ), f"{path.name}: redraw with: uv run python -m chan.factor_models_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    @staticmethod
    def _paragraphs() -> list[str]:
        return [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]

    @staticmethod
    def _embed(name: str, paragraph: str) -> None:
        assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", paragraph), name

    def test_the_residuals_sketch_follows_lesson_2s_display_equation(self) -> None:
        """It sits after the paragraph that opens on the regression and the
        equation under it, and before the list that opens with the Python never
        using its factors."""
        paragraphs = self._paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(FOLLOWS[0])]
        assert paragraphs[index + 1].startswith("```math")
        self._embed(GIFS[0], paragraphs[index + 2])
        assert paragraphs[index + 3].startswith("1. **The Python never uses its factors.**")

    def test_the_sign_flip_sketch_follows_its_paragraph_before_the_table(self) -> None:
        paragraphs = self._paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(FOLLOWS[1])]
        self._embed(GIFS[1], paragraphs[index + 1])
        assert paragraphs[index + 2].startswith("```math")
        assert "Factor, 752 pairs" in paragraphs[index + 2]

    def test_the_residuals_sketch_sits_in_lesson_2_and_the_flip_in_lesson_3(self) -> None:
        text = POST.read_text(encoding="utf-8")
        residuals, flip = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lesson_2 = text.index("## Lesson 2:")
        lesson_3 = text.index("## Lesson 3:")
        own = text.index("**Example 7.4’s own factors.**")
        lesson_4 = text.index("## Lesson 4:")
        assert lesson_2 < residuals < lesson_3 < own < flip < lesson_4

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Each label is quoted after the one drawn before it, and a label drawn
        more than once, such as the sign flip sketch's "f" and "+", is quoted
        each time."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_it_is_schematic_and_whether_it_is_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "It is schematic and carries no figures from the run" in alt, scene.slug
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_the_module_says_both_are_schematic(self) -> None:
        assert "Both sketches are schematic and carry no figures from the run" in (
            sketches.__doc__ or ""
        )

    def test_the_footer_links_the_module_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        assert f"({base}src/chan/factor_models_whiteboard.py)" in footer
        assert f"({base}tests/test_factor_models_whiteboard.py)" in footer


# --- Lesson 2: the residuals cancel -------------------------------------------


def _days(scene, kind: str):
    return [s for s in scene.strokes if re.fullmatch(rf"{kind}-\d+", s.gid)]


class TestTheResidualsSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "The residuals cancel, so the sums match"
        assert every[0].labels == RESIDUALS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert _stroke(scene, "axis").color == MUTED
        assert _label(scene, "one stock’s year (schematic)").color == MUTED
        assert {bar.color for bar in _days(scene, "return")} == {INK}
        assert _label(scene, "daily returns").color == INK
        assert _stroke(scene, "fitted").color == ACCENT
        assert _label(scene, "fitted values").color == ACCENT
        assert _label(scene, "+ return above the fit").color == GOOD
        assert _label(scene, "− return below the fit").color == LOST
        assert (_stroke(scene, "total-returns").color, _label(scene, "Σ returns").color) == (
            INK,
            INK,
        )
        assert (_stroke(scene, "total-fitted").color, _label(scene, "Σ fitted").color) == (
            ACCENT,
            ACCENT,
        )
        for rank in range(len(RANKED)):
            assert _stroke(scene, f"ranked-{rank}").color == INK
            assert _stroke(scene, f"ranked-fit-{rank}").color == ACCENT

    def test_the_fit_is_on_an_intercept_and_five_factor_series(self) -> None:
        assert FACTOR_SERIES.shape == (5, len(RETURNS))
        design = np.column_stack([np.ones(len(RETURNS)), FACTOR_SERIES.T])
        expected = design @ np.linalg.lstsq(design, RETURNS, rcond=None)[0]
        assert fitted() == pytest.approx(expected, abs=1e-12)

    def test_each_bar_stands_on_the_axis_at_its_return(self, every) -> None:
        bars = _days(every[0], "return")
        assert len(bars) == len(RETURNS) == 12
        for day, bar in enumerate(bars):
            assert bar.x == pytest.approx([day_x(day)] * bar.points)
            assert bar.y[0] == pytest.approx(AXIS_Y)
            assert _height(bar) == pytest.approx(RETURN_SCALE * RETURNS[day])
        assert (RETURNS > 0).any() and (RETURNS < 0).any()

    def test_each_dot_sits_beside_its_bar_at_the_fitted_value(self, every) -> None:
        dots = _stroke(every[0], "fitted")
        assert dots.dots > 0
        assert dots.x - np.array([day_x(day) for day in range(len(RETURNS))]) == pytest.approx(
            [DOT_OFFSET] * len(RETURNS)
        )
        assert dots.y == pytest.approx(AXIS_Y + RETURN_SCALE * fitted())

    def test_the_fit_wanders_rather_than_following_a_line(self, every) -> None:
        """The regressors are factor series, not time, so the dots are far
        from any straight line across the days."""
        dots = _stroke(every[0], "fitted")
        line = np.polyval(np.polyfit(dots.x, dots.y, 1), dots.x)
        assert np.abs(dots.y - line).max() > 0.3

    def test_each_tick_joins_a_dot_to_its_bar_in_the_ink_of_its_sign(self, every) -> None:
        scene = every[0]
        dots = _stroke(scene, "fitted")
        ticks = _days(scene, "gap")
        assert len(ticks) == len(RETURNS)
        for day, tick in enumerate(ticks):
            assert tick.x == pytest.approx([dots.x[day]] * tick.points)
            assert tick.y[0] == pytest.approx(dots.y[day])
            assert tick.y[-1] == pytest.approx(AXIS_Y + RETURN_SCALE * RETURNS[day])
            assert tick.color == (GOOD if _height(tick) > 0 else LOST), tick.gid
        assert {tick.color for tick in ticks} == {GOOD, LOST}

    def test_every_tick_is_long_enough_to_see(self, every) -> None:
        """At about 68 pixels to a unit, a gap of a tenth is about 7 pixels."""
        assert min(abs(_height(tick)) for tick in _days(every[0], "gap")) > 0.1

    def test_the_gaps_sum_to_zero(self, every) -> None:
        assert float((RETURNS - fitted()).sum()) == pytest.approx(0.0, abs=1e-12)
        assert sum(_height(tick) for tick in _days(every[0], "gap")) == pytest.approx(0.0, abs=1e-9)

    def test_the_two_totals_stand_at_the_same_height_the_summed_returns(self, every) -> None:
        """Both are sums of daily returns, the Python's ``window.sum(axis=1)``,
        and not a compounded year."""
        scene = every[0]
        returns, fit = _stroke(scene, "total-returns"), _stroke(scene, "total-fitted")
        assert returns.y[0] == fit.y[0] == pytest.approx(TOTALS_BASE)
        assert _height(returns) == pytest.approx(TOTAL_SCALE * RETURNS.sum())
        assert _height(fit) == pytest.approx(_height(returns), abs=1e-12)
        compounded = float(np.prod(1 + RETURNS) - 1)
        assert abs(_height(returns) - TOTAL_SCALE * compounded) > 0.1
        assert _label(scene, "=").x == pytest.approx((returns.x[0] + fit.x[0]) / 2)

    def test_the_python_ranks_on_the_summed_returns_the_sketch_draws(self) -> None:
        """The identity the sketch draws, in the code the post's numbers come
        from: the Python's summed fitted values are each stock's summed return."""
        window = np.random.default_rng(7).normal(0, 0.02, size=(9, 40))
        assert python_expected(window) == pytest.approx(summed_returns(window), abs=1e-14)
        assert summed_returns(window) == pytest.approx(window.sum(axis=1))

    def test_the_ranked_column_falls_with_a_dot_beside_each_end(self, every) -> None:
        scene = every[0]
        assert list(RANKED) == sorted(RANKED, reverse=True)
        tops = []
        for rank, length in enumerate(RANKED):
            bar, dot = _stroke(scene, f"ranked-{rank}"), _stroke(scene, f"ranked-fit-{rank}")
            assert bar.y == pytest.approx([bar.y[0]] * bar.points)
            assert bar.x.max() - bar.x.min() == pytest.approx(length)
            assert (dot.x[0] - bar.x.max(), dot.y[0]) == (pytest.approx(DOT_OFFSET), bar.y[0])
            tops.append(bar.y[0])
        assert tops == sorted(tops, reverse=True)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "twelve black bars, some above it and some below" in alt
        assert len(RETURNS) == 12
        assert "rather than following a straight line" in alt
        assert "It is green where the return sits above the dot" in alt
        assert "red where it sits below" in alt
        assert "stand at the same height" in alt
        assert "four black bars, each with a brown dot at its end, shrink from top to bottom" in alt
        assert len(RANKED) == 4


# --- Lesson 3: a sign flip changes both members of a pair ----------------------


class TestTheSignFlipSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "A sign flip changes both members of a pair"
        assert every[1].labels == FLIP_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[1]
        for k in range(len(WEIGHTS)):
            assert _stroke(scene, f"weights-{k}").color == INK
            assert _stroke(scene, f"fresh-{k}").color == LOST
        assert _label(scene, "same direction, sign flipped").color == LOST
        for gid, ink in (
            ("pair-f", INK),
            ("pair-g", INK),
            ("pair-product", GOOD),
            ("naive-f", INK),
            ("naive-g", LOST),
            ("naive-product", LOST),
            ("flipped-f", LOST),
            ("flipped-g", LOST),
            ("flipped-product", GOOD),
            ("check", GOOD),
        ):
            assert _stroke(scene, gid).color == ink, gid
        for gid in ("base-pair", "base-naive", "base-flipped"):
            assert _stroke(scene, gid).color == MUTED, gid
        signs = [s for s in scene.steps if isinstance(s, Label) and s.text in ("+", "−")]
        assert [(s.text, s.color) for s in signs] == [("+", GOOD), ("−", LOST), ("+", GOOD)]

    def test_the_fresh_arrows_are_the_weights_reversed(self, every) -> None:
        """Same stocks, same lengths, every direction flipped."""
        scene = every[1]
        shift = PANELS[1] - PANELS[0]
        for k, weight in enumerate(WEIGHTS):
            day_t, fresh = _stroke(scene, f"weights-{k}"), _stroke(scene, f"fresh-{k}")
            assert (day_t.y[0], fresh.y[0]) == (pytest.approx(ARROW_Y), pytest.approx(ARROW_Y))
            tip = day_t.y[np.argmax(np.abs(day_t.y - ARROW_Y))]
            assert tip - ARROW_Y == pytest.approx(weight)
            assert fresh.x[0] == pytest.approx(day_t.x[0] + shift)
            assert fresh.y - ARROW_Y == pytest.approx(-(day_t.y - ARROW_Y))
        assert (WEIGHTS > 0).any() and (WEIGHTS < 0).any()

    def test_the_pair_is_day_ts_weights_on_day_t_and_on_day_t_plus_1(self, every) -> None:
        scene = every[1]
        f, g = pair()
        assert (f, g) == (pytest.approx(WEIGHTS @ DAY_T), pytest.approx(WEIGHTS @ DAY_AFTER))
        assert f > 0 and g > 0
        assert _height(_stroke(scene, "pair-f")) == pytest.approx(VALUE_SCALE * f)
        assert _height(_stroke(scene, "pair-g")) == pytest.approx(VALUE_SCALE * g)
        assert _height(_stroke(scene, "pair-product")) == pytest.approx(PRODUCT_SCALE * f * g)

    def test_fresh_weights_read_f_then_minus_g_and_the_product_turns_negative(self, every) -> None:
        scene = every[1]
        f, g = pair()
        assert -WEIGHTS @ DAY_AFTER == pytest.approx(-g)
        assert _height(_stroke(scene, "naive-f")) == pytest.approx(VALUE_SCALE * f)
        assert _height(_stroke(scene, "naive-g")) == pytest.approx(-VALUE_SCALE * g)
        product = _height(_stroke(scene, "naive-product"))
        assert product == pytest.approx(-_height(_stroke(scene, "pair-product")))
        assert product < 0

    def test_a_flip_reverses_both_members_and_keeps_the_product(self, every) -> None:
        scene = every[1]
        f, g = pair()
        assert (-WEIGHTS @ DAY_T, -WEIGHTS @ DAY_AFTER) == (pytest.approx(-f), pytest.approx(-g))
        assert _height(_stroke(scene, "flipped-f")) == pytest.approx(-VALUE_SCALE * f)
        assert _height(_stroke(scene, "flipped-g")) == pytest.approx(-VALUE_SCALE * g)
        assert _height(_stroke(scene, "flipped-product")) == pytest.approx(
            _height(_stroke(scene, "pair-product"))
        )

    def test_every_bar_stands_on_its_panels_base(self, every) -> None:
        scene = every[1]
        for gid in [
            s.gid for s in scene.strokes if s.gid.split("-")[0] in ("pair", "naive", "flipped")
        ]:
            if gid == "pair-bracket":
                continue
            assert _stroke(scene, gid).y[0] == pytest.approx(VALUE_BASE), gid

    def test_each_letter_sits_beyond_the_base_from_its_bar(self, every) -> None:
        """A bar standing up has its name below the base, and one hanging down
        has it above, so no name sits on its bar."""
        scene = every[1]
        letters = [
            s
            for s in scene.steps
            if isinstance(s, Label) and s.text in ("f", "g", "−f", "−g", "f·g", "f·(−g)")
        ]
        assert len(letters) == 8
        for label in letters:
            bar = _stroke(scene, label.names)
            assert label.x == pytest.approx(bar.x[0]), label.text
            assert (label.y < VALUE_BASE) == (_height(bar) > 0), label.text

    def test_a_flip_moves_no_uncentred_correlation(self) -> None:
        """The statistic the run reports, Σfg/√(Σf²Σg²), on made-up pairs:
        flipping both members of one pair leaves it where it was, while
        flipping only one member, as fresh weights would, moves it."""
        rng = np.random.default_rng(11)
        today, tomorrow = rng.normal(size=40), rng.normal(size=40)
        both_today, both_tomorrow = today.copy(), tomorrow.copy()
        both_today[5] *= -1
        both_tomorrow[5] *= -1
        assert uncentred(both_today, both_tomorrow) == pytest.approx(uncentred(today, tomorrow))
        one = tomorrow.copy()
        one[5] *= -1
        assert uncentred(today, one) != pytest.approx(uncentred(today, tomorrow))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "six black arrows, some up and some down" in alt
        assert len(WEIGHTS) == 6
        assert "the same six arrows are drawn again in red with every direction reversed" in alt
        assert "a black bar marked “f” stands up and a red bar marked “−g” hangs down" in alt
        assert "hangs down in red" in alt
        assert "red bars marked “−f” and “−g” both hang down" in alt
        assert "stands up as tall as the first product" in alt
        assert "beside a green check" in alt
