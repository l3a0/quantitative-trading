"""The pins for the six whiteboard GIFs in the post on mean reversion on USD.CAD.

Each GIF sketches one scene of the post's section "The tests and the file" and
sits right after the text it draws. Its shapes are schematic, so what is pinned
here is what a reader takes from it: which scenes there are and in which order
the post reads them, what each one says and draws, that a label never appears
before the stroke it names, that no label touches a line, how long each GIF
shows before it loops, and each file's size, frame count and loop.

Two labels quote the run. The half-life scene and the linear rule's warning
print the lookback, the half-life rounded, and the count of closes. Both are
read from the run rather than written in, and the tests below hand the scenes
a run with another lookback and fewer closes to prove it. The numbers come
from the vintage and the specification ``tests/test_usdcad_mean_reversion.py``
names as its ``SPEC``, which failure messages here carry:
``pythoncodesanddata/inputData_USDCAD.csv``, vendor ``chan-py``, basis
``raw``, saved 2018-10-13, its 16:59 bar of each day, 1,216 closes and a
lookback of 115 days.

Two draws on one machine give the same bytes, and a test holds that. Whether a
committed GIF equals a fresh draw depends on the font, because the hand font
is whichever one is installed and font rasterising varies by platform. So that
comparison runs only on macOS arm64 with Comic Sans MS installed, where the
committed files were drawn, and skips elsewhere with the reason. The frame
count, the size, the loop and the timing of each committed file are pinned
everywhere.
"""

from __future__ import annotations

import dataclasses
import hashlib
import logging
import platform
import re
import warnings

import numpy as np
import pytest
from PIL import Image

from chan import usdcad_mean_reversion
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_mean_reversion import read_sources, stationarity_tests
from chan.usdcad_tests_whiteboard import (
    FRAME_MS,
    HOLD_MS,
    LABEL_MS,
    TITLE_MS,
    Label,
    Stroke,
    clearances,
    hand_font,
    main,
    make_usdcad_tests_whiteboards,
    palette,
    render,
    scenes,
    timeline,
)
from chan.vintage import VintageUnavailable
from tests.test_usdcad_mean_reversion import SPEC

TITLES = [
    "The question",
    "ADF",
    "Hurst",
    "Variance ratio",
    "Half-life",
    "The linear rule",
]

GIFS = [
    "usdcad_tests_question.gif",
    "usdcad_tests_adf.gif",
    "usdcad_tests_hurst.gif",
    "usdcad_tests_variance_ratio.gif",
    "usdcad_tests_half_life.gif",
    "usdcad_tests_linear_rule.gif",
]

#: Each scene's strokes, by their ids, in the order they are drawn.
STROKES = [
    ["mean", "price", "pull"],
    ["mean", "rise", "high", "fall"],
    ["start", "wide-up", "wide-down", "narrow-up", "narrow-down"],
    ["floor", "two-day", "one-day", "gap"],
    ["axes", "decay", "half"],
    ["mean", "price", "above", "below", "warning", "bang", "bang-dot"],
]

LABELS = [
    ["Random walk?", "Pulled back?"],
    ["high close…", "…then a fall", "λ < 0"],
    ["random walk, H = 0.5", "reverting, H < 0.5", r"variance $\sim \tau^{2H}$"],
    ["2-day variance", "2 × 1-day variance", "ratio < 1 → pulled back"],
    ["distance from the mean", "half", "≈ 115 days", "−ln 2 / λ"],
    ["z = +2 → short 2", "z = −1.5 → long 1.5", "115 days measured on all 1,216 closes"],
]

#: The frames each GIF takes, and how long one pass shows, in milliseconds.
FRAMES = [29, 31, 29, 30, 29, 32]
MS = [7350, 7800, 7600, 7700, 7850, 7900]

#: How far, in pixels, every label and title must sit from the nearest stroke.
#: The sketch's wobble moves a line a pixel or two off its points, so this
#: leaves room for it with a visible gap to spare.
CLEAR_PX = 10
#: Labels that state something about the whole scene rather than name a
#: stroke. Each stands apart from every stroke, by at least
#: :data:`APART_PX`, so it cannot be read as one curve's label. The Hurst
#: formula once sat beside the end of the lower green curve, 12 pixels from
#: it, and read as that curve's label.
STATEMENTS = {"λ < 0", r"variance $\sim \tau^{2H}$"}
APART_PX = 25


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def run(sources):
    return stationarity_tests(*sources)


