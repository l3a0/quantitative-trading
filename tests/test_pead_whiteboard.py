"""The pins for the two whiteboard GIFs in the post-earnings drift post.

One sketches the strategy's single trade across two days, and one Lesson 4's
one position that the ``smartstd`` helper flips.

1. The trade sketch is schematic: its price path, the size of its gap and
   the exact times of its red marks inside their sessions are made up, so no
   test here reads a figure off it. What is
   pinned is what a reader takes from it. The brass bracket spans the night
   from the close to the open, the gap is the jump at the open from the
   close's level, the green bar runs from the open to the close and nowhere
   in the night, and the two red marks sit inside the day before's session
   and inside today's after the open.
2. The flip sketch is not schematic. Its figures come from
   :class:`chan.pead_whiteboard.HelperFlip`, which reads :func:`chan.pead.pead`
   on the committed files, and the run reads committed vintages, so the tests
   read the run directly rather than a frozen copy of its figures. What is
   pinned is each figure it prints, that the two ticks and the dot sit at one
   affine function of their values, and that a made-up set of figures moves
   the words with them. ``tests/test_pead.py`` holds the same figures on its
   own derivation, in ``TestTheHelperMovesADigit``.

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

from chan import pead_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.pead_whiteboard import (
    CLOSE,
    CLOSE_LEVEL,
    LINE_Y,
    NEWS_IN_CLOSE_X,
    OPEN,
    OPEN_LEVEL,
    PREVIOUS_CLOSE,
    SESSION_START,
    TOO_LATE_X,
    HelperFlip,
    gif_name,
    main,
    make_pead_whiteboards,
    on_line,
    price_at,
    scenes,
    sketch_timeline,
)
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

POST = REPO_ROOT / "blog" / "post-earnings-drift-lessons.md"

#: Every GIF in the order :func:`make_pead_whiteboards` writes them.
GIFS = ["pead_sketch_one_trade.gif", "pead_sketch_helper_flip.gif"]

#: What each GIF follows: the strategy's list, keyed on its last item's
#: opening, and Lesson 4's paragraph on the one position.
SIZING_ITEM = "4. **The sizing.**"
FLIP_PARAGRAPH = "The one position that changes is PNW"

TRADE_LABELS = [
    "close 4:00 p.m.",
    "open 9:30 a.m.",
    "close",
    "the day before",
    "today",
    "announced here: counts",
    "the gap: the signal",
    "held: the return earned",
    "nothing held\novernight",
    "news already in the close,\nso the gap misses it",
    "too late: the trade\nopened at 9:30",
]

FLIP_LABELS = [
    "half the Algorithmic Trading helper’s deviation: 0.4189%",
    "long",
    "half the first edition’s deviation: 0.4213%",
    "no trade",
    "PNW’s gap on 2012-02-24: 0.4212%",
    "the long lost 0.36%: annual return 0.0667 with it, 0.0668 without",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def flip() -> HelperFlip:
    return HelperFlip.from_run()


@pytest.fixture(scope="module")
def every(flip):
    return scenes(flip)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_pead_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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
        assert sketches.PACED == ("one_trade", "helper_flip")
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
        again = make_pead_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_charts(self) -> None:
        """No chart starts like these, so the prefix check above reads only
        this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert {"pead_cumulative_return.png", "pead_edgar_rerun.png"} <= names

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
            ), f"{path.name}: redraw with: uv run python -m chan.pead_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_the_trade_sketch_follows_the_strategys_list(self) -> None:
        """Right after the list whose last item is the sizing, and before the
        paragraph on the two files."""
        paragraphs = _paragraphs()
        (index,) = [
            k
            for k, p in enumerate(paragraphs)
            if any(line.startswith(SIZING_ITEM) for line in p.splitlines())
        ]
        assert paragraphs[index].splitlines()[-1].startswith(SIZING_ITEM)
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", paragraphs[index + 1]
        )
        caption = paragraphs[index + 2]
        assert caption.startswith("*The sketch is schematic.") and caption.endswith("*")
        assert paragraphs[index + 3].startswith("Two files carry the data")

    def test_the_flip_sketch_follows_its_paragraph_with_a_caption(self) -> None:
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(FLIP_PARAGRAPH)]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[1])}\)", paragraphs[index + 1]
        )
        caption = paragraphs[index + 2]
        assert caption.startswith("*Drawn to one scale from the run.") and caption.endswith("*")
        for mark in ("black dot", "green tick", "red tick"):
            assert mark in caption, mark
        assert (
            "past the green tick, so with the *Algorithmic Trading* helper the rule goes long"
            in caption
        )
        assert (
            "short of the red tick, so with the first edition’s helper it takes no trade" in caption
        )

    def test_the_trade_sketch_sits_in_the_strategy_and_the_flip_in_lesson_4(self) -> None:
        text = POST.read_text(encoding="utf-8")
        trade, flip_at = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        strategy = text.index("## The strategy and the two files")
        lesson_1 = text.index("## Lesson 1:")
        lesson_4 = text.index("## Lesson 4:")
        lesson_5 = text.index("## Lesson 5:")
        assert strategy < trade < lesson_1 < lesson_4 < flip_at < lesson_5

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

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

    def test_each_alt_text_says_it_is_slow_and_whether_it_is_schematic(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        trade, flip_scene = every
        assert "schematic and carries no figures from the run" in _alt(text, trade)
        flip_alt = _alt(text, flip_scene)
        assert "schematic" not in flip_alt
        assert "drawn to one scale from the run" in flip_alt
        for scene in every:
            alt = _alt(text, scene)
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_the_module_says_which_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "This sketch is schematic and carries no figures from the run" in doc
        assert "This sketch is not schematic" in doc


# --- The strategy: one trade, two days ------------------------------------------


class TestTheTradeSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "One trade, two days"
        assert every[0].labels == TRADE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        for gid, ink in (
            ("axis", MUTED),
            ("tick-previous-close", MUTED),
            ("tick-open", MUTED),
            ("tick-close", MUTED),
            ("price-before", INK),
            ("bracket", ACCENT),
            ("close-level", MUTED),
            ("gap", INK),
            ("price-today", INK),
            ("held", GOOD),
            ("news-in-close", LOST),
            ("too-late", LOST),
        ):
            assert _stroke(scene, gid).color == ink, gid
            for label in _labels_of(scene, gid):
                assert label.color == ink, label.text

    def test_the_ticks_sit_at_the_close_the_open_and_the_close(self, every) -> None:
        scene = every[0]
        for gid, x, text in (
            ("tick-previous-close", PREVIOUS_CLOSE, "close 4:00 p.m."),
            ("tick-open", OPEN, "open 9:30 a.m."),
            ("tick-close", CLOSE, "close"),
        ):
            assert set(_stroke(scene, gid).x) == {x}, gid
            assert _label(scene, text).x == x, text
        assert SESSION_START < PREVIOUS_CLOSE < OPEN < CLOSE

    def test_each_session_runs_between_its_ticks(self, every) -> None:
        scene = every[0]
        before, today = _stroke(scene, "price-before"), _stroke(scene, "price-today")
        assert (before.x.min(), before.x.max()) == (SESSION_START, PREVIOUS_CLOSE)
        assert (today.x.min(), today.x.max()) == (OPEN, CLOSE)
        assert before.y[-1] == pytest.approx(CLOSE_LEVEL)
        assert today.y[0] == pytest.approx(OPEN_LEVEL)

    def test_the_bracket_spans_the_night_above_both_sessions(self, every) -> None:
        scene = every[0]
        bracket = _stroke(scene, "bracket")
        assert (bracket.x.min(), bracket.x.max()) == (PREVIOUS_CLOSE, OPEN)
        prices = np.concatenate([_stroke(scene, g).y for g in ("price-before", "price-today")])
        assert bracket.y.min() > prices.max()

    def test_the_gap_climbs_at_the_open_from_the_closes_level(self, every) -> None:
        scene = every[0]
        gap = _stroke(scene, "gap")
        assert (gap.x[0], gap.y[0]) == (OPEN, CLOSE_LEVEL)
        assert gap.y.max() == pytest.approx(OPEN_LEVEL)
        assert OPEN_LEVEL > CLOSE_LEVEL
        level = _stroke(scene, "close-level")
        assert set(level.y) == {CLOSE_LEVEL} and (level.x.min(), level.x.max()) == (
            PREVIOUS_CLOSE,
            OPEN,
        )

    def test_only_the_open_to_the_close_is_held(self, every) -> None:
        """The green bar runs from the open to the close, and nothing green
        crosses either night."""
        scene = every[0]
        held = _stroke(scene, "held")
        assert (held.x.min(), held.x.max()) == (OPEN, CLOSE)
        green = np.concatenate([s.x for s in scene.strokes if s.color == GOOD])
        assert ((green >= OPEN) & (green <= CLOSE)).all()
        assert held.width > 3

    def test_each_session_is_named_under_its_own_span(self, every) -> None:
        scene = every[0]
        assert SESSION_START < _label(scene, "the day before").x < PREVIOUS_CLOSE
        assert OPEN < _label(scene, "today").x < CLOSE

    def test_the_closes_level_is_dashed(self, every) -> None:
        assert _stroke(every[0], "close-level").dashed

    def test_each_red_mark_sits_inside_its_session_on_its_price(self, every) -> None:
        """One in the day before's session, so its news is in that close, and
        one in today's after the open, too late for a trade opened at it."""
        scene = every[0]
        assert SESSION_START < NEWS_IN_CLOSE_X < PREVIOUS_CLOSE
        assert OPEN < TOO_LATE_X < CLOSE
        for gid, x in (("news-in-close", NEWS_IN_CLOSE_X), ("too-late", TOO_LATE_X)):
            mark = _stroke(scene, gid)
            assert set(mark.x) == {x}, gid
            assert mark.y.min() < price_at(x) < mark.y.max(), gid

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "A brown bracket spans the night from that close to the next open" in alt
        assert "A grey dashed line carries the close’s level across the night" in alt
        assert "a black arrow at the open climbs from it to the higher open" in alt
        assert "A thick green bar runs beneath it from the open to the close" in alt
        assert "a red mark crosses the day before’s price inside its session" in alt
        assert "a red mark crosses today’s price after the open" in alt


# --- Lesson 4: one position the helper flips ------------------------------------


class TestTheFlipSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "One position the helper flips"
        assert every[1].labels == FLIP_LABELS

    def test_the_run_gives_the_figures_it_prints(self, flip: HelperFlip) -> None:
        """The figures ``tests/test_pead.py`` pins on its own derivation, read
        here from the run the sketch draws."""
        assert (flip.symbol, flip.day) == ("PNW", "2012-02-24")
        assert [sketches.percent(v) for v in (flip.gap, flip.half_book_two)] == [
            "0.4212",
            "0.4189",
        ]
        assert sketches.percent(flip.half_first_edition) == "0.4213"
        assert flip.half_book_two <= flip.gap < flip.half_first_edition
        assert f"{100 * flip.day_return:.2f}" == "-0.36"
        assert flip.day_return == pytest.approx(-0.0035654362, abs=5e-11)
        assert flip.arithmetic_book_two == pytest.approx(0.066743, abs=5e-7)
        assert flip.arithmetic_first_edition == pytest.approx(0.066833, abs=5e-7)
        assert sketches.printed(flip.arithmetic_book_two) == "0.0667"
        assert sketches.printed(flip.arithmetic_first_edition) == "0.0668"

    def test_its_colours(self, every) -> None:
        scene = every[1]
        for gid, ink in (
            ("line", MUTED),
            ("long-tick", GOOD),
            ("no-trade-tick", LOST),
            ("gap-dot", INK),
        ):
            assert _stroke(scene, gid).color == ink, gid
            for label in _labels_of(scene, gid):
                assert label.color == ink, label.text

    def test_the_ticks_and_the_dot_sit_to_one_scale(self, every, flip) -> None:
        """Each mark's x is one affine function of its value, so the dot's
        place between the ticks is the gap's place between the two half
        deviations."""
        scene = every[1]
        long_tick, no_trade, dot = (
            _stroke(scene, g) for g in ("long-tick", "no-trade-tick", "gap-dot")
        )
        (x_long,), (x_no,), (x_dot,) = set(long_tick.x), set(no_trade.x), set(dot.x)
        values = np.array([flip.half_book_two, flip.half_first_edition, flip.gap])
        xs = np.array([x_long, x_no, x_dot])
        slope, intercept = np.polyfit(values, xs, 1)
        assert xs == pytest.approx(intercept + slope * values, abs=1e-9)
        assert slope > 0
        assert x_long < x_dot < x_no
        assert (x_dot - x_long) / (x_no - x_long) == pytest.approx(
            (flip.gap - flip.half_book_two) / (flip.half_first_edition - flip.half_book_two)
        )
        assert on_line(flip, flip.gap) == x_dot

    def test_the_dot_sits_on_the_line_and_the_ticks_cross_it(self, every) -> None:
        scene = every[1]
        line, dot = _stroke(scene, "line"), _stroke(scene, "gap-dot")
        assert set(line.y) == {LINE_Y} and dot.y.tolist() == [LINE_Y]
        assert line.x.min() < dot.x[0] < line.x.max()
        for gid in ("long-tick", "no-trade-tick"):
            tick = _stroke(scene, gid)
            assert tick.y.min() < LINE_Y < tick.y.max(), gid
            assert line.x.min() < tick.x[0] < line.x.max(), gid

    def test_each_tick_carries_its_words_above_and_below(self, every) -> None:
        """Colour is never the only cue: "long" and "no trade" sit under their
        ticks, and each helper's name and figure above."""
        scene = every[1]
        for gid, word in (("long-tick", "long"), ("no-trade-tick", "no trade")):
            tick = _stroke(scene, gid)
            below, above = sorted(_labels_of(scene, gid), key=lambda label: label.y)
            assert below.text == word and below.x == tick.x[0], gid
            assert below.y < tick.y.min() and above.y > tick.y.max(), gid

    def test_its_words_follow_made_up_figures(self, flip) -> None:
        """A long that made money on another stock and day prints its own
        figures and says it made rather than lost."""
        made_up = replace(
            flip,
            symbol="XYZ",
            day="2011-09-01",
            gap=0.0101,
            half_book_two=0.01,
            half_first_edition=0.0102,
            day_return=0.0123,
            arithmetic_book_two=0.0512,
            arithmetic_first_edition=0.0498,
        )
        scene = scenes(made_up)[1]
        assert scene.labels == [
            "half the Algorithmic Trading helper’s deviation: 1.0000%",
            "long",
            "half the first edition’s deviation: 1.0200%",
            "no trade",
            "XYZ’s gap on 2011-09-01: 1.0100%",
            "the long made 1.23%: annual return 0.0512 with it, 0.0498 without",
        ]
        (x_dot,) = set(_stroke(scene, "gap-dot").x)
        (x_long,) = set(_stroke(scene, "long-tick").x)
        (x_no,) = set(_stroke(scene, "no-trade-tick").x)
        assert (x_dot - x_long) / (x_no - x_long) == pytest.approx(0.5)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "Near its left end a green upright tick" in alt
        assert alt.count("above and “long” below") == 1
        assert alt.count("above and “no trade” below") == 1
        assert "Near its right end a taller red upright tick" in alt
        assert (
            "A black dot sits on the line between the two ticks, just short of the red one" in alt
        )
        scene = every[1]
        long_tick, no_trade = _stroke(scene, "long-tick"), _stroke(scene, "no-trade-tick")
        assert no_trade.y.max() > long_tick.y.max()
        (x_dot,) = set(_stroke(scene, "gap-dot").x)
        assert no_trade.x[0] - x_dot < (x_dot - long_tick.x[0]) / 10

    def test_it_reads_the_files_through_the_scale_break_guard(self, monkeypatch) -> None:
        """Not a second read path that skips the guard :func:`chan.pead.guarded_drift` runs."""
        from chan import pead

        def refuse(*args, **kwargs):
            raise RuntimeError("guard ran")

        monkeypatch.setattr(pead, "refuse_scale_breaks", refuse)
        with pytest.raises(RuntimeError, match="guard ran"):
            HelperFlip.from_run()

    def test_it_refuses_unless_one_long_alone_differs(self, monkeypatch) -> None:
        """With a first-edition deviation far below book two's, many more
        positions open, so the sketch's one-position premise fails."""
        from chan.matlab_helpers import smartstd_book_two

        monkeypatch.setattr(
            sketches, "smartstd_first_edition", lambda x, axis=0: 0.5 * smartstd_book_two(x, axis)
        )
        with pytest.raises(ValueError, match="positions differ between the helpers, not one"):
            HelperFlip.from_run()
