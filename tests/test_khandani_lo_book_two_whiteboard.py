"""The pins for the two whiteboard GIFs in the post on the reversal on Chan's 2012 panel.

One sketches Lesson 2's bounce in CAH's closes, which the rule bought, and one
Lesson 4's average day of the first book's rule on 2006's file and on the
panel.

1. The bounce sketch's figures come from
   :class:`chan.khandani_lo_book_two_whiteboard.Bounce`, which reads
   :func:`chan.khandani_lo_book_two.close_to_close` on the committed panel.
   What is pinned is each figure it prints, that the three dots sit at one
   affine function of their closes, that the fall's ratio lies inside the
   scale-break guard's bound and the rise's past it, and that a made-up set
   of figures moves the words with them.
2. The average-day sketch's figures come from
   :class:`chan.khandani_lo_book_two_whiteboard.AverageDays`, which reads
   :func:`chan.khandani_lo.daily_book` on both files. What is pinned is each
   figure it prints, that every bar, the hatch and the bracket end at one
   affine function of their values, that the title's count is the ratio of
   the two profits rounded and spelled, and that the part kept is less than
   a third of the profit.

The runs read committed vintages, so these tests read the runs directly
rather than a frozen copy of their figures. ``tests/test_khandani_lo.py`` and
``tests/test_khandani_lo_book_two.py`` hold the same figures on their own
derivation.

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

from chan import khandani_lo
from chan import khandani_lo_book_two_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.khandani_lo import ONE_WAY_COST, daily_book, reversal
from chan.khandani_lo_book_two import (
    SOURCE_FILE,
    WINDOW_END,
    WINDOW_START,
    book_two,
    close_to_close,
    held_overnight,
)
from chan.khandani_lo_book_two_whiteboard import (
    BOUGHT_BELOW,
    DAY_X,
    PRICE_AXIS_X,
    PRICE_FOOT,
    PRICE_LOW,
    RISE_X,
    AverageDays,
    Bounce,
    gif_name,
    main,
    make_khandani_lo_book_two_whiteboards,
    on_scale,
    price_y,
    scenes,
    sketch_timeline,
    spelled,
    times_in_words,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.series import SCALE_BREAK_BOUND, load_panel, scale_breaks
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

POST = REPO_ROOT / "blog" / "khandani-lo-reversal-lessons.md"

#: Every GIF in the order :func:`make_khandani_lo_book_two_whiteboards` writes them.
GIFS = [
    "khandani_lo_book_two_sketch_cah_bounce.gif",
    "khandani_lo_book_two_sketch_average_day.gif",
]

#: What each GIF follows: Lesson 2's paragraph on CAH and Lesson 4's on the
#: cost as a share of the profit, each keyed on its opening words.
BOUNCE_PARAGRAPH = "One of them is not."
AVERAGE_DAY_PARAGRAPH = "So over 2006 the cost was"

BOUNCE_LABELS = [
    "CAH’s close",
    "2009-08-31",
    "09-01",
    "09-02",
    "19.96",
    "14.50",
    "23.57",
    "11.00",
    "× 0.7265: inside\nthe check’s bounds",
    "× 1.6255:\npast 1.6, flagged",
    "bought at the close:\n3.17 cents of the $1",
    "up 62.55 percent:\n1.98 cents earned\nthe next day",
    "without CAH: 13.26 percent and 1.2267, neither matches the book",
]

AVERAGE_DAY_LABELS = [
    "0",
    "5",
    "10",
    "basis points a day, of the average gross position",
    "2006, the first book’s file",
    "cost 7.2525",
    "profit 0.5276",
    "2007 to 2011, the panel",
    "cost 7.2868",
    "profit 10.5234",
    "trades 1.4505 and 1.4574 times the position a day",
    "cost is 13.7453 times the profit",
    "kept: 3.2366,\nless than a third",
    "first book’s rule, 5 basis points on every buy and sell, first day’s trades charged",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def frames():
    _, panel = load_panel(SOURCE_FILE)
    _, first_file = load_panel(khandani_lo.SOURCE_FILE)
    return panel, first_file


@pytest.fixture(scope="module")
def bounce(frames) -> Bounce:
    return Bounce.from_panel(frames[0])


@pytest.fixture(scope="module")
def days(frames) -> AverageDays:
    return AverageDays.from_frames(*frames)


@pytest.fixture(scope="module")
def every(bounce, days):
    return scenes(bounce, days)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_khandani_lo_book_two_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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
        assert sketches.PACED == ("cah_bounce", "average_day")
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
        again = make_khandani_lo_book_two_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart_and_the_other_sketches(self) -> None:
        """No other file starts like these, so the prefix check above reads
        only this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert "khandani_lo_book_two.png" in names

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
            ), f"{path.name}: redraw with: uv run python -m chan.khandani_lo_book_two_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    @pytest.mark.parametrize(
        ("opening", "name", "lesson", "next_lesson"),
        [
            (BOUNCE_PARAGRAPH, GIFS[0], "## Lesson 2:", "## Lesson 3:"),
            (AVERAGE_DAY_PARAGRAPH, GIFS[1], "## Lesson 4:", "## What this replication"),
        ],
        ids=["bounce", "average day"],
    )
    def test_each_sketch_follows_its_paragraph_with_a_caption(
        self, opening, name, lesson, next_lesson
    ) -> None:
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", paragraphs[index + 1]
        )
        caption = paragraphs[index + 2]
        assert caption.startswith("*Drawn to one scale from the run") and caption.endswith("*")
        text = POST.read_text(encoding="utf-8")
        assert (
            text.index(lesson) < text.index(f"(../docs/figures/{name})") < text.index(next_lesson)
        )

    def test_each_caption_names_the_marks_it_explains(self) -> None:
        """Colour is never the only cue, so each caption names its marks."""
        paragraphs = _paragraphs()
        captions = [paragraphs[k + 1] for k, p in enumerate(paragraphs) if p.startswith("![")]
        captions = [c for c in captions if "Drawn to one scale from the run" in c]
        bounce_caption, day_caption = captions
        for mark in ("black arrow", "red arrow", "green bar", "green bracket"):
            assert mark in bounce_caption, mark
        assert "the fall it lets through" in bounce_caption
        assert "the rise it flags" in bounce_caption
        for mark in ("red bar", "green bar", "red hatching", "brown bracket"):
            assert mark in day_caption, mark

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

    def test_each_alt_text_says_it_is_slow_and_drawn_from_the_run(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "schematic" not in alt
            assert "drawn to one scale from the run" in alt
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_the_module_says_neither_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "Neither is schematic." in doc


# --- Lesson 2: the bounce the rule bought -----------------------------------------


class TestTheBounceSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "The bounce the rule bought"
        assert every[0].labels == BOUNCE_LABELS

    def test_the_run_gives_the_figures_it_prints(self, bounce: Bounce, frames) -> None:
        """Each figure from the panel and the run, derived here a second way."""
        panel, _ = frames
        assert bounce.closes == (19.96, 14.5, 23.57)
        assert panel["CAH"].loc["2009-08-31":"2009-09-02"].tolist() == list(bounce.closes)
        assert bounce.fall == pytest.approx(14.5 / 19.96)
        assert bounce.rise == pytest.approx(23.57 / 14.5)
        assert (f"{bounce.fall:.4f}", f"{bounce.rise:.4f}") == ("0.7265", "1.6255")
        assert bounce.bound == pytest.approx(1.6, abs=1e-12)
        assert SCALE_BREAK_BOUND == pytest.approx(math.log(1.6))
        assert bounce.weight == pytest.approx(0.031684, abs=5e-7)
        assert bounce.rise - 1 == pytest.approx(0.6255, abs=5e-5)
        assert bounce.earned == pytest.approx(0.019819, abs=5e-7)
        assert (sketches.cents(bounce.weight), sketches.cents(bounce.earned)) == ("3.17", "1.98")
        assert 100 * bounce.apr_without == pytest.approx(13.26, abs=5e-3)
        assert bounce.sharpe_without == pytest.approx(1.2267, abs=5e-5)

    def test_the_weight_is_the_one_example_4_3_holds(self, frames, bounce: Bounce) -> None:
        """CAH's weight at the 2009-09-01 close is :class:`BookTwo`'s, and
        what it earned is its term in the next day's sum."""
        panel, first_file = frames
        _, opens = load_panel(SOURCE_FILE, field="Open")
        run = book_two(opens, panel, first_file).close_to_close
        column = panel.columns.get_loc("CAH")
        row = run.days.get_loc(pd.Timestamp("2009-09-01"))
        assert run.weights[row, column] == bounce.weight
        assert np.nansum(np.abs(run.weights[row])) == pytest.approx(1.0)
        returns = khandani_lo.daily_returns(panel.loc[run.days].to_numpy(dtype=float))
        others = run.weights.copy()
        others[:, column] = 0.0
        term = (
            held_overnight(run.weights, returns)[row + 1] - held_overnight(others, returns)[row + 1]
        )
        assert term == pytest.approx(bounce.earned, abs=1e-15)

    def test_the_guard_lets_the_fall_through_and_flags_the_rise(self, frames, bounce) -> None:
        panel, _ = frames
        series = panel["CAH"].loc[WINDOW_START:WINDOW_END].dropna()
        flagged = {str(day.date()) for day in scale_breaks(series)}
        assert "2009-09-02" in flagged and "2009-09-01" not in flagged
        assert abs(math.log(bounce.fall)) < SCALE_BREAK_BOUND < abs(math.log(bounce.rise))
        assert bounce.flagged == ("2009-09-02",)

    def test_the_figures_without_cah_are_example_4_3_on_the_rest(self, frames, bounce) -> None:
        panel, _ = frames
        without = close_to_close(panel.drop(columns=["CAH"]), start=WINDOW_START, end=WINDOW_END)
        assert (without.apr, without.sharpe) == (bounce.apr_without, bounce.sharpe_without)

    def test_its_colours(self, every) -> None:
        scene = every[0]
        for gid, ink in (
            ("price-axis", MUTED),
            ("time-axis", MUTED),
            ("day-tick-0", MUTED),
            ("price-tick-0", MUTED),
            ("close-0", INK),
            ("close-1", INK),
            ("close-2", INK),
            ("fall", INK),
            ("rise", LOST),
            ("bought", GOOD),
            ("earned", GOOD),
        ):
            assert _stroke(scene, gid).color == ink, gid
            for label in _labels_of(scene, gid):
                assert label.color == ink, label.text

    def test_the_dots_and_price_ticks_sit_to_one_scale(self, every, bounce) -> None:
        """Each dot's height is one affine function of its close, and each
        price tick is at its dot's height."""
        scene = every[0]
        heights = np.array([_stroke(scene, f"close-{k}").y[0] for k in range(3)])
        closes = np.array(bounce.closes)
        slope, intercept = np.polyfit(closes, heights, 1)
        assert heights == pytest.approx(intercept + slope * closes, abs=1e-9)
        assert slope > 0
        assert heights.tolist() == [price_y(c) for c in bounce.closes]
        for k, close in enumerate(bounce.closes):
            tick = _stroke(scene, f"price-tick-{k}")
            assert set(tick.y) == {heights[k]}
            assert _label(scene, f"{close:.2f}").y == heights[k]
            assert tick.x.min() < PRICE_AXIS_X < tick.x.max()

    def test_each_dot_stands_over_its_day(self, every) -> None:
        scene = every[0]
        for k, x in enumerate(DAY_X):
            assert _stroke(scene, f"close-{k}").x.tolist() == [x]
            assert set(_stroke(scene, f"day-tick-{k}").x) == {x}
            (label,) = _labels_of(scene, f"day-tick-{k}")
            assert label.x == x and label.y < PRICE_FOOT
        assert DAY_X[0] < DAY_X[1] < DAY_X[2]

    def test_the_arrows_run_from_dot_to_dot(self, every) -> None:
        """The black arrow points down from the first close to the second, and
        the red one up from the second to the third, each between its dots."""
        scene = every[0]
        dots = [
            (_stroke(scene, f"close-{k}").x[0], _stroke(scene, f"close-{k}").y[0]) for k in range(3)
        ]
        for gid, (a, b) in (("fall", (dots[0], dots[1])), ("rise", (dots[1], dots[2]))):
            arrow = _stroke(scene, gid)
            assert a[0] < arrow.x.min() and arrow.x.max() < b[0], gid
            tip = np.argmax(arrow.x)
            assert (arrow.y[tip] < arrow.y[0]) == (b[1] < a[1]), gid
        assert dots[1][1] < dots[0][1] < dots[2][1]

    def test_the_green_mark_sits_under_the_bought_close(self, every) -> None:
        """Beside the dot rather than on it, so the dot does not hide it."""
        scene = every[0]
        bought, dot = _stroke(scene, "bought"), _stroke(scene, "close-1")
        assert set(bought.y) == {dot.y[0] - BOUGHT_BELOW}
        assert bought.x.min() < dot.x[0] < bought.x.max()
        assert bought.width > 3

    def test_the_bracket_spans_the_rise(self, every) -> None:
        scene = every[0]
        bracket = _stroke(scene, "earned")
        low, high = _stroke(scene, "close-1").y[0], _stroke(scene, "close-2").y[0]
        assert (bracket.y.min(), bracket.y.max()) == (low, high)
        upright = bracket.y[bracket.x == RISE_X]
        assert (upright.min(), upright.max()) == (low, high)
        assert RISE_X > DAY_X[2]

    def test_the_foot_tick_marks_where_the_price_axis_starts(self, every) -> None:
        """The axis starts at 11 rather than 0, and its foot tick says so."""
        scene = every[0]
        foot = _stroke(scene, "price-tick-foot")
        assert set(foot.y) == {price_y(PRICE_LOW)} == {PRICE_FOOT}
        assert foot.x.max() == PRICE_AXIS_X
        label = _label(scene, f"{PRICE_LOW:.2f}")
        assert (label.y, label.names) == (PRICE_FOOT, "price-tick-foot")

    def test_its_words_follow_made_up_figures(self, bounce: Bounce) -> None:
        made_up = replace(
            bounce,
            closes=(30.0, 25.0, 41.0),
            weight=0.0125,
            earned=0.0125 * (41 / 25 - 1),
            apr_without=0.1111,
            sharpe_without=1.0101,
        )
        scene = sketches._bounce(made_up)
        assert scene.labels[4:] == [
            "30.00",
            "25.00",
            "41.00",
            "11.00",
            "× 0.8333: inside\nthe check’s bounds",
            "× 1.6400:\npast 1.6, flagged",
            "bought at the close:\n1.25 cents of the $1",
            "up 64.00 percent:\n0.80 cents earned\nthe next day",
            "without CAH: 11.11 percent and 1.0101, neither matches the book",
        ]

    @pytest.mark.parametrize(
        ("change", "message"),
        [
            ({"closes": (20.0, 11.0, 23.57)}, "lets the fall through"),
            ({"flagged": ()}, "lets the fall through"),
            ({"weight": -0.01}, "bought CAH"),
            ({"apr_without": 0.137}, "neither figure"),
            ({"sharpe_without": 1.26}, "neither figure"),
        ],
        ids=["fall flagged", "rise not flagged", "shorted", "apr matches", "sharpe matches"],
    )
    def test_it_refuses_figures_that_make_its_words_false(self, bounce, change, message) -> None:
        with pytest.raises(ValueError, match=message):
            replace(bounce, **change).refuse_false_words()

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "three black dots stand at those closes above the three days" in alt
        assert "the middle one lowest and the last one highest" in alt
        assert "A black arrow runs down from the first dot to the second" in alt
        assert "A red arrow runs up from the second dot to the third" in alt
        assert "A thick green bar sits just under the second dot" in alt
        assert "spans the rise from the second dot’s height to the third’s" in alt


# --- Lesson 4: same trading, twenty times the profit --------------------------------


class TestTheAverageDaySketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Same trading, twenty times the profit"
        assert every[1].labels == AVERAGE_DAY_LABELS

    def test_the_runs_give_the_figures_it_prints(self, days: AverageDays, frames) -> None:
        """The figures the two runs' own tests pin, read here from the runs
        the sketch draws, with the panel's through :class:`BookTwo`."""
        panel, first_file = frames
        year = daily_book(reversal(first_file))
        _, opens = load_panel(SOURCE_FILE, field="Open")
        on_panel = daily_book(book_two(opens, panel, first_file).first_rule_on_panel)
        assert (days.year_profit, days.year_cost) == (1e4 * year.profit, 1e4 * year.cost)
        assert (days.panel_profit, days.panel_cost) == (1e4 * on_panel.profit, 1e4 * on_panel.cost)
        assert (days.year_turnover, days.panel_turnover) == (year.turnover, on_panel.turnover)
        assert days.year_profit == pytest.approx(0.5276, abs=5e-5)
        assert days.year_cost == pytest.approx(7.2525, abs=5e-5)
        assert days.year_turnover == pytest.approx(1.4505, abs=5e-5)
        assert days.year_cost_per_profit == pytest.approx(13.7453, abs=5e-5)
        assert days.panel_profit == pytest.approx(10.5234, abs=5e-5)
        assert days.panel_cost == pytest.approx(7.2868, abs=5e-5)
        assert days.panel_turnover == pytest.approx(1.4574, abs=5e-5)
        assert days.panel_cost / days.panel_profit == pytest.approx(0.6924, abs=5e-5)
        assert days.profit_ratio == pytest.approx(19.94, abs=5e-3)

    def test_the_part_kept_is_the_profit_less_the_cost_and_under_a_third(self, days) -> None:
        assert days.panel_kept == days.panel_profit - days.panel_cost
        assert days.panel_kept == pytest.approx(3.2366, abs=5e-5)
        assert days.panel_kept / days.panel_profit == pytest.approx(0.3076, abs=5e-5)
        assert days.panel_kept < days.panel_profit / 3

    def test_the_title_spells_the_profit_ratio_rounded_to_a_whole_number(self, days) -> None:
        """19.94 rounds to 20, which is what the title and the post's "about
        twenty times" say. The ratio sits 0.44 from the 19.5 below which it
        would read nineteen."""
        assert round(days.profit_ratio) == 20
        assert times_in_words(days.profit_ratio) == "twenty"
        assert days.profit_ratio - 19.5 == pytest.approx(0.44, abs=5e-3)
        assert [spelled(n) for n in (0, 7, 13, 20, 21, 99, 100)] == [
            "no",
            "seven",
            "thirteen",
            "twenty",
            "twenty-one",
            "ninety-nine",
            "100",
        ]

    def test_the_closing_line_names_the_runs_cost(self, every) -> None:
        assert ONE_WAY_COST == pytest.approx(5e-4)
        assert every[1].labels[-1].startswith(f"first book’s rule, {ONE_WAY_COST * 1e4:g} basis")

    def test_its_colours(self, every) -> None:
        scene = every[1]
        for gid, ink in (
            ("axis", MUTED),
            ("tick-0", MUTED),
            ("year-cost", LOST),
            ("year-profit", GOOD),
            ("panel-cost", LOST),
            ("panel-profit", GOOD),
            ("short", LOST),
            ("kept", ACCENT),
        ):
            assert _stroke(scene, gid).color == ink, gid
        for text, ink in (
            ("cost 7.2525", LOST),
            ("profit 0.5276", GOOD),
            ("cost 7.2868", LOST),
            ("profit 10.5234", GOOD),
            ("cost is 13.7453 times the profit", LOST),
            ("kept: 3.2366,\nless than a third", ACCENT),
            ("trades 1.4505 and 1.4574 times the position a day", MUTED),
            ("basis points a day, of the average gross position", MUTED),
            (
                "first book’s rule, 5 basis points on every buy and sell,"
                " first day’s trades charged",
                MUTED,
            ),
        ):
            assert _label(scene, text).color == ink, text

    def test_every_bar_names_cost_or_profit(self, every) -> None:
        """Colour is never the only cue: each red bar's label says cost and
        each green bar's says profit."""
        scene = every[1]
        for gid in ("year-cost", "year-profit", "panel-cost", "panel-profit"):
            bar = _stroke(scene, gid)
            word = "cost" if bar.color == LOST else "profit"
            (label,) = [s for s in _labels_of(scene, gid) if s.y == bar.y[0]]
            assert label.text.startswith(f"{word} "), gid
            assert label.x < bar.x.min()

    def test_every_bar_and_mark_sits_to_one_scale(self, every, days) -> None:
        """Each bar starts at zero and ends at one affine function of its
        figure, and the ticks sit on the same scale."""
        scene = every[1]
        values = np.array(
            [days.year_cost, days.year_profit, days.panel_cost, days.panel_profit, 0, 5, 10]
        )
        ends = np.array(
            [
                _stroke(scene, gid).x.max()
                for gid in ("year-cost", "year-profit", "panel-cost", "panel-profit")
            ]
            + [_stroke(scene, f"tick-{p}").x[0] for p in (0, 5, 10)]
        )
        slope, intercept = np.polyfit(values, ends, 1)
        assert ends == pytest.approx(intercept + slope * values, abs=1e-9)
        assert slope > 0
        for gid in ("year-cost", "year-profit", "panel-cost", "panel-profit"):
            assert _stroke(scene, gid).x.min() == on_scale(0), gid
            assert len(set(_stroke(scene, gid).y)) == 1, gid

    def test_the_hatch_runs_from_2006s_profit_to_its_cost(self, every, days) -> None:
        scene = every[1]
        hatch, profit = _stroke(scene, "short"), _stroke(scene, "year-profit")
        assert (hatch.x.min(), hatch.x.max()) == pytest.approx(
            (on_scale(days.year_profit), on_scale(days.year_cost))
        )
        assert hatch.x.max() == pytest.approx(_stroke(scene, "year-cost").x.max())
        assert hatch.y.min() < profit.y[0] < hatch.y.max()

    def test_the_bracket_runs_from_the_panels_cost_to_its_profit(self, every, days) -> None:
        scene = every[1]
        bracket, cost = _stroke(scene, "kept"), _stroke(scene, "panel-cost")
        assert (bracket.x.min(), bracket.x.max()) == (
            cost.x.max(),
            _stroke(scene, "panel-profit").x.max(),
        )
        assert bracket.y.min() < cost.y[0] < bracket.y.max()
        run = bracket.x[bracket.y == cost.y[0]]
        assert (run.min(), run.max()) == (bracket.x.min(), bracket.x.max())
        assert bracket.x.max() - bracket.x.min() == pytest.approx(
            sketches.PER_POINT * days.panel_kept
        )

    def test_each_pair_sits_under_its_heading(self, every) -> None:
        scene = every[1]
        year_heading = _label(scene, "2006, the first book’s file")
        panel_heading = _label(scene, "2007 to 2011, the panel")
        year = [_stroke(scene, g).y[0] for g in ("year-cost", "year-profit")]
        panel = [_stroke(scene, g).y[0] for g in ("panel-cost", "panel-profit")]
        assert year_heading.y > max(year) > min(year) > panel_heading.y > max(panel)
        assert min(panel) > _stroke(scene, "axis").y[0]

    def test_its_words_follow_made_up_figures(self, days: AverageDays) -> None:
        made_up = replace(
            days,
            year_profit=2.0,
            year_cost=6.0,
            year_turnover=1.2,
            panel_profit=6.4,
            panel_cost=5.0,
            panel_turnover=1.0,
        )
        scene = sketches._average_day(made_up)
        assert scene.title == "Same trading, three times the profit"
        assert scene.labels[5:13] == [
            "cost 6.0000",
            "profit 2.0000",
            "2007 to 2011, the panel",
            "cost 5.0000",
            "profit 6.4000",
            "trades 1.2000 and 1.0000 times the position a day",
            "cost is 3.0000 times the profit",
            "kept: 1.4000,\nless than a third",
        ]

    @pytest.mark.parametrize(
        ("change", "message"),
        [
            ({"year_cost": 0.4}, "2006's cost passes its profit"),
            ({"panel_cost": 11.0}, "less than a third"),
            ({"panel_cost": 6.0}, "less than a third"),
        ],
        ids=["2006 pays its cost", "panel loses", "panel keeps a third or more"],
    )
    def test_it_refuses_figures_that_make_its_words_false(self, days, change, message) -> None:
        with pytest.raises(ValueError, match=message):
            replace(days, **change).refuse_false_words()

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "a short green bar labelled “profit 0.5276”" in alt
        assert "about as long as the first, sits above a long green bar" in alt
        assert (
            "a red hatched stretch runs from the end of the short green bar to where the red "
            "cost bar above it ends" in alt
        )
        assert (
            "a brown bracket runs from the end of the red cost bar to where the green profit "
            "bar below it ends" in alt
        )
