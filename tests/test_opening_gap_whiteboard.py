"""The pins for the two whiteboard GIFs in the opening gap post, both in Lesson 1.

One sketches the worked day's point that line 23's sign pays a long when the
price falls from the open, and one the point that Chan's Python port, which
takes the text's sign, never holds a long.

1. The worked day sketch is schematic. What is pinned is that its returns are
   :func:`chan.opening_gap.daily_returns` on the post's worked day, that the
   open and both closes sit on one price scale, so the rise to 120 is twice
   the fall to 90, that the previous high sits below the open and the
   previous low above it, and that each reading's row is in the colour its
   sign calls for.
2. The port sketch's geometry is schematic, and its counts come from the run.
   What is pinned is that both columns share the two levels, that the
   script's zones sit where its tests put them, that the port's short zone
   runs from the lower level past the top of its long zone, that the long
   zone is redrawn red after the short is set, and that the port's short test
   passes every open its long test passes. The counts it prints are derived
   here from :func:`chan.opening_gap.python_port` on the committed file
   rather than restated, since ``tests/test_opening_gap.py`` already pins
   them, and a made-up set of counts checks that the words follow the data.

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

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import opening_gap as og
from chan import opening_gap_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.opening_gap_whiteboard import (
    FOOT_Y,
    LOWER_Y,
    PORT_X,
    SCRIPT_X,
    TIP_Y,
    TOP_Y,
    UPPER_Y,
    PortCounts,
    gif_name,
    main,
    make_opening_gap_whiteboards,
    price_y,
    scenes,
    sketch_timeline,
    worked_days,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import GOOD, INK, LOST, MUTED
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

POST = REPO_ROOT / "blog" / "opening-gap-lessons.md"

#: Every GIF in the order :func:`make_opening_gap_whiteboards` writes them.
GIFS = ["opening_gap_sketch_two_signs.gif", "opening_gap_sketch_port_never_long.gif"]

#: The paragraph each GIF follows, by its opening words.
WORKED_DAY_PARAGRAPH = "Take a long day. The open jumped above the previous high"
PORT_PARAGRAPH = "Chan’s later Python port of the script, `gapFutures_FSTX.py`"

TWO_SIGNS_LABELS = [
    "a long day",
    "yesterday’s high",
    "open 100",
    "close 90",
    "literal: long earns +10%",
    "momentum: long earns −10%",
    "a short day",
    "yesterday’s low",
    "open 100",
    "close 120",
    "literal: short earns +20%",
    "momentum: short earns −20%",
    "line 23 pays when the jump reverses",
]


def port_labels(counts: PortCounts) -> list[str]:
    """The port sketch's words, its two counts written from ``counts``."""
    return [
        "the script",
        "the port",
        "open price",
        "high × (1 + 0.1σ)",
        "low × (1 − 0.1σ)",
        "high, low: the previous day’s",
        "σ: the 90-day standard deviation",
        "long",
        "flat",
        "short",
        "long",
        "short: open ≥ low × (1 − 0.1σ)",
        "short set last, so it wins",
        "→ short",
        "flat",
        f"long on {counts.long:,} days, short on {counts.short:,}",
        f"all {counts.upward:,} upward jumps sold",
    ]


#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def port():
    """Chan's Python port on the committed file, read through the replication's own reader."""
    _, prices = og.read_sources()
    return og.python_port(prices)


@pytest.fixture(scope="module")
def counts():
    return PortCounts.from_run()


@pytest.fixture(scope="module")
def every(counts):
    return scenes(counts)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_opening_gap_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels_named(scene, text):
    return [s for s in scene.steps if isinstance(s, Label) and s.text == text]


def _index(scene, gid):
    return next(k for k, s in enumerate(scene.steps) if getattr(s, "gid", None) == gid)


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


