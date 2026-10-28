"""The pins for the two whiteboard GIFs in the VX calendar spread post.

One sketches Lesson 2's claim that S holds one pair while its signal reads
the front pair, and one Lesson 4's claim that the shipped spacing of 12 months
leaves the near leg alone. What is pinned is what a reader takes from each.

1. The Lesson 2 sketch draws Chan's file. Every date, count and place it
   prints is read from :func:`chan.calendar_spread_reversion.calendar_schedule`
   with S's ``spread_month`` of 1 and from
   :func:`chan.vx_calendar_spread.near_leg_rank` on the committed VX strip,
   and the tests here derive each one again rather than trusting the sketch's
   own reading. Every mark sits on the axis at its own trading day, and a
   made-up hold shows the labels follow the run.
2. The Lesson 4 sketch draws one day of the shipped schedule, 2010-01-04.
   Which contracts are priced, which pair is held and the closing counts are
   derived here again from the same schedule, the way
   ``tests/test_vx_calendar_spread.py`` derives the counts.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, the green edge on the pale tint, each GIF's size,
frames, loop and timing, the first sketch's slower pace, that two draws give
the same bytes, and that each committed GIF is a fresh draw, a comparison that
runs only on macOS arm64 with Comic Sans MS, as
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

import matplotlib
import numpy as np
import pandas as pd
import pytest
from PIL import Image

from chan import usdcad_tests_whiteboard as whiteboard
from chan import vx_calendar_spread_whiteboard as sketches
from chan.calendar_spread_reversion import NUM_DAYS_END, calendar_schedule
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.roll_returns import load_strip
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
from chan.vx_calendar_spread import SPREAD_MONTH, START, near_leg_rank
from chan.vx_calendar_spread_whiteboard import (
    AXIS_X0,
    AXIS_X1,
    Hold,
    Shipped,
    Stretch,
    box_x,
    day_x,
    gif_name,
    main,
    make_vx_calendar_spread_whiteboards,
    scenes,
    sketch_timeline,
)

POST = REPO_ROOT / "blog" / "vx-calendar-spread-lessons.md"

#: Every GIF in the order :func:`make_vx_calendar_spread_whiteboards` writes them.
GIFS = [
    "vx_calendar_spread_sketch_one_hold.gif",
    "vx_calendar_spread_sketch_twelve_apart.gif",
]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "The script holds each pair for at least 63 days and lets it go 10 days before",
    "Run on VX with Chan’s setting, its schedule holds a pair on 1,284 days",
)

VINTAGE = (
    "data/inputdatadaily_vx_20120507/, vendor chan-mat, basis raw, saved 2012-05-08, "
    "72 contracts from VX-2007F to VX-2012Z"
)
HOLD_SPEC = f"{VINTAGE}; S's schedule, calendarSpdsMeanReversion.m with spreadMonth=1, holddays 63"
SHIPPED_SPEC = f"{VINTAGE}; the script as shipped, spreadMonth=12, holddays 63"

HOLD_LABELS = [
    "VX-2009G",
    "Feb, 02-18",
    "VX-2009H",
    "Mar, 03-18",
    "VX-2009J",
    "Apr, 04-15",
    "VX-2009K",
    "May, 05-20",
    "each tick: a contract’s last priced day, which the script takes as its expiry",
    "S holds",
    "near VX-2009K, far VX-2009M: 02-04 to 05-06, 64 days",
    "10 days to its",
    "last priced day",
    "4th",
    "near leg’s place",
    "10 days",
    "3rd",
    "20 days",
    "2nd",
    "19 days",
    "front",
    "same pair: 15 days",
    "G and H",
    "signal reads",
    "H and J",
    "J and K",
    "K and M",
]

TWELVE_LABELS = [
    *"FGHJKMNQUVXZFGHJ",
    "priced that day: 8 contracts",
    "near: VX-2010J",
    "+12 months",
    "far: VX-2011J, no price",
    "letters are months: F to Z run Jan to Dec 2010, then F to J run Jan to Apr 2011",
    "the script adds up the legs that have a price, so it holds VX-2010J alone",
    "near leg alone on 1,183 of 1,284 held days",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def contracts() -> pd.DataFrame:
    return load_strip("VX").contracts


@pytest.fixture(scope="module")
def hold(contracts) -> Hold:
    return Hold.from_contracts(contracts)


@pytest.fixture(scope="module")
def shipped(contracts) -> Shipped:
    return Shipped.from_contracts(contracts)


@pytest.fixture(scope="module")
def every(hold, shipped):
    return scenes(hold, shipped)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_vx_calendar_spread_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels_of(scene, gid):
    return [s.text for s in scene.steps if isinstance(s, Label) and s.names == gid]


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

    def test_every_pale_tint_has_a_green_edge(self, every) -> None:
        """The tint alone stands 1.29 to 1 against the white board, under WCAG
        2.1's 3 to 1 for a graphical object, so the one tint gets a green edge
        round all four sides."""
        assert sketches.TINT_EDGE >= 1.0
        tints = [fill for scene in every for fill in scene.fills if fill.color == whiteboard.TINT]
        assert [fill.gid for fill in tints] == ["same"]
        scene = every[0]
        for fill in tints:
            edges = [
                s
                for s in scene.strokes
                if s.color == GOOD
                and s.width == sketches.TINT_EDGE
                and s.x.min() == pytest.approx(fill.x0)
                and s.x.max() == pytest.approx(fill.x1)
                and s.y.min() == pytest.approx(fill.y0)
                and s.y.max() == pytest.approx(fill.y1)
            ]
            assert edges, fill.gid


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
        one_hold, twelve_apart = every
        for scene in every:
            assert (sketch_timeline(scene)[0].done, sketch_timeline(scene)[0].ms) == (0, TITLE_MS)
        assert sketch_timeline(one_hold)[-1].ms == sketches.PACED_HOLD_MS
        assert sketch_timeline(twelve_apart)[-1].ms == HOLD_MS

    def test_the_lesson_2_sketch_builds_slowly_and_holds_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace. The Lesson 4 sketch keeps the usual pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("one_hold",)
        scene = every[0]
        frames = sketch_timeline(scene)
        labels = [
            f
            for f in frames[:-1]
            if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
        ]
        assert labels
        assert {f.ms for f in labels} == {sketches.PACED_LABEL_MS}
        assert [(f.done, f.partial) for f in frames] == [
            (f.done, f.partial) for f in timeline(scene)
        ]
        assert sketch_timeline(every[1]) == timeline(every[1])

    def test_an_unpaced_scene_keeps_the_usual_pace(self, every, monkeypatch) -> None:
        monkeypatch.setattr(sketches, "PACED", ())
        for scene in every:
            assert sketch_timeline(scene) == timeline(scene)

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_vx_calendar_spread_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "vx_calendar_spread.png").exists()

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
            ), f"{path.name}: redraw with: uv run python -m chan.vx_calendar_spread_whiteboard"


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

    def test_each_sits_in_its_lesson(self) -> None:
        text = POST.read_text(encoding="utf-8")
        one_hold, twelve_apart = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lesson = [text.index(f"## Lesson {k}:") for k in (2, 3, 4)]
        assert lesson[0] < one_hold < lesson[1] < lesson[2] < twelve_apart
        assert twelve_apart < text.index("## What this replication cannot say")

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Every label but the Lesson 4 sketch's month letters, which its alt
        text names as a run, F to Z and F to J."""
        for scene in every:
            alt, at = _alt(scene), 0
            for label in scene.labels:
                if len(label) == 1:
                    continue
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_it_is_drawn_from_the_run_and_its_pace(self, every) -> None:
        one_hold, twelve_apart = (_alt(scene) for scene in every)
        for alt in (one_hold, twelve_apart):
            assert "schematic" not in alt
        assert "drawn slowly" in one_hold and "twelve seconds" in one_hold
        assert "drawn slowly" not in twelve_apart

    def test_the_module_says_neither_sketch_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "Neither sketch is schematic." in doc


