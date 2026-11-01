"""The pins for the whiteboard GIF in the build board post.

The sketch draws the board before and after the move as two rows of boxes,
the update a session made by hand above the one GitHub makes now. It is
schematic: its boxes, sizes and spacing are made up, so no test here reads a
figure off it. What is pinned is what a reader takes from it.

1. The top row's five steps in the post's order, and a vermilion arrow
   labelled "refused" from the write back to the read, for the version pin.
2. The bottom row's five steps, and a berry arrow labelled
   "PR merges / CI finishes" that enters the GitHub event from below with no
   box behind it, because GitHub records those events itself.
3. Words the sketch must not carry: the script that built the board, since
   deleted, a clock or schedule, and a link beside the label, since a
   "blocked by" link starts no run.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, the GIF's size, frames, loop and timing, its
slower pace, that two draws give the same bytes, and that the committed GIF
is a fresh draw, a comparison that runs only on macOS arm64 with Comic Sans
MS, as ``tests/test_usdcad_tests_whiteboard.py`` explains. The check that
``docs/figures`` holds exactly the GIFs the modules draw lives in
``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS` from
here.
"""

from __future__ import annotations

import hashlib
import math
import platform
import re

import matplotlib
import pytest
from PIL import Image

from chan import build_board_whiteboard as sketches
from chan import palette, regime_figure
from chan import usdcad_tests_whiteboard as whiteboard
from chan.build_board_whiteboard import (
    AFTER,
    BEFORE,
    EVENT_FROM_Y,
    RETURN_Y,
    ROWS,
    gif_name,
    main,
    make_build_board_whiteboards,
    scenes,
    sketch_timeline,
    spans,
)
from chan.palette import ACCENT, GOOD, LOST
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import INK, MUTED
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

POST = REPO_ROOT / "blog" / "build-board-on-github-lessons.md"

#: Every GIF in the order :func:`make_build_board_whiteboards` writes them.
GIFS = ["build_board_sketch_update_flow.gif"]

#: Words in the paragraph the GIF follows. The test keys on this sentence
#: rather than on the paragraph's first characters, since its opening once
#: changed when a heading took over its bold "After."
FOLLOWS = "A session no longer writes the board."

