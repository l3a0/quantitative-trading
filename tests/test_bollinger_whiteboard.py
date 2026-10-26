"""The pins for the two whiteboard GIFs in the post on Bollinger bands on GLD and USO.

The first sketches sixteen days on which a held long turns short on one close.
The second sketches eleven days on which dividing the moving deviation by n
rather than n − 1 opens a short that ``bollinger.m`` never opens.

The sketches are not schematic. Their figures come from
:class:`chan.bollinger_whiteboard.BandRun`, which reads
:func:`chan.bollinger.example_three_two` and
:func:`chan.bollinger_figures.zscore_divided_by_n` on the committed file, so the
tests read the run directly rather than a frozen copy of its figures. What is
pinned is each z-score and unit the sketches draw, that every dot sits at its
z-score on one affine scale, that each strip shows the units of the day above
it, the counts the labels print, that made-up figures move the words with them,
and that a run whose days would make the words false is refused.
``tests/test_bollinger.py`` holds the run's own counts, the 15 days the units
differ and the 76 and 77 exits, on its own derivation.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, the GIF's size, frames, loop and timing, that two
draws give the same bytes, and that the committed GIF is a fresh draw, a
comparison that runs only on macOS arm64 with Comic Sans MS, as
``tests/test_usdcad_tests_whiteboard.py`` explains. The check that
``docs/figures`` holds exactly the GIFs the modules draw lives in
``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS` from
here.
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

from chan import bollinger_whiteboard as sketches
from chan import price_spread
from chan import usdcad_tests_whiteboard as whiteboard
from chan.bollinger_whiteboard import (
    BESIDE,
    BandRun,
    divisor_x,
    divisor_y,
    exits,
    factor,
    gif_name,
    main,
    make_bollinger_whiteboards,
    runs,
    scenes,
    sketch_timeline,
    turn_x,
    turn_y,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.series import WindowCrossesScaleBreak
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
from chan.vintage import VintageUnavailable

POST = REPO_ROOT / "blog" / "bollinger-band-lessons.md"

#: Every GIF in the order :func:`make_bollinger_whiteboards` writes them.
GIFS = ["bollinger_sketch_one_close.gif", "bollinger_sketch_two_divisors.gif"]

#: What each GIF follows: the paragraph on the turn, in "The rule and the
#: file", and the last item of Lesson 3's list.
TURN_PARAGRAPH = "At these thresholds"
SHARPE_ITEM = "2. **The Sharpe ratio** becomes 0.984872"

ONE_CLOSE_LABELS = [
    "+1",
    "0",
    "−1",
    "2006-07-27 to 2006-08-17",
    "units held",
    "flat",
    "long",
    "enters below −1",
    "back inside the band, still long",
    "one close: exit at 0 and short above +1",
    "short",
    "flat",
    "long",
]
TWO_DIVISORS_LABELS = [
    "+1",
    "short above +1",
    "0",
    "left dots: divide by n − 1",
    "2007-05-24 to 2007-06-08",
    "right dots: divide by n",
    "0.9867 × 1.0260 = 1.0124",
    "n − 1 (bollinger.m)",
    "flat throughout",
    "n",
    "flat",
    "short",
    "flat",
    "a 77th exit, on 2007-06-07",
    "the units differ on 7 days here and 15 in all",
]

#: The z-scores and units each sketch draws, at the four decimals the post's
#: review read them at, on the vintage and specification of
#: ``tests/test_bollinger.py``.
TURN_ZSCORES = [
    -0.1236,
    -1.3093,
    -1.5118,
    -1.1334,
    -1.0805,
    -1.0197,
    -0.8435,
    -0.9234,
    -1.0568,
    -1.1949,
    -0.2699,
    1.3034,
    1.0361,
    0.3265,
    -0.6626,
    -1.9089,
]
TURN_UNITS = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, 0, 1]
DIVISOR_ZSCORES = [
    0.2889,
    0.8246,
    0.9867,
    0.8486,
    0.8912,
    0.9675,
    0.8078,
    0.4669,
    0.1545,
    -0.4483,
    -0.8599,
]
DIVISOR_ZSCORES_N = [
    0.2964,
    0.8461,
    1.0124,
    0.8706,
    0.9143,
    0.9927,
    0.8288,
    0.4791,
    0.1585,
    -0.4600,
    -0.8822,
]
DIVISOR_UNITS_N = [0, 0, -1, -1, -1, -1, -1, -1, -1, 0, 0]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def run() -> BandRun:
    return BandRun.from_run()


@pytest.fixture(scope="module")
def every(run):
    return scenes(run)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, run):
    return make_bollinger_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"), run=run)


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    (found,) = [s for s in scene.steps if isinstance(s, Label) and s.text == text]
    return found


def _labels_of(scene, gid):
    return [s for s in scene.steps if isinstance(s, Label) and s.names == gid]


def _bars(scene, prefix):
    return [s for s in scene.strokes if re.fullmatch(rf"{prefix}-\d+", s.gid)]


def _word(scene, bar) -> str:
    (word,) = [
        label.text for label in _labels_of(scene, bar.gid) if label.text in sketches.WORD.values()
    ]
    return word


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


def _held_word(scene, prefix: str, x: float) -> str:
    """The word of the bar in strip ``prefix`` that covers ``x``."""
    (bar,) = [b for b in _bars(scene, prefix) if b.x.min() < x < b.x.max()]
    return _word(scene, bar)


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
        """The sketches draw no tint today. One that did would need the green
        edge the equity seasonals module's ``_tinted`` draws, since the tint
        alone stands 1.29 to 1 against the board."""
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
        assert sketches.PACED == ("one_close", "two_divisors")
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

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, run) -> None:
        again = make_bollinger_whiteboards(out_dir=tmp_path, run=run)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        """No chart starts like these GIFs, so the prefix check above reads
        only this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert "bollinger_band.png" in names

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
            ), f"{path.name}: redraw with: uv run python -m chan.bollinger_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys, run
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(BandRun, "from_run", classmethod(lambda cls, closes=None: run))
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("the committed file's hash does not match its manifest"),
            WindowCrossesScaleBreak("USO changed scale on 2008-01-02"),
        ],
        ids=["vintage", "scale break"],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:

        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(sketches, "read_sources", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)


