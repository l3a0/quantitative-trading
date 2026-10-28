"""The pins for the two whiteboard GIFs in the long GLD, short gold futures post.

One sketches the opening's claim that owning the metal and shorting its
future leaves only the roll return, and one Lesson 4's claim that an offset
between the two legs' recording times would put two moves of gold into each
day's change in log(GC / GLD). What is pinned is what a reader takes from each.

1. The opening's sketch is schematic and carries no figures. Its words name
   neither GLD nor GC, because the post names them only in the next
   paragraph, and it draws no total and no −4.9 percent. Each strike crosses
   the spot return it strikes out and no other label.
2. The Lesson 4 sketch is schematic apart from its last line, which reads the
   bound from :attr:`chan.gld_gc.Identity.gap_share` on the committed files.
   The test derives that bound again from :func:`chan.gld_gc.identity`
   rather than trusting the sketch's own reading, and a made-up bound shows
   the line follows the run. Its GC tick is dashed and its words say "if",
   because the post concludes the file is not recorded at 1:30 p.m.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, both
sketches' slower pace, that two draws give the same bytes, and that each
committed GIF is a fresh draw, a comparison that runs only on macOS arm64
with Comic Sans MS, as ``tests/test_usdcad_tests_whiteboard.py`` explains.
The one exception to the clearance rule is each strike over the spot return
it strikes out. The check that ``docs/figures`` holds exactly the GIFs the
modules draw lives in ``tests/test_equity_seasonals_whiteboard.py``, which
reads :data:`GIFS` from here.
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

from chan import gld_gc
from chan import gld_gc_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.gld_gc_whiteboard import (
    GC_AT,
    GLD_AT,
    Bound,
    day_x,
    gif_name,
    main,
    make_gld_gc_whiteboards,
    price,
    scenes,
    sketch_timeline,
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
    Scene,
    clearances,
    hand_font,
    timeline,
)

POST = REPO_ROOT / "blog" / "gld-gc-lessons.md"

#: Every GIF in the order :func:`make_gld_gc_whiteboards` writes them.
GIFS = [
    "gld_gc_sketch_roll_left.gif",
    "gld_gc_sketch_two_moves.gif",
]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "Ernest Chan’s *Algorithmic Trading* turns the split into a trade.",
    "Of a 24-hour day, a share of 0.001775 is about 2.6 minutes",
)

SPEC = (
    "GC from inputdata_gc_1600_20100802/gc.csv, chan-mat, raw, saved 2012-05-07, and GLD from "
    "inputdata_etf/gld.csv, chan-mat, adjusted, saved 2012-04-10; half the squared ratio of "
    "the daily change in log(GC / GLD)'s standard deviation over n to GLD's daily log return's, "
    "over the 752 kept days"
)

ROLL_LABELS = [
    "own the metal:",
    "+ spot return",
    "short the future:",
    "− spot return",
    "− roll return",
    "left: − roll return",
    "in contango the roll return is below 0, so − roll return is above 0",
]

MOVES_LABELS = [
    "if GC were recorded at 1:30 p.m.",
    "GLD recorded at 4 p.m.",
    "yesterday",
    "today",
    "each day’s log(GC / GLD) carries that day’s move over the gap",
    "each change carries two: today’s, and yesterday’s with its sign flipped",
    "each move carries the gap’s share of a day’s variance, so the change carries twice that",
    "at most 0.001775 of a day, about 2.6 minutes, against 150",
]

#: Each strike, and the one label it strikes out.
STRUCK = {"strike-own": "+ spot return", "strike-short": "− spot return"}

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def bound() -> Bound:
    return Bound.from_run()


@pytest.fixture(scope="module")
def every(bound):
    return scenes(bound)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, bound):
    return make_gld_gc_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"), bound=bound)


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels_of(scene, gid):
    return [s.text for s in scene.steps if isinstance(s, Label) and s.names == gid]


def _font(monkeypatch, fallback: bool) -> None:
    if fallback:
        monkeypatch.setattr(whiteboard, "hand_font", lambda: whiteboard.FALLBACK_FONT)


def _without(scene, gids=(), texts=()) -> Scene:
    """The scene with the strokes ``gids`` and the labels ``texts`` left out."""
    kept = tuple(
        s
        for s in scene.steps
        if not (isinstance(s, Label) and s.text in texts) and getattr(s, "gid", None) not in gids
    )
    return Scene(scene.title, scene.slug, kept)


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

    def test_neither_draws_a_tint(self, every) -> None:
        """No pale tint, so none needs the green edge the shared rules ask of one."""
        assert not [fill for scene in every for fill in scene.fills]


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, every, monkeypatch, fallback) -> None:
        """Every label clears every stroke, except that each strike crosses the
        spot return it strikes out. Leaving the strikes out, every label clears
        the rest. Keeping one strike and leaving out only the label it strikes,
        every other label, the other spot return included, clears it too."""
        _font(monkeypatch, fallback)
        for scene in every:
            parts = [_without(scene, gids=STRUCK)] + [
                _without(scene, gids=set(STRUCK) - {gid}, texts={text})
                for gid, text in STRUCK.items()
            ]
            for part in parts:
                found = clearances(part)
                assert set(found) == {*part.labels, part.title}
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
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace, in both sketches."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("roll_left", "two_moves")
        for scene in every:
            frames = sketch_timeline(scene)
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            assert labels, scene.slug
            assert {f.ms for f in labels} == {sketches.PACED_LABEL_MS}, scene.slug
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, bound) -> None:
        again = make_gld_gc_whiteboards(out_dir=tmp_path, bound=bound)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "gld_gc.png").exists()

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
            ), f"{path.name}: redraw with: uv run python -m chan.gld_gc_whiteboard"


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

    def test_each_sits_in_its_section(self) -> None:
        """The first sits before the paragraph that names GLD and GC, and the
        second under the bound's heading, before Chan's other GC series."""
        text = POST.read_text(encoding="utf-8")
        roll_left, two_moves = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        why = text.index("## Why own the metal and short the future")
        names = text.index("Owning gold bars is awkward, so the long leg is GLD")
        bound = text.index("### A bound of about 2.6 minutes, against the caveat’s 150")
        other = text.index("### Chan’s other GC series, for contrast")
        assert why < roll_left < names
        assert bound < two_moves < other

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        for scene in every:
            alt, at = _alt(scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_how_much_is_schematic_and_names_its_pace(self, every) -> None:
        roll_left, two_moves = (_alt(scene) for scene in every)
        assert "It is schematic and carries no figures." in roll_left
        assert "It is schematic apart from its last line, which reads the run’s bound." in two_moves
        for alt in (roll_left, two_moves):
            assert "drawn slowly" in alt and "twelve seconds" in alt

    def test_the_module_says_how_much_of_each_sketch_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "The first sketch is schematic and carries no figures." in doc
        assert "The second is schematic apart from its last line." in doc


# --- Why own the metal and short the future: the roll return is left ----------


class TestTheRollLeftSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "The spot returns cancel, and the roll return is left"
        assert every[0].labels == ROLL_LABELS

    def test_it_names_neither_leg_by_its_ticker(self, every) -> None:
        """The post names GLD and GC only in the paragraph after this sketch."""
        scene = every[0]
        for text in (scene.title, *scene.labels, _alt(scene)):
            assert not re.search(r"\b(GLD|GC)\b", text), text

    def test_it_draws_no_total_and_no_figure(self, every) -> None:
        """No leg's total and no −4.9 percent: the only digit drawn is the 0
        that the roll return is set against."""
        scene = every[0]
        digits = set(re.findall(r"\d", " ".join([scene.title, *scene.labels])))
        assert digits == {"0"}

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert {s.gid: s.color for s in scene.strokes} == {
            "own": GOOD,
            "short": LOST,
            "strike-own": INK,
            "strike-short": INK,
            "left": ACCENT,
            "check": GOOD,
        }
        assert [_label(scene, text).color for text in ROLL_LABELS] == [
            GOOD,
            GOOD,
            LOST,
            LOST,
            LOST,
            ACCENT,
            GOOD,
        ]

    def test_each_label_names_the_stroke_it_sits_beside(self, every) -> None:
        scene = every[0]
        assert _labels_of(scene, "own") == ROLL_LABELS[:2]
        assert _labels_of(scene, "short") == ROLL_LABELS[2:5]
        assert _labels_of(scene, "left") == [ROLL_LABELS[5]]
        assert _labels_of(scene, "check") == [ROLL_LABELS[6]]

    def test_the_long_points_up_and_the_short_down(self, every) -> None:
        """Each arrow's shaft starts at its first point and its head sits where
        the shaft ends, so the long's first point is its lowest and the
        short's its highest, each on the far side of its row."""
        scene = every[0]
        own, short = _stroke(scene, "own"), _stroke(scene, "short")
        assert own.y[0] == own.y.min() < _label(scene, "own the metal:").y < own.y.max()
        assert short.y[0] == short.y.max() > _label(scene, "short the future:").y > short.y.min()
        for arrow, leg in ((own, "own the metal:"), (short, "short the future:")):
            assert arrow.x.max() < _label(scene, leg).x

    def test_the_two_spot_returns_share_a_column_and_sit_on_their_legs_rows(self, every) -> None:
        scene = every[0]
        plus, minus = _label(scene, "+ spot return"), _label(scene, "− spot return")
        assert plus.x == minus.x
        assert plus.y == _label(scene, "own the metal:").y
        assert minus.y == _label(scene, "short the future:").y == _label(scene, "− roll return").y
        assert _label(scene, "− roll return").x > minus.x

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_each_strike_crosses_its_spot_return_from_corner_to_corner(
        self, every, monkeypatch, fallback
    ) -> None:
        """A slash that starts left of and below its label's box, ends right
        of and above it, and so crosses the whole word, and that nothing but
        that label touches."""
        _font(monkeypatch, fallback)
        scene = every[0]
        boxes, to_pixels = _boxes(scene)
        found = dict(boxes)
        for gid, text in STRUCK.items():
            strike, box = _stroke(scene, gid), found[text]
            xy = to_pixels.transform(np.column_stack([strike.x, strike.y]))
            (x0, y0), (x1, y1) = xy[0], xy[-1]
            assert x0 < box.x0 and y0 < box.y0, (gid, fallback)
            assert x1 > box.x1 and y1 > box.y1, (gid, fallback)
        assert {t: p for t, p in clearances(scene).items() if p < CLEAR_PX}.keys() == set(
            STRUCK.values()
        )

    def test_each_strike_comes_after_the_term_it_strikes_and_before_what_is_left(
        self, every
    ) -> None:
        scene = every[0]
        order = [getattr(s, "gid", None) or s.text for s in scene.steps]
        for gid, text in STRUCK.items():
            assert order.index(text) < order.index(gid) < order.index("left"), gid
        assert order.index("− roll return") < order.index("strike-own")

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[0])
        for phrase in (
            "A green arrow pointing up",
            "a red arrow pointing down",
            "with the two spot returns one above the other",
            "A black slash then strikes out each spot return",
            "A brown arrow points down from the roll return",
            "a green check mark",
        ):
            assert phrase in alt, phrase

    def test_the_brown_arrow_runs_from_the_roll_return_down_to_what_is_left(self, every) -> None:
        scene = every[0]
        arrow = _stroke(scene, "left")
        roll, left = _label(scene, "− roll return"), _label(scene, "left: − roll return")
        assert arrow.y[0] < roll.y and arrow.y.min() > left.y
        assert arrow.y[0] == arrow.y.max()
        assert arrow.x[0] == pytest.approx(left.x)
        boxes, to_pixels = _boxes(scene)
        box = dict(boxes)["− roll return"]
        x_pixels = to_pixels.transform([(arrow.x[0], arrow.y[0])])[0][0]
        assert box.x0 < x_pixels < box.x1

    def test_the_rows_stack_from_the_legs_down_to_the_check(self, every) -> None:
        scene = every[0]
        heights = [
            _label(scene, text).y
            for text in ("own the metal:", "short the future:", "left: − roll return")
        ] + [float(np.median(_stroke(scene, "check").y))]
        assert heights == sorted(heights, reverse=True)