LABELS = [
    "session or\nsub-agent",
    "before (by hand)",
    "read 6 sections\n+ GitHub",
    "edit",
    "render,\n6 checks",
    "write\n+ pin",
    "refused",
    "session",
    "after (from GitHub)",
    "set label",
    "GitHub\nevent",
    "Action\nrebuilds",
    "page",
    "PR merges / CI finishes",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def every():
    return scenes()


@pytest.fixture(scope="module")
def flow(every):
    return every[0]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_build_board_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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


def _paragraphs() -> list[str]:
    return [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]


def _alt(text: str, scene) -> str:
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


def _caption() -> str:
    paragraphs = _paragraphs()
    (index,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{GIFS[0]})" in p]
    return paragraphs[index + 1]


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_is_one_the_post_embeds(self, every) -> None:
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

    def test_every_pale_tint_has_a_blue_edge(self, every) -> None:
        """The sketch draws no tint today. One that does would need a blue edge
        like the green one the equity seasonals module's ``_tinted`` draws,
        since the tint alone stands 1.31 to 1 against the board."""
        pale = {palette.TINT, palette.REJECT_TINT, whiteboard.TINT, whiteboard.REJECT_TINT}
        tints = [fill for scene in every for fill in scene.fills if fill.color in pale]
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

    def test_the_sketch_builds_slowly_and_holds_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("update_flow",)
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

    def test_each_colour_table_holds_the_colour_blind_safe_inks(self, gifs) -> None:
        """Each GIF's colour table holds the berry, blue and vermilion of
        :data:`chan.palette.INKS` and not the shared brass, green and red, so a
        frame quantized onto the renderer's default inks fails here on any
        machine. A sketch need not draw every ink, so this reads the table
        rather than the pixels."""
        rgb = {
            name: tuple(int(c[i : i + 2], 16) for i in (1, 3, 5))
            for name, c in (
                ("berry", ACCENT),
                ("blue", GOOD),
                ("vermilion", LOST),
                ("brass", regime_figure.ACCENT),
                ("green", regime_figure.GOOD),
                ("red", regime_figure.LOST),
            )
        }
        for path in gifs:
            with Image.open(path) as image:
                flat = image.getpalette()
            colours = {tuple(flat[i : i + 3]) for i in range(0, len(flat), 3)}
            for name in ("berry", "blue", "vermilion"):
                assert rgb[name] in colours, (path.name, name)
            for name in ("brass", "green", "red"):
                assert rgb[name] not in colours, (path.name, name)

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_build_board_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

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
            ), f"{path.name}: redraw with: uv run python -m chan.build_board_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_the_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if FOLLOWS in p]
        embed = paragraphs[index + 1]
        assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", embed)

    def test_the_gif_sits_in_the_section_on_the_move(self) -> None:
        text = POST.read_text(encoding="utf-8")
        at = text.index(f"(../docs/figures/{GIFS[0]})")
        section = text.index("## The board before and after the move")
        lesson_1 = text.index("## Lesson 1:")
        assert section < at < lesson_1

    def test_the_boxes_quote_the_counts_the_post_gives(self) -> None:
        text = POST.read_text(encoding="utf-8")
        assert "named six data sections" in text and "against six checks" in text
        assert "read 6 sections\n+ GitHub" in LABELS and "render,\n6 checks" in LABELS

    def test_the_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_its_caption_follows_it_and_says_it_is_schematic(self) -> None:
        caption = _caption()
        assert caption.startswith("*The sketch is schematic.") and caption.endswith("*")
        assert "a line or a comment starts a run of the Action the same way" in caption
        assert (
            "leaves out the scheduled runs, the runs started by hand and the events that start "
            "no run"
        ) in caption

    def test_the_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
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

    def test_the_alt_text_says_it_is_schematic_and_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "schematic and carries no figures from any run" in alt, scene.slug
            assert "drawn slowly" in alt and "twelve seconds" in alt, scene.slug

    def test_the_alt_text_and_caption_name_no_issue_or_pull_request(self, flow) -> None:
        """A post names no issue or pull request, by number or by link."""
        for words in (_alt(POST.read_text(encoding="utf-8"), flow), _caption()):
            assert not re.search(r"#\d|/issues/|/pull/|\bissue\b|\bPR #", words), words

    def test_the_module_says_it_is_schematic(self) -> None:
        assert "The sketch is schematic and carries no figures from any run" in (
            sketches.__doc__ or ""
        )


# --- The board before and after the move ---------------------------------------


def _row_boxes(scene, tag: str, row) -> list:
    return [_stroke(scene, f"{tag}-{name}") for name, _, _ in row]


