"""The pins for the two whiteboard GIFs in the post-earnings drift rerun post.

1. The universe sketch, in Lesson 1, draws ALL's box holding CAL's and PX's
   circles, which overlap in U. It is not drawn to scale. What is pinned is
   which region each count sits in: U inside both circles, the 47 inside CAL
   and outside PX, the 5 inside PX and outside CAL, and the 4 in the box
   outside both. Also pinned are that the brass outline runs only along the
   part of CAL outside PX, that the brace spans the 5's and the 4's words,
   that the 47 is the chart's brass and the 9 the chart's red, and the words
   it prints. Every count is read from the committed ticker table through
   :func:`chan.pead_rerun.read_committed`, and a made-up set moves the words.
2. The clock sketch, in Lesson 2, draws three rows on one clock from 6 a.m.
   to 10 p.m., each span moved 4 hours later. What is pinned is that every
   mark sits at its time under one affine map, the morning span's late copy
   lies inside the session tint and the afternoon span's past it, Apple's two
   dots both lie past the close, each arrow runs exactly 4 hours, and the
   words it prints. The earliest time, the two counts and Apple's times are
   read from the committed index, which ``tests/test_earnings_filings.py``
   pins on the same reader. The 4 hours and the 5 are constants from a
   sample the repository does not hold, so the caption says so and nothing
   here derives them.

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
import pandas as pd
import pytest
from PIL import Image

from chan import pead_rerun
from chan import pead_rerun_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.earnings_filings import Release, read_index
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.pead_rerun_figures import GROUP_STYLE, RERUN_FIGURE
from chan.pead_rerun_whiteboard import (
    BOX,
    BRACE,
    CAL_CENTRE,
    HOUR_X,
    HOURS,
    LATE_HOURS,
    PX_CENTRE,
    RADIUS,
    ROWS_Y,
    TINT_TOP,
    WINTER_HOURS,
    FilingTimes,
    Universes,
    clock_text,
    gif_name,
    hour_x,
    main,
    make_pead_rerun_whiteboards,
    read_figures,
    scenes,
    sketch_timeline,
)
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    HOLD_MS,
    REJECT_TINT,
    TITLE_MS,
    WIDTH,
    Frame,
    Label,
    Stroke,
    clearances,
    hand_font,
    timeline,
)

POST = REPO_ROOT / "blog" / "pead-edgar-rerun-lessons.md"

#: Every GIF in the order :func:`make_pead_rerun_whiteboards` writes them.
GIFS = ["pead_rerun_sketch_where_the_56_go.gif", "pead_rerun_sketch_four_hours_late.gif"]

#: What each GIF follows: the last item of Lesson 1's list of why the 56 fail,
#: and the last item of Lesson 2's list of what a late time does.
UNIVERSE_ITEM = "2. **Forty-three lack the prices to check.**"
LATE_ITEM = "3. **A filer that files during the session gains a wrong flag.**"

UNIVERSE_LABELS = [
    "ALL 497",
    "CAL 488",
    "PX 446",
    "U 441",
    "47",
    "47: the filer passes, the series does not:\n"
    "4 reused tickers hold another company’s series\n"
    "and 43 lack prices for the whole window",
    "5",
    "4",
    "5: the series passes,\nthe filer does not",
    "4: neither passes",
    "the 9 that fail the filer check",
    "47 + 5 + 4 = 56 outside U",
]

LATE_LABELS = [
    "under daylight saving time, 5 hours in winter",
    "6 a.m.",
    "9:30 a.m.",
    "4:00 p.m.",
    "10 p.m.",
    "405 accepted during the session, where R1 flags nothing",
    "1,460 filings\naccepted before\nthe open",
    "read late: inside the session",
    "nothing counts\nhow many of the\n1,460 read late",
    "Apple, about 4:30 p.m.",
    "same flag, the next morning",
    "flags the next day, whose gap\nopens after its news is out",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def figures() -> tuple[Universes, FilingTimes]:
    return read_figures()


@pytest.fixture(scope="module")
def every(figures):
    return scenes(*figures)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_pead_rerun_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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


def _paragraphs() -> list[str]:
    return [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]


def _distance(point, centre) -> float:
    return math.hypot(point[0] - centre[0], point[1] - centre[1])


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

    def test_each_draws_its_strokes_in_order(self, every) -> None:
        assert [s.gid for s in every[0].strokes] == ["box", "cal", "px", "cal-only", "brace"]
        assert [s.gid for s in every[1].strokes] == [
            "clock",
            "session-edge",
            "morning",
            "morning-shift",
            "morning-late",
            "apple",
            "apple-shift",
            "apple-late",
            "afternoon",
            "afternoon-shift",
            "afternoon-late",
        ]

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
        """The one tint is the session's, the shared red at the palette's
        lightest blend, about 1.3 to 1 against the board and under WCAG 2.1's
        3 to 1 for a graphical object. So it gets a red edge, LOST, that runs
        round it. No sketch draws the green tint."""
        assert sketches.TINT_EDGE >= 1.0
        fills = [(scene, fill) for scene in every for fill in scene.fills]
        assert [fill.gid for _, fill in fills] == ["session"]
        for scene, fill in fills:
            assert fill.color == REJECT_TINT
            edges = [
                s
                for s in scene.strokes
                if s.color == LOST
                and s.width == sketches.TINT_EDGE
                and s.x.min() == pytest.approx(fill.x0)
                and s.x.max() == pytest.approx(fill.x1)
                and s.y.min() == pytest.approx(fill.y0)
                and s.y.max() == pytest.approx(fill.y1)
            ]
            assert edges, (scene.slug, fill.gid)

    def test_no_two_labels_in_a_scene_share_their_words(self, every) -> None:
        """:func:`clearances` keys its result by a label's words, so two labels
        with the same words would hide one of them from the clearance test."""
        for scene in every:
            assert len(set(scene.labels)) == len(scene.labels), scene.slug


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
        """Each label and tint alone for 0.9 s and the drawing for 12 s, the
        equity post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("where_the_56_go", "four_hours_late")
        for scene in every:
            frames = sketch_timeline(scene)
            shown = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and not isinstance(scene.steps[f.done - 1], Stroke)
            ]
            assert shown, scene.slug
            assert {f.ms for f in shown} == {sketches.PACED_LABEL_MS}, scene.slug
            assert frames[-1].ms == sketches.PACED_HOLD_MS
            assert [(f.done, f.partial) for f in frames] == [
                (f.done, f.partial) for f in timeline(scene)
            ]

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_pead_rerun_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_chart_and_the_drift_posts_sketches(self) -> None:
        """No other file starts like these, so the prefix check above reads
        only this module's GIFs, and the drift post's prefix finds none of them."""
        from chan import pead_whiteboard

        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert RERUN_FIGURE in names and not RERUN_FIGURE.startswith(sketches.GIF_PREFIX)
        assert not [name for name in GIFS if name.startswith(pead_whiteboard.GIF_PREFIX)]

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
            ), f"{path.name}: redraw with: uv run python -m chan.pead_rerun_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]

    def test_it_reads_the_files_through_the_runs_own_reader(self, monkeypatch) -> None:
        """Not a second read path: the counts come from the same
        :func:`chan.pead_rerun.read_committed` the runs and the chart read."""

        def refuse(*args, **kwargs):
            raise RuntimeError("read_committed ran")

        monkeypatch.setattr(pead_rerun, "read_committed", refuse)
        with pytest.raises(RuntimeError, match="read_committed ran"):
            read_figures()