# --- Lesson 4: an offset puts two moves in each day's change ------------------


class TestTheBound:
    def test_it_is_the_runs(self, bound) -> None:
        """Read again from :func:`chan.gld_gc.identity` rather than through
        :class:`Bound`, and from the two standard deviations it is built on."""
        sources = gld_gc.read_sources()
        found = gld_gc.identity(sources, gld_gc.gld_gc(sources))
        assert bound.gap_share == found.gap_share, SPEC
        assert bound.gap_share == pytest.approx(
            (found.sampled_at_1600.spread / found.gld_spread) ** 2 / 2
        )
        assert bound.gap_share == pytest.approx(0.0017752507, abs=5e-11), SPEC

    def test_its_minutes_are_that_share_of_a_24_hour_day(self, bound) -> None:
        assert bound.minutes == pytest.approx(bound.gap_share * 1440)
        assert f"{bound.minutes:.1f}" == "2.6"

    def test_the_caveat_is_two_and_a_half_hours(self, bound) -> None:
        assert bound.caveat_minutes == 150


#: A made-up bound, so the line that should follow the run does.
OTHER = Bound(gap_share=0.0123456, caveat_minutes=120)


class TestTheTwoMovesSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "An offset puts two moves in each day’s change"
        assert every[1].labels == MOVES_LABELS

    def test_its_last_line_follows_the_bound(self, bound) -> None:
        scene = scenes(OTHER)[1]
        assert scene.labels[-1] == "at most 0.012346 of a day, about 17.8 minutes, against 120"
        assert scene.labels[:-1] == MOVES_LABELS[:-1]
        assert scenes(bound)[1].labels[-1] == (
            f"at most {bound.gap_share:.6f} of a day, about {bound.gap_share * 1440:.1f} "
            f"minutes, against 150"
        )

    def test_it_reads_as_a_supposition(self, every) -> None:
        """The post concludes the file is not recorded at 1:30 p.m., so the
        1:30 tick is dashed and its words say what would follow if it were."""
        scene = every[1]
        assert _label(scene, MOVES_LABELS[0]).text.startswith("if GC were ")
        assert all(_stroke(scene, f"gc-{day}").dashed for day in (0, 1))
        assert not any(_stroke(scene, f"gld-{day}").dashed for day in (0, 1))

    def test_it_uses_no_word_the_post_defines_later(self, every) -> None:
        """The post defines a change that reverses two paragraphs on."""
        scene = every[1]
        for text in (scene.title, *scene.labels, _alt(scene)):
            assert "revers" not in text.lower(), text

    def test_it_writes_no_minus_on_todays_move(self, every) -> None:
        assert not [text for text in every[1].labels if "−" in text or " - " in text]

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert {s.gid: s.color for s in scene.strokes} == {
            "price": ACCENT,
            "gc-0": MUTED,
            "gld-0": INK,
            "gc-1": MUTED,
            "gld-1": INK,
            "move-0": ACCENT,
            "move-1": ACCENT,
            "check": GOOD,
        }
        assert [_label(scene, text).color for text in MOVES_LABELS] == [
            MUTED,
            INK,
            MUTED,
            MUTED,
            INK,
            INK,
            INK,
            GOOD,
        ]

    def test_each_day_has_its_two_ticks_one_gap_apart(self, every) -> None:
        scene = every[1]
        for day in (0, 1):
            gc, gld = _stroke(scene, f"gc-{day}"), _stroke(scene, f"gld-{day}")
            assert gc.x == pytest.approx(np.full(gc.points, day_x(day, GC_AT)))
            assert gld.x == pytest.approx(np.full(gld.points, day_x(day, GLD_AT)))
            assert gc.x[0] < gld.x[0]
        x, y = price()
        for gid in ("gc-0", "gld-0", "gc-1", "gld-1"):
            tick = _stroke(scene, gid)
            at = float(np.interp(tick.x[0], x, y))
            assert tick.y.min() < at < tick.y.max(), gid

    def test_the_tick_labels_sit_over_their_ticks(self, every) -> None:
        scene = every[1]
        gc, gld = _label(scene, MOVES_LABELS[0]), _label(scene, MOVES_LABELS[1])
        assert gc.ha == "right" and gc.x > _stroke(scene, "gc-0").x[0] - 0.3
        assert gld.ha == "left" and gld.x < _stroke(scene, "gld-0").x[0] + 0.3
        assert gc.y > _stroke(scene, "gc-0").y.max()
        assert gld.y > _stroke(scene, "gld-0").y.max()

    def test_each_brace_spans_its_days_gap_where_gold_rises(self, every) -> None:
        """The brace runs from the 1:30 tick to the 4 p.m. tick on its day,
        under both, and the price moves up over that gap on each day."""
        scene = every[1]
        x, y = price()
        for day in (0, 1):
            brace = _stroke(scene, f"move-{day}")
            start, end = day_x(day, GC_AT), day_x(day, GLD_AT)
            assert (brace.x.min(), brace.x.max()) == pytest.approx((start, end))
            assert brace.y.max() <= _stroke(scene, f"gc-{day}").y.min()
            assert np.interp(end, x, y) > np.interp(start, x, y) + 0.2, day

    def test_the_gap_is_drawn_about_twice_its_share_of_a_day(self, bound) -> None:
        """A day runs from one day's tick to the same tick the next, so the
        drawn gap's share of it against 150 minutes' share of 24 hours is the
        "about twice" the alt text and the module docstring say."""
        drawn = (GLD_AT - GC_AT) / (sketches.DAY_X0[1] - sketches.DAY_X0[0])
        assert round(drawn / (bound.caveat_minutes / 1440)) == 2

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[1])
        for phrase in (
            "A wiggly brown line, gold’s price, runs across two days",
            "a dashed grey tick stands where GC would be recorded",
            "a solid black tick a little later stands where GLD is recorded",
            "drawn about twice as wide as two and a half hours of a day would be",
            "A brown brace under each day spans the gap between its two ticks, "
            "where the price rises",
            "a green check mark",
        ):
            assert phrase in alt, phrase

    def test_the_day_names_sit_in_their_days(self, every) -> None:
        scene = every[1]
        yesterday, today = _label(scene, "yesterday"), _label(scene, "today")
        assert yesterday.x < day_x(0, GC_AT) < today.x < day_x(1, GC_AT)
        assert today.x >= sketches.DAY_X0[1]

    def test_the_price_wanders_without_a_jump(self) -> None:
        """No step that comes back the next day. The steepest the price climbs
        or falls is 2 board units up for 1 across, where a jump would stand
        upright."""
        x, y = price()
        assert np.abs(np.diff(y) / np.diff(x)).max() < 2
        assert (x[0], x[-1]) == (sketches.PRICE_KNOTS[0][0], sketches.PRICE_KNOTS[-1][0])

    def test_the_lines_of_words_run_down_the_board(self, every) -> None:
        scene = every[1]
        heights = [_label(scene, text).y for text in MOVES_LABELS[4:]]
        assert heights == sorted(heights, reverse=True)
        assert max(heights) < min(s.y.min() for s in scene.strokes if s.gid.startswith("move"))