def _span(stroke) -> tuple[float, float]:
    """The lowest and highest point of an upright stroke."""
    return float(stroke.y.min()), float(stroke.y.max())


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
        assert [fill for scene in every for fill in scene.fills] == []

    def test_every_colour_is_a_shared_ink(self, every) -> None:
        """The post's chart draws in the shared inks, so its sketches do too
        until the post moves to :mod:`chan.palette`."""
        shared = {INK, MUTED, GOOD, LOST}
        for scene in every:
            for step in scene.steps:
                assert step.color in shared, (scene.slug, step)


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
        assert sketches.PACED == ("two_signs", "port_never_long")
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
        again = make_opening_gap_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_chart(self) -> None:
        """No chart or sibling GIF starts like these, so the prefix check above
        reads only this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert not "opening_gap.png".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.opening_gap_whiteboard"


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
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (worked,) = [k for k, p in enumerate(paragraphs) if p.startswith(WORKED_DAY_PARAGRAPH)]
        (port,) = [k for k, p in enumerate(paragraphs) if p.startswith(PORT_PARAGRAPH)]
        for index, name in zip((worked, port), GIFS, strict=True):
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_both_sit_in_lesson_1(self) -> None:
        text = POST.read_text(encoding="utf-8")
        worked, port = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        assert text.index("## Lesson 1:") < worked < port < text.index("## Lesson 2:")

    def test_each_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count("(../docs/figures/opening_gap.png)") == 1

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_it_is_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_each_alt_text_says_what_is_schematic(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        assert "It is schematic, drawn from the worked day above" in _alt(text, every[0])
        assert (
            "Its levels and zones are schematic, and only its two closing counts come from the run"
            in _alt(text, every[1])
        )

    def test_the_module_says_which_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "The first sketch is schematic and carries no figure from the data." in doc
        assert "The second sketch's geometry is schematic too" in doc
        assert "Its counts come from the run" in doc


# --- Lesson 1: one day, two signs ---------------------------------------------


class TestTheWorkedDaySketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "One day, two signs"
        assert every[0].labels == TWO_SIGNS_LABELS

    def test_the_worked_day_is_the_posts(self) -> None:
        """An open of 100, falling to 90 on the long day and rising to 120 on
        the short, as the paragraph the sketch follows says."""
        long_day, short_day = worked_days()
        assert (long_day.side, long_day.open, long_day.close) == ("long", 100.0, 90.0)
        assert (short_day.side, short_day.open, short_day.close) == ("short", 100.0, 120.0)
        paragraph = next(
            p
            for p in POST.read_text(encoding="utf-8").split("\n\n")
            if p.startswith(WORKED_DAY_PARAGRAPH)
        )
        assert "falls from 100 at the open to 90 at the close, the long earns 10 percent" in (
            paragraph
        )
        assert "a rise from 100 to 120 earns the short 20 percent" in paragraph

    def test_its_returns_are_line_23s_both_ways(self) -> None:
        """Each row prints :func:`chan.opening_gap.daily_returns` on the day,
        and the two readings differ only in sign."""
        for day in worked_days():
            for reading in og.READINGS:
                expected = og.daily_returns(
                    np.array([og.SIDES[day.side]]),
                    np.array([day.open]),
                    np.array([day.close]),
                    reading=reading,
                )[0]
                assert day.earns(reading) == expected
            assert day.earns("literal") == -day.earns("momentum") > 0

    def test_a_made_up_day_moves_the_words(self) -> None:
        made_up = worked_days(open_=50.0, long_close=40.0, short_close=65.0)
        labels = sketches._two_signs(made_up).labels
        for text in (
            "open 50",
            "close 40",
            "close 65",
            "literal: long earns +20%",
            "momentum: long earns −20%",
            "literal: short earns +30%",
            "momentum: short earns −30%",
        ):
            assert text in labels, text

    def test_its_colours(self, every) -> None:
        scene = every[0]
        for side in ("long", "short"):
            level = _stroke(scene, f"{side}-level")
            assert (level.color, level.dashed) == (MUTED, True)
            assert _stroke(scene, f"{side}-open").color == INK
            assert _stroke(scene, f"{side}-move").color == INK
        for text in ("yesterday’s high", "yesterday’s low"):
            assert _label(scene, text).color == MUTED
        for text in TWO_SIGNS_LABELS:
            if text.startswith("literal"):
                assert _label(scene, text).color == GOOD, text
            elif text.startswith("momentum"):
                assert _label(scene, text).color == LOST, text
            elif not text.startswith("yesterday"):
                assert _label(scene, text).color == INK, text

    def test_open_and_close_sit_on_one_price_scale(self, every) -> None:
        """Each arrow runs from its open to its close at one height per point
        of price, so the short day's rise of 20 is twice the long day's fall
        of 10, and each open and close label sits level with its end."""
        scene = every[0]
        lengths = {}
        for day in worked_days():
            move = _stroke(scene, f"{day.side}-move")
            open_y, close_y = price_y(day.open, day.open), price_y(day.close, day.open)
            assert (move.y[0], move.y[-1]) == pytest.approx((open_y, close_y))
            assert set(np.round(_stroke(scene, f"{day.side}-open").y, 12)) == {round(open_y, 12)}
            lengths[day.side] = abs(close_y - open_y)
            assert (close_y - open_y) / (day.close - day.open) == pytest.approx(sketches.PER_POINT)
            open_words = [s for s in _labels_named(scene, f"open {day.open:g}")]
            assert open_y in {s.y for s in open_words}
            assert _label(scene, f"close {day.close:g}").y == pytest.approx(close_y)
        assert lengths["short"] == pytest.approx(2 * lengths["long"])

    def test_the_high_sits_below_the_open_and_the_low_above(self, every) -> None:
        """So each open has jumped past the previous day's range, and each
        arrow crosses back through it."""
        scene = every[0]
        long_day, short_day = worked_days()
        high = _stroke(scene, "long-level")
        low = _stroke(scene, "short-level")
        assert set(np.round(high.y, 12)) == {round(sketches.OPEN_Y - sketches.LEVEL_GAP, 12)}
        assert set(np.round(low.y, 12)) == {round(sketches.OPEN_Y + sketches.LEVEL_GAP, 12)}
        assert price_y(long_day.close, long_day.open) < high.y[0] < sketches.OPEN_Y
        assert sketches.OPEN_Y < low.y[0] < price_y(short_day.close, short_day.open)
        for level, side in ((high, "long"), (low, "short")):
            arrow_x = _stroke(scene, f"{side}-move").x[0]
            assert level.x.min() < arrow_x < level.x.max()

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "a dashed grey line marked “yesterday’s high” sits just below a black tick" in alt
        assert "a black arrow runs down from the tick, through that line, to “close 90”" in alt
        assert "a dashed grey line marked “yesterday’s low” sits just above a black tick" in alt
        assert "twice as far as the left arrow falls" in alt
        assert "in green, “literal: long earns +10%”, and in red, “momentum" in alt
        assert "in green, “literal: short earns +20%”, and in red, “momentum" in alt
        assert worked_days()[0].side == "long" and sketches.PANEL_XS[0] < sketches.PANEL_XS[1]


# --- Lesson 1: why the port never holds a long ---------------------------------


class TestThePortCounts:
    def test_they_are_the_ports_on_the_committed_file(self, counts, port) -> None:
        """Derived here from the port's own positions and tests rather than
        restated, since ``TestChansPythonPort`` pins the numbers."""
        held = port.positions
        assert counts == PortCounts(
            long=int((held == 1).sum()),
            short=int((held == -1).sum()),
            upward=int(port.longs.sum()),
            sold=int((port.longs & (held == -1)).sum()),
        )

    def test_the_port_is_never_long_and_sells_every_upward_jump(self, counts, port) -> None:
        assert counts.long == 0
        assert counts.sold == counts.upward == int(port.longs.sum()) > 0
        assert counts.short == int((port.shorts).sum())

    def test_the_upward_jumps_are_the_scripts_long_days(self, counts) -> None:
        """The port's long test is the script's, so its upward jumps are the
        days the script is long."""
        _, prices = og.read_sources()
        assert counts.upward == int((og.opening_gap(prices).positions == 1).sum())


class TestThePortSketch:
    def test_its_words(self, every, counts) -> None:
        assert every[1].title == "Why Chan’s Python port never holds a long"
        assert every[1].labels == port_labels(counts)

    def test_made_up_counts_move_the_words(self) -> None:
        made_up = PortCounts(long=0, short=2345, upward=301, sold=299)
        labels = scenes(made_up)[1].labels
        assert "long on 0 days, short on 2,345" in labels
        assert "299 of 301 upward jumps sold" in labels
        every_one = scenes(PortCounts(long=0, short=1200, upward=1100, sold=1100))[1].labels
        assert "all 1,100 upward jumps sold" in every_one

    def test_a_port_that_is_ever_long_is_refused(self) -> None:
        """The title would be false."""
        with pytest.raises(ValueError, match="never long"):
            scenes(PortCounts(long=1, short=1717, upward=278, sold=277))

    def test_its_colours(self, every) -> None:
        scene = every[1]
        for gid in ("script-axis", "port-axis", "upper-level", "lower-level"):
            assert _stroke(scene, gid).color == MUTED, gid
        for gid in ("upper-level", "lower-level"):
            assert _stroke(scene, gid).dashed, gid
        for gid in ("script-long", "port-long"):
            assert _stroke(scene, gid).color == GOOD, gid
        for gid in ("script-short", "port-short", "port-redrawn"):
            assert _stroke(scene, gid).color == LOST, gid
        for label in _labels_named(scene, "long"):
            assert label.color == GOOD
        for label in _labels_named(scene, "flat"):
            assert label.color == MUTED
        for text in ("short", "short: open ≥ low × (1 − 0.1σ)", "→ short"):
            assert _label(scene, text).color == LOST, text
        for text in (
            "open price",
            "high × (1 + 0.1σ)",
            "low × (1 − 0.1σ)",
            "high, low: the previous day’s",
            "σ: the 90-day standard deviation",
            "short set last, so it wins",
        ):
            assert _label(scene, text).color == MUTED, text
        for text in ("the script", "the port", *every[1].labels[-2:]):
            assert _label(scene, text).color == INK, text

    def test_both_columns_share_the_two_levels(self, every) -> None:
        scene = every[1]
        upper, lower = _stroke(scene, "upper-level"), _stroke(scene, "lower-level")
        assert set(np.round(upper.y, 12)) == {UPPER_Y} and set(np.round(lower.y, 12)) == {LOWER_Y}
        assert FOOT_Y < LOWER_Y < UPPER_Y < TOP_Y < TIP_Y
        for level in (upper, lower):
            assert level.x.min() < SCRIPT_X and level.x.max() > _stroke(scene, "port-short").x[0]
        assert _label(scene, "high × (1 + 0.1σ)").y == UPPER_Y
        assert _label(scene, "low × (1 − 0.1σ)").y == LOWER_Y

    def test_the_scripts_zones_sit_where_its_tests_put_them(self, every) -> None:
        """Long above the upper level, short below the lower, and only the
        grey axis between."""
        scene = every[1]
        assert _span(_stroke(scene, "script-long")) == pytest.approx((UPPER_Y, TOP_Y))
        assert _span(_stroke(scene, "script-short")) == pytest.approx((FOOT_Y, LOWER_Y))
        for gid in ("script-long", "script-short"):
            assert set(_stroke(scene, gid).x) == {SCRIPT_X}
        long_words, flat_words = _labels_named(scene, "long")[0], _labels_named(scene, "flat")[0]
        assert UPPER_Y < long_words.y < TOP_Y
        assert LOWER_Y < flat_words.y < UPPER_Y
        assert FOOT_Y < _label(scene, "short").y < LOWER_Y

    def test_the_ports_short_zone_covers_its_long_zone(self, every) -> None:
        """The short zone runs from the lower level past the top of the long
        zone, the long zone is redrawn red over the green after the short is
        set, and the port's flat words sit below the lower level."""
        scene = every[1]
        long_zone = _stroke(scene, "port-long")
        short_zone = _stroke(scene, "port-short")
        redrawn = _stroke(scene, "port-redrawn")
        assert _span(long_zone) == pytest.approx((UPPER_Y, TOP_Y))
        assert set(long_zone.x) == {PORT_X}
        assert short_zone.y[0] == pytest.approx(LOWER_Y)
        assert short_zone.y.max() == pytest.approx(TIP_Y) and TIP_Y > TOP_Y
        assert set(np.round(short_zone.x[: np.argmax(short_zone.y) + 1], 12)) == {
            round(PORT_X + sketches.SHORT_DX, 12)
        }
        assert np.array_equal(redrawn.x, long_zone.x) and np.array_equal(redrawn.y, long_zone.y)
        assert redrawn.width > long_zone.width
        order = [_index(scene, gid) for gid in ("port-long", "port-short", "port-redrawn")]
        assert order == sorted(order)
        note = scene.steps.index(_label(scene, "short set last, so it wins"))
        assert order[1] < note < order[2]
        assert _labels_named(scene, "flat")[1].y < LOWER_Y

    def test_the_ports_short_test_passes_every_open_its_long_test_passes(self) -> None:
        """What the drawing claims, on made-up days: any open at or above the
        upper level is also at or above the lower one, so the flipped short
        test passes it, and the short, set after the long, holds the day."""
        rng = np.random.default_rng(11)
        lows = 100 + rng.normal(0, 5, 400)
        highs = lows + rng.uniform(0, 4, 400)
        spread = np.abs(rng.normal(0.01, 0.005, 400))
        opens = np.r_[np.nan, highs[:-1]] * (1 + rng.uniform(-0.05, 0.05, 400))
        longs, shorts = og.python_port_qualifiers(opens, highs, lows, spread)
        assert longs.sum() > 0
        assert not (longs & ~shorts).any()
        assert not (og._held(longs, shorts) == 1).any()

    def test_its_alt_text_says_what_the_picture_shows(self, every, counts) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "Two grey upward arrows stand side by side" in alt
        assert "Two dashed grey lines cross both" in alt
        assert "a green bar above the upper line is marked “long”" in alt
        assert "a red bar below the lower line “short”" in alt
        assert "A red arrow then rises beside it from the lower line to past the top" in alt
        assert "The green bar is redrawn red" in alt
        assert "Below the lower line the port’s arrow is bare, marked “flat”" in alt
        assert f"“long on {counts.long:,} days, short on {counts.short:,}”" in alt
        assert SCRIPT_X < PORT_X