class TestThePost:
    def test_the_turn_sketch_follows_its_own_paragraph_with_a_caption(self) -> None:
        """The paragraph on the turn opens on its own, split from the one on
        strict comparisons, and the GIF and its caption follow it, before the
        subheading on the data."""
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(TURN_PARAGRAPH)]
        assert paragraphs[index - 1].startswith("Each comparison is strict")
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", paragraphs[index + 1]
        )
        caption = paragraphs[index + 2]
        assert caption.startswith("*Drawn to one scale from the run") and caption.endswith("*")
        assert paragraphs[index + 3] == "### The prices, the days traded and the script"

    def test_the_footer_links_the_sketch_code_and_its_tests(self) -> None:
        footer = _paragraphs()[-1]
        for path in ("src/chan/bollinger_whiteboard.py", "tests/test_bollinger_whiteboard.py"):
            assert f"/blob/main/{path})" in footer

    def test_the_divisor_sketch_follows_lesson_3s_list_with_a_caption(self) -> None:
        """After the list's last item, not after the paragraph above the list,
        which would cut the list from its paragraph."""
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if SHARPE_ITEM in p]
        items = paragraphs[index].splitlines()
        assert items[0].startswith("1. **The APR** becomes")
        assert items[-1].startswith(SHARPE_ITEM)
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[1])}\)", paragraphs[index + 1]
        )
        caption = paragraphs[index + 2]
        assert caption.startswith("*Drawn to one scale from the run") and caption.endswith("*")
        assert paragraphs[index + 3].startswith("Swapping the moving average")

    def test_each_sketch_sits_in_its_section(self) -> None:
        text = POST.read_text(encoding="utf-8")
        turn, divisors = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        assert text.index("## The rule and the file") < turn < text.index("## Lesson 1:")
        assert text.index("## Lesson 3:") < divisors < text.index("## Lesson 4:")

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Each label is quoted after the one drawn before it, and a label drawn
        more than once, such as "flat", is quoted each time."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                quoted = f"“{label}”"
                found = alt.find(quoted, at)
                assert found >= 0, (scene.slug, label)
                at = found + len(quoted)

    def test_each_alt_text_says_it_is_drawn_to_scale_and_slowly(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "drawn to one scale from the run" in alt, scene.slug
            assert "schematic" not in alt, scene.slug
            assert "drawn slowly" in alt and "twelve seconds" in alt, scene.slug

    def test_the_module_says_it_is_not_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "The sketches are not schematic." in doc


# --- Sixteen days of the band -------------------------------------------------


class TestTheTurnSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "Sixteen days of the band"
        assert every[0].labels == ONE_CLOSE_LABELS

    def test_the_run_gives_the_days_it_draws(self, run) -> None:
        turn = run.turn
        assert [str(d.date()) for d in (turn.days[0], turn.days[-1])] == [
            "2006-07-27",
            "2006-08-17",
        ]
        assert len(turn.days) == 16
        assert [round(float(z), 4) for z in turn.zscore] == TURN_ZSCORES
        assert turn.units.tolist() == TURN_UNITS
        assert str(turn.days[11].date()) == "2006-08-11"

    def test_its_colours(self, every) -> None:
        """Red dashed entry lines, a grey solid exit line, black dots, a brown
        ring, and each strip bar in the ink of its word."""
        scene = every[0]
        for gid, ink, dashed in (
            ("short-entry", LOST, True),
            ("exit", MUTED, False),
            ("long-entry", LOST, True),
        ):
            level = _stroke(scene, gid)
            assert (level.color, level.dashed) == (ink, dashed), gid
        assert _stroke(scene, "zscore").color == INK
        assert _stroke(scene, "zscore").dots > 0
        assert _stroke(scene, "turn").color == ACCENT
        for bar in _bars(scene, "units"):
            word = _word(scene, bar)
            assert bar.color == {"long": GOOD, "short": LOST, "flat": MUTED}[word], bar.gid
            assert (bar.width < 3) == (word == "flat"), bar.gid
        for text, ink in (
            ("+1", LOST),
            ("0", MUTED),
            ("−1", LOST),
            ("units held", INK),
            ("enters below −1", GOOD),
            ("back inside the band, still long", MUTED),
            ("one close: exit at 0 and short above +1", ACCENT),
        ):
            assert _label(scene, text).color == ink, text

    def test_every_dot_sits_at_its_z_score_on_one_scale(self, every, run) -> None:
        """Evenly spaced days across, and each height one affine function of
        the z-score, the same one the levels sit on."""
        scene = every[0]
        dots = _stroke(scene, "zscore")
        z = run.turn.zscore
        assert dots.x == pytest.approx(np.linspace(*sketches.TURN_X, 16))
        slope, intercept = np.polyfit(z, dots.y, 1)
        assert dots.y == pytest.approx(intercept + slope * z, abs=1e-12)
        assert (slope, intercept) == pytest.approx((sketches.TURN_PER_Z, sketches.TURN_ZERO))
        for gid, level in (("short-entry", 1), ("exit", 0), ("long-entry", -1)):
            line = _stroke(scene, gid)
            assert line.y == pytest.approx([float(turn_y(level))] * line.points), gid
            assert line.x.min() < dots.x.min() and line.x.max() > dots.x.max(), gid

    def test_the_strip_shows_each_days_units_under_its_dot(self, every, run) -> None:
        scene = every[0]
        words = [_held_word(scene, "units", x) for x in turn_x(run.turn)]
        assert words == [sketches.WORD[float(u)] for u in run.turn.units]
        assert words == ["flat"] + ["long"] * 10 + ["short"] * 3 + ["flat", "long"]

    def test_the_ring_circles_the_turn_and_its_note_sits_beside_it(self, every, run) -> None:
        """The day the long turns short, whose z-score is above 1 the day after
        one below 0."""
        scene = every[0]
        x, y = turn_x(run.turn), turn_y(run.turn.zscore)
        ring = _stroke(scene, "turn")
        (turned,) = [
            t for t in range(1, 16) if run.turn.units[t - 1] == 1 and run.turn.units[t] == -1
        ]
        assert str(run.turn.days[turned].date()) == "2006-08-11"
        assert run.turn.zscore[turned - 1] < 0 < 1 < run.turn.zscore[turned]
        assert ring.x.mean() == pytest.approx(x[turned], abs=0.02)
        assert (ring.y.max() + ring.y.min()) / 2 == pytest.approx(y[turned])
        note = _label(scene, "one close: exit at 0 and short above +1")
        assert note.ha == "right" and note.x < ring.x.min() and note.y > ring.y.max() - 0.2

    def test_the_notes_sit_under_the_days_they_name(self, every, run) -> None:
        """The entry's note ends just past the day the long enters, and the
        note on the band sits centred under the first days back inside it."""
        scene = every[0]
        x = turn_x(run.turn)
        z = run.turn.zscore
        entry = _label(scene, "enters below −1")
        assert entry.x == pytest.approx(x[1] + sketches.ENTRY_NOTE_PAST)
        assert z[1] < -1 < z[0]
        inside = _label(scene, "back inside the band, still long")
        assert inside.x == pytest.approx((x[6] + x[7]) / 2)
        assert [str(run.turn.days[t].date()) for t in (6, 7)] == ["2006-08-04", "2006-08-07"]
        assert all(-1 < z[t] < 0 and run.turn.units[t] == 1 for t in (6, 7))
        assert z[5] < -1 and z[8] < -1
        assert inside.names == "inside"
        bracket = _stroke(scene, "inside")
        assert bracket.color == MUTED
        assert x[5] < bracket.x.min() < x[6] and x[7] < bracket.x.max() < x[8]
        assert bracket.y.max() < float(turn_y(-1))

    def test_its_title_counts_the_days_it_draws(self, run) -> None:
        shorter = replace(
            run.turn,
            days=run.turn.days[:-1],
            zscore=run.turn.zscore[:-1],
            units=run.turn.units[:-1],
            zscore_n=run.turn.zscore_n[:-1],
            units_n=run.turn.units_n[:-1],
        )
        scene = scenes(replace(run, turn=shorter))[0]
        assert scene.title == "Fifteen days of the band"
        assert "2006-07-27 to 2006-08-16" in scene.labels
        assert _stroke(scene, "zscore").points == 15

    def test_it_refuses_a_count_its_title_cannot_spell(self, run) -> None:
        t = run.turn
        short = replace(
            t,
            days=t.days[:10],
            zscore=t.zscore[:10],
            units=t.units[:10],
            zscore_n=t.zscore_n[:10],
            units_n=t.units_n[:10],
        )
        with pytest.raises(ValueError, match="no word for 10"):
            scenes(replace(run, turn=short))

    def test_its_alt_text_says_what_the_picture_shows(self, run) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), scenes(run)[0])
        z, units = run.turn.zscore, run.turn.units
        assert "Sixteen black dots" in alt and len(z) == 16
        assert "The first dot sits just below 0." in alt and -0.5 < z[0] < 0
        assert "The next nine sit near −1, seven of them below it and two just above it" in alt
        assert np.count_nonzero(z[1:10] < -1) == 7
        assert np.count_nonzero((-1 < z[1:10]) & (z[1:10] < -0.8)) == 2
        assert "The eleventh rises to just below 0, and the twelfth jumps above +1" in alt
        assert -0.5 < z[10] < 0 < 1 < z[11]
        assert "The one after stays just above +1" in alt and 1 < z[12] < 1.1
        assert "turns into a thick green bar marked “long” at the second dot" in alt
        assert "A brown ring circles the twelfth dot, the first above +1" in alt
        assert "a thick red bar marked “short” runs for three days" in alt
        assert "“flat” for one day and a green bar marked “long” on the last day" in alt
        assert runs(units) == [
            (0, 0, 0.0),
            (1, 10, 1.0),
            (11, 13, -1.0),
            (14, 14, 0.0),
            (15, 15, 1.0),
        ]

    @pytest.mark.parametrize(
        ("edit", "words"),
        [
            (lambda u, z: (np.where(u == -1, 0.0, u), z), "one turn"),
            (lambda u, z: (u, np.where(np.arange(16) == 11, 0.9, z)), "exit at 0 and the entry"),
            (lambda u, z: (u, np.where(np.arange(16) == 1, -0.9, z)), "entered below −1"),
            (lambda u, z: (u, np.where((z > -1) & (z < 0) & (u == 1), -1.1, z)), "inside the band"),
            (lambda u, z: (u, np.where(np.arange(16) == 10, 0.1, z)), "exit at 0 and the entry"),
            (lambda u, z: (np.where(np.arange(16) < 11, 1.0, u), z), "entered below −1"),
        ],
        ids=[
            "no turn",
            "turn below 1",
            "entry inside",
            "never inside",
            "day before the turn above 0",
            "long held from the first day",
        ],
    )
    def test_it_refuses_days_that_would_make_its_words_false(self, run, edit, words) -> None:
        units, zscore = edit(run.turn.units.copy(), run.turn.zscore.copy())
        bad = replace(run, turn=replace(run.turn, units=units, zscore=zscore))
        with pytest.raises(ValueError, match=words):
            scenes(bad)


