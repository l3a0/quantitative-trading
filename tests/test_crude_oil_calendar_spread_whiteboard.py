"""The pins for the two whiteboard GIFs in the crude oil calendar spread post.

One sketches item 6 of "The spread, the signal and the file", the schedule,
and one Lesson 2's claim that the script sells the spread where the roll
return is high. What is pinned is what a reader takes from each.

1. The schedule sketch draws Chan's file. Every date and count it prints is
   read from :func:`chan.calendar_spread_reversion.calendar_schedule` on the
   committed CL strip, and the tests here derive each one again from that
   schedule rather than trusting the sketch's own reading. Every mark sits on
   the axis at its own trading day, and a made-up schedule shows the labels
   follow the run.
2. The Lesson 2 sketch is schematic apart from its closing note. Its curves are
   made up, so what is pinned is their shape: the roll return above its
   average and the spread below its own on every sample of the tint, a place
   before the tint where the two are not mirrored, and the spread still
   falling after the arrows. Its two counts are derived from the run here, the
   way ``tests/test_calendar_spread_reversion.py`` derives them.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, the green edge on the pale tint, each GIF's size,
frames, loop and timing, both sketches' slower pace, that two draws give the
same bytes, and that each committed GIF is a fresh draw, a comparison that
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

from chan import crude_oil_calendar_spread_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.calendar_spread_reversion import (
    HOLDDAYS,
    NUM_DAYS_END,
    START,
    calendar_schedule,
    held_log_spread,
    held_spread_zscore,
    run_spread,
)
from chan.crude_oil_calendar_spread_whiteboard import (
    AXIS_X0,
    AXIS_X1,
    Schedule,
    Signs,
    Window,
    board_curves,
    day_x,
    gif_name,
    main,
    make_crude_oil_calendar_spread_whiteboards,
    scenes,
    shapes,
    sketch_timeline,
    tint_start,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.price_spread import zscore
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.roll_returns import load_strip, roll_returns
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
from tests.test_calendar_spread_reversion import VINTAGE, _month

POST = REPO_ROOT / "blog" / "crude-oil-calendar-spread-lessons.md"

#: Every GIF in the order :func:`make_crude_oil_calendar_spread_whiteboards` writes them.
GIFS = ["crude_oil_calendar_spread_schedule.gif", "crude_oil_calendar_spread_script_sells.gif"]

#: The paragraph each GIF follows, by its opening words. The schedule sketch
#: follows a short lead-in, and the Lesson 2 sketch the paragraph on
#: what the script does.
FOLLOWS = (
    "On Chan’s file, item 6’s schedule",
    "The script does the opposite.",
)

SCHEDULE_SPEC = f"{VINTAGE}; calendarSpdsMeanReversion.m's schedule, c against c + 12, holddays 63"
SIGNS_SPEC = (
    f"{VINTAGE}; S's held rows from 2008-01-02, the roll return's z-score and the held "
    "pair's own, both over 36 rows"
)

SCHEDULE_LABELS = [
    "Dec 2007",
    "Nov 2008",
    "K",
    "04-22",
    "M",
    "05-20",
    "N",
    "06-20",
    "Q",
    "07-22",
    "U",
    "08-20",
    "short K2008, long K2009: 12-05 to 04-08, 85 days",
    "10 days to K2008’s last priced day",
    "M2008 to 05-06: 19 days apart",
    "N2008 to 06-06: 41 days apart",
    "Q2008 to 07-08: 62 days apart",
    "skipped, too short",
    "short U2008, long U2009",
    "04-09 to 08-06, 84 days",
    "a later pair is held only when its last day comes at least 63 trading days after its first",
]

SELLS_LABELS = [
    "trading days",
    "roll return",
    "held spread",
    "dashed: 36-day averages",
    "roll return’s z-score above 0",
    "script: sell the spread,",
    "short far and long near",
    "reversion would buy it here",
    "the script’s bet pays",
    "if the spread keeps falling",
    "the two z-scores have opposite signs on 841 of 1,097 held days from 2008-01-02",
    "short far on all 554 held days with the roll return’s z-score above 0",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def strip():
    return load_strip("CL")


@pytest.fixture(scope="module")
def schedule_run(strip) -> Schedule:
    return Schedule.from_contracts(strip.contracts)


@pytest.fixture(scope="module")
def signs() -> Signs:
    return Signs.from_run()


@pytest.fixture(scope="module")
def every(schedule_run, signs):
    return scenes(schedule_run, signs)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_crude_oil_calendar_spread_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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


def _alt(text: str, scene) -> str:
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
        2.1's 3 to 1 for a graphical object, so the Lesson 2 sketch's one tint
        gets a green edge that runs along its top and bottom and spans it."""
        assert sketches.TINT_EDGE >= 1.0
        tints = [fill for scene in every for fill in scene.fills if fill.color == whiteboard.TINT]
        assert [fill.gid for fill in tints] == ["high"]
        scene = every[1]
        for fill in tints:
            edges = [
                s
                for s in scene.strokes
                if s.color == GOOD
                and s.width == sketches.TINT_EDGE
                and s.x.min() <= fill.x0 + 1e-9
                and s.x.max() >= fill.x1 - 1e-9
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
        for scene in every:
            steps = sketch_timeline(scene)
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            assert steps[-1].ms == sketches.PACED_HOLD_MS, scene.slug

    def test_both_build_slowly_and_hold_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("schedule", "script_sells")
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

    def test_an_unpaced_scene_keeps_the_usual_pace(self, every, monkeypatch) -> None:
        monkeypatch.setattr(sketches, "PACED", ())
        for scene in every:
            assert sketch_timeline(scene) == timeline(scene)
            assert sketch_timeline(scene)[-1].ms == HOLD_MS

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_crude_oil_calendar_spread_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        """No chart or sibling GIF starts like these, so the prefix check above
        reads only this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "calendar_spread_reversion.png").exists()

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
            ), (
                f"{path.name}: redraw with: "
                "uv run python -m chan.crude_oil_calendar_spread_whiteboard"
            )


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

    def test_the_schedule_sketchs_lead_in_follows_the_second_equation(self) -> None:
        """A GIF straight after the list would come between the list and "The
        model writes a contract expiring at T as", which items 3 and 4 point to
        as the first equation below the list. So the lead-in sits after the
        paragraph that closes the second equation, and names item 6."""
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(FOLLOWS[0])]
        assert paragraphs[index - 1].endswith("When γ rises, the spread falls.")
        assert "item 6" in paragraphs[index]
        assert "\n6. **The schedule.**" in "\n" + "\n".join(paragraphs)

    def test_the_lead_in_counts_the_pairs_held_and_skipped(self, strip, schedule_run) -> None:
        """A pair is skipped only when its last day would come too soon after its
        first, so every near contract the schedule never holds short is one the
        lead-in calls skipped.
        Most are, across the file and in 2008, the year the sketch draws."""
        (lead_in,) = [p for p in _paragraphs() if p.startswith(FOLLOWS[0])]
        near = (calendar_schedule(strip.contracts) == -1).any().iloc[:-12]
        in_2008 = near[[name[3:7] == "2008" for name in near.index]]
        assert (len(in_2008), int(in_2008.sum())) == (12, 4), SCHEDULE_SPEC
        assert int((~near).sum()) > int(near.sum()), SCHEDULE_SPEC
        assert len(schedule_run.skipped) == 3, SCHEDULE_SPEC
        assert (schedule_run.before.near, schedule_run.after.near) == ("CL-2008K", "CL-2008U")
        for phrase in (
            "holds one pair at a time and skips every pair whose last day would come fewer than "
            "63 trading days after its first, which is most of them.",
            "Of the twelve pairs whose near contract delivers in 2008, "
            "it holds four and skips eight.",
            "holds the pair short K2008 and long K2009, skips the three pairs whose near "
            "contracts are M2008, N2008 and Q2008, and then holds the pair short U2008 and long "
            "U2009.",
            f"so K2008 delivers in {_month(schedule_run.before.near)} "
            f"and U2008 in {_month(schedule_run.after.near)}.",
        ):
            assert phrase in lead_in, phrase

    def test_the_schedule_sits_in_its_section_and_the_other_in_lesson_2(self) -> None:
        text = POST.read_text(encoding="utf-8")
        schedule_at, sells_at = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        section = text.index("## The spread, the signal and the file")
        lesson_1 = text.index("## Lesson 1:")
        lesson_2 = text.index("## Lesson 2:")
        lesson_3 = text.index("## Lesson 3:")
        assert section < schedule_at < lesson_1 < lesson_2 < sells_at < lesson_3

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_whether_it_is_schematic_and_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        schedule, sells = every
        assert "schematic" not in _alt(text, schedule)
        assert "It is schematic: its curves are made up" in _alt(text, sells)
        for scene in every:
            alt = _alt(text, scene)
            assert "drawn slowly" in alt, scene.slug
            assert "twelve seconds" in alt, scene.slug

    def test_the_module_says_which_sketch_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "The Lesson 2 sketch is schematic apart from its closing note." in doc
        assert "The sketch is not schematic." in doc


# --- The schedule: one pair at a time, a year apart ----------------------------


class TestTheScheduleFigures:
    def test_the_pairs_held_either_side_of_the_skipped_ones(self, schedule_run) -> None:
        assert schedule_run.before == Window(
            "CL-2008K", "CL-2009K", "2007-12-05", "2008-04-08", 84, held=True
        ), SCHEDULE_SPEC
        assert schedule_run.after == Window(
            "CL-2008U", "CL-2009U", "2008-04-09", "2008-08-06", 83, held=True
        ), SCHEDULE_SPEC
        assert (schedule_run.before.days, schedule_run.after.days) == (85, 84), SCHEDULE_SPEC

    def test_the_skipped_windows(self, schedule_run) -> None:
        assert [(w.near, w.far, w.first, w.last, w.apart) for w in schedule_run.skipped] == [
            ("CL-2008M", "CL-2009M", "2008-04-09", "2008-05-06", 19),
            ("CL-2008N", "CL-2009N", "2008-04-09", "2008-06-06", 41),
            ("CL-2008Q", "CL-2009Q", "2008-04-09", "2008-07-08", 62),
        ], SCHEDULE_SPEC
        assert not any(w.held for w in schedule_run.skipped)

    def test_q2008s_window_holds_63_days_and_is_still_skipped(self, schedule_run) -> None:
        """The rule counts how far the last day comes after the first, so a
        window of 63 days, both ends included, is 62 apart and falls short."""
        q = schedule_run.skipped[-1]
        assert (q.days, q.apart, HOLDDAYS) == (63, 62, 63), SCHEDULE_SPEC
        assert q.apart < schedule_run.holddays <= schedule_run.after.apart

    def test_each_near_contracts_last_priced_day(self, schedule_run) -> None:
        assert schedule_run.expiries == (
            ("K", "2008-04-22"),
            ("M", "2008-05-20"),
            ("N", "2008-06-20"),
            ("Q", "2008-07-22"),
            ("U", "2008-08-20"),
        ), SCHEDULE_SPEC

    def test_the_axis_runs_over_every_trading_day_from_december_2007_to_november_2008(
        self, schedule_run, strip
    ) -> None:
        index = strip.contracts.index
        expected = index[(index >= "2007-12-01") & (index <= "2008-11-30")]
        assert schedule_run.days == tuple(str(d.date()) for d in expected)
        assert (schedule_run.days[0], schedule_run.days[-1]) == ("2007-12-03", "2008-11-28")

    def test_the_held_windows_are_the_ones_the_script_holds(self, schedule_run, strip) -> None:
        """Read again from the script's own schedule: −1 on the near contract
        and +1 on the far one, on exactly the window's days."""
        held = calendar_schedule(strip.contracts)
        for window in (schedule_run.before, schedule_run.after):
            near = held[window.near]
            far = held[window.far]
            days = near.index[near.to_numpy() == -1]
            assert (str(days[0].date()), str(days[-1].date())) == (window.first, window.last)
            assert len(days) == window.days
            assert (far.loc[days] == 1).all()
            assert int(window.far[-5:-1]) == int(window.near[-5:-1]) + 1
            assert window.far[-1] == window.near[-1]

    def test_the_script_holds_nothing_on_a_skipped_near_contract(self, schedule_run, strip) -> None:
        held = calendar_schedule(strip.contracts)
        for window in schedule_run.skipped:
            assert (held[window.near] != -1).all(), window.near

    def test_each_skipped_window_ends_10_days_before_its_last_priced_day(
        self, schedule_run, strip
    ) -> None:
        index = strip.contracts.index
        expiry = dict(schedule_run.expiries)
        for window in (*schedule_run.skipped, schedule_run.before, schedule_run.after):
            last = index.get_loc(pd.Timestamp(window.last))
            assert index.get_loc(pd.Timestamp(expiry[window.near[-1]])) - last == NUM_DAYS_END
            assert index.get_loc(pd.Timestamp(window.first)) + window.apart == last

    def test_a_shorter_rule_would_have_held_q2008_and_is_refused(self, strip, monkeypatch) -> None:
        """The sketch's words say exactly the windows under the rule's length are
        skipped. Read against a rule of 62 days, Q2008's 62 would pass, so the
        reading refuses rather than draw a skip the rule does not make."""
        monkeypatch.setattr(sketches, "HOLDDAYS", 62)
        with pytest.raises(ValueError, match="under the rule's length"):
            Schedule.from_contracts(strip.contracts)


#: A made-up schedule, so a word or a mark that should follow the run does.
OTHER = Schedule(
    days=tuple(str(d.date()) for d in pd.bdate_range("2010-01-04", periods=200)),
    before=Window("CL-2010H", "CL-2011H", "2010-01-04", "2010-04-02", 64, held=True),
    skipped=(Window("CL-2010J", "CL-2011J", "2010-04-05", "2010-05-03", 20, held=False),),
    after=Window("CL-2010K", "CL-2011K", "2010-04-05", "2010-07-16", 74, held=True),
    expiries=(("H", "2010-04-16"), ("J", "2010-05-17"), ("K", "2010-07-30")),
    holddays=70,
    days_to_expiry=10,
)


class TestTheScheduleSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "One pair at a time, a year apart"
        assert every[0].labels == SCHEDULE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        inks = {
            "axis": MUTED,
            "before": INK,
            "days-to-expiry": MUTED,
            "after": INK,
            **{f"expiry-{letter}": MUTED for letter in "KMNQU"},
            **{f"skipped-{k}": LOST for k in range(3)},
            **{f"cross-{k}": LOST for k in range(3)},
        }
        assert {s.gid: s.color for s in scene.strokes} == inks
        colours = [_label(scene, text).color for text in SCHEDULE_LABELS]
        assert colours == [MUTED] * 12 + [INK, MUTED, LOST, LOST, LOST, LOST, INK, INK, MUTED]

    def test_each_label_names_the_stroke_it_sits_beside(self, every) -> None:
        scene = every[0]
        assert _labels_of(scene, "axis") == SCHEDULE_LABELS[:2]
        for k, letter in enumerate("KMNQU"):
            assert _labels_of(scene, f"expiry-{letter}") == SCHEDULE_LABELS[2 + 2 * k : 4 + 2 * k]
        assert _labels_of(scene, "before") == [SCHEDULE_LABELS[12]]
        assert _labels_of(scene, "days-to-expiry") == [SCHEDULE_LABELS[13]]
        for k in range(3):
            assert _labels_of(scene, f"cross-{k}") == [SCHEDULE_LABELS[14 + k]] + (
                ["skipped, too short"] if k == 2 else []
            )
        assert _labels_of(scene, "after") == SCHEDULE_LABELS[-3:]

    def test_the_axis_places_each_day_at_an_affine_function_of_its_count(
        self, schedule_run
    ) -> None:
        days = schedule_run.days
        step = (AXIS_X1 - AXIS_X0) / (len(days) - 1)
        for k in (0, 1, 50, len(days) - 1):
            assert day_x(schedule_run, days[k]) == pytest.approx(AXIS_X0 + k * step)

    def test_each_tick_sits_at_its_last_priced_day_with_its_letter_above_and_date_below(
        self, every, schedule_run
    ) -> None:
        scene = every[0]
        axis_y = _stroke(scene, "axis").y[0]
        for letter, date in schedule_run.expiries:
            tick = _stroke(scene, f"expiry-{letter}")
            x = day_x(schedule_run, date)
            assert tick.x == pytest.approx(np.full(tick.points, x))
            assert tick.y.max() == pytest.approx(axis_y) and tick.y.min() < axis_y
            above, below = _label(scene, letter), _label(scene, date[5:])
            assert (above.x, below.x) == (pytest.approx(x), pytest.approx(x))
            assert below.y < axis_y < above.y

    def test_each_bar_runs_from_its_first_day_to_its_last(self, every, schedule_run) -> None:
        scene = every[0]
        for gid, window in (("before", schedule_run.before), ("after", schedule_run.after)):
            bar = _stroke(scene, gid)
            assert (bar.x.min(), bar.x.max()) == pytest.approx(
                (day_x(schedule_run, window.first), day_x(schedule_run, window.last))
            ), gid
        for k, window in enumerate(schedule_run.skipped):
            span, cross = _stroke(scene, f"skipped-{k}"), _stroke(scene, f"cross-{k}")
            x0, x1 = day_x(schedule_run, window.first), day_x(schedule_run, window.last)
            assert (span.x.min(), span.x.max()) == pytest.approx((x0, x1)), k
            assert float(np.mean([cross.x.min(), cross.x.max()])) == pytest.approx((x0 + x1) / 2)
            assert float(np.mean([cross.y.min(), cross.y.max()])) == pytest.approx(
                float(np.median(span.y))
            )
            # An X reaches all four corners, so both its strokes are drawn.
            cx, cy = (x0 + x1) / 2, float(np.median(span.y))
            for dx, dy in ((-1, -1), (1, 1), (-1, 1), (1, -1)):
                reach = np.hypot(
                    cross.x - cx - dx * sketches.CROSS, cross.y - cy - dy * sketches.CROSS
                )
                assert reach.min() < 1e-6, (k, dx, dy)

    def test_the_skipped_windows_start_where_the_next_held_pair_does(
        self, every, schedule_run
    ) -> None:
        scene = every[0]
        start = _stroke(scene, "after").x.min()
        assert day_x(schedule_run, schedule_run.after.first) == pytest.approx(start)
        for k in range(3):
            assert _stroke(scene, f"skipped-{k}").x.min() == pytest.approx(start)
        assert start > _stroke(scene, "before").x.max()

    def test_the_bracket_runs_from_the_first_pairs_end_to_its_near_contracts_last_day(
        self, every, schedule_run
    ) -> None:
        scene = every[0]
        bracket = _stroke(scene, "days-to-expiry")
        assert (bracket.x.min(), bracket.x.max()) == pytest.approx(
            (
                day_x(schedule_run, schedule_run.before.last),
                day_x(schedule_run, dict(schedule_run.expiries)["K"]),
            )
        )

    def test_the_rows_stack_from_the_first_pair_down_to_the_axis(self, every) -> None:
        scene = every[0]
        heights = [
            float(np.median(_stroke(scene, gid).y))
            for gid in ("before", "skipped-0", "skipped-1", "skipped-2", "after", "axis")
        ]
        assert heights == sorted(heights, reverse=True)

    def test_a_made_up_schedule_moves_the_words_and_the_marks(self) -> None:
        scene = scenes(OTHER, Signs(10, 7, 4, 4))[0]
        assert scene.labels[:2] == ["Jan 2010", "Oct 2010"]
        assert scene.labels[2:8] == ["H", "04-16", "J", "05-17", "K", "07-30"]
        assert "short H2010, long H2011: 01-04 to 04-02, 65 days" in scene.labels
        assert "10 days to H2010’s last priced day" in scene.labels
        assert "J2010 to 05-03: 20 days apart" in scene.labels
        assert "short K2010, long K2011" in scene.labels
        assert "04-05 to 07-16, 75 days" in scene.labels
        assert scene.labels[-1].startswith(
            "a later pair is held only when its last day comes at least 70 "
        )
        assert _stroke(scene, "after").x.max() == pytest.approx(day_x(OTHER, "2010-07-16"))


# --- Lesson 2: high roll return, low spread, and the script sells ---------------


@pytest.fixture(scope="module")
def held_rows(strip):
    """S's held rows from 2008-01-02, with the roll return's z-score and the
    held pair's own, read the way ``tests/test_calendar_spread_reversion.py``
    reads them."""
    contracts = strip.contracts
    gamma = roll_returns(contracts)
    filled = gamma.ffill()
    schedule = calendar_schedule(contracts)
    run = run_spread(contracts, gamma, start=START)
    assert run.lookback == 36
    frame = pd.DataFrame(
        {
            "spread": held_log_spread(contracts, schedule),
            "gamma": filled,
            "z": zscore(filled.to_numpy(), 36),
            "own": held_spread_zscore(contracts, schedule, 36),
            "far": (run.positions.to_numpy() * (schedule.to_numpy() == 1)).sum(axis=1),
        }
    )
    held = frame["spread"].notna() & frame["gamma"].notna()
    return frame.loc[held.to_numpy() & (frame.index >= START)]


class TestTheSignsFigures:
    def test_the_counts_the_sketch_prints(self, signs) -> None:
        assert signs == Signs(held=1097, opposite=841, high=554, short_far=554), SIGNS_SPEC
        assert signs.start == "2008-01-02"
        assert signs.all_short

    def test_each_count_is_the_runs(self, signs, held_rows) -> None:
        z, own, far = held_rows["z"], held_rows["own"], held_rows["far"]
        assert signs.held == len(held_rows)
        assert signs.opposite == int((np.sign(z) != np.sign(own)).sum())
        assert signs.high == int((z > 0).sum())
        assert signs.short_far == int((far[z > 0] == -1).sum())

    def test_the_spread_sits_below_its_own_average_on_only_377_of_the_554(self, held_rows) -> None:
        """Why the curves are drawn as a rough inverse and not a mirror: on the
        days the roll return's z-score is above 0, the spread's own is below 0
        on only 377 of 554."""
        high = held_rows[held_rows["z"] > 0]
        assert (int((high["own"] < 0).sum()), len(high)) == (377, 554), SIGNS_SPEC

    def test_a_run_that_is_not_short_far_on_every_high_day_is_refused(self) -> None:
        """The closing note says "all", so a count that is not all has no words to print."""
        with pytest.raises(ValueError, match="553 of the 554"):
            scenes(OTHER, Signs(1097, 841, 554, 553))

    def test_made_up_counts_move_the_closing_note(self) -> None:
        scene = scenes(OTHER, Signs(2000, 1500, 1200, 1200))[1]
        assert scene.labels[-2:] == [
            "the two z-scores have opposite signs on 1,500 of 2,000 held days from 2008-01-02",
            "short far on all 1,200 held days with the roll return’s z-score above 0",
        ]


class TestTheScriptSellsSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "High roll return, low spread, and the script sells"
        assert every[1].labels == SELLS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert {s.gid: s.color for s in scene.strokes} == {
            "days": MUTED,
            "gamma": ACCENT,
            "gamma-average": ACCENT,
            "spread": INK,
            "spread-average": INK,
            "high-edge": GOOD,
            "sell": LOST,
            "buy": GOOD,
        }
        assert [s.gid for s in scene.strokes if s.dashed] == ["gamma-average", "spread-average"]
        colours = [_label(scene, text).color for text in SELLS_LABELS]
        assert colours == [
            MUTED,
            ACCENT,
            INK,
            MUTED,
            MUTED,
            LOST,
            LOST,
            GOOD,
            INK,
            INK,
            MUTED,
            MUTED,
        ]

    def test_each_label_names_the_stroke_it_sits_beside(self, every) -> None:
        scene = every[1]
        assert _labels_of(scene, "days") == [SELLS_LABELS[0], *SELLS_LABELS[-2:]]
        assert _labels_of(scene, "gamma") == ["roll return"]
        assert _labels_of(scene, "spread") == ["held spread", *SELLS_LABELS[8:10]]
        assert _labels_of(scene, "spread-average") == ["dashed: 36-day averages"]
        assert _labels_of(scene, "high-edge") == ["roll return’s z-score above 0"]
        assert _labels_of(scene, "sell") == SELLS_LABELS[5:7]
        assert _labels_of(scene, "buy") == ["reversion would buy it here"]

    def test_the_roll_return_runs_above_the_spread(self, every) -> None:
        scene = every[1]
        lowest_gamma = min(_stroke(scene, g).y.min() for g in ("gamma", "gamma-average"))
        highest_spread = max(_stroke(scene, g).y.max() for g in ("spread", "spread-average"))
        assert lowest_gamma > highest_spread > _stroke(scene, "days").y.max()

    def test_each_average_is_the_trailing_mean_of_its_curve(self) -> None:
        """Each dashed line is the mean of the last :data:`WINDOW` samples, on
        samples that run back before the first one drawn."""
        t, gamma, gamma_avg, spread, spread_avg = shapes()
        assert len(t) == sketches.SAMPLES and t[0] == 0 and t[-1] == pytest.approx(1)
        k = 40
        full = np.arange(-sketches.LEAD, sketches.SAMPLES) / (sketches.SAMPLES - 1)
        assert np.isclose(full[sketches.LEAD + k], t[k])
        assert gamma_avg[k] == pytest.approx(gamma[k - sketches.WINDOW + 1 : k + 1].mean())
        assert spread_avg[k] == pytest.approx(spread[k - sketches.WINDOW + 1 : k + 1].mean())

    def test_inside_the_tint_the_roll_return_is_high_and_the_spread_low(self, every) -> None:
        scene = every[1]
        x, gy, gay, sy, say = board_curves()
        tint = next(f for f in scene.fills if f.gid == "high")
        inside = x >= tint.x0
        assert tint.x0 == pytest.approx(x[tint_start()])
        assert tint.x1 == pytest.approx(x[-1])
        assert (gy[inside] > gay[inside]).all()
        assert (sy[inside] < say[inside]).all()
        assert tint.y0 < sy.min() and tint.y1 > gy.max()

    def test_outside_the_tint_the_two_are_not_mirrored_everywhere(self) -> None:
        """A rough inverse, not a mirror: somewhere before the tint the roll
        return and the spread sit on the same side of their averages."""
        _, gamma, gamma_avg, spread, spread_avg = shapes()
        before = slice(0, tint_start())
        same = (gamma[before] > gamma_avg[before]) == (spread[before] > spread_avg[before])
        assert same.any() and not same.all()

    @pytest.mark.parametrize("start", [0.2, 0.4], ids=["roll return low", "spread high"])
    def test_a_tint_that_covers_a_day_it_should_not_is_refused(self, monkeypatch, start) -> None:
        """From 0.2 the roll return still dips under its average. From 0.4 it
        stays above, and the spread is what still sits above its own."""
        _, gamma, gamma_avg, spread, spread_avg = shapes()
        t = shapes()[0]
        first = int(np.flatnonzero(t >= start)[0])
        gamma_high = bool((gamma > gamma_avg)[first:].all())
        assert gamma_high == (start == 0.4)
        assert not (spread < spread_avg)[first:].all()
        monkeypatch.setattr(sketches, "TINT_FROM", start)
        with pytest.raises(ValueError, match="every sample of the tint"):
            tint_start()

    def test_both_arrows_point_at_the_spread_inside_the_tint(self, every) -> None:
        """Each tip sits on the solid spread, not on its dashed average just above it.

        Inside the tint the two black lines run about 0.2 apart, so a tip
        placed by its distance from one spot can land on either. Each tip is
        held to the spread at its own x, and nearer it than the average.
        """
        scene = every[1]
        x, _, _, sy, say = board_curves()
        tint = next(f for f in scene.fills if f.gid == "high")
        tips = {}
        for gid in ("sell", "buy"):
            arrow = _stroke(scene, gid)
            tip = int(np.flatnonzero(np.isclose(arrow.x, arrow.x.min()))[0])
            tx, ty = float(arrow.x[tip]), float(arrow.y[tip])
            spread, average = float(np.interp(tx, x, sy)), float(np.interp(tx, x, say))
            assert tint.x0 < tx < tint.x1, gid
            assert abs(ty - spread) < 0.05, gid
            assert abs(ty - spread) < abs(ty - average), gid
            assert arrow.x[0] > tint.x1, gid
            tips[gid] = tx
        assert tips["sell"] < tips["buy"]
        assert _stroke(scene, "sell").y[0] > _stroke(scene, "buy").y[0]

    def test_the_spread_keeps_falling_after_the_arrows(self, every) -> None:
        x, _, _, sy, _ = board_curves()
        spot = int(
            np.argmin(
                np.abs(
                    x
                    - (sketches.CURVE_X0 + (sketches.CURVE_X1 - sketches.CURVE_X0) * sketches.SPOT)
                )
            )
        )
        assert sy[-1] == sy[spot:].min() < sy[spot] - 0.3

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "only the two counts in its closing note come from the run" in alt
        assert (
            "where the roll return sits above its dashed average and the spread below its own"
            in alt
        )
        assert "A red arrow points at the spread inside the box" in alt
        assert "a green arrow points at the spread just to the right of the red one" in alt


class TestTheScheduleAltText:
    def test_it_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "three red bars start the day after the black bar ends" in alt
        assert "each crossed with a red X" in alt
        assert "starts at the same place as the red bars" in alt


# --- Proposed by the round 1 completeness lens ----------------------------------

#: The word each alt text uses for each ink.
INK_WORDS = {INK: "black", MUTED: "grey", LOST: "red", GOOD: "green", ACCENT: "brown"}


class TestTheScheduleRefusals:
    """Each guard in :meth:`Schedule.from_contracts` and :func:`scenes` stands
    for a sentence on the sketch, so each is made to fire. The skipped windows'
    half of the length guard fires in ``TestTheScheduleFigures``."""

    def test_a_pair_that_does_not_end_10_days_early_is_refused(self, strip, monkeypatch) -> None:
        monkeypatch.setattr(sketches, "NUM_DAYS_END", 9)
        with pytest.raises(ValueError, match="does not end 9 days early"):
            Schedule.from_contracts(strip.contracts)

    def test_a_pair_that_does_not_start_the_day_after_the_last_ended_is_refused(
        self, strip, monkeypatch
    ) -> None:
        moved = calendar_schedule(strip.contracts).copy()
        first = moved.index[moved["CL-2008U"].to_numpy() == -1][0]
        moved.loc[first, ["CL-2008U", "CL-2009U"]] = 0
        monkeypatch.setattr(sketches, "calendar_schedule", lambda contracts: moved)
        with pytest.raises(ValueError, match="does not start the day after"):
            Schedule.from_contracts(strip.contracts)

    def test_a_longer_rule_that_would_skip_u2008_too_is_refused(self, strip, monkeypatch) -> None:
        """U2008's window is 83 days apart, so a rule of 84 would skip it as well."""
        monkeypatch.setattr(sketches, "HOLDDAYS", 84)
        with pytest.raises(ValueError, match="under the rule's length"):
            Schedule.from_contracts(strip.contracts)

    def test_a_rule_equal_to_u2008s_gap_still_holds_it(self, strip, monkeypatch) -> None:
        """The guard's other edge: a pair 83 days apart meets a rule of 83."""
        monkeypatch.setattr(sketches, "HOLDDAYS", 83)
        assert Schedule.from_contracts(strip.contracts).after.apart == 83

    def test_a_pair_that_ends_later_than_the_rule_is_refused(self, strip, monkeypatch) -> None:
        """Each pair ends 10 days early, a day later than a rule of 11 wants.

        A rule of 9 above is the other direction.
        """
        monkeypatch.setattr(sketches, "NUM_DAYS_END", 11)
        with pytest.raises(ValueError, match="does not end 11 days early"):
            Schedule.from_contracts(strip.contracts)

    @pytest.mark.parametrize("pair", ["CL-2008K", "CL-2008U"])
    def test_either_held_pair_ending_a_day_sooner_is_refused(
        self, strip, monkeypatch, pair
    ) -> None:
        """Each held pair's end is checked, so dropping either one's last day is refused."""
        moved = calendar_schedule(strip.contracts).copy()
        last = moved.index[moved[pair].to_numpy() == -1][-1]
        far = f"CL-{int(pair[3:7]) + 1}{pair[-1]}"
        moved.loc[last, [pair, far]] = 0
        monkeypatch.setattr(sketches, "calendar_schedule", lambda contracts: moved)
        with pytest.raises(ValueError, match="does not end 10 days early"):
            Schedule.from_contracts(strip.contracts)

    @pytest.mark.parametrize("count", [0, 4])
    def test_a_schedule_with_no_row_for_its_skips_is_refused(self, count) -> None:
        made_up = Schedule(**{**OTHER.__dict__, "skipped": (OTHER.skipped[0],) * count})
        with pytest.raises(ValueError, match="rows for 1 to 3 skipped windows"):
            scenes(made_up, Signs(10, 7, 4, 4))


class TestTheScheduleSketchFollowsTheRun:
    def test_the_bracket_label_reads_its_days_from_the_run(self) -> None:
        made_up = Schedule(**{**OTHER.__dict__, "days_to_expiry": 7})
        scene = scenes(made_up, Signs(10, 7, 4, 4))[0]
        assert "7 days to H2010’s last priced day" in scene.labels

    def test_the_skip_label_sits_left_of_the_red_bars_at_their_middle(self, every) -> None:
        scene = every[0]
        label = _label(scene, "skipped, too short")
        heights = [float(np.median(_stroke(scene, f"skipped-{k}").y)) for k in range(3)]
        assert label.ha == "right"
        assert label.x < min(_stroke(scene, f"skipped-{k}").x.min() for k in range(3))
        assert label.y == pytest.approx(heights[1])

    def test_the_held_bars_are_thicker_than_the_skipped_ones_and_the_bracket(self, every) -> None:
        """The alt text calls the held pairs thick bars and the bracket thin."""
        scene = every[0]
        held = {_stroke(scene, gid).width for gid in ("before", "after")}
        skipped = {_stroke(scene, f"skipped-{k}").width for k in range(3)}
        assert min(held) > max(skipped) > _stroke(scene, "days-to-expiry").width


class TestTheAltTextsSayWhatIsDrawn:
    def test_the_schedule_alt_text_names_each_ink_and_place(self, every, schedule_run) -> None:
        scene = every[0]
        alt = _alt(POST.read_text(encoding="utf-8"), scene)
        ink = {s.gid: INK_WORDS[s.color] for s in scene.strokes}
        for phrase in (
            f"A {ink['axis']} trading-day axis runs along the bottom",
            f"a {ink['expiry-K']} tick below it at each near contract’s last priced day",
            f"A thick {ink['before']} bar near the top",
            "ends just before the K tick",
            f"a thin {ink['days-to-expiry']} bracket runs from its end to the K tick",
            f"in {INK_WORDS[_label(scene, 'skipped, too short').color]} to their left",
            f"Under them a second thick {ink['after']} bar",
            "“short U2008, long U2009” on its left and “04-09 to 08-06, 84 days” on its right",
            f"A {INK_WORDS[_label(scene, SCHEDULE_LABELS[-1]).color]} note at the bottom",
        ):
            assert phrase in alt, phrase
        k_tick = day_x(schedule_run, dict(schedule_run.expiries)["K"])
        assert _stroke(scene, "before").x.max() < k_tick
        after = _stroke(scene, "after")
        left, right = (_label(scene, text) for text in SCHEDULE_LABELS[18:20])
        assert left.x <= after.x.min() and right.x >= after.x.max()

    def test_the_lesson_2_alt_text_names_each_ink_and_direction(self, every) -> None:
        scene = every[1]
        alt = _alt(POST.read_text(encoding="utf-8"), scene)
        ink = {s.gid: INK_WORDS[s.color] for s in scene.strokes}
        for phrase in (
            f"a {ink['gamma']} line labelled “roll return” wanders and then climbs",
            f"with a dashed {ink['gamma-average']} line, its average",
            f"a {ink['spread']} line labelled “held spread” moves roughly opposite",
            f"with a dashed {ink['spread-average']} line trailing behind it",
            f"A pale green box with a {ink['high-edge']} edge",
            f"The {ink['spread']} spread keeps falling to the box’s right edge",
            f"A {ink['days']} axis labelled “trading days”",
            f"a {INK_WORDS[_label(scene, 'dashed: 36-day averages').color]} note under it",
            f"Two {INK_WORDS[_label(scene, SELLS_LABELS[-1]).color]} lines close it",
        ):
            assert phrase in alt, phrase
        _, gy, _, sy, _ = board_curves()
        assert gy[-1] == gy.max() and sy[-1] == sy.min()
