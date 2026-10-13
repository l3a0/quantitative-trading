"""The pins for the whiteboard GIF in the post on mean reversion on USD.CAD.

The GIF sketches the post's section "The tests and the file" in six scenes. Its
shapes are schematic, so what is pinned here is what a reader takes from it:
which scenes come in which order, what each one says, that a label never
appears before the stroke it names, how long each scene shows, and the file's
size, frame count and loop.

Two labels quote the run. The half-life scene and the linear rule's warning
print the lookback, the half-life rounded, and the count of closes. Both are
read from the run rather than written in, and the tests below hand the scenes
a run with another lookback and fewer closes to prove it. The numbers come
from the vintage and the specification ``tests/test_usdcad_mean_reversion.py``
names as its ``SPEC``, which failure messages here carry:
``pythoncodesanddata/inputData_USDCAD.csv``, vendor ``chan-py``, basis
``raw``, saved 2018-10-13, its 16:59 bar of each day, 1,216 closes and a
lookback of 115 days.

Two draws on one machine give the same bytes, and a test holds that. Whether
the committed GIF equals a fresh draw depends on the font, because the hand
font is whichever one is installed and font rasterising varies by platform.
So that comparison runs only on macOS arm64 with Comic Sans MS installed,
where the committed file was drawn, and skips elsewhere with the reason. The
frame count, the size, the loop and the timing of the committed file are
pinned everywhere.
"""

from __future__ import annotations

import dataclasses
import hashlib
import logging
import platform
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
    WHITEBOARD_GIF,
    Label,
    Stroke,
    hand_font,
    main,
    make_usdcad_tests_whiteboard,
    palette,
    render,
    scenes,
    timeline,
)
from chan.vintage import VintageUnavailable
from tests.test_usdcad_mean_reversion import SPEC

TITLES = [
    "1  The question",
    "2  ADF",
    "3  Hurst",
    "4  Variance ratio",
    "5  Half-life",
    "6  The linear rule",
]

LABELS = [
    ["Random walk?", "Pulled back?"],
    ["high close…", "…then a fall", "λ < 0"],
    ["random walk, H = 0.5", "reverting, H < 0.5", r"variance $\sim \tau^{2H}$"],
    ["2-day variance", "2 × 1-day variance", "ratio < 1 → pulled back"],
    ["distance from the mean", "half", "≈ 115 days", "−ln 2 / λ"],
    [
        "z = +2 → short 2",
        "z = −1.5 → long 1.5",
        "!",
        "115 days measured on all 1,216 closes",
    ],
]

#: The frames the six scenes take, and how long each scene shows, in seconds.
FRAMES = 178
SECONDS = [5.1, 5.55, 5.35, 5.45, 5.6, 5.7]


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
    return timeline(drawn)


@pytest.fixture(scope="module")
def gif(tmp_path_factory, sources):
    out = tmp_path_factory.mktemp("whiteboard") / WHITEBOARD_GIF
    return make_usdcad_tests_whiteboard(out=out, sources=sources)


@pytest.fixture(scope="module")
def question(drawn):
    """Scene 1 drawn on its own, which is enough to watch strokes and labels."""
    first = drawn[:1]
    return timeline(first), render(first, timeline(first))


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

    def test_the_gif_is_drawn_from_the_sources_handed_in(
        self, monkeypatch, tmp_path, sources
    ) -> None:
        """The first 800 closes have a half-life that rounds to 100 days, as
        ``tests/test_usdcad_mean_reversion_figures.py`` pins, so a GIF that
        read the file or wrote 115 in would fail here."""
        seen = []
        original = whiteboard.scenes

        def record(run):
            seen.append((run.lookback, len(run.closes)))
            return original(run)

        monkeypatch.setattr(whiteboard, "scenes", record)
        entry, closes = sources
        make_usdcad_tests_whiteboard(out=tmp_path / WHITEBOARD_GIF, sources=(entry, closes[:800]))
        assert seen == [(100, 800)]


