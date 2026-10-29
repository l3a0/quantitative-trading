"""The pins for the two whiteboard GIFs in the capped Kelly allocation post.

One sketches Lesson 2's point that the corner's extra return outweighs its
extra drag, and one Lesson 4's point that the line ``F1 + F2 = 2`` fixes the
gross leverage only between its two corners. What is pinned is what a reader
takes from each.

1. The return-against-drag sketch draws two columns, the proportional split
   and the corner, each a green bar up to its return, a red segment down from
   the bar's top by its drag and a black tick at its growth rate. What is
   pinned is that every mark sits at an affine function of its figure on one
   scale shared by both columns, that the green bracket spans the two tops
   and the red bracket the top 0.147014 of the corner's red segment, and the
   figures it prints: 0.914785, 0.097986, 0.816798, 1.2, 0.245, 0.955,
   0.285215, 0.147014 and 0.138202.
2. The gross-against-net sketch draws F1 across and F2 up in equal units.
   What is pinned is that the pale green tint stays inside the triangle
   whose gross leverage is at most the cap and that its green edge runs
   round that triangle, that every point of the black line, the green
   stretch and the red stretch lies on ``F1 + F2 = cap``, that the green
   stretch runs from (2, 0) to the corner and the red one from the corner
   past the unbounded peak, that the green dot sits on the corner and the
   hollow red circle round the peak, and the figures it prints: 0.955,
   0.962956 and 2.578643.

Every figure a sketch prints is read from the run, so the tests compute each
again through :mod:`chan.kelly_allocation`'s own functions rather than
trusting :class:`SketchFigures`. Made-up figures check that the words, the
title and the colours follow the data.

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
from dataclasses import replace

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import kelly_allocation_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.kelly_allocation import (
    CORRELATION,
    MAX_LEVERAGE,
    MEANS,
    VOLS,
    Allocation,
    best_allocation_at_cap,
    covariance,
    growth_rate,
    kelly_leverages,
    proportional_cap,
    segment_stationary_point,
)
from chan.kelly_allocation_whiteboard import (
    BASE_Y,
    CORNER_X,
    LINE_END_F1,
    PER_LEVERAGE,
    PER_UNIT,
    SPLIT_X,
    SketchFigures,
    Terms,
    at,
    figure,
    gif_name,
    main,
    make_kelly_allocation_whiteboards,
    scenes,
    sketch_timeline,
    value_y,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    HOLD_MS,
    REJECT_TINT,
    TINT,
    TITLE_MS,
    WIDTH,
    Fill,
    Frame,
    Label,
    clearances,
    hand_font,
    timeline,
)

POST = REPO_ROOT / "blog" / "capped-kelly-allocation-lessons.md"

#: Every GIF in the order :func:`make_kelly_allocation_whiteboards` writes them.
GIFS = [
    "kelly_allocation_sketch_return_against_drag.gif",
    "kelly_allocation_sketch_gross_against_net.gif",
]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "So the proportional split saves 0.147014 of drag",
    "The allocation is not allowed. F1 is negative",
)

SPEC = (
    "Example 8.2 as the book states it: means 0.30 and 0.60, volatilities 0.26 and 0.35, "
    "correlation 0, risk-free rate 0, a cap of 2 on gross leverage, vintage none, synthetic"
)

DRAG_LABELS = [
    "proportional split",
    "corner",
    "return 0.914785",
    "drag 0.097986",
    "growth 0.816798",
    "return 1.2",
    "drag 0.245",
    "growth 0.955",
    "gives up 0.285215",
    "of return",
    "saves 0.147014 of drag",
    "corner grows faster by 0.138202",
]

NET_LABELS = [
    "F1",
    "−2",
    "2",
    "gross ≤ 2, allowed",
    "F2",
    "net = 2",
    "here net = gross",
    "corner, g = 0.955",
    "unbounded peak, g = 0.962956",
    "gross 2.578643, outside",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def figures() -> SketchFigures:
    return SketchFigures.from_run()


@pytest.fixture(scope="module")
def cov():
    return covariance(VOLS, CORRELATION)


@pytest.fixture(scope="module")
def every(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, figures):
    return make_kelly_allocation_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), figures=figures
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _fill(scene, gid):
    return next(f for f in scene.fills if f.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels_of(scene, gid):
    return [s.text for s in scene.steps if isinstance(s, Label) and s.names == gid]


def _font(monkeypatch, fallback: bool) -> None:
    if fallback:
        monkeypatch.setattr(whiteboard, "hand_font", lambda: whiteboard.FALLBACK_FONT)


def _boxes(scene):
    with matplotlib.rc_context(whiteboard._style()):
        canvas, artists = whiteboard._board(scene)
        whiteboard._show(scene, artists, Frame(len(scene.steps), 0, 0))
        canvas.draw()
        renderer = canvas.get_renderer()
        to_pixels = artists[0].axes.transData
        boxes = [
            (artist.get_text(), artist.get_window_extent(renderer))
            for artist in artists
            if hasattr(artist, "get_text") and artist.get_visible()
        ]
        return boxes, to_pixels


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


def _leverage(stroke) -> tuple[np.ndarray, np.ndarray]:
    """A stroke's points as (F1, F2), undoing :func:`at`."""
    origin_x, origin_y = at(0.0, 0.0)
    return (stroke.x - origin_x) / PER_LEVERAGE, (stroke.y - origin_y) / PER_LEVERAGE