@pytest.fixture(scope="module")
def drawn(run):
    return scenes(run)


@pytest.fixture(scope="module")
def frames(drawn):
    return [timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, sources):
    return make_usdcad_tests_whiteboards(
        out_dir=tmp_path_factory.mktemp("whiteboards"), sources=sources
    )


@pytest.fixture(scope="module")
def question(drawn):
    """The first scene drawn, which is enough to watch strokes and labels."""
    steps = timeline(drawn[0])
    return steps, render(drawn[0], steps)


def _durations(path) -> list[int]:
    with Image.open(path) as image:
        durations = []
        for index in range(image.n_frames):
            image.seek(index)
            durations.append(image.info["duration"])
        return durations


def _inked(image: Image.Image) -> int:
    """How many pixels are not the white board, which is palette entry 0."""
    return int((np.asarray(image) != 0).sum())


class TestTheScenes:
    def test_there_are_six_in_the_order_the_section_reads_them(self, drawn) -> None:
        assert [scene.title for scene in drawn] == TITLES

    def test_no_title_carries_a_scene_number(self, drawn) -> None:
        """Each GIF stands alone beside its own text, so a number such as
        "3" in front of "Hurst" would count scenes the reader never sees
        together."""
        for scene in drawn:
            assert not re.search(r"\d", scene.title), scene.title

    def test_each_scene_has_its_own_gif_named_for_it(self, drawn) -> None:
        assert [scene.gif for scene in drawn] == GIFS
        assert not [name for name in GIFS if re.search(r"\d", name)]

    def test_each_scene_draws_its_strokes_in_order(self, drawn) -> None:
        assert [[s.gid for s in scene.strokes] for scene in drawn] == STROKES

    def test_each_scene_says_what_it_should(self, drawn) -> None:
        assert [scene.labels for scene in drawn] == LABELS, SPEC

    def test_every_label_names_a_stroke_drawn_before_it(self, drawn) -> None:
        for scene in drawn:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if isinstance(s, Stroke)]
                    assert step.names in earlier, (scene.title, step.text)

    def test_only_the_hurst_formula_is_parsed_as_math(self, drawn) -> None:
        maths = [step.text for scene in drawn for step in scene.steps if getattr(step, "math", 0)]
        assert maths == [r"variance $\sim \tau^{2H}$"]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, drawn) -> None:
        """A stroke with fewer points than frames would repeat a frame, and the
        GIF writer merges repeated frames, which would change the count."""
        for scene in drawn:
            for stroke in scene.strokes:
                assert stroke.points >= stroke.frames, (scene.title, stroke.gid)
                assert stroke.points == len(stroke.y)


class TestTheLabelsStayClearOfTheLines:
    def test_every_label_and_title_clears_every_stroke(self, drawn) -> None:
        for scene in drawn:
            found = clearances(scene)
            assert sorted(found) == sorted([*scene.labels, scene.title])
            for text, pixels in found.items():
                assert pixels >= CLEAR_PX, (scene.title, text, round(pixels, 1))

    def test_a_statement_about_the_scene_stands_apart_from_every_curve(self, drawn) -> None:
        found = {text: px for scene in drawn for text, px in clearances(scene).items()}
        assert STATEMENTS <= set(found)
        for text in STATEMENTS:
            assert found[text] >= APART_PX, (text, round(found[text], 1))

    def test_the_hurst_formula_sits_under_the_starting_point(self, drawn) -> None:
        """Left of where the curves end and below where they start, so it
        reads as a statement about both pairs."""
        hurst = drawn[2]
        start = next(s for s in hurst.strokes if s.gid == "start")
        formula = next(s for s in hurst.steps if isinstance(s, Label) and s.math)
        assert formula.x <= start.x[0]
        assert formula.y < min(float(s.y.min()) for s in hurst.strokes)

    def test_the_measure_sees_a_label_on_a_line(self, drawn) -> None:
        """A label moved onto its own stroke reads as touching, so the two
        tests above can fail."""
        hurst = drawn[2]
        steps = tuple(
            dataclasses.replace(s, x=0.6, y=2.0) if isinstance(s, Label) and s.math else s
            for s in hurst.steps
        )
        moved = dataclasses.replace(hurst, steps=steps)
        assert clearances(moved)[r"variance $\sim \tau^{2H}$"] < 0


