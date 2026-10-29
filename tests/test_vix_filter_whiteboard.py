"""The pins for the two whiteboard GIFs in the VIX filter post, in Lessons 3 and 4.

One sketches how the four readings Lesson 3 names treat one US holiday on
FSTX's calendar, and one how few of buy on gap's kept days carry its sum.

1. The holiday sketch's columns and arrows are laid out schematically, and
   its figures come from the run. What is pinned is that :class:`HolidayWeek`
   is what :mod:`chan.vix_filter`'s own steps give on the committed files,
   each read derived here a second way from the run's functions, that each
   arrow runs from its day's column to the column of the close it reads, and
   that each verdict is in the colour and word its outcome calls for.
2. The kept-days sketch's ticks and bars stand evenly apart, and their
   heights and every figure come from the run. What is pinned is that
   :class:`KeptDays` is :attr:`chan.vix_filter.VixFilter.buy_on_gap`'s kept
   days, derived here a second way, that each bar stands at an affine
   function of its return with zero on the zero line, that the grey ticks
   are the days that held nothing, and that a made-up set of figures moves
   the words.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, both
sketches' slower pace, that two draws give the same bytes, and that each
committed GIF is a fresh draw, a comparison that runs only on macOS arm64
with Comic Sans MS, as ``tests/test_usdcad_tests_whiteboard.py`` explains.
The check that ``docs/figures`` holds exactly the GIFs the modules draw lives
in ``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS`
from here.

Every figure is read from three vintages under one specification, the ones
``tests/test_vix_filter.py`` states: ``vix/vix.csv`` chan-csv raw saved
2012-05-09, the stock panel chan-mat adjusted saved 2012-04-25 and
``fstx.csv`` chan-mat adjusted saved 2012-05-18, with a day kept when
``backshift(1, vix) > 35`` on each joined calendar. The figures were measured
after the run, so they are exploratory and decide nothing.
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
from chan import vix_filter as vf
from chan import vix_filter_whiteboard as sketches
from chan.khandani_lo import plain_sharpe
from chan.paths import FIGURES_DIR, REPO_ROOT
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
from chan.vintage import VintageUnavailable
from chan.vix_filter_whiteboard import (
    COLUMN_XS,
    LANE,
    ROW_YS,
    TICKS_Y,
    WEEK,
    ZERO_Y,
    HolidayRead,
    HolidayWeek,
    KeptDays,
    bar_scale,
    bar_x,
    figures,
    gif_name,
    main,
    make_vix_filter_whiteboards,
    scenes,
    sketch_timeline,
    tick_xs,
)

POST = REPO_ROOT / "blog" / "vix-filter-lessons.md"

#: Every GIF in the order :func:`make_vix_filter_whiteboards` writes them.
GIFS = ["vix_filter_sketch_one_holiday.gif", "vix_filter_sketch_kept_days.gif"]

#: The paragraph each GIF follows, by its opening words.
HOLIDAY_PARAGRAPH = "The join lands 2.6 percent and 0.16."
KEPT_PARAGRAPH = "A kept day is not a day traded."

SPEC = (
    "vix/vix.csv chan-csv raw saved 2012-05-09, the stock panel chan-mat adjusted saved "
    "2012-04-25, fstx.csv chan-mat adjusted saved 2012-05-18; backshift(1, vix) > 35 on "
    "each joined calendar; measured after the run, so exploratory"
)
#: Six decimals, the precision every computed pin is held at.
SIX = 1e-6

day = pd.Timestamp
WED, THU, FRI = WEEK

HOLIDAY_LABELS = [
    "Wed 11-26",
    "Thu 11-27",
    "Fri 11-28",
    "VIX closed",
    "54.92",
    "none: US holiday",
    "55.28",
    "read by 12-01",
    "FSTX traded",
    "Join",
    "not on the joined calendar",
    "kept",
    "Latest close",
    "kept",
    "kept",
    "Filled forward",
    "kept",
    "kept",
    "Row back",
    "kept",
    "dropped",
]

KEPT_LABELS = [
    "190 kept days",
    "170 held nothing: each earns 0",
    "20 held a position",
    "0",
    "8 gained, above 0",
    "12 lost, below 0",
    "2009-04-21: 0.093601",
    "that day is 0.722090 of the 0.129625 the kept days sum to",
    "the other 189: 252 × mean 0.048032, Sharpe 0.855003",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def sources() -> vf.Sources:
    return vf.read_sources()


@pytest.fixture(scope="module")
def result(sources) -> vf.VixFilter:
    return vf.vix_filters(sources)


@pytest.fixture(scope="module")
def week(sources) -> HolidayWeek:
    return HolidayWeek.from_sources(sources)


@pytest.fixture(scope="module")
def kept(result) -> KeptDays:
    return KeptDays.from_filtered(result.buy_on_gap)


@pytest.fixture(scope="module")
def every(week, kept):
    return scenes(week, kept)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_vix_filter_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels_named(scene, text):
    return [s for s in scene.steps if isinstance(s, Label) and s.text == text]


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
        from chan import vix_filter_figures

        assert vix_filter_figures.ACCENT == ACCENT
        shared = {INK, MUTED, ACCENT, GOOD, LOST}
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
        assert sketches.PACED == ("one_holiday", "kept_days")
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_vix_filter_whiteboards(out_dir=tmp_path)
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
        assert not "vix_filter.png".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.vix_filter_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]

    def test_figures_reads_the_folder_it_is_given(self, tmp_path) -> None:
        """An empty folder holds no vintage, so a read of it must fail rather
        than fall back to the committed files."""
        with pytest.raises(VintageUnavailable):
            figures(tmp_path)

    def test_figures_are_the_runs(self, week, kept) -> None:
        """Compared through ``repr``, since a missing close is NaN and NaN
        equals nothing, itself included."""
        found_week, found_kept = figures()
        assert found_kept == kept
        assert repr(found_week) == repr(week)


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (holiday,) = [k for k, p in enumerate(paragraphs) if p.startswith(HOLIDAY_PARAGRAPH)]
        (kept,) = [k for k, p in enumerate(paragraphs) if p.startswith(KEPT_PARAGRAPH)]
        for index, name in zip((holiday, kept), GIFS, strict=True):
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_sits_in_its_lesson(self) -> None:
        text = POST.read_text(encoding="utf-8")
        holiday, kept = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        assert text.index("## Lesson 3:") < holiday < text.index("## Lesson 4:")
        assert text.index("### How few kept days were traded") < kept
        assert kept < text.index("(../docs/figures/vix_filter.png)") < text.index("## Lesson 5:")

    def test_each_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count("(../docs/figures/vix_filter.png)") == 1

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
            assert "drawn slowly" in alt, scene.slug
            assert "twelve seconds" in alt, scene.slug

    def test_the_module_says_what_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "Every figure either sketch prints, and every bar's height, is read from the" in doc
        assert "Two parts of the layout are schematic." in doc


# --- Lesson 3: one US holiday, four readings ----------------------------------


class TestTheHolidayWeek:
    def test_its_closes_and_trade_days_are_the_files(self, week, sources) -> None:
        """VIX closed 54.92 on the Wednesday and 55.28 on the Friday and has no
        close on Thanksgiving, while FSTX traded all three days."""
        assert week.days == (day("2008-11-26"), day("2008-11-27"), day("2008-11-28"))
        assert week.closes[0] == sources.vix[WED] == 54.92
        assert math.isnan(week.closes[1]) and THU not in sources.vix.index
        assert week.closes[2] == sources.vix[FRI] == 55.28
        assert week.traded == (True, True, True)
        assert all(d in sources.fstx.index for d in WEEK)
        assert week.next_day == day("2008-12-01")

    def test_the_join_drops_the_holiday_from_its_calendar(self, week, result) -> None:
        """Derived from the run's own filtered FSTX: the Thursday is not a
        joined day, and the Friday is kept on the Wednesday's close."""
        literal = result.literal
        assert THU not in literal.days
        joined = list(literal.days)
        friday = joined.index(FRI)
        assert joined[friday - 1] == WED
        assert bool(literal.qualifies[friday])
        holiday = week.read("Join", THU)
        assert (holiday.source, holiday.kept) == (None, None) and math.isnan(holiday.close)
        assert week.read("Join", FRI) == HolidayRead("Join", FRI, WED, 54.92, True)

    def test_the_latest_close_reads_the_wednesday_twice(self, week, sources) -> None:
        fstx_days = sources.fstx.index
        latest = vf.latest_close_before(fstx_days, sources.vix)
        for d in (THU, FRI):
            assert latest[fstx_days.get_loc(d)] == 54.92
            assert week.read("Latest close", d) == HolidayRead("Latest close", d, WED, 54.92, True)

    def test_filled_forward_reads_the_same_here(self, week, sources) -> None:
        fstx_days = sources.fstx.index
        filled = sources.vix.reindex(fstx_days, method="ffill").to_numpy(dtype=float)
        kept = vf.qualifies(filled)
        for d in (THU, FRI):
            k = fstx_days.get_loc(d)
            assert filled[k - 1] == 54.92 and bool(kept[k])
            assert week.read("Filled forward", d) == HolidayRead(
                "Filled forward", d, WED, 54.92, True
            )

    def test_a_row_back_drops_the_friday_on_the_holidays_missing_close(self, week, sources) -> None:
        fstx_days = sources.fstx.index
        raw = sources.vix.reindex(fstx_days).to_numpy(dtype=float)
        kept = vf.qualifies(raw)
        thursday, friday = fstx_days.get_loc(THU), fstx_days.get_loc(FRI)
        assert raw[thursday - 1] == 54.92 and bool(kept[thursday])
        assert math.isnan(raw[friday - 1]) and not kept[friday]
        assert week.read("Row back", THU) == HolidayRead("Row back", THU, WED, 54.92, True)
        dropped = week.read("Row back", FRI)
        assert (dropped.source, dropped.kept) == (THU, False) and math.isnan(dropped.close)

    def test_no_day_drawn_reads_the_fridays_close(self, week, result) -> None:
        """55.28 is read first by the next trade day, 2008-12-01, so the
        sketch greys it and names that day."""
        assert all(r.source != FRI for r in week.reads)
        joined = list(result.literal.days)
        assert joined[joined.index(day("2008-12-01")) - 1] == FRI

    def test_a_week_with_no_holiday_is_refused(self, sources) -> None:
        with pytest.raises(ValueError, match="middle day"):
            sketches._one_holiday(
                HolidayWeek.from_sources(
                    sources, (day("2008-11-24"), day("2008-11-25"), day("2008-11-26"))
                )
            )

    def test_a_week_whose_holiday_fstx_did_not_trade_is_refused(self, week) -> None:
        """The sketch draws a check for every day, so a middle day with no
        VIX close that FSTX did not trade either is refused."""
        made_up = HolidayWeek(
            week.days, week.closes, (True, False, True), week.reads, week.next_day
        )
        with pytest.raises(ValueError, match="middle day"):
            sketches._one_holiday(made_up)


class TestTheHolidaySketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "One US holiday, four readings"
        assert every[0].labels == HOLIDAY_LABELS

    def test_each_arrow_runs_from_its_day_to_the_close_it_reads(self, every, week) -> None:
        """The tail at the day's column, the tip at the read close's column,
        the Thursday's above its row and the Friday's below."""
        scene = every[0]
        columns = dict(zip(WEEK, COLUMN_XS, strict=True))
        drawn = 0
        for reading, y in zip(sketches.READINGS, ROW_YS, strict=True):
            for d, lane in ((THU, y + LANE), (FRI, y - LANE)):
                read = week.read(reading, d)
                gid = f"{reading}-{d.date()}"
                if read.source is None:
                    assert gid not in {s.gid for s in scene.strokes}
                    continue
                arrow = _stroke(scene, gid)
                # The tail sits at the day's column, and the shaft runs level
                # in its lane leftwards to the tip, the arrow's leftmost point.
                assert (arrow.x[0], arrow.y[0]) == pytest.approx((columns[d], lane))
                tip = int(np.argmin(arrow.x))
                assert arrow.x[tip] == pytest.approx(columns[read.source])
                assert np.allclose(arrow.y[: tip + 1], lane)
                assert arrow.color == INK
                drawn += 1
        assert drawn == 7

    def test_its_verdicts_follow_the_reads(self, every, week) -> None:
        scene = every[0]
        verdicts = [
            s for s in scene.steps if isinstance(s, Label) and s.text in ("kept", "dropped")
        ]
        expected = [r for r in week.reads if r.kept is not None]
        assert len(verdicts) == len(expected) == 7
        for label, read in zip(verdicts, expected, strict=True):
            assert label.names == f"{read.reading}-{read.day.date()}"
            assert (label.text, label.color) == (("kept", GOOD) if read.kept else ("dropped", LOST))

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert _stroke(scene, "top-rule").color == MUTED
        for d in WEEK:
            assert _stroke(scene, f"traded-{d.date()}").color == INK
        for text in ("55.28", "read by 12-01", "not on the joined calendar"):
            assert _label(scene, text).color == MUTED, text
        for text in ("54.92", "none: US holiday", "VIX closed", "FSTX traded", *sketches.READINGS):
            assert _label(scene, text).color == INK, text

    def test_the_headings_checks_and_words_sit_with_their_columns(self, every, week) -> None:
        """Each day's heading and check stand in its column, and each kept or
        dropped word starts just right of its own arrow's tail, in its lane."""
        scene = every[0]
        for d, x in zip(WEEK, COLUMN_XS, strict=True):
            heading = _label(scene, d.strftime("%a %m-%d"))
            assert (heading.x, heading.ha) == (x, "center")
            check = _stroke(scene, f"traded-{d.date()}")
            assert (check.x.min() + check.x.max()) / 2 == pytest.approx(x)
        verdicts = iter(
            s for s in scene.steps if isinstance(s, Label) and s.text in ("kept", "dropped")
        )
        for read in (r for r in week.reads if r.kept is not None):
            arrow = _stroke(scene, f"{read.reading}-{read.day.date()}")
            word = next(verdicts)
            assert (word.x, word.y) == pytest.approx((arrow.x[0] + sketches.VERDICT_DX, arrow.y[0]))

    def test_the_columns_stand_evenly_apart(self, every) -> None:
        """The alt text and the docstring say the layout is schematic with
        even columns, so the spacing is held directly, not through COLUMN_XS."""
        scene = every[0]
        xs = [_label(scene, d.strftime("%a %m-%d")).x for d in WEEK]
        assert np.allclose(np.diff(xs), xs[1] - xs[0]) and xs[1] > xs[0]

    def test_the_closes_sit_in_their_columns(self, every) -> None:
        scene = every[0]
        for text, x in zip(("54.92", "none: US holiday", "55.28"), COLUMN_XS, strict=True):
            assert _label(scene, text).x == x
            assert _label(scene, text).ha == "center"

    def test_a_read_of_a_day_not_drawn_is_refused(self, week) -> None:
        reads = tuple(
            HolidayRead(r.reading, r.day, day("2008-11-25"), 60.9, True)
            if (r.reading, r.day) == ("Latest close", THU)
            else r
            for r in week.reads
        )
        made_up = HolidayWeek(week.days, week.closes, week.traded, reads, week.next_day)
        with pytest.raises(ValueError, match="not drawn"):
            sketches._one_holiday(made_up)

    @pytest.mark.parametrize("source", [FRI, THU], ids=["itself", "a later day"])
    def test_a_read_of_its_own_day_or_a_later_one_is_refused(self, week, source) -> None:
        """A drawn column is not enough: a day reads an earlier close, so an
        arrow from the Friday to itself or from the Thursday to the Friday
        would draw a look-ahead no reading makes."""
        target = ("Row back", FRI) if source == FRI else ("Latest close", THU)
        later = FRI if source == THU else source
        reads = tuple(
            HolidayRead(r.reading, r.day, later, 55.28, True) if (r.reading, r.day) == target else r
            for r in week.reads
        )
        made_up = HolidayWeek(week.days, week.closes, week.traded, reads, week.next_day)
        with pytest.raises(ValueError, match="not drawn"):
            sketches._one_holiday(made_up)

    def test_made_up_closes_and_verdicts_move_the_words(self, week) -> None:
        reads = tuple(
            HolidayRead(r.reading, r.day, r.source, 30.0, False) if r.kept else r
            for r in week.reads
        )
        made_up = HolidayWeek(
            week.days, (30.0, math.nan, 31.5), week.traded, reads, day("2008-12-02")
        )
        labels = sketches._one_holiday(made_up).labels
        assert "30.00" in labels and "31.50" in labels and "read by 12-02" in labels
        assert "kept" not in labels and labels.count("dropped") == 7

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "In the “Join” row the Thursday has no arrow" in alt
        assert "both arrows run back to the Wednesday" in alt
        assert "the Friday’s arrow runs back only to the Thursday" in alt
        assert "No arrow reaches the Friday’s grey “55.28”" in alt