# --- Lesson 2: one hold of S ---------------------------------------------------


class TestTheHoldFigures:
    def test_the_pair_and_its_days(self, hold) -> None:
        assert (hold.near, hold.far, hold.first, hold.last, hold.held) == (
            "VX-2009K",
            "VX-2009M",
            "2009-02-04",
            "2009-05-06",
            64,
        ), HOLD_SPEC
        assert hold.expiry == "2009-05-20", HOLD_SPEC

    def test_the_stretches_under_it(self, hold) -> None:
        assert hold.stretches == (
            Stretch("2009-02-04", "2009-02-18", 10, 4, "VX-2009G", "VX-2009H", "2009-02-18"),
            Stretch("2009-02-19", "2009-03-18", 20, 3, "VX-2009H", "VX-2009J", "2009-03-18"),
            Stretch("2009-03-19", "2009-04-15", 19, 2, "VX-2009J", "VX-2009K", "2009-04-15"),
            Stretch("2009-04-16", "2009-05-06", 15, 1, "VX-2009K", "VX-2009M", "2009-05-20"),
        ), HOLD_SPEC
        assert sum(s.days for s in hold.stretches) == hold.held

    def test_each_figure_is_the_runs(self, hold, contracts) -> None:
        """Read again from S's own schedule and near_leg_rank, and the two
        nearest priced contracts on each held day."""
        schedule = calendar_schedule(contracts, spread_month=SPREAD_MONTH)
        days = schedule.index[(schedule[hold.near] == -1).to_numpy()]
        assert (str(days[0].date()), str(days[-1].date()), len(days)) == (
            hold.first,
            hold.last,
            hold.held,
        )
        assert (schedule.loc[days, hold.far] == 1).all()
        rank = near_leg_rank(contracts, schedule).loc[days]
        for stretch in hold.stretches:
            span = rank.loc[stretch.first : stretch.last]
            assert len(span) == stretch.days and (span == stretch.place).all()
            for day in span.index:
                priced = contracts.columns[contracts.loc[day].notna().to_numpy()]
                assert tuple(priced[:2]) == (stretch.front, stretch.back), day
        priced = contracts.notna()
        for stretch in hold.stretches:
            last = priced.index[priced[stretch.front].to_numpy()][-1]
            assert str(last.date()) == stretch.front_ends

    def test_the_hold_ends_10_days_before_its_near_legs_last_priced_day(
        self, hold, contracts
    ) -> None:
        index = contracts.index
        gap = index.get_loc(pd.Timestamp(hold.expiry)) - index.get_loc(pd.Timestamp(hold.last))
        assert gap == NUM_DAYS_END == hold.days_to_expiry == 10

    def test_the_axis_runs_over_every_trading_day_from_february_to_may_2009(
        self, hold, contracts
    ) -> None:
        index = contracts.index
        expected = index[(index >= "2009-02-01") & (index <= "2009-05-31")]
        assert hold.days == tuple(str(d.date()) for d in expected)
        assert (hold.days[0], hold.days[-1]) == ("2009-02-02", "2009-05-29")

    def test_the_hold_lies_in_ss_window_of_held_days(self, hold) -> None:
        """The post counts S's held days from 2008-10-27, and this hold is one of them."""
        assert pd.Timestamp(hold.first) >= START

    def test_a_hold_that_does_not_end_10_days_early_is_refused(
        self, contracts, monkeypatch
    ) -> None:
        monkeypatch.setattr(sketches, "NUM_DAYS_END", 9)
        with pytest.raises(ValueError, match="does not end 9 days early"):
            Hold.from_contracts(contracts)

    def test_a_last_stretch_reading_another_pair_is_refused(self, contracts, monkeypatch) -> None:
        """Holding VX-2009K against VX-2009N, two months on, the last stretch
        still reads K and M, so the sketch has no "same pair" to tint."""
        monkeypatch.setattr(sketches, "SPREAD_MONTH", 2)
        with pytest.raises(ValueError, match="does not read the pair held"):
            Hold.from_contracts(contracts)