class TestThePost:
    def test_each_gif_follows_its_list_with_a_caption(self) -> None:
        """Each embed comes right after the list it draws, then an italic
        caption, then the paragraph or heading that followed the list."""
        paragraphs = _paragraphs()
        for item, name, after in (
            (UNIVERSE_ITEM, GIFS[0], "### What the 56 stocks add to A’s return"),
            (LATE_ITEM, GIFS[1], "## Lesson 3:"),
        ):
            (index,) = [
                k
                for k, p in enumerate(paragraphs)
                if any(line.startswith(item) for line in p.splitlines())
            ]
            assert paragraphs[index].splitlines()[-1].startswith(item), name
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name
            caption = paragraphs[index + 2]
            assert caption.startswith("*") and caption.endswith("*"), name
            assert paragraphs[index + 3].startswith(after), name

    def test_each_sits_in_its_lesson(self) -> None:
        text = POST.read_text(encoding="utf-8")
        universe, late = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        assert text.index("## Lesson 1:") < universe < text.index("## Lesson 2:")
        assert text.index("## Lesson 2:") < late < text.index("## Lesson 3:")

    def test_each_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count(f"(../docs/figures/{RERUN_FIGURE})") == 1

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

    def test_each_alt_text_says_it_is_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "drawn slowly" in alt, scene.slug
            assert "twelve seconds" in alt, scene.slug

    def test_the_captions_say_what_the_sketches_cannot(self) -> None:
        """The circles are not to scale, and the 4 and 5 hours come from a
        sample the repository does not hold."""
        paragraphs = _paragraphs()
        captions = [
            paragraphs[k + 1]
            for k, p in enumerate(paragraphs)
            if any(f"(../docs/figures/{name})" in p for name in GIFS)
        ]
        universe, late = captions
        assert "not drawn to scale" in universe
        assert "248 filings" in late
        assert "while planning the rerun" in late
        assert "does not hold" in late and "nothing pins" in late

    def test_the_module_says_which_is_drawn_to_scale(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "This sketch is not drawn to scale." in doc
        assert "It is drawn to one scale of the clock." in doc


# --- Lesson 1: where the 56 go ---------------------------------------------------


#: The counts ``research/filings/earnings/tickers.csv`` gives, as committed at
#: 699a5f7c, read with Chan's flag file through ``read_committed``.
#: ``tests/test_pead_rerun.py`` pins the four universes, the 47, the 9 and the
#: 4 / 36 / 7 split of the 47 on its own derivation. The split of the 9 into
#: 5 in PX alone and 4 outside both is first pinned here.
PINNED_UNIVERSES = Universes(
    all=497, cal=488, px=446, u=441, cal_only=47, px_only=5, neither=4, reused=4, unpriced=43
)


class TestTheUniverses:
    def test_the_committed_table_gives_the_counts_the_post_prints(self, figures) -> None:
        universes, _ = figures
        assert universes == PINNED_UNIVERSES
        assert (universes.outside, universes.no_filer) == (56, 9)

    def test_the_regions_partition_the_stocks_outside_u(self, figures) -> None:
        f, _ = figures
        assert f.cal_only + f.px_only + f.neither == f.all - f.u
        assert f.reused + f.unpriced == f.cal_only
        assert f.px_only + f.neither == f.all - f.cal

    def test_from_sources_splits_by_the_tables_two_checks(self) -> None:
        """On a made-up table of six stocks, each region and each reason for a
        failed series lands where its row's checks put it."""
        rows = {
            "A": ("pass", "pass"),
            "B": ("pass", "returns"),
            "C": ("pass", "missing"),
            "D": ("pass", "none"),
            "E": ("name", "pass"),
            "F": ("silent", "none"),
        }
        sources = pead_rerun.read_committed()
        template = sources.table[0]
        table = [
            replace(template, ticker=t, cik_check=c, archive_check=a) for t, (c, a) in rows.items()
        ]
        flags = sources.flags.iloc[:, :0].assign(**dict.fromkeys(rows, 0))
        made_up = replace(sources, table=table, flags=flags)
        assert Universes.from_sources(made_up) == Universes(
            all=6, cal=4, px=2, u=1, cal_only=3, px_only=1, neither=1, reused=1, unpriced=2
        )


class TestTheUniverseSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "Where the 56 go"
        assert every[0].labels == UNIVERSE_LABELS

    def test_its_colours(self, every) -> None:
        """The 47 in the chart's brass and the 9 in the chart's red, so a
        reader can carry each group from the chart to the sketch."""
        scene = every[0]
        for gid, ink in (
            ("box", MUTED),
            ("cal", INK),
            ("px", INK),
            ("cal-only", ACCENT),
            ("brace", LOST),
        ):
            assert _stroke(scene, gid).color == ink, gid
        assert GROUP_STYLE["CAL, no checked series"][0] == ACCENT
        assert GROUP_STYLE["no checked CIK"][0] == LOST
        assert GROUP_STYLE["U"][0] == INK
        expected = dict.fromkeys(UNIVERSE_LABELS, INK)
        expected["ALL 497"] = MUTED
        for text in UNIVERSE_LABELS[4:6]:
            expected[text] = ACCENT
        for text in UNIVERSE_LABELS[6:11]:
            expected[text] = LOST
        for label in (s for s in scene.steps if isinstance(s, Label)):
            assert label.color == expected[label.text], label.text

    def test_the_box_holds_both_circles(self, every) -> None:
        scene = every[0]
        x0, y0, x1, y1 = BOX
        for gid in ("cal", "px"):
            circle = _stroke(scene, gid)
            assert x0 < circle.x.min() and circle.x.max() < x1, gid
            assert y0 < circle.y.min() and circle.y.max() < y1, gid
        box = _stroke(scene, "box")
        assert (box.x.min(), box.y.min(), box.x.max(), box.y.max()) == pytest.approx(BOX)

    def test_each_count_sits_in_its_region(self, every) -> None:
        """U inside both circles, the 47 in CAL alone, the 5 in PX alone and
        the 4 in the box outside both."""
        scene = every[0]

        def inside(text, centre):
            label = _label(scene, text)
            return _distance((label.x, label.y), centre) < RADIUS

        assert inside("U 441", CAL_CENTRE) and inside("U 441", PX_CENTRE)
        assert inside("47", CAL_CENTRE) and not inside("47", PX_CENTRE)
        assert inside("5", PX_CENTRE) and not inside("5", CAL_CENTRE)
        assert not inside("4", CAL_CENTRE) and not inside("4", PX_CENTRE)
        four = _label(scene, "4")
        x0, y0, x1, y1 = BOX
        assert x0 < four.x < x1 and y0 < four.y < y1

    def test_each_circle_is_named_on_its_own_side(self, every) -> None:
        """CAL's name sits over the left circle, PX's over the right, each
        above its circle and nearer its own centre than the other's."""
        scene = every[0]
        cal, px = _label(scene, "CAL 488"), _label(scene, "PX 446")
        assert CAL_CENTRE[0] < PX_CENTRE[0]
        assert cal.ha == "left" and px.ha == "right"
        assert cal.x < CAL_CENTRE[0] and px.x > PX_CENTRE[0]
        assert _distance((cal.x, cal.y), CAL_CENTRE) < _distance((cal.x, cal.y), PX_CENTRE)
        assert _distance((px.x, px.y), PX_CENTRE) < _distance((px.x, px.y), CAL_CENTRE)
        assert min(cal.y, px.y) > CAL_CENTRE[1] + RADIUS / 2
        assert (_label(scene, "CAL 488").names, _label(scene, "PX 446").names) == ("cal", "px")

    def test_the_brass_outline_runs_only_round_cal_outside_px(self, every) -> None:
        scene = every[0]
        crescent = _stroke(scene, "cal-only")
        points = np.column_stack([crescent.x, crescent.y])
        to_cal = np.hypot(*(points - CAL_CENTRE).T)
        to_px = np.hypot(*(points - PX_CENTRE).T)
        assert (to_cal <= RADIUS + 1e-9).all()
        assert (to_px >= RADIUS - 1e-9).all()
        on_a_circle = np.isclose(to_cal, RADIUS) | np.isclose(to_px, RADIUS)
        assert on_a_circle.all()
        assert crescent.x.min() == pytest.approx(CAL_CENTRE[0] - RADIUS, abs=1e-3)
        assert crescent.width > _stroke(scene, "cal").width

    def test_the_brace_spans_the_words_of_the_5_and_the_4(self, every) -> None:
        scene = every[0]
        brace = _stroke(scene, "brace")
        b0, b1, by = BRACE
        assert (brace.x.min(), brace.x.max()) == pytest.approx((b0, b1))
        five = _label(scene, UNIVERSE_LABELS[8])
        four = _label(scene, UNIVERSE_LABELS[9])
        assert b0 <= five.x < four.x < b1
        assert five.y < brace.y.min() and four.y < brace.y.min()
        assert _label(scene, "the 9 that fail the filer check").y > brace.y.max()

    def test_made_up_counts_move_the_words(self) -> None:
        made_up = Universes(
            all=500,
            cal=480,
            px=450,
            u=440,
            cal_only=40,
            px_only=10,
            neither=10,
            reused=6,
            unpriced=34,
        )
        scene = scenes(made_up, FilingTimes("07:00:00", 10, 20, ("2011-01-18T17:00:00",)))[0]
        assert scene.title == "Where the 60 go"
        assert scene.labels == [
            "ALL 500",
            "CAL 480",
            "PX 450",
            "U 440",
            "40",
            "40: the filer passes, the series does not:\n"
            "6 reused tickers hold another company’s series\n"
            "and 34 lack prices for the whole window",
            "10",
            "10",
            "10: the series passes,\nthe filer does not",
            "10: neither passes",
            "the 20 that fail the filer check",
            "40 + 10 + 10 = 60 outside U",
        ]

    @pytest.mark.parametrize(
        "change",
        [
            {"cal": 487},
            {"px": 447},
            {"neither": 5},
            {"reused": 5},
            {"px_only": 0, "px": 441, "neither": 9},
        ],
        ids=str,
    )
    def test_counts_the_drawing_would_misdescribe_are_refused(self, change) -> None:
        with pytest.raises(ValueError, match="these counts disagree"):
            sketches._where_the_56_go(replace(PINNED_UNIVERSES, **change))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        f = PINNED_UNIVERSES
        for phrase in (
            "It is not drawn to scale.",
            "Inside it two black circles overlap, the left labelled “CAL 488” and the right "
            "“PX 446”, and the overlap is labelled “U 441”.",
            "A thick brass line then traces the part of the left circle that lies outside the "
            f"right one, labelled “{f.cal_only}”, and brass words",
            f"In red, the part of the right circle outside the left is labelled “{f.px_only}”, "
            f"and the corner of the box outside both circles “{f.neither}”.",
            "Red words beside the box",
            "a red brace above them",
        ):
            assert phrase in alt, phrase

    def test_its_caption_says_where_the_counts_and_colours_come_from(self) -> None:
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{GIFS[0]})" in p]
        caption = paragraphs[index + 1]
        f = PINNED_UNIVERSES
        assert "so they are not drawn to scale." in caption
        assert "Every count comes from the committed table of tickers." in caption
        assert (
            "The brass and the red are the colours of the chart’s lines for the same "
            f"{f.cal_only} and {f.no_filer} stocks."
        ) in caption