class TestTheNumbersComeFromTheRun:
    def test_the_run_has_1216_closes_and_a_115_day_lookback(self, run) -> None:
        assert (len(run.closes), run.lookback) == (1216, 115), SPEC
        assert round(run.half_life) == 115, SPEC

    def test_the_half_life_scene_prints_the_runs_lookback(self, run) -> None:
        other = dataclasses.replace(run, lookback=100)
        assert "≈ 100 days" in scenes(other)[4].labels
        assert "≈ 115 days" not in scenes(other)[4].labels

    def test_the_warning_prints_the_runs_lookback_and_closes(self, run) -> None:
        other = dataclasses.replace(run, lookback=100, closes=run.closes.iloc[:1000])
        assert scenes(other)[5].labels[-1] == "100 days measured on all 1,000 closes"

    def test_the_gifs_are_drawn_from_the_sources_handed_in(
        self, monkeypatch, tmp_path, sources
    ) -> None:
        """The first 800 closes have a half-life that rounds to 100 days, as
        ``tests/test_usdcad_mean_reversion_figures.py`` pins, so a GIF that
        read the file or wrote 115 in would fail here."""
        seen = []
        original = whiteboard.scenes

        def record(run):
            seen.append((run.lookback, len(run.closes)))
            return original(run)[4:5]

        monkeypatch.setattr(whiteboard, "scenes", record)
        entry, closes = sources
        make_usdcad_tests_whiteboards(out_dir=tmp_path, sources=(entry, closes[:800]))
        assert seen == [(100, 800)]


class TestTheTimeline:
    def test_each_gif_takes_the_frames_and_time_it_should(self, frames) -> None:
        assert [len(f) for f in frames] == FRAMES
        assert [sum(frame.ms for frame in f) for f in frames] == MS

    def test_each_gif_opens_on_its_title_alone(self, frames) -> None:
        for steps in frames:
            assert (steps[0].done, steps[0].partial, steps[0].ms) == (0, 0, TITLE_MS)

    def test_each_gif_holds_its_finished_drawing_for_four_seconds(self, drawn, frames) -> None:
        assert HOLD_MS == 4000
        for scene, steps in zip(drawn, frames, strict=True):
            last = steps[-1]
            assert (last.done, last.partial, last.ms) == (len(scene.steps), 0, HOLD_MS)
            assert all(frame.ms < HOLD_MS for frame in steps[:-1])

    def test_strokes_draw_at_ten_frames_a_second_and_labels_pop_in(self, drawn, frames) -> None:
        """Every frame between a GIF's title and its held last frame is a
        stroke's frame of 100 ms or a label's single frame of 350 ms."""
        for scene, steps in zip(drawn, frames, strict=True):
            for frame in steps[1:-1]:
                if frame.partial:
                    assert frame.ms == FRAME_MS
                    continue
                latest = scene.steps[frame.done - 1]
                assert frame.ms == (LABEL_MS if isinstance(latest, Label) else FRAME_MS)
        assert FRAME_MS == 100

    def test_a_label_appears_only_once_its_stroke_is_complete(self, drawn, frames) -> None:
        for scene, steps in zip(drawn, frames, strict=True):
            for frame in steps:
                complete = {s.gid for s in scene.steps[: frame.done] if isinstance(s, Stroke)}
                for step in scene.steps[: frame.done]:
                    if isinstance(step, Label):
                        assert step.names in complete, step.text

    def test_a_stroke_grows_frame_by_frame(self, drawn, frames) -> None:
        """The question's price line shows a longer prefix on each of its 14 frames."""
        price = drawn[0].steps[1]
        assert price.gid == "price"
        shown = [f.partial for f in frames[0] if f.done == 1 and f.partial]
        assert len(shown) == price.frames - 1 == 13
        assert shown == sorted(set(shown))
        assert shown[-1] < price.points