#: A made-up hold, so a word or a mark that should follow the run does.
OTHER = Hold(
    days=tuple(str(d.date()) for d in pd.bdate_range("2010-02-01", periods=60)),
    near="VX-2010J",
    far="VX-2010K",
    first="2010-02-03",
    last="2010-04-05",
    held=44,
    expiry="2010-04-19",
    stretches=(
        Stretch("2010-02-03", "2010-03-17", 31, 2, "VX-2010H", "VX-2010J", "2010-03-17"),
        Stretch("2010-03-18", "2010-04-05", 13, 1, "VX-2010J", "VX-2010K", "2010-04-19"),
    ),
    days_to_expiry=7,
)


class TestTheHoldSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "S holds one pair while its signal reads four"
        assert every[0].labels == HOLD_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        inks = {
            "axis": MUTED,
            "hold": INK,
            "days-to-expiry": MUTED,
            "same-edge": GOOD,
            **{f"expiry-{letter}": MUTED for letter in "GHJK"},
            **{f"place-{k}": INK for k in range(4)},
            **{f"front-{k}": ACCENT for k in range(4)},
        }
        assert {s.gid: s.color for s in scene.strokes} == inks
        colours = {text: _label(scene, text).color for text in HOLD_LABELS}
        assert {t for t, c in colours.items() if c == MUTED} == {
            *HOLD_LABELS[:9],
            "10 days to its",
            "last priced day",
        }
        assert {t for t, c in colours.items() if c == ACCENT} == {
            "G and H",
            "H and J",
            "J and K",
            "K and M",
            "signal reads",
        }
        assert [t for t, c in colours.items() if c == GOOD] == ["same pair: 15 days"]
        assert not [t for t, c in colours.items() if c == LOST]

    def test_the_bar_names_no_side(self, every) -> None:
        """The script reverses both legs whenever the z-score is above 0, so S
        is neither long nor short either leg throughout the hold."""
        words = " ".join(every[0].labels).lower()
        assert not [w for w in ("long", "short", "buy", "sell") if w in words]

    def test_each_label_names_the_stroke_it_sits_beside(self, every) -> None:
        scene = every[0]
        assert _labels_of(scene, "axis") == [HOLD_LABELS[8]]
        for k, letter in enumerate("GHJK"):
            assert _labels_of(scene, f"expiry-{letter}") == HOLD_LABELS[2 * k : 2 * k + 2]
        assert _labels_of(scene, "hold") == HOLD_LABELS[9:11]
        assert _labels_of(scene, "days-to-expiry") == HOLD_LABELS[11:13]
        assert _labels_of(scene, "place-0") == ["4th", "near leg’s place", "10 days"]
        assert _labels_of(scene, "place-3") == ["front"]
        assert _labels_of(scene, "same-edge") == ["same pair: 15 days"]
        assert _labels_of(scene, "front-0") == ["G and H", "signal reads"]
        assert _labels_of(scene, "front-3") == ["K and M"]

    def test_the_axis_places_each_day_at_an_affine_function_of_its_count(self, hold) -> None:
        step = (AXIS_X1 - AXIS_X0) / (len(hold.days) - 1)
        for k in (0, 1, 40, len(hold.days) - 1):
            assert day_x(hold, hold.days[k]) == pytest.approx(AXIS_X0 + k * step)

    def test_each_tick_sits_at_its_front_contracts_last_priced_day(self, every, hold) -> None:
        scene = every[0]
        axis_y = _stroke(scene, "axis").y[0]
        for stretch in hold.stretches:
            tick = _stroke(scene, f"expiry-{stretch.front[-1]}")
            x = day_x(hold, stretch.front_ends)
            assert tick.x == pytest.approx(np.full(tick.points, x))
            assert tick.y.max() == pytest.approx(axis_y) and tick.y.min() < axis_y
            assert _label(scene, stretch.front).x == pytest.approx(x)
            assert _label(scene, stretch.front).y < axis_y

    def test_the_bar_and_bracket_run_to_their_days(self, every, hold) -> None:
        scene = every[0]
        bar, bracket = _stroke(scene, "hold"), _stroke(scene, "days-to-expiry")
        assert (bar.x.min(), bar.x.max()) == pytest.approx(
            (day_x(hold, hold.first), day_x(hold, hold.last))
        )
        assert (bracket.x.min(), bracket.x.max()) == pytest.approx(
            (day_x(hold, hold.last), day_x(hold, hold.expiry))
        )
        assert bar.width > _stroke(scene, "place-0").width
        assert bar.width > bracket.width

    def test_each_stretch_and_front_pair_runs_to_its_days(self, every, hold) -> None:
        """The near leg's places tile the hold, and each front pair runs from
        its stretch's first day to its front contract's tick, so the last one
        runs past the hold to VX-2009K's tick."""
        scene = every[0]
        for k, stretch in enumerate(hold.stretches):
            place, front = _stroke(scene, f"place-{k}"), _stroke(scene, f"front-{k}")
            x0 = day_x(hold, stretch.first)
            assert (place.x.min(), place.x.max()) == pytest.approx((x0, day_x(hold, stretch.last)))
            assert (front.x.min(), front.x.max()) == pytest.approx(
                (x0, day_x(hold, stretch.front_ends))
            )
        assert _stroke(scene, "front-3").x.max() > _stroke(scene, "hold").x.max()

    def test_the_tint_covers_the_last_stretch_alone(self, every, hold) -> None:
        scene = every[0]
        (tint,) = scene.fills
        last = hold.stretches[-1]
        assert (tint.x0, tint.x1) == pytest.approx(
            (day_x(hold, last.first), day_x(hold, last.last))
        )
        place = float(np.median(_stroke(scene, "place-3").y))
        assert tint.y0 < place < tint.y1
        assert tint.x0 > _stroke(scene, "place-2").x.max()

    def test_the_rows_stack_from_the_bar_down_to_the_axis(self, every) -> None:
        scene = every[0]
        heights = [
            float(np.median(_stroke(scene, gid).y))
            for gid in ("hold", "place-0", "front-0", "axis")
        ]
        assert heights == sorted(heights, reverse=True)

    def test_a_made_up_hold_moves_the_words_and_the_marks(self) -> None:
        scene = scenes(OTHER, Shipped.from_run())[0]
        assert scene.title == "S holds one pair while its signal reads two"
        assert scene.labels[:4] == ["VX-2010H", "Mar, 03-17", "VX-2010J", "Apr, 04-19"]
        assert "near VX-2010J, far VX-2010K: 02-03 to 04-05, 44 days" in scene.labels
        assert "7 days to its" in scene.labels
        assert "2nd" in scene.labels and "31 days" in scene.labels
        assert "same pair: 13 days" in scene.labels
        assert ["H and J", "J and K"] == [t for t in scene.labels if " and " in t]
        assert _stroke(scene, "hold").x.max() == pytest.approx(day_x(OTHER, "2010-04-05"))