class TestTheTimeline:
    def test_the_six_scenes_take_178_frames(self, frames) -> None:
        assert len(frames) == FRAMES
        assert [f.scene for f in frames] == sorted(f.scene for f in frames)

    def test_each_scene_shows_for_four_to_six_seconds(self, frames) -> None:
        seconds = [sum(f.ms for f in frames if f.scene == i) / 1000 for i in range(6)]
        assert seconds == SECONDS
        assert all(4 <= s <= 6 for s in seconds)

    def test_each_scene_opens_on_its_title_alone(self, frames) -> None:
        for index in range(6):
            first = next(f for f in frames if f.scene == index)
            assert (first.done, first.partial, first.ms) == (0, 0, TITLE_MS)

    def test_each_scene_holds_on_its_complete_last_frame(self, drawn, frames) -> None:
        for index, scene in enumerate(drawn):
            last = [f for f in frames if f.scene == index][-1]
            assert last.done == len(scene.steps)
            assert last.partial == 0
            assert last.ms == LABEL_MS + HOLD_MS

    def test_strokes_draw_at_ten_frames_a_second_and_labels_pop_in(self, drawn, frames) -> None:
        """Every frame between a scene's title and its held last frame is a
        stroke's frame of 100 ms or a label's single frame of 350 ms."""
        for index, scene in enumerate(drawn):
            middle = [f for f in frames if f.scene == index][1:-1]
            for frame in middle:
                if frame.partial:
                    assert frame.ms == FRAME_MS
                    continue
                latest = scene.steps[frame.done - 1]
                assert frame.ms == (LABEL_MS if isinstance(latest, Label) else FRAME_MS)
        assert FRAME_MS == 100

    def test_a_label_appears_only_once_its_stroke_is_complete(self, drawn, frames) -> None:
        for frame in frames:
            steps = drawn[frame.scene].steps
            complete = {s.gid for s in steps[: frame.done] if isinstance(s, Stroke)}
            for step in steps[: frame.done]:
                if isinstance(step, Label):
                    assert step.names in complete, step.text

    def test_a_stroke_grows_frame_by_frame(self, drawn, frames) -> None:
        """Scene 1's price line shows a longer prefix on each of its 14 frames."""
        price = drawn[0].steps[1]
        assert price.gid == "price"
        shown = [f.partial for f in frames if f.scene == 0 and f.done == 1 and f.partial]
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
            render(drawn, timeline(drawn))
        messages = [str(w.message) for w in caught] + [r.getMessage() for r in caplog.records]
        assert not [m for m in messages if "glyph" in m.lower()], messages


class TestTheGif:
    def test_it_is_680_by_320_with_178_frames(self, gif) -> None:
        with Image.open(gif) as image:
            assert image.size == (680, 320)
            assert image.n_frames == FRAMES

    def test_it_loops_forever(self, gif) -> None:
        with Image.open(gif) as image:
            assert image.info["loop"] == 0

    def test_each_frame_shows_as_long_as_the_timeline_says(self, gif, frames) -> None:
        assert _durations(gif) == [f.ms for f in frames]
        assert sum(_durations(gif)) == 32_750

    def test_it_is_under_3_mb(self, gif) -> None:
        assert gif.stat().st_size < 3_000_000

    def test_two_draws_give_the_same_bytes(self, gif, tmp_path, sources) -> None:
        again = make_usdcad_tests_whiteboard(out=tmp_path / WHITEBOARD_GIF, sources=sources)
        assert again.read_bytes() == gif.read_bytes()


class TestTheCommittedGif:
    def test_it_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, frames) -> None:
        committed = FIGURES_DIR / WHITEBOARD_GIF
        with Image.open(committed) as image:
            assert (image.size, image.n_frames, image.info["loop"]) == ((680, 320), FRAMES, 0)
        assert _durations(committed) == [f.ms for f in frames]

    def test_it_is_a_fresh_draw_byte_for_byte(self, gif) -> None:
        system, machine, font = platform.system(), platform.machine(), hand_font()
        if (system, machine, font) != ("Darwin", "arm64", "Comic Sans MS"):
            pytest.skip(
                f"the committed GIF was drawn on Darwin arm64 in Comic Sans MS, and this is "
                f"{system} {machine} drawing in {font}"
            )
        committed = (FIGURES_DIR / WHITEBOARD_GIF).read_bytes()
        assert (
            hashlib.sha256(gif.read_bytes()).hexdigest() == hashlib.sha256(committed).hexdigest()
        ), "redraw it with: uv run python -m chan.usdcad_tests_whiteboard"


class TestTheCommand:
    def test_it_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []

        def draw(**kwargs):
            drawn.append(kwargs)
            return FIGURES_DIR / WHITEBOARD_GIF

        monkeypatch.setattr(whiteboard, "make_usdcad_tests_whiteboard", draw)
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / WHITEBOARD_GIF}" in capsys.readouterr().out

    def test_drawing_with_no_out_writes_the_committed_path(self, monkeypatch, sources) -> None:
        saved = []
        monkeypatch.setattr(whiteboard, "read_sources", lambda: sources)
        monkeypatch.setattr(Image.Image, "save", lambda self, path, **kw: saved.append(path))
        assert make_usdcad_tests_whiteboard() == FIGURES_DIR / WHITEBOARD_GIF
        assert saved == [FIGURES_DIR / WHITEBOARD_GIF]

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

        monkeypatch.setattr(whiteboard, "make_usdcad_tests_whiteboard", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2009-01-02")

        monkeypatch.setattr(usdcad_mean_reversion, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale on 2009-01-02"):
            make_usdcad_tests_whiteboard(out=tmp_path / WHITEBOARD_GIF)