# --- Lesson 4: what buy on gap's kept days earned ------------------------------


class TestTheKeptDays:
    def test_they_are_buy_on_gaps_kept_days(self, kept, result) -> None:
        """Derived here a second way from the run's own filtered returns."""
        long = result.buy_on_gap
        returns = pd.Series(long.daily, index=long.days)[long.qualifies]
        held = pd.Series(long.held, index=long.days)[long.qualifies]
        assert kept.kept == len(returns) == 190
        assert kept.held_days == tuple(returns.index[held.to_numpy()])
        assert kept.held == pytest.approx(tuple(returns[held.to_numpy()]), abs=0)
        assert kept.places == tuple(int(k) for k in np.flatnonzero(held.to_numpy()))
        assert (returns[~held.to_numpy()] == 0).all()
        assert kept.total == pytest.approx(float(returns.sum()), abs=1e-15)

    def test_the_figures_the_sketch_prints(self, kept) -> None:
        """The post's figures, held at six decimals."""
        assert (kept.kept, len(kept.held), kept.unheld) == (190, 20, 170), SPEC
        assert (kept.gained, kept.lost) == (8, 12), SPEC
        assert kept.held_days[kept.top] == day("2009-04-21"), SPEC
        assert kept.held[kept.top] == pytest.approx(0.093601, abs=SIX), SPEC
        assert kept.total == pytest.approx(0.129625, abs=SIX), SPEC
        assert kept.share == pytest.approx(0.722090, abs=SIX), SPEC
        assert kept.rest_return == pytest.approx(0.048032, abs=SIX), SPEC
        assert kept.rest_sharpe == pytest.approx(0.855003, abs=SIX), SPEC

    def test_the_rest_is_the_other_189_kept_days(self, kept, result) -> None:
        returns = result.buy_on_gap.filtered
        rest = np.delete(returns, int(np.argmax(returns)))
        assert len(rest) == 189
        assert kept.rest_return == pytest.approx(252 * rest.mean(), abs=1e-15)
        assert kept.rest_sharpe == pytest.approx(plain_sharpe(rest), abs=1e-15)

    def test_several_bars_are_slivers(self, kept) -> None:
        """The smallest held day, 2008-11-06, returned 0.000025, so the
        sketch labels the counts rather than relying on every bar showing."""
        smallest = int(np.argmin(np.abs(kept.held)))
        assert kept.held_days[smallest] == day("2008-11-06"), SPEC
        assert abs(kept.held[smallest]) == pytest.approx(0.000025, abs=SIX), SPEC

    @pytest.mark.parametrize("earned", [0.002, -0.002], ids=["gained", "lost"])
    def test_a_kept_day_without_a_position_that_earned_is_refused(self, earned) -> None:
        """Either sign: "each earns 0" is false whether the day gained or lost."""
        days = pd.date_range("2020-01-01", periods=4)
        made_up = vf.Filtered(
            name="made up",
            days=days,
            daily=np.array([0.0, 0.01, earned, -0.01]),
            held=np.array([False, True, False, True]),
            qualifies=np.array([False, True, True, True]),
            calendar_days=4,
        )
        with pytest.raises(ValueError, match="no position"):
            KeptDays.from_filtered(made_up)