# --- Lesson 4: twelve months apart ----------------------------------------------


class TestTheShippedFigures:
    def test_the_day_it_draws(self, shipped) -> None:
        assert shipped.day == "2010-01-04"
        assert shipped.priced == tuple(f"VX-2010{m}" for m in "FGHJKMNQ"), SHIPPED_SPEC
        assert shipped.row == (
            *(f"VX-2010{m}" for m in "FGHJKMNQUVXZ"),
            *(f"VX-2011{m}" for m in "FGHJ"),
        ), SHIPPED_SPEC
        assert (shipped.near, shipped.far, shipped.spread_month) == (
            "VX-2010J",
            "VX-2011J",
            12,
        ), SHIPPED_SPEC

    def test_the_day_is_the_runs(self, shipped, contracts) -> None:
        """Read again from the shipped schedule: on 2010-01-04 it holds −1 on
        VX-2010J and +1 on VX-2011J, VX-2010J has a price and VX-2011J none,
        and VX-2010J is the 4th priced contract, not the front."""
        schedule = calendar_schedule(contracts)
        day = schedule.loc[shipped.day]
        assert day[day != 0].to_dict() == {shipped.near: -1.0, shipped.far: 1.0}
        prices = contracts.loc[shipped.day]
        assert tuple(prices.index[prices.notna()]) == shipped.priced
        assert np.isfinite(prices[shipped.near]) and np.isnan(prices[shipped.far])
        assert near_leg_rank(contracts, schedule).loc[shipped.day] == 4

    def test_the_counts_are_the_runs(self, shipped, contracts) -> None:
        assert (shipped.held, shipped.both, shipped.near_alone, shipped.neither) == (
            1284,
            84,
            1183,
            17,
        ), SHIPPED_SPEC
        schedule = calendar_schedule(contracts).to_numpy()
        priced = contracts.notna().to_numpy()
        held = (schedule != 0).any(axis=1)
        near = ((schedule == -1) & priced).any(axis=1)
        far = ((schedule == 1) & priced).any(axis=1)
        assert shipped.near_alone == int((held & near & ~far).sum())
        assert shipped.held == int(held.sum())

    def test_both_legs_are_priced_only_from_2006_12_29_to_2007_05_02(self, contracts) -> None:
        """Why the closing note counts the near leg alone rather than saying
        the far leg never has a price: both legs are priced on 84 days."""
        schedule = calendar_schedule(contracts).to_numpy()
        priced = contracts.notna().to_numpy()
        both = ((schedule == -1) & priced).any(axis=1) & ((schedule == 1) & priced).any(axis=1)
        days = contracts.index[both]
        assert (len(days), str(days[0].date()), str(days[-1].date())) == (
            84,
            "2006-12-29",
            "2007-05-02",
        ), SHIPPED_SPEC

    def test_a_day_with_the_far_leg_priced_is_refused(self, contracts, monkeypatch) -> None:
        """A schedule pairing VX-2010J with VX-2010K that day holds two priced
        legs, so there is no leg alone to draw."""
        moved = calendar_schedule(contracts).copy()
        day = pd.Timestamp(sketches.DAY)
        moved.loc[day, "VX-2011J"] = 0
        moved.loc[day, "VX-2010K"] = 1
        monkeypatch.setattr(sketches, "calendar_schedule", lambda frame: moved)
        with pytest.raises(ValueError, match="not priced alone"):
            Shipped.from_contracts(contracts)

    def test_a_day_whose_priced_contracts_skip_one_is_refused(self, contracts, monkeypatch) -> None:
        """The boxes draw the priced contracts as one unbroken run from the
        front. On 2007-01-03, one of the 84 days with both legs priced, the
        priced contracts skip one, so the reading refuses before it asks
        whether the near leg is alone."""
        monkeypatch.setattr(sketches, "DAY", "2007-01-03")
        with pytest.raises(ValueError, match="have a gap"):
            Shipped.from_contracts(contracts)


class TestTheTwelveApartSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "On 2010-01-04 the far leg has no price"
        assert every[1].labels == TWELVE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[1]
        inks = {
            **{f"box-{k}": INK for k in range(8)},
            **{f"box-{k}": MUTED for k in range(8, 16)},
            "priced": MUTED,
            "near": ACCENT,
            "later": ACCENT,
        }
        assert {s.gid: s.color for s in scene.strokes} == inks
        assert [s.gid for s in scene.strokes if s.dashed] == [f"box-{k}" for k in range(8, 16)]
        colours = [s.color for s in scene.steps if isinstance(s, Label)]
        assert colours == [INK] * 8 + [MUTED] * 8 + [
            MUTED,
            ACCENT,
            ACCENT,
            LOST,
            MUTED,
            MUTED,
            MUTED,
        ]

    def test_each_box_sits_at_an_affine_function_of_its_place(self, every) -> None:
        scene = every[1]
        for k in range(16):
            box = _stroke(scene, f"box-{k}")
            assert (box.x.min() + box.x.max()) / 2 == pytest.approx(box_x(k))
            assert box.x.max() - box.x.min() == pytest.approx(sketches.BOX_W)
        assert box_x(1) - box_x(0) == pytest.approx(sketches.BOX_PITCH)
        assert sketches.BOX_PITCH > sketches.BOX_W

    def test_the_ring_circles_the_near_leg_alone(self, every, shipped) -> None:
        scene = every[1]
        ring = _stroke(scene, "near")
        k = shipped.row.index(shipped.near)
        assert (ring.x.min() + ring.x.max()) / 2 == pytest.approx(box_x(k))
        box = _stroke(scene, f"box-{k}")
        cx, cy = box_x(k), float(np.mean([box.y.min(), box.y.max()]))
        # Every corner of the near leg's box lies inside the ring.
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            corner = (dx * sketches.BOX_W / 2 / sketches.RING_RX) ** 2 + (
                dy * (box.y.max() - box.y.min()) / 2 / sketches.RING_RY
            ) ** 2
            assert corner < 1
        assert ring.x.min() > box_x(k - 1) and ring.x.max() < box_x(k + 1)
        assert _label(scene, f"near: {shipped.near}").x == pytest.approx(cx)
        assert _label(scene, f"near: {shipped.near}").y < cy

    def test_the_arrow_runs_from_the_near_leg_to_the_far_one(self, every, shipped) -> None:
        scene = every[1]
        arrow = _stroke(scene, "later")
        near_x, far_x = (box_x(shipped.row.index(s)) for s in (shipped.near, shipped.far))
        assert arrow.x[0] == pytest.approx(near_x)
        assert arrow.x[39] == pytest.approx(far_x)
        assert arrow.y.max() > _stroke(scene, "near").y.max()
        assert shipped.row.index(shipped.far) - shipped.row.index(shipped.near) == 12

    def test_the_bracket_spans_the_priced_boxes(self, every, shipped) -> None:
        scene = every[1]
        bracket = _stroke(scene, "priced")
        n = len(shipped.priced)
        assert (bracket.x.min(), bracket.x.max()) == pytest.approx(
            (box_x(0) - sketches.BOX_W / 2, box_x(n - 1) + sketches.BOX_W / 2)
        )

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[1])
        for phrase in (
            "eight solid boxes",
            "eight dashed boxes",
            "F to Z",
            "F to J",
        ):
            assert phrase in alt, phrase


class TestTheHoldAltText:
    def test_it_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[0])
        for phrase in ("thick black bar", "grey bracket", "pale green box with a green edge"):
            assert phrase in alt, phrase