class TestTheDrawing:
    def test_ink_only_grows_within_a_scene(self, question) -> None:
        _, images = question
        inked = [_inked(image) for image in images]
        assert inked == sorted(inked)
        assert inked[0] > 0, "the title shows on the first frame"

    def test_a_partial_stroke_inks_less_than_the_whole(self, question) -> None:
        steps, images = question
        price = [k for k, f in enumerate(steps) if f.done == 1 and f.partial]
        whole = next(k for k, f in enumerate(steps) if f.done == 2)
        assert _inked(images[price[0]]) < _inked(images[price[-1]]) < _inked(images[whole])

    def test_each_label_adds_ink_on_the_frame_it_appears(self, drawn, question) -> None:
        steps, images = question
        labels = [i + 1 for i, s in enumerate(drawn[0].steps) if isinstance(s, Label)]
        for done in labels:
            k = next(k for k, f in enumerate(steps) if f.done == done and f.partial == 0)
            assert _inked(images[k]) > _inked(images[k - 1]), done

    def test_every_frame_uses_the_fixed_palette(self, question) -> None:
        _, images = question
        expected = palette().getpalette()
        for image in images:
            assert image.mode == "P"
            assert image.getpalette() == expected

    def test_the_palette_is_white_and_five_inks_at_five_blends(self) -> None:
        colours = palette().getpalette()
        assert colours[:3] == [255, 255, 255]
        assert len({tuple(colours[i : i + 3]) for i in range(0, len(colours), 3)}) == 26

    def test_no_glyph_falls_back_to_an_empty_box(self, drawn, caplog) -> None:
        """λ, ∼, ≈, −, → and × must all be drawn by some installed font."""
        with warnings.catch_warnings(record=True) as caught, caplog.at_level(logging.WARNING):
            warnings.simplefilter("always")
            for scene in drawn:
                steps = timeline(scene)
                render(scene, steps[-1:])
        messages = [str(w.message) for w in caught] + [r.getMessage() for r in caplog.records]
        assert not [m for m in messages if "glyph" in m.lower()], messages


class TestTheGifs:
    def test_there_are_six_named_for_their_scenes(self, gifs) -> None:
        assert [path.name for path in gifs] == GIFS

    def test_each_is_680_by_320_with_its_frames(self, gifs) -> None:
        for path, count in zip(gifs, FRAMES, strict=True):
            with Image.open(path) as image:
                assert (image.size, image.n_frames) == ((680, 320), count), path.name

    def test_each_loops_forever(self, gifs) -> None:
        for path in gifs:
            with Image.open(path) as image:
                assert image.info["loop"] == 0, path.name

    def test_each_frame_shows_as_long_as_the_timeline_says(self, gifs, frames) -> None:
        for path, steps, total in zip(gifs, frames, MS, strict=True):
            durations = _durations(path)
            assert durations == [f.ms for f in steps], path.name
            assert (durations[-1], sum(durations)) == (HOLD_MS, total), path.name

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, sources) -> None:
        again = make_usdcad_tests_whiteboards(out_dir=tmp_path, sources=sources)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_old_combined_gif_is_gone(self) -> None:
        assert not (FIGURES_DIR / "usdcad_tests_whiteboard.gif").exists()

    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, frames) -> None:
        for name, count, steps in zip(GIFS, FRAMES, frames, strict=True):
            committed = FIGURES_DIR / name
            with Image.open(committed) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == ((680, 320), count, 0)
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
            ), f"{path.name}: redraw with: uv run python -m chan.usdcad_tests_whiteboard"


class TestTheCommand:
    def test_it_writes_every_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []

        def draw(**kwargs):
            drawn.append(kwargs)
            return [FIGURES_DIR / name for name in GIFS]

        monkeypatch.setattr(whiteboard, "make_usdcad_tests_whiteboards", draw)
        main()
        assert drawn == [{}]
        out = capsys.readouterr().out
        assert out.splitlines() == [f"wrote {FIGURES_DIR / name}" for name in GIFS]

    def test_drawing_with_no_out_dir_writes_the_committed_paths(self, monkeypatch, sources) -> None:
        saved = []
        monkeypatch.setattr(whiteboard, "read_sources", lambda: sources)
        monkeypatch.setattr(whiteboard, "render", lambda scene, frames: [Image.new("P", (1, 1))])
        monkeypatch.setattr(Image.Image, "save", lambda self, path, **kw: saved.append(path))
        paths = make_usdcad_tests_whiteboards()
        assert paths == saved == [FIGURES_DIR / name for name in GIFS]

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage of USDCAD saved 2018-10-13"),
            WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2008-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(whiteboard, "make_usdcad_tests_whiteboards", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2009-01-02")

        monkeypatch.setattr(usdcad_mean_reversion, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale on 2009-01-02"):
            make_usdcad_tests_whiteboards(out_dir=tmp_path)