# --- Lesson 2: four hours late ---------------------------------------------------


#: What ``research/filings/earnings/index.jsonl`` gives, the EDGAR fetch of
#: 2026-10-10 as committed at 699a5f7c. ``tests/test_earnings_filings.py``
#: pins the same figures in ``TestTheCommittedIndex`` on the same reader.
PINNED_TIMES = FilingTimes(
    earliest="06:00:43",
    before_open=1460,
    in_session=405,
    apple=(
        "2011-01-18T16:30:27", "2011-04-20T16:30:30", "2011-07-19T16:29:56",
        "2011-10-18T16:31:02", "2012-01-24T16:30:34", "2012-04-24T16:30:55",
    ),
)  # fmt: skip


class TestTheFilingTimes:
    def test_the_committed_index_gives_the_times_the_post_prints(self, figures) -> None:
        _, times = figures
        assert times == PINNED_TIMES
        assert times == FilingTimes.from_index(read_index())
        assert clock_text(times.apple_hours) == "4:30 p.m."

    def test_from_index_counts_the_open_in_the_session_and_the_close_outside_it(self) -> None:
        """Made-up filings on each side of 9:30 and 4:00, and Apple's mean
        rounded to five minutes rather than any coarser step."""

        def release(ticker: str, stamp: str) -> Release:
            return Release(ticker, 1, stamp, "8-K", "2.02", "", stamp[:10], stamp, "")

        index = [
            release("X", "2011-03-01T09:29:59"),
            release("X", "2011-03-01T09:30:00"),
            release("X", "2011-03-01T15:59:59"),
            release("X", "2011-03-01T16:00:00"),
            release("AAPL", "2011-03-01T16:40:00"),
            release("AAPL", "2011-03-02T16:44:00"),
        ]
        times = FilingTimes.from_index(index)
        assert (times.earliest, times.before_open, times.in_session) == ("09:29:59", 1, 2)
        assert times.apple == ("2011-03-01T16:40:00", "2011-03-02T16:44:00")
        assert clock_text(times.apple_hours) == "4:40 p.m."

    def test_r1_flags_none_of_the_405_and_none_of_the_1460_read_late(self) -> None:
        """The labels say R1 flags nothing in the session, which holds only if
        no filing fell on a day the market was shut, where R1 moves even a
        session time to the next trading day. Checked against R1 itself."""
        sources = pead_rerun.read_committed()
        stamps = [pd.Timestamp(release.accepted) for release in sources.releases]
        opens, closes = pd.Timedelta(hours=9.5), pd.Timedelta(hours=16)
        session = [s for s in stamps if opens <= s - s.normalize() < closes]
        morning = [s for s in stamps if s - s.normalize() < opens]
        assert (len(session), len(morning)) == (405, 1460)
        assert all(pead_rerun.r1_day(s, sources.days) is None for s in session)
        for late in (LATE_HOURS, WINTER_HOURS):
            shifted = [s + pd.Timedelta(hours=late) for s in morning]
            assert all(pead_rerun.r1_day(s, sources.days) is None for s in shifted), late

    def test_the_shift_is_a_constant_from_the_unpinned_sample(self) -> None:
        """Constants, since the sample of 248 filings is not committed."""
        assert (LATE_HOURS, WINTER_HOURS) == (4, 5)
        doc = " ".join((sketches.__doc__ or "").split())
        assert "a check of 248 filings made while planning the rerun" in doc
        assert "The repository does not hold that sample" in doc

    @pytest.mark.parametrize("late", [3, 7])
    def test_a_shift_the_drawing_would_misdescribe_is_refused(self, monkeypatch, late) -> None:
        """Three hours would leave the earliest morning filing before the
        open, and seven would carry 9:30 past the close and put noon before
        the open."""
        monkeypatch.setattr(sketches, "LATE_HOURS", late)
        with pytest.raises(ValueError, match="these times do not"):
            sketches._four_hours_late(PINNED_TIMES)

    def test_noon_on_the_drawing_is_the_close_less_the_shift(self, every) -> None:
        assert _stroke(every[1], "afternoon").x.min() == pytest.approx(hour_x(16.0 - LATE_HOURS))

    @pytest.mark.parametrize(
        ("value", "minutes", "text"),
        [(6.0, False, "6 a.m."), (9.5, True, "9:30 a.m."), (16.0, True, "4:00 p.m."),
         (22.0, False, "10 p.m."), (12.0, True, "12:00 p.m."), (16.5, True, "4:30 p.m.")],
    )  # fmt: skip
    def test_clock_text_writes_times_as_the_post_does(self, value, minutes, text) -> None:
        assert clock_text(value, minutes=minutes) == text


class TestTheLateSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Four hours late"
        assert every[1].labels == LATE_LABELS

    def test_no_label_counts_the_span_from_noon(self, every) -> None:
        """Nothing pins how many filings were accepted from noon on, so the
        only count in the session is the whole session's."""
        numbers = {
            n for text in every[1].labels for n in re.findall(r"\d[\d,]*", text.replace(":", " "))
        }
        assert numbers == {"5", "6", "9", "30", "4", "00", "10", "405", "1", "1,460"}

    def test_its_colours(self, every) -> None:
        """A late copy is red where it changes R1's flag and green where it keeps it."""
        scene = every[1]
        for gid, ink in (
            ("clock", MUTED),
            ("session-edge", LOST),
            ("morning", INK),
            ("morning-shift", INK),
            ("morning-late", LOST),
            ("apple", INK),
            ("apple-shift", INK),
            ("apple-late", GOOD),
            ("afternoon", INK),
            ("afternoon-shift", INK),
            ("afternoon-late", LOST),
        ):
            assert _stroke(scene, gid).color == ink, gid
        expected = {
            **dict.fromkeys(LATE_LABELS[:5], MUTED),
            LATE_LABELS[5]: LOST,
            LATE_LABELS[6]: INK,
            LATE_LABELS[7]: LOST,
            LATE_LABELS[8]: MUTED,
            LATE_LABELS[9]: INK,
            LATE_LABELS[10]: GOOD,
            LATE_LABELS[11]: LOST,
        }
        for label in (s for s in scene.steps if isinstance(s, Label)):
            assert label.color == expected[label.text], label.text

    def test_the_session_tint_runs_from_the_open_to_the_close(self, every) -> None:
        scene = every[1]
        (session,) = scene.fills
        assert (session.x0, session.x1) == pytest.approx((hour_x(9.5), hour_x(16.0)))
        assert session.y0 == sketches.CLOCK_Y and session.y1 == TINT_TOP
        for gid in ("morning-shift", "afternoon-shift"):
            assert _stroke(scene, gid).y.max() < TINT_TOP, gid

    def test_the_clock_is_one_affine_scale(self, every) -> None:
        scene = every[1]
        clock = _stroke(scene, "clock")
        assert (clock.x.min(), clock.x.max()) == pytest.approx(HOUR_X)
        assert hour_x(HOURS[0]) == HOUR_X[0] and hour_x(HOURS[1]) == HOUR_X[1]
        for text, hours in (("9:30 a.m.", 9.5), ("4:00 p.m.", 16.0)):
            assert _label(scene, text).x == pytest.approx(hour_x(hours)), text

    def test_each_span_and_dot_sits_at_its_times(self, every, figures) -> None:
        _, f = figures
        scene = every[1]
        early, apple = f.earliest_hours, f.apple_hours
        assert early == pytest.approx(6 + 43 / 3600)
        assert apple == pytest.approx(16.5)
        for gid, start, end in (
            ("morning", early, 9.5),
            ("morning-late", early + LATE_HOURS, 9.5 + LATE_HOURS),
            ("afternoon", 16.0 - LATE_HOURS, 16.0),
            ("afternoon-late", 16.0, 16.0 + LATE_HOURS),
        ):
            span = _stroke(scene, gid)
            assert (span.x.min(), span.x.max()) == pytest.approx((hour_x(start), hour_x(end))), gid
        assert _stroke(scene, "apple").x.tolist() == pytest.approx([hour_x(apple)])
        assert _stroke(scene, "apple-late").x.tolist() == pytest.approx(
            [hour_x(apple + LATE_HOURS)]
        )

    def test_a_morning_read_late_lands_inside_the_session_and_apples_stays_after_it(
        self, every
    ) -> None:
        """Both shifts, 4 hours and 5, take the earliest morning filing into
        the session, and Apple's past the close either way."""
        scene = every[1]
        (session,) = scene.fills
        late = _stroke(scene, "morning-late")
        assert session.x0 < late.x.min() and late.x.max() < session.x1
        winter = hour_x(PINNED_TIMES.earliest_hours + WINTER_HOURS), hour_x(9.5 + WINTER_HOURS)
        assert session.x0 < winter[0] and winter[1] < session.x1
        morning = _stroke(scene, "morning")
        assert morning.x.max() == pytest.approx(session.x0)
        for gid in ("apple", "apple-late"):
            assert _stroke(scene, gid).x[0] > session.x1, gid
        assert _stroke(scene, "afternoon").x.min() > session.x0
        assert _stroke(scene, "afternoon").x.max() == pytest.approx(session.x1)
        assert _stroke(scene, "afternoon-late").x.min() == pytest.approx(session.x1)

    def test_each_arrow_runs_four_hours(self, every) -> None:
        """Every shift's shaft runs exactly :data:`LATE_HOURS` on the clock,
        less the gaps that keep an arrow off Apple's two dots."""
        scene = every[1]
        hour = (HOUR_X[1] - HOUR_X[0]) / (HOURS[1] - HOURS[0])
        for gid in ("morning-shift", "afternoon-shift"):
            arrow = _stroke(scene, gid)
            assert arrow.x.max() - arrow.x.min() == pytest.approx(LATE_HOURS * hour), gid
            assert arrow.x[0] == arrow.x.min(), gid
        apple = _stroke(scene, "apple-shift")
        assert apple.x.max() - apple.x.min() == pytest.approx(
            LATE_HOURS * hour - 2 * sketches.DOT_GAP
        )
        assert apple.x[0] == apple.x.min()

    def test_the_rows_run_top_to_bottom(self, every) -> None:
        scene = every[1]
        heights = [np.median(_stroke(scene, gid).y) for gid in ("morning", "apple", "afternoon")]
        assert heights == pytest.approx(list(ROWS_Y), abs=1e-9)
        assert heights[0] > heights[1] > heights[2] > sketches.CLOCK_Y

    def test_made_up_times_move_the_words(self) -> None:
        made_up = FilingTimes(
            earliest="07:15:00",
            before_open=12,
            in_session=34,
            apple=("2011-01-18T17:01:00", "2011-04-20T16:59:00"),
        )
        scene = scenes(PINNED_UNIVERSES, made_up)[1]
        assert scene.labels[5] == "34 accepted during the session, where R1 flags nothing"
        assert scene.labels[6] == "12 filings\naccepted before\nthe open"
        assert scene.labels[8] == "nothing counts\nhow many of the\n12 read late"
        assert scene.labels[9] == "Apple, about 5:00 p.m."
        assert _stroke(scene, "morning").x.min() == pytest.approx(hour_x(7.25))

    @pytest.mark.parametrize(
        "change",
        [
            {"earliest": "05:00:00"},
            {"earliest": "09:45:00"},
            {"apple": ("2011-01-18T15:30:00",)},
            {"apple": ("2011-01-18T17:30:00",)},
            {"in_session": 0},
            {"before_open": 0},
        ],
        ids=str,
    )
    def test_times_the_drawing_would_misdescribe_are_refused(self, change) -> None:
        """A morning filing a late read would leave before the session, an
        Apple time in the session or past 5 p.m., whose winter copy runs off
        the clock, and an empty session."""
        with pytest.raises(ValueError, match="these times do not"):
            sketches._four_hours_late(replace(PINNED_TIMES, **change))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        """Each time and place the alt text gives is built from the figures,
        so a changed shift or Apple time leaves it stale and fails here."""
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        f = PINNED_TIMES
        opens, closes = 9.5, 16.0
        for phrase in (
            "It is drawn to one scale of the clock.",
            f"from {clock_text(HOURS[0], minutes=False)} to {clock_text(HOURS[1], minutes=False)}",
            f"The session from {clock_text(opens)} to {clock_text(closes)} is tinted red",
            f"moves a span or a time {LATE_HOURS} hours later",
            f"its red copy {LATE_HOURS} hours later lies inside the tint, labelled to the right "
            "of the tint",
            f"a green dot at about {clock_text(f.apple_hours + LATE_HOURS)}",
            f"a black span runs inside the tint from noon to the close, and its red copy runs "
            f"from the close to {clock_text(closes + LATE_HOURS, minutes=False)}, past the close",
        ):
            assert phrase in alt, phrase
        assert clock_text(closes - LATE_HOURS) == "12:00 p.m."

    def test_its_caption_says_where_the_shift_and_the_counts_come_from(self) -> None:
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{GIFS[1]})" in p]
        caption = paragraphs[index + 1]
        f = PINNED_TIMES
        assert caption.startswith(f"*The {LATE_HOURS}-hour shift, and the {WINTER_HOURS} hours")
        assert (
            f"The earliest time, the {f.before_open:,}, the {f.in_session} and Apple’s times "
            "come from the committed index."
        ) in caption