class TestTheUpdateFlowSketch:
    def test_its_words(self, flow) -> None:
        assert flow.title == "The board before and after the move"
        assert flow.labels == LABELS

    def test_it_says_set_label_alone_and_names_no_script_or_clock(self, flow) -> None:
        """A "blocked by" link starts no run, the script the post names has
        since been deleted, and the scheduled runs are left out."""
        words = " ".join(label.replace("\n", " ") for label in flow.labels).lower()
        assert "set label" in words
        for absent in ("link", "build_board", ".py", "clock", "schedule", "cron", "minutes"):
            assert absent not in words, absent

    def test_its_colours(self, flow) -> None:
        for tag, row in (("before", BEFORE), ("after", AFTER)):
            for name, words, _ in row:
                assert _stroke(flow, f"{tag}-{name}").color == INK, name
                assert _label(flow, words).color == INK, words
            for name, _, _ in row[1:]:
                assert _stroke(flow, f"{tag}-to-{name}").color == INK, name
            assert _label(flow, ROWS[tag][0]).color == MUTED
        assert _stroke(flow, "refused").color == LOST
        assert _label(flow, "refused").color == LOST
        assert _stroke(flow, "github-records").color == ACCENT
        assert _label(flow, "PR merges / CI finishes").color == ACCENT

    def test_each_coloured_arrow_carries_its_own_words(self, flow) -> None:
        """Colour is never the only cue: the refusal and GitHub's own events
        each carry a label naming what they are."""
        assert [s.text for s in _labels_of(flow, "refused")] == ["refused"]
        assert [s.text for s in _labels_of(flow, "github-records")] == ["PR merges / CI finishes"]

    def test_each_row_runs_left_to_right_on_one_line(self, flow) -> None:
        for tag, row in (("before", BEFORE), ("after", AFTER)):
            _, bottom, top = ROWS[tag]
            boxes = _row_boxes(flow, tag, row)
            for box in boxes:
                assert (box.y.min(), box.y.max()) == pytest.approx((bottom, top)), box.gid
            for one, other in zip(boxes, boxes[1:], strict=False):
                assert one.x.max() < other.x.min(), (one.gid, other.gid)
            assert boxes[0].x.min() > 0 and boxes[-1].x.max() < 10

    def test_the_before_row_sits_above_the_after_row(self, flow) -> None:
        assert ROWS["before"][1] > ROWS["after"][2]
        for tag in ("before", "after"):
            heading, _, top = ROWS[tag]
            assert _label(flow, heading).y > top

    def test_each_box_holds_its_words_at_its_centre(self, flow) -> None:
        for tag, row in (("before", BEFORE), ("after", AFTER)):
            for name, words, _ in row:
                box, label = _stroke(flow, f"{tag}-{name}"), _label(flow, words)
                assert label.names == f"{tag}-{name}"
                assert label.x == pytest.approx((box.x.min() + box.x.max()) / 2)
                assert label.y == pytest.approx((box.y.min() + box.y.max()) / 2)

    def test_each_arrow_runs_from_one_box_to_the_next(self, flow) -> None:
        for tag, row in (("before", BEFORE), ("after", AFTER)):
            edges = spans(row)
            for previous, (name, _, _) in zip(row, row[1:], strict=False):
                arrow = _stroke(flow, f"{tag}-to-{name}")
                assert edges[previous[0]][1] < arrow.x[0] < arrow.x.max() < edges[name][0]
                assert arrow.x.argmax() > 0, name

    def test_the_refusal_runs_from_the_write_back_to_the_read(self, flow) -> None:
        """It leaves the bottom of "write + pin", runs left beneath the row and
        ends with its head under "read 6 sections + GitHub", pointing up."""
        edges = spans(BEFORE)
        _, bottom, _ = ROWS["before"]
        refused = _stroke(flow, "refused")
        x0, x1 = edges["write"]
        assert x0 < refused.x[0] < x1 and refused.y[0] < bottom
        assert refused.y.min() == pytest.approx(RETURN_Y) and RETURN_Y < bottom
        # The head's two strokes meet at the tip and end below it, so the tip
        # is the highest point the arrow reaches under the read.
        r0, r1 = edges["read"]
        under_read = (refused.x > r0) & (refused.x < r1)
        tip = refused.y[under_read].max()
        assert tip == pytest.approx(refused.y[0]) and tip < bottom
        assert r0 < refused.x[-1] < r1 and refused.y[-1] < tip
        # After the shaft's last visit to the tip, only the head's two arms
        # follow, each 0.22 long, so a head flipped to point down fails here.
        last = len(refused.y) - 1 - refused.y[::-1].argmax()
        assert (tip - refused.y[last:]).max() <= 0.22
        label = _label(flow, "refused")
        assert RETURN_Y < label.y < bottom
        assert r1 < label.x < x0

    def test_the_berry_arrow_rises_into_the_event_from_empty_board(self, flow) -> None:
        """It enters the bottom of "GitHub event" from below, and no box sits
        beneath the bottom row for it to come from."""
        edges = spans(AFTER)
        _, bottom, _ = ROWS["after"]
        arrow = _stroke(flow, "github-records")
        e0, e1 = edges["event"]
        assert arrow.y[0] == pytest.approx(EVENT_FROM_Y)
        assert arrow.x[0] == pytest.approx((e0 + e1) / 2)
        assert arrow.y.max() < bottom and arrow.y.argmax() > 0
        others = [s for s in flow.strokes if s.gid != "github-records"]
        assert all(stroke.y.min() >= bottom for stroke in others if stroke.gid != "refused")
        assert _stroke(flow, "refused").y.min() > ROWS["after"][2]
        assert _label(flow, "PR merges / CI finishes").y < bottom

    def test_its_alt_text_says_what_the_picture_shows(self, flow) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), flow)
        assert "Two rows of black boxes, joined left to right by black arrows" in alt
        assert "A vermilion arrow labelled “refused” leaves the bottom of “write + pin”" in alt
        assert "rises into “read 6 sections + GitHub”" in alt
        assert "a berry arrow labelled “PR merges / CI finishes” rises from the blank whiteboard below" in alt
        assert "under a grey heading “before (by hand)”" in alt
        assert "under a grey heading “after (from GitHub)”" in alt
        assert "into the bottom of “GitHub event”, with no box behind it" in alt