def _made_up() -> KeptDays:
    return KeptDays(
        kept=12,
        places=(1, 4, 7, 10),
        held_days=(day("2020-01-02"), day("2020-01-07"), day("2020-01-10"), day("2020-01-15")),
        held=(-0.02, 0.05, 0.01, -0.005),
        total=0.035,
        rest_return=-0.315,
        rest_sharpe=-1.25,
    )


class TestTheKeptDaysSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "What buy on gap’s kept days earned"
        assert every[1].labels == KEPT_LABELS

    def test_made_up_figures_move_the_words(self) -> None:
        labels = sketches._kept_days(_made_up()).labels
        assert labels == [
            "12 kept days",
            "8 held nothing: each earns 0",
            "4 held a position",
            "0",
            "2 gained, above 0",
            "2 lost, below 0",
            "2020-01-07: 0.050000",
            "that day is 1.428571 of the 0.035000 the kept days sum to",
            "the other 11: 252 × mean −0.315000, Sharpe −1.250000",
        ]

    @pytest.mark.parametrize(
        ("places", "held"),
        [((0,), (-0.01,)), ((0,), (0.0,)), ((), ())],
        ids=["lost", "flat", "none held"],
    )
    def test_a_rule_whose_largest_held_day_did_not_gain_is_refused(self, places, held) -> None:
        """The struck bar's share of the sum needs a day that gained, so a
        largest held day that lost, earned exactly 0, or does not exist is refused."""
        days = tuple(day("2020-01-02") for _ in held)
        made_up = KeptDays(3, places, days, held, sum(held), 0.0, 0.0)
        with pytest.raises(ValueError, match="gained"):
            sketches._kept_days(made_up)

    @pytest.mark.parametrize("which", ["run", "made up", "loss largest"])
    def test_each_bar_stands_at_an_affine_function_of_its_return(self, every, kept, which) -> None:
        """The third case's largest bar is a loss, so the scale has to come
        from the largest bar either way, not the largest gain."""
        days = {
            "run": kept,
            "made up": _made_up(),
            "loss largest": KeptDays(
                kept=5,
                places=(1, 3),
                held_days=(day("2020-01-02"), day("2020-01-06")),
                held=(0.01, -0.05),
                total=-0.04,
                rest_return=-12.6,
                rest_sharpe=-1.0,
            ),
        }[which]
        scene = every[1] if which == "run" else sketches._kept_days(days)
        scale = bar_scale(days)
        assert max(abs(v) for v in days.held) * scale == pytest.approx(sketches.TALLEST)
        for k, (d, value) in enumerate(zip(days.held_days, days.held, strict=True)):
            bar = _stroke(scene, f"bar-{d.date()}")
            # An outline from the zero line to the bar's value, centred on its place.
            assert (bar.x.min(), bar.x.max()) == pytest.approx(
                (bar_x(k) - sketches.BAR_HALF, bar_x(k) + sketches.BAR_HALF)
            )
            end = ZERO_Y + scale * value
            assert (bar.y.min(), bar.y.max()) == pytest.approx(
                (min(ZERO_Y, end), max(ZERO_Y, end)), abs=1e-12
            )
            assert (bar.x[0], bar.y[0]) == pytest.approx((bar.x[-1], bar.y[-1]))
        xs = [bar_x(k) for k in range(len(days.held))]
        assert np.allclose(np.diff(xs), sketches.BAR_STEP)
        zero = _stroke(scene, "zero")
        assert set(np.round(zero.y, 12)) == {ZERO_Y}
        assert zero.x.min() < xs[0] and xs[-1] < zero.x.max()

    def test_its_colours(self, every, kept) -> None:
        """Gains green above zero, losses red below, the largest in brass."""
        scene = every[1]
        for k, (d, value) in enumerate(zip(kept.held_days, kept.held, strict=True)):
            bar = _stroke(scene, f"bar-{d.date()}")
            if k == kept.top:
                assert bar.color == ACCENT
            else:
                assert bar.color == (GOOD if value > 0 else LOST), d
        assert _stroke(scene, "kept").color == INK
        assert _stroke(scene, "unheld").color == MUTED
        assert _stroke(scene, "zero").color == MUTED
        assert _stroke(scene, "strike").color == INK
        colours = {
            "190 kept days": INK,
            "170 held nothing: each earns 0": MUTED,
            "0": MUTED,
            "20 held a position": INK,
            "8 gained, above 0": GOOD,
            "12 lost, below 0": LOST,
            "2009-04-21: 0.093601": ACCENT,
            "that day is 0.722090 of the 0.129625 the kept days sum to": ACCENT,
            "the other 189: 252 × mean 0.048032, Sharpe 0.855003": INK,
        }
        for text, colour in colours.items():
            assert _label(scene, text).color == colour, text

    @pytest.mark.parametrize("which", ["run", "made up"])
    def test_the_gained_and_lost_words_point_at_a_bar_of_their_sign(
        self, every, kept, which
    ) -> None:
        days = kept if which == "run" else _made_up()
        scene = every[1] if which == "run" else sketches._kept_days(days)
        pairs = list(zip(days.held_days, days.held, strict=True))
        first_gain = next(d for d, v in pairs if v > 0)
        first_loss = next(d for d, v in pairs if v < 0)
        assert _label(scene, f"{days.gained} gained, above 0").names == f"bar-{first_gain.date()}"
        assert _label(scene, f"{days.lost} lost, below 0").names == f"bar-{first_loss.date()}"

    def test_the_ticks_stand_evenly_apart(self, every, kept) -> None:
        """Read from the drawn tick tops rather than from ``tick_xs``, so a
        row that bunches its ticks fails."""
        ticks = _stroke(every[1], "kept")
        tops = np.unique(ticks.x[ticks.y == sketches.TICKS_Y + sketches.TICK_HIGH])
        assert len(tops) == kept.kept
        gaps = np.diff(tops)
        assert np.allclose(gaps, gaps[0]) and gaps[0] > 0

    def test_the_grey_ticks_are_the_days_that_held_nothing(self, every, kept) -> None:
        """One black tick per kept day, then a grey tick over each of the 170
        that held nothing, so the 20 held days stay black in date order."""
        scene = every[1]
        xs = tick_xs(kept.kept)
        ticks = _stroke(scene, "kept")
        grey = _stroke(scene, "unheld")
        tops = sketches.TICKS_Y + sketches.TICK_HIGH
        assert np.allclose(np.sort(np.unique(ticks.x[ticks.y == tops])), xs)
        greyed = np.unique(grey.x[grey.y == tops])
        assert len(greyed) == kept.unheld == 170
        held_xs = set(np.round(xs[list(kept.places)], 12))
        assert held_xs.isdisjoint(set(np.round(greyed, 12)))
        assert len(held_xs) == len(kept.held) == 20
        assert set(np.round(ticks.y, 12)) == {TICKS_Y, round(tops, 12)}

    def test_the_strike_crosses_the_largest_bar(self, every, kept) -> None:
        scene = every[1]
        strike = _stroke(scene, "strike")
        top = _stroke(scene, f"bar-{kept.held_days[kept.top].date()}")
        x = top.x[0]
        assert strike.x.min() < x < strike.x.max()
        assert top.y.min() < strike.y.min() and strike.y.max() < top.y.max()
        steps = list(scene.steps)
        assert steps.index(top) < steps.index(strike) < steps.index(_label(scene, KEPT_LABELS[-1]))

    def test_its_alt_text_says_what_the_picture_shows(self, every, kept) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert f"A row of {kept.kept} thin black ticks" in alt
        assert f"{kept.unheld} of them turn grey" in alt
        assert "A black dot then appears over each of the other ticks" in alt
        assert f"{len(kept.held)} bars stand evenly spaced in date order on it" in alt
        assert "with green bars above it and short red bars below" in alt
        assert "Several are so short they show only as dashes on the line" in alt
        assert "One brass bar stands far above the rest" in alt
        assert "A black line then strikes through the brass bar" in alt

    def test_the_bar_shapes_the_alt_text_names(self, kept) -> None:
        """Three claims the alt text makes about the bars' sizes, measured on
        the run's bars at the board's scale.

        1. Several are dashes: at least two bars are shorter than the
           outline's own width.
        2. The red bars are short: every loss is under a tenth of the tallest.
        3. The brass bar stands far above the rest: at least twice the next.
        """
        px_per_unit = HEIGHT / (whiteboard.YLIM[1] - whiteboard.YLIM[0])
        outline_px = sketches.BAR_LINE * whiteboard.DPI / 72
        heights = np.abs(np.array(kept.held)) * bar_scale(kept) * px_per_unit
        assert int((heights < outline_px).sum()) >= 2, SPEC
        losses = [abs(v) for v in kept.held if v < 0]
        assert max(losses) * bar_scale(kept) < 0.1 * sketches.TALLEST, SPEC
        ordered = sorted(kept.held, reverse=True)
        assert ordered[0] == kept.held[kept.top] and ordered[0] >= 2 * ordered[1], SPEC

    def test_a_dot_marks_each_held_day_in_the_row(self, every, kept) -> None:
        """One black dot over the tick of each kept day that held a position,
        above the row and drawn after the grey."""
        scene = every[1]
        dots = _stroke(scene, "held")
        assert dots.dots > 0 and dots.color == INK
        assert np.allclose(dots.x, tick_xs(kept.kept)[list(kept.places)])
        assert set(np.round(dots.y, 12)) == {
            round(TICKS_Y + sketches.TICK_HIGH + sketches.HELD_DOT_DY, 12)
        }
        steps = list(scene.steps)
        assert steps.index(_stroke(scene, "unheld")) < steps.index(dots)
        assert _label(scene, "20 held a position").names == "held"