# --- The figures, read from the run ----------------------------------------------


class TestTheFigures:
    """Each figure computed again here from :mod:`chan.kelly_allocation`, not
    through :class:`SketchFigures`, and pinned at the precision the post
    prints it."""

    def test_the_proportional_split(self, figures, cov) -> None:
        f = proportional_cap(kelly_leverages(MEANS, cov), MAX_LEVERAGE)
        assert figures.split.leverages == pytest.approx(tuple(f), abs=1e-15)
        assert figures.split.ret == pytest.approx(float(f @ np.asarray(MEANS)), abs=1e-15)
        assert figures.split.drag == pytest.approx(float(f @ cov @ f / 2), abs=1e-15)
        assert figures.split.growth == pytest.approx(growth_rate(f, MEANS, cov), abs=1e-15)
        assert (figure(figures.split.ret), figure(figures.split.drag)) == (
            "0.914785",
            "0.097986",
        ), SPEC
        assert figure(figures.split.growth) == "0.816798", SPEC

    def test_the_corner(self, figures, cov) -> None:
        best = best_allocation_at_cap(MEANS, cov, MAX_LEVERAGE)
        assert figures.corner.leverages == best.leverages == (0.0, 2.0)
        assert figures.corner.growth == pytest.approx(best.growth, abs=1e-15)
        assert figures.corner_growth == best.growth
        assert [figure(v) for v in (figures.corner.ret, figures.corner.drag)] == ["1.2", "0.245"]
        assert figure(figures.corner_growth) == figure(figures.corner.growth) == "0.955"

    def test_the_differences(self, figures) -> None:
        assert figure(figures.given_up) == "0.285215", SPEC
        assert figure(figures.saved) == "0.147014", SPEC
        assert figure(figures.faster) == "0.138202", SPEC
        assert figures.faster == pytest.approx(figures.given_up - figures.saved, abs=1e-15)

    def test_the_unbounded_peak(self, figures, cov) -> None:
        raw = segment_stationary_point(MEANS, cov, MAX_LEVERAGE)
        assert figures.peak.leverages == (MAX_LEVERAGE - raw, raw)
        assert figures.peak.growth == growth_rate((MAX_LEVERAGE - raw, raw), MEANS, cov)
        assert figures.peak.gross == pytest.approx(abs(MAX_LEVERAGE - raw) + abs(raw))
        assert [figure(v) for v in (*figures.peak.leverages, figures.peak.growth)] == [
            "−0.289321",
            "2.289321",
            "0.962956",
        ], SPEC
        assert figure(figures.peak.gross) == "2.578643", SPEC
        assert figures.peak_outside and figures.cap == MAX_LEVERAGE

    def test_a_figure_drops_trailing_zeros_and_writes_a_typographic_minus(self) -> None:
        assert [figure(v) for v in (1.2, 0.245, 2.0, -0.5, 0.9147846)] == [
            "1.2",
            "0.245",
            "2",
            "−0.5",
            "0.914785",
        ]


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

    def test_every_label_names_a_stroke_or_tint_drawn_before_it(self, every) -> None:
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

    def test_every_pale_tint_has_an_edge_in_its_ink(self, every) -> None:
        """A tint stands about 1.3 to 1 against the white board, under WCAG
        2.1's 3 to 1 for a graphical object, so each tinted bar gets an edge
        round its rectangle, green for the pale green and red for the pale red."""
        scene = every[0]
        assert scene.fills
        for fill in scene.fills:
            ink = {TINT: GOOD, REJECT_TINT: LOST}[fill.color]
            edge = _stroke(scene, f"{fill.gid}-edge")
            assert edge.color == ink and edge.width >= 1.0, fill.gid
            assert (edge.x.min(), edge.x.max()) == pytest.approx((fill.x0, fill.x1)), fill.gid
            assert (edge.y.min(), edge.y.max()) == pytest.approx((fill.y0, fill.y1)), fill.gid
        assert not every[1].fills


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
            for text, box in _boxes(scene)[0]:
                inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                assert inside >= INSIDE_PX, (scene.title, text, round(inside, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_no_two_labels_touch(self, every, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in every:
            boxes = _boxes(scene)[0]
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
        """Each label and tint alone for 0.9 s and the drawing for 12 s, the
        equity post's slow pace, in both sketches. A tint here is a fill, which
        only Lesson 2's sketch has, since Lesson 4's triangle is a stroke."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("return_against_drag", "gross_against_net")
        for scene in every:
            frames = sketch_timeline(scene)
            shown_whole = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label | Fill)
            ]
            # Every label and tint but the last step, which the hold covers.
            expected = {
                k + 1 for k, step in enumerate(scene.steps) if isinstance(step, Label | Fill)
            } - {len(scene.steps)}
            assert {f.done for f in shown_whole} == expected, scene.slug
            assert any(isinstance(scene.steps[k - 1], Fill) for k in expected) == bool(
                scene.fills
            ), scene.slug
            assert {f.ms for f in shown_whole} == {sketches.PACED_LABEL_MS}, scene.slug
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, figures) -> None:
        again = make_kelly_allocation_whiteboards(out_dir=tmp_path, figures=figures)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "kelly_allocation.png").exists()

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
            ), f"{path.name}: redraw with: uv run python -m chan.kelly_allocation_whiteboard"


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
        paragraphs = _paragraphs()
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_sits_in_its_lesson(self) -> None:
        text = POST.read_text(encoding="utf-8")
        drag, net = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lessons = [text.index(f"## Lesson {k}:") for k in (2, 3, 4, 5)]
        assert lessons[0] < drag < lessons[1]
        assert lessons[2] < net < lessons[3]

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        for scene in every:
            alt, at_ = _alt(scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at_)
                assert found >= 0, (scene.slug, label)
                at_ = found + len(label) + 2

    def test_each_alt_text_names_its_pace_and_its_scale(self, every) -> None:
        drag, net = (_alt(scene) for scene in every)
        for alt in (drag, net):
            assert "drawn slowly" in alt and "twelve seconds" in alt
        assert "every part to one scale" in drag
        assert "to one scale in equal units" in net

    def test_the_module_says_neither_sketch_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "Neither sketch is schematic." in doc


# --- Lesson 2: return against drag ------------------------------------------------


#: Made-up figures where spreading the cap wins, so the title, the closing
#: line and its colour should all turn round.
SPREAD_WINS = replace(
    SketchFigures.from_run(),
    split=Terms((1.0, 1.0), 0.9, 0.1, 0.8),
    corner=Terms((0.0, 2.0), 1.0, 0.3, 0.7),
)


class TestTheReturnAgainstDragSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "The split saves less drag than it gives up in return"
        assert every[0].labels == DRAG_LABELS

    def test_its_words_follow_the_figures(self) -> None:
        scene = scenes(SPREAD_WINS)[0]
        assert scene.title == "The split saves more drag than it gives up in return"
        assert scene.labels[-1] == "proportional split grows faster by 0.1"
        assert _label(scene, scene.labels[-1]).color == ACCENT
        assert scene.labels[2:8] == [
            "return 0.9",
            "drag 0.1",
            "growth 0.8",
            "return 1",
            "drag 0.3",
            "growth 0.7",
        ]
        assert scene.labels[8] == "gives up 0.1" and scene.labels[10] == "saves 0.2 of drag"

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert {s.gid: s.color for s in scene.strokes} == {
            "baseline": MUTED,
            "split-return-edge": GOOD,
            "split-drag-edge": LOST,
            "split-growth": INK,
            "corner-return-edge": GOOD,
            "corner-drag-edge": LOST,
            "corner-growth": INK,
            "guide": MUTED,
            "given-up": GOOD,
            "saved": LOST,
        }
        assert {f.gid: f.color for f in scene.fills} == {
            "split-return": TINT,
            "split-drag": REJECT_TINT,
            "corner-return": TINT,
            "corner-drag": REJECT_TINT,
        }
        assert [_label(scene, text).color for text in DRAG_LABELS] == [
            ACCENT,
            GOOD,
            GOOD,
            LOST,
            INK,
            GOOD,
            LOST,
            INK,
            GOOD,
            GOOD,
            LOST,
            GOOD,
        ]
        assert _stroke(scene, "guide").dashed

    def test_each_label_names_the_mark_it_reads(self, every) -> None:
        scene = every[0]
        for name, offset in (("split", 2), ("corner", 5)):
            assert _labels_of(scene, f"{name}-return") == [DRAG_LABELS[offset]]
            assert _labels_of(scene, f"{name}-drag") == [DRAG_LABELS[offset + 1]]
            assert _labels_of(scene, f"{name}-growth") == [
                DRAG_LABELS[offset + 2],
                *(["corner grows faster by 0.138202"] if name == "corner" else []),
            ]
        assert _labels_of(scene, "given-up") == DRAG_LABELS[8:10]
        assert _labels_of(scene, "saved") == [DRAG_LABELS[10]]

    @pytest.mark.parametrize("which", ["run", "made up"])
    def test_every_mark_sits_at_its_figure_on_one_scale(self, every, which) -> None:
        """The bar from the baseline to the return, the red segment from the
        growth rate to the return, and the tick at the growth rate, each at
        ``BASE_Y + PER_UNIT * value`` in both columns."""
        figs = SketchFigures.from_run() if which == "run" else SPREAD_WINS
        scene = every[0] if which == "run" else scenes(SPREAD_WINS)[0]
        for name, x, terms in (("split", SPLIT_X, figs.split), ("corner", CORNER_X, figs.corner)):
            bar, drag = _fill(scene, f"{name}-return"), _fill(scene, f"{name}-drag")
            assert (bar.x0, bar.x1) == (drag.x0, drag.x1) == x
            assert bar.y0 == pytest.approx(BASE_Y)
            assert bar.y1 == pytest.approx(BASE_Y + PER_UNIT * terms.ret)
            assert drag.y1 == pytest.approx(bar.y1)
            assert drag.y1 - drag.y0 == pytest.approx(PER_UNIT * terms.drag)
            tick = _stroke(scene, f"{name}-growth")
            assert tick.y == pytest.approx(np.full(tick.points, BASE_Y + PER_UNIT * terms.growth))
            assert tick.x.min() < x[0] and tick.x.max() > x[1]
            assert drag.y0 == pytest.approx(tick.y[0])
        baseline = _stroke(scene, "baseline")
        assert baseline.y == pytest.approx(np.full(baseline.points, BASE_Y))
        assert baseline.x.min() < SPLIT_X[0] and baseline.x.max() > CORNER_X[1]

    def test_the_return_bracket_spans_the_two_tops_from_the_guide(self, every, figures) -> None:
        scene = every[0]
        guide, bracket = _stroke(scene, "guide"), _stroke(scene, "given-up")
        split_top, corner_top = value_y(figures.split.ret), value_y(figures.corner.ret)
        assert guide.y == pytest.approx(np.full(guide.points, split_top))
        assert guide.x.min() == pytest.approx(SPLIT_X[1])
        assert guide.x.max() == pytest.approx(bracket.x.min())
        assert (bracket.y.min(), bracket.y.max()) == pytest.approx((split_top, corner_top))
        assert bracket.y.max() - bracket.y.min() == pytest.approx(PER_UNIT * figures.given_up)
        assert bracket.x.max() < CORNER_X[0]
        for text in DRAG_LABELS[8:10]:
            label = _label(scene, text)
            assert label.ha == "right" and label.x < bracket.x.min() and label.y > split_top

    def test_the_drag_bracket_spans_the_top_of_the_corners_red_segment(
        self, every, figures
    ) -> None:
        """Its span is the 0.147014 of drag the split saves, the part of the
        corner's red segment beyond the split's own drag."""
        scene = every[0]
        bracket, red = _stroke(scene, "saved"), _fill(scene, "corner-drag")
        assert bracket.y.max() == pytest.approx(red.y1)
        assert bracket.y.max() - bracket.y.min() == pytest.approx(PER_UNIT * figures.saved)
        assert bracket.y.min() - red.y0 == pytest.approx(PER_UNIT * figures.split.drag)
        assert bracket.x.min() > CORNER_X[1]
        label = _label(scene, DRAG_LABELS[10])
        assert label.x > bracket.x.max()
        assert bracket.y.min() < label.y < bracket.y.max()

    def test_each_columns_figures_sit_beside_it(self, every) -> None:
        """Beside the split the three figures read down in the order the
        column stacks them, return over drag over growth. Beside the corner
        the drag sits above the growth tick and the growth below it."""
        scene = every[0]
        for text in DRAG_LABELS[2:5]:
            label = _label(scene, text)
            assert label.ha == "right" and label.x < SPLIT_X[0], text
        ret, drag, growth = (_label(scene, text).y for text in DRAG_LABELS[2:5])
        assert ret > drag > growth
        tick = _stroke(scene, "corner-growth").y[0]
        assert _label(scene, DRAG_LABELS[6]).y > tick > _label(scene, DRAG_LABELS[7]).y
        returned = _label(scene, "return 1.2")
        assert returned.ha == "center" and returned.x == pytest.approx(sum(CORNER_X) / 2)
        assert returned.y > _fill(scene, "corner-return").y1
        for text in DRAG_LABELS[6:8]:
            label = _label(scene, text)
            assert label.ha == "left" and label.x > CORNER_X[1], text
        for name, x in (("proportional split", SPLIT_X), ("corner", CORNER_X)):
            label = _label(scene, name)
            assert label.x == pytest.approx(sum(x) / 2) and label.y < BASE_Y

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[0])
        for phrase in (
            "A grey baseline carries two columns",
            "named “proportional split” in brown and “corner” in green",
            "a pale green bar with a green edge, rising from the baseline to its return",
            "A pale red segment with a red edge hangs down from the bar’s top by its drag",
            "a black tick crosses the column where the drag ends, at its growth rate",
            "A dashed grey guide carries the proportional split’s top across to the corner",
            "a green bracket spans the gap between the two tops",
            "A red bracket beside the top of the corner’s red segment spans the part of its "
            "drag beyond the proportional split’s",
            "A closing green line",
        ):
            assert phrase in alt, phrase

    def test_its_alt_text_places_each_figure_where_the_picture_does(self, every, figures) -> None:
        """Each position word is read from the scene: which column is taller,
        and which side of its column each column's figures sit."""
        alt, scene = _alt(every[0]), every[0]
        taller = "taller" if figures.corner.ret > figures.split.ret else "shorter"
        returned = _label(scene, "return 1.2")
        above = "above" if returned.y > _fill(scene, "corner-return").y1 else "below"
        left = "Left" if _label(scene, DRAG_LABELS[2]).x < SPLIT_X[0] else "Right"
        right = "right" if _label(scene, DRAG_LABELS[7]).x > CORNER_X[1] else "left"
        for phrase in (
            f"The corner’s column stands {taller}, with “return 1.2” {above} it",
            f"{left} of the proportional split’s column the words read",
            f"and “growth 0.955” to its {right}",
        ):
            assert phrase in alt, phrase


# --- Lesson 4: gross against net ------------------------------------------------


#: Made-up figures whose unbounded peak sits inside the cap, so its words and
#: its colour should follow.
PEAK_INSIDE = replace(
    SketchFigures.from_run(),
    peak=Allocation((0.4, 1.6), 0.9),
)


#: Made-up figures with a cap of 3, so every figure and tint that reads the
#: cap should follow it.
CAP_THREE = replace(SketchFigures.from_run(), cap=3.0)


class TestTheGrossAgainstNetSketch:
    def test_its_words_and_tint_follow_the_cap(self) -> None:
        scene = scenes(CAP_THREE)[1]
        assert scene.title == "F1 + F2 = 3 leaves the gross cap past the corner"
        assert scene.labels[1:4] == ["−3", "3", "gross ≤ 3, allowed"]
        assert "net = 3" in scene.labels
        f1, f2 = _leverage(_stroke(scene, "allowed"))
        assert (np.abs(f1) + f2).max() < 3.0 and (np.abs(f1) + f2).max() > 2.9
        edge = _leverage(_stroke(scene, "allowed-edge"))
        assert (edge[0].min(), edge[0].max(), edge[1].max()) == pytest.approx((-3.0, 3.0, 3.0))
        ticks = [_label(scene, text).x for text in ("−3", "3")]
        assert ticks == pytest.approx([at(-3.0, 0.0)[0], at(3.0, 0.0)[0]])

    def test_its_words(self, every) -> None:
        assert every[1].title == "F1 + F2 = 2 leaves the gross cap past the corner"
        assert every[1].labels == NET_LABELS

    def test_its_words_and_colours_follow_the_peak(self) -> None:
        scene = scenes(PEAK_INSIDE)[1]
        assert scene.labels[-2:] == ["unbounded peak, g = 0.9", "gross 2, inside"]
        assert _stroke(scene, "peak").color == GOOD
        assert {_label(scene, text).color for text in scene.labels[-2:]} == {GOOD}

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert {s.gid: s.color for s in scene.strokes} == {
            "f1-axis": MUTED,
            "allowed": TINT,
            "allowed-edge": GOOD,
            "f2-axis": MUTED,
            "net": INK,
            "equal": GOOD,
            "corner": GOOD,
            "past": LOST,
            "peak": LOST,
        }
        assert [_label(scene, text).color for text in NET_LABELS] == [
            MUTED,
            MUTED,
            MUTED,
            GOOD,
            MUTED,
            INK,
            GOOD,
            GOOD,
            LOST,
            LOST,
        ]

    def test_each_label_names_the_mark_it_reads(self, every) -> None:
        scene = every[1]
        assert _labels_of(scene, "f1-axis") == NET_LABELS[:3]
        assert _labels_of(scene, "allowed-edge") == [NET_LABELS[3]]
        assert _labels_of(scene, "f2-axis") == [NET_LABELS[4]]
        assert _labels_of(scene, "net") == [NET_LABELS[5]]
        assert _labels_of(scene, "equal") == [NET_LABELS[6]]
        assert _labels_of(scene, "corner") == [NET_LABELS[7]]
        assert _labels_of(scene, "peak") == NET_LABELS[8:]

    def test_its_units_are_equal_across_and_up(self, every) -> None:
        """One unit of leverage spans the same pixels across as up, to within
        a third of a pixel, because the board is 10 units by 4.7 at 680 by 320."""
        _, to_pixels = _boxes(every[1])
        (x0, y0), (x1, _), (_, y2) = to_pixels.transform([at(0, 0), at(1, 0), at(0, 1)])
        assert abs((x1 - x0) - (y2 - y0)) < 1 / 3

    def test_the_axes_reach_past_the_triangle(self, every) -> None:
        scene = every[1]
        f1, f2 = _leverage(_stroke(scene, "f1-axis")), _leverage(_stroke(scene, "f2-axis"))
        assert f1[0][0] == pytest.approx(-2.2) and f1[0].max() == pytest.approx(2.2)
        assert f2[0][0] == pytest.approx(0.0) and f2[1].max() == pytest.approx(2.6)
        assert f2[1][0] == pytest.approx(0.0) and f1[1][0] == pytest.approx(0.0)

    def test_the_tint_stays_inside_the_triangle_and_fills_it(self, every, figures) -> None:
        """Every point of the pale green rows has a gross leverage below the
        cap and an F2 above 0, by at least half the pen, and the rows reach
        within a few pixels of each slanted side and of the top."""
        tint = _stroke(every[1], "allowed")
        f1, f2 = _leverage(tint)
        pen = tint.width * whiteboard.DPI / 72 / sketches.PIXELS_PER_UNIT / PER_LEVERAGE
        assert (np.abs(f1) + f2).max() <= figures.cap - pen / 2 * math.sqrt(2) + 1e-9
        assert f2.min() >= pen / 2 - 1e-9
        assert (np.abs(f1) + f2).max() > figures.cap - 0.1 and f2.max() > figures.cap - 0.1
        rows = np.unique(np.round(f2, 9))
        gap = np.diff(rows).max() * PER_LEVERAGE * sketches.PIXELS_PER_UNIT
        assert gap < tint.width * whiteboard.DPI / 72

    def test_the_green_edge_runs_round_the_triangle(self, every, figures) -> None:
        edge = _stroke(every[1], "allowed-edge")
        f1, f2 = _leverage(edge)
        cap = figures.cap
        assert (np.abs(f1) + f2).max() == pytest.approx(cap)
        assert f2.min() == pytest.approx(0.0) and f2.max() == pytest.approx(cap)
        assert (f1.min(), f1.max()) == pytest.approx((-cap, cap))
        on_side = np.isclose(np.abs(f1) + f2, cap) | np.isclose(f2, 0.0)
        assert on_side.all()

    @pytest.mark.parametrize("gid", ["net", "equal", "past"])
    def test_every_point_of_the_line_has_a_net_of_the_cap(self, every, figures, gid) -> None:
        f1, f2 = _leverage(_stroke(every[1], gid))
        assert f1 + f2 == pytest.approx(np.full(len(f1), figures.cap))

    def test_the_stretches_split_at_the_corner(self, every, figures) -> None:
        """Green from (cap, 0) to the corner, where net equals gross, and red
        from the corner past the unbounded peak, where it does not."""
        scene = every[1]
        corner = figures.corner.leverages
        net = _leverage(_stroke(scene, "net"))
        equal = _leverage(_stroke(scene, "equal"))
        past = _leverage(_stroke(scene, "past"))
        assert (net[0][0], net[1][0]) == pytest.approx((figures.cap, 0.0))
        assert (net[0][-1], net[1][-1]) == pytest.approx((LINE_END_F1, figures.cap - LINE_END_F1))
        assert (equal[0][0], equal[1][0]) == pytest.approx((figures.cap, 0.0))
        assert (equal[0][-1], equal[1][-1]) == pytest.approx(corner)
        assert (equal[0].min(), past[0].max()) == pytest.approx((0.0, 0.0))
        assert (past[0][0], past[1][0]) == pytest.approx(corner)
        assert (past[0][-1], past[1][-1]) == pytest.approx((net[0][-1], net[1][-1]))
        assert past[0][-1] < figures.peak.leverages[0] < 0
        gross_equal = np.abs(equal[0]) + np.abs(equal[1])
        assert gross_equal == pytest.approx(np.full(len(gross_equal), figures.cap))
        assert (np.abs(past[0][1:]) + np.abs(past[1][1:]) > figures.cap).all()
        assert _stroke(scene, "equal").width > _stroke(scene, "net").width
        assert _stroke(scene, "past").width > _stroke(scene, "net").width

    def test_the_dot_sits_on_the_corner_and_the_circle_round_the_peak(self, every, figures) -> None:
        scene = every[1]
        dot = _stroke(scene, "corner")
        assert (dot.x[0], dot.y[0]) == pytest.approx(at(*figures.corner.leverages))
        ring = _stroke(scene, "peak")
        centre = at(*figures.peak.leverages)
        radii = np.hypot(ring.x - centre[0], ring.y - centre[1])
        assert radii == pytest.approx(np.full(ring.points, sketches.RING))
        assert (ring.x[0], ring.y[0]) == pytest.approx((ring.x[-1], ring.y[-1]))

    def test_the_peaks_words_sit_left_of_it(self, every, figures) -> None:
        scene = every[1]
        x, y = at(*figures.peak.leverages)
        first, second = (_label(scene, text) for text in NET_LABELS[8:])
        assert first.ha == second.ha == "right"
        assert first.x < x and second.x < x
        assert first.y == pytest.approx(y) and second.y < first.y

    def test_each_axis_is_named_at_its_arrow_tip(self, every) -> None:
        """F1 sits just past the right end of the axis across, and F2 level
        with the top of the axis up, beside it."""
        scene = every[1]
        f1_axis, f2_axis = _stroke(scene, "f1-axis"), _stroke(scene, "f2-axis")
        f1, f2 = _label(scene, "F1"), _label(scene, "F2")
        assert f1.x > f1_axis.x.max() and f1.x - f1_axis.x.max() < 0.5
        assert f1.y == pytest.approx(at(0.0, 0.0)[1])
        assert f2.y == pytest.approx(f2_axis.y.max())
        assert f2.x > f2_axis.x.max() and f2.x - f2_axis.x.max() < 0.5

    def test_the_line_runs_past_the_peak_and_stops_short_of_the_axis_tip(self, figures) -> None:
        assert LINE_END_F1 < figures.peak.leverages[0]
        assert figures.cap - LINE_END_F1 < sketches.F2_REACH

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[1])
        for phrase in (
            "A grey axis runs across",
            "a triangle with corners at −2 and 2 on that axis and its top at F2 = 2 is shaded "
            "pale green with a green edge",
            "the region where the gross leverage is at most 2",
            "A grey axis rises through the triangle’s top",
            "A black line",
            "redrawn green",
            "a green dot marks the triangle’s top",
            "The stretch past the corner is redrawn red",
            "a hollow red circle on it, outside the triangle, marks the unbounded peak",
        ):
            assert phrase in alt, phrase

    def test_its_alt_text_places_each_mark_where_the_picture_does(self, every, figures) -> None:
        """Each position word is read from the scene: where the black line
        ends and its label sits, which edge the green stretch runs along,
        which half of the diamond is tinted, and where the tint's label sits."""
        alt, scene = _alt(every[1]), every[1]
        net = _leverage(_stroke(scene, "net"))
        end = "upper left" if net[0][-1] < 0 < net[1][-1] - net[1][0] else "upper right"
        net_label = _label(scene, "net = 2")
        upper = "upper" if net_label.y > at(0.0, figures.cap)[1] else "lower"
        equal = _leverage(_stroke(scene, "equal"))
        edge = "right" if equal[0].min() >= 0 else "left"
        tint = _leverage(_stroke(scene, "allowed"))
        half = "upper" if tint[1].min() > 0 else "lower"
        allowed = _label(scene, "gross ≤ 2, allowed")
        under = "under" if allowed.y < at(0.0, 0.0)[1] else "above"
        for phrase in (
            f"labelled “net = 2” at its {upper} end",
            f"on past it to the {end}",
            f"Its stretch along the triangle’s {edge} edge",
            f"It is the {half} half of the region where the gross leverage is at most 2",
            f"labelled “gross ≤ 2, allowed” {under} the axis",
        ):
            assert phrase in alt, phrase