# --- One close, two divisors --------------------------------------------------


class TestTheDivisorSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "One close, two divisors"
        assert every[1].labels == TWO_DIVISORS_LABELS

    def test_the_run_gives_the_figures_it_draws(self, run) -> None:
        """Each day's z-score under both divisors, the units under each, and
        the counts over the whole run that ``tests/test_bollinger.py`` pins on
        its own derivation."""
        stretch = run.divisors
        assert [str(d.date()) for d in (stretch.days[0], stretch.days[-1])] == [
            "2007-05-24",
            "2007-06-08",
        ]
        assert [round(float(z), 4) for z in stretch.zscore] == DIVISOR_ZSCORES
        assert [round(float(z), 4) for z in stretch.zscore_n] == DIVISOR_ZSCORES_N
        assert stretch.units.tolist() == [0] * 11
        assert stretch.units_n.tolist() == DIVISOR_UNITS_N
        assert (run.differ, run.exits, run.exits_n) == (15, 76, 77)
        assert int(np.count_nonzero(stretch.units != stretch.units_n)) == 7

    def test_the_n_z_score_is_the_n_minus_1_one_times_root_20_over_19(self, run) -> None:
        stretch = run.divisors
        assert factor() == pytest.approx(math.sqrt(20 / 19))
        assert f"{factor():.4f}" == "1.0260"
        assert stretch.zscore_n == pytest.approx(stretch.zscore * factor(), rel=1e-12)

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert (_stroke(scene, "short-entry").color, _stroke(scene, "short-entry").dashed) == (
            LOST,
            True,
        )
        assert (_stroke(scene, "exit").color, _stroke(scene, "exit").dashed) == (MUTED, False)
        assert _stroke(scene, "zscore").color == INK
        assert _stroke(scene, "zscore-n").color == ACCENT
        assert _stroke(scene, "entry").color == ACCENT
        for prefix in ("n1", "n"):
            for bar in _bars(scene, prefix):
                word = "flat" if prefix == "n1" else _word(scene, bar)
                assert bar.color == {"short": LOST, "flat": MUTED}[word], bar.gid
                assert (bar.width < 3) == (word == "flat"), bar.gid
        for text, ink in (
            ("+1", LOST),
            ("short above +1", LOST),
            ("0", MUTED),
            ("left dots: divide by n − 1", INK),
            ("right dots: divide by n", ACCENT),
            ("0.9867 × 1.0260 = 1.0124", ACCENT),
            ("n − 1 (bollinger.m)", INK),
            ("flat throughout", MUTED),
            ("n", ACCENT),
            ("a 77th exit, on 2007-06-07", ACCENT),
            ("the units differ on 7 days here and 15 in all", MUTED),
        ):
            assert _label(scene, text).color == ink, text

    def test_each_days_two_dots_sit_side_by_side_at_their_z_scores(self, every, run) -> None:
        """The n − 1 dot a fixed step left of its day and the n dot the same
        step right, both on one affine scale, the one the levels sit on, since
        their heights differ by a pixel or two."""
        scene = every[1]
        x = divisor_x(run.divisors)
        black, brown = _stroke(scene, "zscore"), _stroke(scene, "zscore-n")
        assert black.x == pytest.approx(x - BESIDE)
        assert brown.x == pytest.approx(x + BESIDE)
        z = np.concatenate([run.divisors.zscore, run.divisors.zscore_n])
        heights = np.concatenate([black.y, brown.y])
        slope, intercept = np.polyfit(z, heights, 1)
        assert heights == pytest.approx(intercept + slope * z, abs=1e-12)
        assert (slope, intercept) == pytest.approx((sketches.DIVISOR_PER_Z, sketches.DIVISOR_ZERO))
        for gid, level in (("short-entry", 1), ("exit", 0)):
            line = _stroke(scene, gid)
            assert line.y == pytest.approx([float(divisor_y(level))] * line.points), gid
        pixels = (brown.y[2] - black.y[2]) * HEIGHT / whiteboard.YLIM[1]
        assert 0 < pixels < 2

    def test_the_legend_names_each_dot_by_its_side(self, every) -> None:
        """Colour is never the only cue, so the legend says left and right."""
        scene = every[1]
        left, right = (
            _label(scene, "left dots: divide by n − 1"),
            _label(scene, "right dots: divide by n"),
        )
        assert (left.names, right.names) == ("zscore", "zscore-n")
        assert left.y == right.y < float(divisor_y(0))

    def test_the_ring_circles_the_pair_that_straddles_plus_1(self, every, run) -> None:
        scene = every[1]
        stretch = run.divisors
        (entered,) = [t for t in range(11) if stretch.units_n[t] != stretch.units[t]][:1]
        assert str(stretch.days[entered].date()) == "2007-05-29"
        assert stretch.zscore[entered] < 1 < stretch.zscore_n[entered]
        ring = _stroke(scene, "entry")
        black, brown = _stroke(scene, "zscore"), _stroke(scene, "zscore-n")
        assert ring.x.min() < black.x[entered] < brown.x[entered] < ring.x.max()
        assert ring.y.min() < black.y[entered] < brown.y[entered] < ring.y.max()
        label = _label(scene, "0.9867 × 1.0260 = 1.0124")
        assert label.names == "entry" and label.x > ring.x.max()

    def test_each_strip_shows_each_days_units_under_its_dots(self, every, run) -> None:
        scene = every[1]
        x = divisor_x(run.divisors)
        (flat,) = _bars(scene, "n1")
        assert flat.x.min() < x.min() and x.max() < flat.x.max()
        assert _labels_of(scene, flat.gid)[-1].text == "flat throughout"
        assert [_held_word(scene, "n", v) for v in x] == [
            sketches.WORD[float(u)] for u in run.divisors.units_n
        ]

    def test_the_exit_label_sits_where_the_short_ends(self, every, run) -> None:
        scene = every[1]
        (short,) = [b for b in _bars(scene, "n") if _word(scene, b) == "short"]
        label = _label(scene, "a 77th exit, on 2007-06-07")
        assert label.x == pytest.approx(short.x.max())
        assert label.y < min(b.y.min() for b in _bars(scene, "n"))

    def test_its_alt_text_and_caption_say_what_the_picture_shows(self, run) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), scenes(run)[1])
        z, zn = run.divisors.zscore, run.divisors.zscore_n
        assert "two dots for each of 11 traded days" in alt and len(z) == 11
        assert "each level with its black neighbour to the eye" in alt
        assert np.all(np.abs(zn - z) * sketches.DIVISOR_PER_Z * HEIGHT / whiteboard.YLIM[1] < 2)
        assert "The dots start at about 0.3" in alt and round(float(z[0]), 1) == 0.3
        assert "between about 0.8 and +1 from the second day to the seventh" in alt
        assert np.all((0.8 < z[1:7]) & (z[1:7] < 1)) and z[7] < 0.8
        assert "the last two sit below 0" in alt
        assert np.all(z[-2:] < 0) and np.all(z[:-2] > 0)
        assert "the black dot sits just under +1 and the brown just over it" in alt
        assert "a thin grey line marked “flat” for two days" in alt
        assert "a thick red bar marked “short” from the ringed day for seven days" in alt
        assert "a thin grey line marked “flat” for the last two" in alt
        assert runs(run.divisors.units_n) == [(0, 1, 0.0), (2, 8, -1.0), (9, 10, 0.0)]
        paragraphs = _paragraphs()
        (index,) = [
            k
            for k, p in enumerate(paragraphs)
            if f"({GIFS[1]})" in p.replace("../docs/figures/", "")
        ]
        assert "differ by too little to see at this scale" in paragraphs[index + 1]

    def test_its_counts_follow_made_up_figures(self, run) -> None:
        """Another run's counts print their own words."""
        scene = scenes(replace(run, differ=20, exits=10, exits_n=11))[1]
        assert "an 11th exit, on 2007-06-07" in scene.labels
        assert "the units differ on 7 days here and 20 in all" in scene.labels
        scene = scenes(replace(run, exits=21, exits_n=22))[1]
        assert "a 22nd exit, on 2007-06-07" in scene.labels
        scene = scenes(replace(run, exits=22, exits_n=23))[1]
        assert "a 23rd exit, on 2007-06-07" in scene.labels
        scene = scenes(replace(run, exits=17, exits_n=18))[1]
        assert "an 18th exit, on 2007-06-07" in scene.labels
        scene = scenes(replace(run, exits=79, exits_n=80))[1]
        assert "an 80th exit, on 2007-06-07" in scene.labels

    @pytest.mark.parametrize(
        ("change", "words"),
        [
            (lambda r: replace(r, exits_n=r.exits), "one more exit"),
            (lambda r: replace(r, exits_n=r.exits + 2), "one more exit"),
            (
                lambda r: replace(
                    r,
                    divisors=replace(
                        r.divisors, units_n=np.array([0, 0, -1, 0, 1, -1, 0, 0, 0, 0, 0.0])
                    ),
                ),
                "one exit under n",
            ),
            (
                lambda r: replace(
                    r, divisors=replace(r.divisors, units=np.where(np.arange(11) == 4, -1.0, 0.0))
                ),
                "flat throughout",
            ),
            (
                lambda r: replace(r, divisors=replace(r.divisors, zscore_n=r.divisors.zscore)),
                "under 1 and the n z-score over it",
            ),
            (
                lambda r: replace(r, divisors=replace(r.divisors, units_n=np.zeros(11))),
                "one short entered under n",
            ),
            (
                lambda r: replace(
                    r,
                    divisors=replace(r.divisors, units_n=np.where(np.arange(11) >= 2, -1.0, 0.0)),
                ),
                "one exit under n",
            ),
            (
                lambda r: replace(
                    r, divisors=replace(r.divisors, zscore=r.divisors.zscore_n.copy())
                ),
                "under 1 and the n z-score over it",
            ),
        ],
        ids=[
            "exit count",
            "exit count high",
            "two exits",
            "n − 1 not flat",
            "no straddle",
            "no entry",
            "no exit",
            "both over 1",
        ],
    )
    def test_it_refuses_figures_that_would_make_its_words_false(self, run, change, words) -> None:
        with pytest.raises(ValueError, match=words):
            scenes(change(run))


