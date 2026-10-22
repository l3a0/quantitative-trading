"""The pins for the two whiteboard GIFs in the post on Chan's Johansen test on three ETFs.

One sketches Lesson 3, the trace statistic stacking the eigen statistics, and
one Lesson 4, the pair's two relations spanning EWA held alone.

The trace-stack sketch draws the triplet's Johansen test, which
:mod:`chan.etf_cointegration` computes from the committed vintage, so its
tests read the run itself. The vintage is ``inputdata_etf/``, Chan's
``inputData_ETF.mat`` saved 2012-04-10, read for EWA, EWC and IGE through
``chan.series.load_panel``. The specification is ``cointegrationTests.m``'s
``johansen([y, x, z], 0, 1)``, columns EWC, EWA, IGE.
``tests/test_etf_cointegration.py`` pins the same statistics and critical
values against Chan's printout. What is pinned here is that the sketch draws
them: each block's height is affine in its statistic, the stack's top is the
trace statistic, each bar sits at its critical value, and made-up figures move
the marks and the words.

The two-relations sketch is schematic and carries no figures, so what is
pinned for it is what a reader takes from it: two relations pointing different
ways, EWA alone as the far corner of the parallelogram they make, and the
test's claim stated as a condition.

The rules every sketch shares are pinned too: no label touches a line, leaves
the board or touches another label, in the installed hand font and in the
wider fallback, each file's size, frame count, loop and timing, and its place
in the post right after the paragraph it draws, with alt text that quotes its
labels in drawing order.

Two draws on one machine give the same bytes. Whether a committed GIF equals a
fresh draw depends on the font, as ``tests/test_usdcad_tests_whiteboard.py``
explains, so that comparison runs only on macOS arm64 with Comic Sans MS.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import platform
import re

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import etf_cointegration_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.etf_cointegration import etf_cointegration, read_sources
from chan.etf_cointegration_whiteboard import (
    FLOOR,
    SCALE,
    StackRefused,
    TraceStack,
    _trace_stack,
    _two_relations,
    gif_name,
    main,
    make_etf_cointegration_whiteboards,
    scenes,
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

POST = REPO_ROOT / "blog" / "johansen-etf-lessons.md"

GIFS = ["etf_cointegration_trace_stack.gif", "etf_cointegration_two_relations.gif"]
#: The opening words of the paragraph each GIF follows, in the same order.
FOLLOWS = (
    "The first eigenvalue alone is not strong enough",
    "Chan reads the two relations as two hedge ratios",
)

STACK_LABELS = [
    "16.897",
    "eigen test, r ≤ 0",
    "90% eigen bar, 18.893",
    "falls short",
    "the same piece",
    "16.897",
    "trace test, r ≤ 0",
    "+ 13.061",
    "+ 4.471",
    "95% trace bar, 29.796",
    "34.429 clears it",
]
RELATION_LABELS = [
    "shares of EWA",
    "shares of EWC",
    "relation 1",
    "relation 2",
    "a mix of relations 1 and 2",
    "EWA alone (1, 0)",
    "if both relations revert, so does EWA alone",
]

#: Made-up figures that keep the sketch's words true, so a mark or a word that
#: should follow the run's figures is seen to.
OTHER = TraceStack(pieces=(12.0, 10.0, 6.0), trace=28.0, eigen_bar=15.0, trace_bar=22.0)

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def result():
    return etf_cointegration(read_sources()[1])


@pytest.fixture(scope="module")
def stack(result):
    return TraceStack.from_run(result)


@pytest.fixture(scope="module")
def every(stack):
    return scenes(stack)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, stack):
    return make_etf_cointegration_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), stack=stack
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _labels(scene, text):
    return [s for s in scene.steps if isinstance(s, Label) and s.text == text]


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

    def test_neither_carries_a_tint(self, every) -> None:
        """A pale tint needs a green edge to read, as the equity seasonals
        module's ``_tinted`` draws. These two carry none, so none is owed."""
        assert [scene.fills for scene in every] == [[], []]


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
            steps = timeline(scene)
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(path) == [f.ms for f in steps], path.name

    def test_each_opens_on_its_title_and_holds_its_drawing(self, every) -> None:
        for scene in every:
            steps = timeline(scene)
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            assert steps[-1].ms == HOLD_MS, scene.slug

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, stack) -> None:
        again = make_etf_cointegration_whiteboards(out_dir=tmp_path, stack=stack)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, every) -> None:
        for name, scene in zip(GIFS, every, strict=True):
            steps = timeline(scene)
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
            ), f"{path.name}: redraw with: uv run python -m chan.etf_cointegration_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(self, monkeypatch, capsys, stack) -> None:
        written = []

        def write(scene, folder):
            written.append((scene.slug, folder))
            return folder / gif_name(scene)

        monkeypatch.setattr(sketches, "_write", write)
        monkeypatch.setattr(TraceStack, "read", classmethod(lambda cls: stack))
        main()
        assert [folder for _, folder in written] == [FIGURES_DIR, FIGURES_DIR]
        assert capsys.readouterr().out.splitlines() == [
            f"wrote {FIGURES_DIR / name}" for name in GIFS
        ]


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """A label drawn twice, such as the first piece's 16.897, is quoted twice."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            at = 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + 1

    def test_the_two_relations_alt_text_says_it_is_schematic(self, every) -> None:
        assert "It is schematic and carries no figures." in _alt(
            POST.read_text(encoding="utf-8"), every[1]
        )


class TestTheStackFigures:
    def test_they_are_the_triplets_test(self, stack, result) -> None:
        """Rows r ≤ 0 to r ≤ 2 of the eigen statistic, the trace statistic for
        r ≤ 0, and the 90 percent eigen and 95 percent trace critical values,
        columns 0 and 1 of :data:`chan.johansen.LEVELS`."""
        triplet = result.triplet
        assert stack.pieces == tuple(triplet.eigen)
        assert stack.trace == triplet.trace[0]
        assert stack.eigen_bar == triplet.eigen_critical[0, 0]
        assert stack.trace_bar == triplet.trace_critical[0, 1]

    def test_they_print_as_the_post_prints_them(self, stack) -> None:
        printed = [f"{v:.3f}" for v in (*stack.pieces, stack.trace, stack.eigen_bar)]
        assert printed + [f"{stack.trace_bar:.3f}"] == [
            "16.897",
            "13.061",
            "4.471",
            "34.429",
            "18.893",
            "29.796",
        ]

    @pytest.mark.parametrize(
        "changes",
        [
            {"trace": 28.5},
            {"eigen_bar": 11.0},
            {"trace_bar": 29.0},
        ],
        ids=["pieces not adding up", "first piece clearing", "stack short of its bar"],
    )
    def test_figures_the_words_would_misdescribe_are_refused(self, changes) -> None:
        with pytest.raises(StackRefused):
            dataclasses.replace(OTHER, **changes)


def _top(stroke) -> float:
    return float(stroke.y.max())


def _bottom(stroke) -> float:
    return float(stroke.y.min())


class TestTheStackSketch:
    def test_its_words(self, every) -> None:
        assert every[0].labels == STACK_LABELS

    def test_its_colours(self, every) -> None:
        """The first piece is black in both columns, the two the trace test
        adds are brown, the verdicts are red and green, and the bars and floor
        are black and grey. Each verdict is said in words too."""
        scene = every[0]
        colours = {s.gid: s.color for s in scene.strokes}
        assert colours == {
            "floor": MUTED,
            "eigen-1": INK,
            "eigen-bar": INK,
            "same": MUTED,
            "trace-1": INK,
            "trace-2": ACCENT,
            "trace-3": ACCENT,
            "trace-bar": INK,
        }
        assert [_stroke(scene, g).dashed for g in ("eigen-bar", "trace-bar")] == [True, True]
        assert _labels(scene, "falls short")[0].color == LOST
        assert _labels(scene, "34.429 clears it")[0].color == GOOD
        for text in ("+ 13.061", "+ 4.471"):
            assert _labels(scene, text)[0].color == ACCENT

    def test_each_block_is_affine_in_its_value(self, stack) -> None:
        """Every block's height is its statistic times one scale, on the run's
        figures and on made-up ones, and each piece starts where the last ends."""
        for figures in (stack, OTHER):
            scene = _trace_stack(figures)
            first, second, third = figures.pieces
            for gid, value in (
                ("eigen-1", first),
                ("trace-1", first),
                ("trace-2", second),
                ("trace-3", third),
            ):
                block = _stroke(scene, gid)
                assert _top(block) - _bottom(block) == pytest.approx(SCALE * value), gid
            assert _bottom(_stroke(scene, "eigen-1")) == _bottom(_stroke(scene, "trace-1")) == FLOOR
            assert _bottom(_stroke(scene, "trace-2")) == pytest.approx(
                _top(_stroke(scene, "trace-1"))
            )
            assert _bottom(_stroke(scene, "trace-3")) == pytest.approx(
                _top(_stroke(scene, "trace-2"))
            )

    def test_the_stacks_top_is_the_trace_statistic(self, stack) -> None:
        for figures in (stack, OTHER):
            top = _top(_stroke(_trace_stack(figures), "trace-3"))
            assert top == pytest.approx(FLOOR + SCALE * figures.trace)

    def test_each_bar_sits_at_its_critical_value(self, stack) -> None:
        for figures in (stack, OTHER):
            scene = _trace_stack(figures)
            for gid, bar in (("eigen-bar", figures.eigen_bar), ("trace-bar", figures.trace_bar)):
                line = _stroke(scene, gid)
                assert np.allclose(line.y, FLOOR + SCALE * bar), gid

    def test_the_piece_stops_short_and_the_stack_clears(self, stack) -> None:
        scene = _trace_stack(stack)
        assert _top(_stroke(scene, "eigen-1")) < _stroke(scene, "eigen-bar").y[0]
        assert _top(_stroke(scene, "trace-3")) > _stroke(scene, "trace-bar").y[0]

    def test_each_bar_spans_its_own_column(self, stack) -> None:
        """Each bar crosses the column it judges and no other, so the eye
        cannot read the eigen bar against the stack."""
        scene = _trace_stack(stack)
        for bar, block, other in (
            ("eigen-bar", "eigen-1", "trace-1"),
            ("trace-bar", "trace-1", "eigen-1"),
        ):
            line, column, away = (_stroke(scene, g) for g in (bar, block, other))
            assert line.x.min() <= column.x.min() and line.x.max() >= column.x.max(), bar
            assert line.x.max() < away.x.min() or line.x.min() > away.x.max(), bar

    def test_the_same_piece_arrow_runs_from_one_column_to_the_other(self, stack) -> None:
        scene = _trace_stack(stack)
        same, left, right = (_stroke(scene, g) for g in ("same", "eigen-1", "trace-1"))
        assert left.x.max() < same.x[0] < same.x.max() < right.x.min()
        assert _top(left) == pytest.approx(_top(right))

    def test_each_bar_names_its_level_and_the_99_percent_is_left_out(self, every) -> None:
        labels = every[0].labels
        assert [w for w in labels if "bar" in w] == [
            "90% eigen bar, 18.893",
            "95% trace bar, 29.796",
        ]
        assert not [w for w in labels if "99" in w]

    def test_other_figures_move_the_words(self) -> None:
        assert _trace_stack(OTHER).labels == [
            "12.000",
            "eigen test, r ≤ 0",
            "90% eigen bar, 15.000",
            "falls short",
            "the same piece",
            "12.000",
            "trace test, r ≤ 0",
            "+ 10.000",
            "+ 6.000",
            "95% trace bar, 22.000",
            "28.000 clears it",
        ]


class TestTheTwoRelationsSketch:
    def test_its_words(self, every) -> None:
        assert every[1].labels == RELATION_LABELS

    def test_it_is_schematic_and_takes_no_figures(self, every) -> None:
        """No label prints a decimal, and the scene is built with no input."""
        assert not [w for w in every[1].labels if re.search(r"\d\.\d", w)]
        again = _two_relations()
        assert again.labels == every[1].labels
        for drawn, redrawn in zip(every[1].strokes, again.strokes, strict=True):
            assert np.array_equal(drawn.x, redrawn.x) and np.array_equal(drawn.y, redrawn.y)

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert {s.gid: s.color for s in scene.strokes} == {
            "ewa-axis": MUTED,
            "ewc-axis": MUTED,
            "relation-1": INK,
            "relation-2": INK,
            "mix": MUTED,
            "ewa": ACCENT,
        }
        assert _stroke(scene, "mix").dashed
        assert _labels(scene, "EWA alone (1, 0)")[0].color == ACCENT

    def test_the_relations_point_different_ways_from_the_origin(self, every) -> None:
        scene = every[1]
        one, two = _stroke(scene, "relation-1"), _stroke(scene, "relation-2")
        origin = (_stroke(scene, "ewc-axis").x[0], _stroke(scene, "ewa-axis").y[0])
        assert (one.x[0], one.y[0]) == (two.x[0], two.y[0]) == origin
        a = np.array(sketches.RELATION_1) - origin
        b = np.array(sketches.RELATION_2) - origin
        assert abs(a[0] * b[1] - a[1] * b[0]) > 1.0
        assert (a[1] > 0, b[1] < 0) == (True, True)

    def test_ewa_alone_lies_on_its_axis_at_the_parallelograms_far_corner(self, every) -> None:
        """EWA alone has no EWC, so its arrow runs along the EWA axis, and it
        ends where the dashed sides, each parallel to the other relation,
        meet."""
        scene = every[1]
        o = np.array(sketches.ORIGIN)
        r1, r2 = np.array(sketches.RELATION_1), np.array(sketches.RELATION_2)
        ewa, mix = _stroke(scene, "ewa"), _stroke(scene, "mix")
        tip = np.array(sketches.EWA_ALONE)
        assert (ewa.x[0], ewa.y[0]) == tuple(o)
        assert tip[1] == o[1] and tip[0] > o[0]
        assert np.allclose(tip - r1, r2 - o) and np.allclose(tip - r2, r1 - o)
        for gid, end in (("relation-1", r1), ("relation-2", r2), ("ewa", tip)):
            arrow = _stroke(scene, gid)
            far = np.argmax(np.hypot(arrow.x - o[0], arrow.y - o[1]))
            assert np.allclose((arrow.x[far], arrow.y[far]), end), gid
        corners = {(round(x, 9), round(y, 9)) for x, y in zip(mix.x, mix.y, strict=True)}
        assert {tuple(np.round(p, 9)) for p in (r1, tip, r2)} <= corners
        assert (mix.x[0], mix.y[0], mix.x[-1], mix.y[-1]) == (*r1, *r2)

    def test_it_closes_on_the_tests_claim_as_a_condition(self, every) -> None:
        last = every[1].steps[-1]
        assert isinstance(last, Label)
        assert last.text.startswith("if both relations revert")