class TestTheReadPath:
    def test_it_reads_the_file_through_the_runs_own_path(self, monkeypatch) -> None:
        """Through :func:`chan.price_spread.read_sources`, whose scale-break
        guard runs on both legs, rather than a second read path that skips it."""

        def refuse(*args, **kwargs):
            raise RuntimeError("read_sources ran")

        monkeypatch.setattr(sketches, "read_sources", refuse)
        with pytest.raises(RuntimeError, match="read_sources ran"):
            BandRun.from_run()

    def test_it_reads_the_closes_it_is_given(self, run) -> None:
        _, closes = price_spread.read_sources()
        again = BandRun.from_run(closes)
        assert again.turn.days == run.turn.days
        np.testing.assert_array_equal(again.divisors.zscore_n, run.divisors.zscore_n)

    def test_the_n_z_score_is_the_figures_dashed_lines(self, monkeypatch) -> None:
        """It comes from ``zscore_divided_by_n``, the helper the figure's
        ``divided_by_n`` trades on, not a second copy of the calculation."""
        monkeypatch.setattr(
            sketches, "zscore_divided_by_n", lambda signal: np.full(len(signal.value), 7.0)
        )
        assert set(BandRun.from_run().divisors.zscore_n.tolist()) == {7.0}

    def test_its_counts_follow_the_closes_it_is_given(self) -> None:
        """The labels' counts come from the run on the closes given, not from the
        committed file. On its first 250 rows both divisors exit equally often, so
        neither a count from the full file nor an ``exits_n`` built as one more than
        ``exits`` passes here."""
        _, closes = price_spread.read_sources()
        shorter = closes.iloc[:250]
        again = BandRun.from_run(shorter)
        band = sketches.example_three_two(shorter).bollinger
        units_n = sketches.divided_by_n(band.signal).units
        assert (again.differ, again.exits, again.exits_n) == (
            int(np.count_nonzero(band.units != units_n)),
            exits(band.units),
            exits(units_n),
        )
        assert again.exits_n == again.exits

    def test_exits_and_runs_count_what_they_say(self) -> None:
        units = np.array([0.0, 1, 1, 0, -1, 1, 0, 0])
        assert exits(units) == 2
        assert runs(units) == [
            (0, 0, 0.0),
            (1, 2, 1.0),
            (3, 3, 0.0),
            (4, 4, -1.0),
            (5, 5, 1.0),
            (6, 7, 0.0),
        ]
