"""The pins for the two whiteboard GIFs in the Kalman filter hedge post.

One sketches the four steps the filter runs each day, on 2007-05-15, and one
Lesson 2's claim that on the file's first two rows the filter forecasts EWC
at 0, so its error is EWC's whole close and the script shorts EWC alone. What
is pinned is what a reader takes from each.

1. The one-day sketch draws every mark to scale on axes zoomed around the
   day. Its forecast sits on yesterday's line at today's EWA, its red bar runs
   from the forecast to the close, its band is the forecast's standard
   deviation either side, and the updated line passes where the update puts
   it. Its closing words split the line's lift at today's EWA into the
   slope's part and the intercept's, and give the share of the miss the lift
   closed, which is 1 − Ve / Q, so the test derives it both ways.
2. The zero-start sketch draws rows 1 to 3 on one dollar scale. Only row 1's
   words say EWC alone, because row 2's position already holds the slope after
   row 2's update, and the test reads that position off the run.

Every figure either sketch draws is read from :func:`chan.kalman_hedge.kalman_hedge`
on the committed file. The tests derive each again from
:func:`chan.kalman_hedge.kalman_filter` rather than trusting the sketch's own
reading, pin them at the precision drawn with :data:`SPEC` in the message, and
draw a made-up set of figures to show the words follow the data.

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

from chan import kalman_hedge
from chan import kalman_hedge_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.kalman_hedge_whiteboard import (
    COLUMN_X,
    DOT_OFFSET,
    HAIR_HALF,
    OneDay,
    Row,
    ZeroStart,
    dollar_y,
    gif_name,
    main,
    make_kalman_hedge_whiteboards,
    scale,
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
    clearances,
    hand_font,
    timeline,
)

POST = REPO_ROOT / "blog" / "kalman-hedge-lessons.md"

#: Every GIF in the order :func:`make_kalman_hedge_whiteboards` writes them.
GIFS = [
    "kalman_hedge_sketch_one_day.gif",
    "kalman_hedge_sketch_zero_start.gif",
]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "After the first day, the filter never becomes confident",
    "**What that trade earns.**",
)

SPEC = (
    "inputdata_etf/ EWA and EWC closes over 1,500 days, KF_beta_EWA_EWC.m's Kalman filter "
    "with delta 0.0001 and Ve 0.001 from a zero start; forecasts are the close minus e, "
    "bands sqrt(Q), slopes and intercepts after each row's update"
)

ONE_DAY_LABELS = [
    "EWA close",
    "EWC close",
    "1 hold",
    "yesterday: slope 1.127974,",
    "intercept 0.471207",
    "EWA 23.31",
    "2 forecast",
    "forecast 26.76",
    "band ±0.24",
    "close 27.15",
    "3 miss",
    "error 0.39",
    "4 update",
    "updated: slope 1.144185,",
    "intercept 0.472220",
    "slope +0.016211 × EWA 23.31 = +0.38, intercept +0.001013: line to 27.14, 98% of the miss",
]

ZERO_LABELS = [
    "forecast 0",
    "close 22.95",
    "error 22.95",
    "band ±0.031623",
    "row 1, 2006-04-26",
    "short EWC alone, 0 EWA shares",
    "forecast 0",
    "close 22.78",
    "error 22.78",
    "band ±0.163213",
    "row 2, 2006-04-27",
    "slope 0 → 1.366666,",
    "after the forecast",
    "+0.74% on 2006-04-27",
    "close 22.94",
    "error 0.85",
    "band ±0.167334",
    "forecast 22.09",
    "row 3, 2006-04-28",
    "forecast uses",
    "slope 1.366666",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def run():
    """The closes and the filter, read without going through the sketch module."""
    _, closes = kalman_hedge.read_sources()
    x = closes[kalman_hedge.X].to_numpy(dtype=float)
    y = closes[kalman_hedge.Y].to_numpy(dtype=float)
    return x, y, kalman_hedge.kalman_filter(closes.index, x, y), kalman_hedge.kalman_hedge(closes)


@pytest.fixture(scope="module")
def day() -> OneDay:
    return OneDay.from_run()


@pytest.fixture(scope="module")
def zero() -> ZeroStart:
    return ZeroStart.from_run()


@pytest.fixture(scope="module")
def every(day, zero):
    return scenes(day, zero)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, day, zero):
    return make_kalman_hedge_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), day=day, zero=zero
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


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

    def test_neither_draws_a_tint(self, every) -> None:
        """No pale tint, so none needs the green edge the shared rules ask of one."""
        assert not [fill for scene in every for fill in scene.fills]


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
        assert sketches.PACED == ("one_day", "zero_start")
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, day, zero) -> None:
        again = make_kalman_hedge_whiteboards(out_dir=tmp_path, day=day, zero=zero)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "kalman_hedge.png").exists()

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
            ), f"{path.name}: redraw with: uv run python -m chan.kalman_hedge_whiteboard"


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

    def test_each_is_followed_by_a_one_sentence_italic_caption(self) -> None:
        """The post captions its chart, so each sketch gets a caption too."""
        paragraphs = _paragraphs()
        for name in GIFS:
            (index,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{name})" in p]
            caption = paragraphs[index + 1]
            assert re.fullmatch(r"\*[^*\n]+\.\*", caption), name
            assert caption.count(". ") == 0, name

    def test_each_sits_in_its_section(self) -> None:
        """The first sits under the filter's section, after its four steps and
        before its two constants. The second sits in Lesson 2, after the
        trade's return and before the figures without the first trade."""
        text = POST.read_text(encoding="utf-8")
        one_day, zero_start = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        steps = text.index("In plain terms, each day runs four steps.")
        constants = text.index("Two constants set the filter’s pace.")
        lesson = text.index("## Lesson 2: the script trades before the filter has learned anything")
        without = text.index("### The figures without the first trade")
        assert steps < one_day < constants
        assert lesson < zero_start < without

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

    def test_each_alt_text_says_it_is_drawn_to_scale_and_names_its_pace(self, every) -> None:
        one_day, zero_start = (_alt(scene) for scene in every)
        assert "every mark is drawn to scale on them" in one_day
        assert "each axis on its own scale" in one_day
        assert "share one dollar scale" in zero_start
        assert "drawn to the same scale" in zero_start
        for alt in (one_day, zero_start):
            assert "drawn slowly" in alt and "twelve seconds" in alt

    def test_the_module_says_neither_sketch_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "Neither sketch is schematic." in doc
        assert "each to its own scale" in doc


# --- The filter and the file: one day of the filter --------------------------


class TestTheDay:
    def test_it_is_the_runs(self, day, run) -> None:
        """Read again from :func:`chan.kalman_hedge.kalman_filter` rather than
        through :class:`OneDay`."""
        x, y, f, _ = run
        (t,) = np.flatnonzero(f.days == "2007-05-15")
        assert (day.ewa, day.close) == (x[t], y[t]), SPEC
        assert (day.slope_before, day.intercept_before) == (f.slope[t - 1], f.intercept[t - 1])
        assert (day.slope_after, day.intercept_after) == (f.slope[t], f.intercept[t])
        assert day.forecast == pytest.approx(f.slope[t - 1] * x[t] + f.intercept[t - 1], abs=1e-12)
        assert day.error == f.error[t]
        assert day.sd == np.sqrt(f.variance[t])

    def test_its_figures(self, day) -> None:
        assert (day.ewa, day.close) == (23.31, 27.15), SPEC
        assert day.slope_before == pytest.approx(1.127974, abs=5e-7), SPEC
        assert day.intercept_before == pytest.approx(0.471207, abs=5e-7), SPEC
        assert day.forecast == pytest.approx(26.764272, abs=5e-7), SPEC
        assert day.error == pytest.approx(0.385728, abs=5e-7), SPEC
        assert day.sd == pytest.approx(0.237529, abs=5e-7), SPEC
        assert day.slope_after == pytest.approx(1.144185, abs=5e-7), SPEC
        assert day.intercept_after == pytest.approx(0.472220, abs=5e-7), SPEC
        assert day.moved == pytest.approx(27.143163, abs=5e-7), SPEC
        assert day.slope_lift == pytest.approx(0.377878, abs=5e-7), SPEC
        assert day.intercept_lift == pytest.approx(0.001013, abs=5e-7), SPEC

    def test_the_two_lifts_add_up_to_the_lines_move(self, day) -> None:
        """At today's EWA the updated line sits above yesterday's by the
        slope's lift plus the intercept's, and the slope's is nearly all of it."""
        assert day.slope_lift + day.intercept_lift == pytest.approx(
            day.moved - day.forecast, abs=1e-12
        )
        assert day.slope_lift > 300 * day.intercept_lift > 0

    def test_the_files_first_row_is_refused(self, run) -> None:
        """Row 1 has no row before it, so no slope and intercept for its
        forecast, and reading one would wrap round to the file's last row."""
        _, _, f, _ = run
        with pytest.raises(ValueError, match="first row"):
            OneDay.from_run(str(f.days[0].date()))
        assert OneDay.from_run(str(f.days[1].date())).slope_before == f.slope[0]

    def test_the_share_closed_is_one_minus_ve_over_q(self, day, run) -> None:
        """The update moves the forecast at today's EWA by the gain's share of
        the miss, which the filter's equations make 1 − Ve / Q."""
        assert day.closed == pytest.approx(1 - kalman_hedge.VE / day.sd**2, abs=1e-9)
        assert day.closed == pytest.approx(0.982276, abs=5e-7), SPEC
        assert f"{day.closed:.0%}" == "98%"

    def test_its_slope_moves_more_than_a_median_days(self, day, run) -> None:
        """The caption calls the day's rise in the slope larger than a median
        day's, the median the post quotes over rows 3 to 1,500."""
        _, _, f, _ = run
        median = np.median(np.abs(np.diff(f.slope)[1:]))
        assert day.slope_after - day.slope_before > median
        paragraphs = _paragraphs()
        (at,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{GIFS[0]})" in p]
        rise = day.slope_after - day.slope_before
        word = "larger" if abs(rise) > median else "smaller"
        moved = "rise" if rise > 0 else "fall"
        assert f"a {moved} in the slope, {word} than a median day’s" in paragraphs[at + 1]

    def test_the_day_is_a_typical_one(self, run) -> None:
        """Its share sits within half a point of the median over rows 3 to
        1,500, so the sketch does not draw an unusual day."""
        _, _, f, _ = run
        shares = 1 - kalman_hedge.VE / f.variance[2:]
        (t,) = np.flatnonzero(f.days == "2007-05-15")
        assert abs((1 - kalman_hedge.VE / f.variance[t]) - np.median(shares)) < 0.005


class TestTheOneDaySketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "One day of the filter"
        assert every[0].labels == ONE_DAY_LABELS

    def test_the_list_names_the_posts_four_steps_in_order(self, every) -> None:
        scene = every[0]
        steps = [_label(scene, f"{n} {word}") for n, word in enumerate(sketches.STEPS, start=1)]
        assert sketches.STEPS == ("hold", "forecast", "miss", "update")
        assert len({label.x for label in steps}) == 1
        heights = [label.y for label in steps]
        assert heights == sorted(heights, reverse=True)
        assert [label.names for label in steps] == ["yesterday", "forecast", "error", "updated"]
        post = POST.read_text(encoding="utf-8")
        titles = ("**Hold a guess.**", "**Forecast.**", "**Measure the miss.**", "**Update")
        assert [post.count(title) for title in titles] == [1, 1, 1, 1]
        at = [post.index(title) for title in titles]
        assert at == sorted(at)

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert {s.gid: s.color for s in scene.strokes} == {
            "ewa-axis": MUTED,
            "ewc-axis": MUTED,
            "yesterday": INK,
            "today": MUTED,
            "forecast": MUTED,
            "band-high": ACCENT,
            "band-low": ACCENT,
            "close": INK,
            "error": LOST,
            "updated": GOOD,
        }
        assert [_label(scene, text).color for text in ONE_DAY_LABELS] == [
            MUTED,
            MUTED,
            INK,
            INK,
            INK,
            MUTED,
            MUTED,
            MUTED,
            ACCENT,
            INK,
            LOST,
            LOST,
            GOOD,
            GOOD,
            GOOD,
            GOOD,
        ]
        steps = [_label(scene, f"{n} {word}") for n, word in enumerate(sketches.STEPS, start=1)]
        marks = {s.gid: s.color for s in scene.strokes}
        assert [label.color for label in steps] == [marks[label.names] for label in steps]

    def test_every_mark_sits_at_its_figure(self, every, day) -> None:
        """One affine map per axis: the forecast tick and the bar's foot at the
        forecast, the dot and the bar's top at the close, the hairlines one
        standard deviation either side, all at today's EWA."""
        scene, s = every[0], scale(day)
        today = s.x(day.ewa)
        tick, close, bar = (_stroke(scene, gid) for gid in ("forecast", "close", "error"))
        high, low = _stroke(scene, "band-high"), _stroke(scene, "band-low")
        assert tick.y == pytest.approx(np.full(tick.points, s.y(day.forecast)))
        assert tick.x.mean() == pytest.approx(today)
        assert (close.x[0], close.y[0]) == pytest.approx((today, s.y(day.close)))
        assert bar.x == pytest.approx(np.full(bar.points, today))
        assert (bar.y[0], bar.y[-1]) == pytest.approx((s.y(day.forecast), s.y(day.close)))
        assert high.y == pytest.approx(np.full(high.points, s.y(day.forecast + day.sd)))
        assert low.y == pytest.approx(np.full(low.points, s.y(day.forecast - day.sd)))
        assert (low.x.min(), low.x.max()) == pytest.approx((today - HAIR_HALF, today + HAIR_HALF))
        axis = _stroke(scene, "today")
        assert axis.x == pytest.approx(np.full(axis.points, today))

    def test_each_line_is_its_slope_and_intercept(self, every, day) -> None:
        """Every point of each line is the line's EWC at that point's EWA, so
        yesterday's passes through the forecast and the update's through the
        moved forecast, a hair below the close."""
        scene, s = every[0], scale(day)
        for gid, line in (("yesterday", day.before), ("updated", day.after)):
            stroke = _stroke(scene, gid)
            expected = [s.y(line(s.ewa_at(x))) for x in stroke.x]
            assert stroke.y == pytest.approx(expected), gid
            assert (stroke.x[0], stroke.x[-1]) == pytest.approx(sketches.PLOT_X), gid
        today = s.x(day.ewa)
        old, new = _stroke(scene, "yesterday"), _stroke(scene, "updated")
        assert np.interp(today, old.x, old.y) == pytest.approx(s.y(day.forecast), abs=1e-3)
        assert np.interp(today, new.x, new.y) == pytest.approx(s.y(day.moved), abs=1e-3)
        left = s.y(day.close) - np.interp(today, new.x, new.y)
        assert 0 < left < 0.03 * (s.y(day.close) - s.y(day.forecast))

    def test_the_zoom_keeps_every_mark_inside_the_plot(self, every, day) -> None:
        scene = every[0]
        for gid in ("yesterday", "updated", "band-high", "band-low", "close", "error"):
            stroke = _stroke(scene, gid)
            assert sketches.PLOT_Y[0] <= stroke.y.min() <= stroke.y.max() <= sketches.PLOT_Y[1]

    def test_the_update_line_appears_after_the_miss(self, every) -> None:
        order = [getattr(s, "gid", None) or s.text for s in every[0].steps]
        assert order.index("yesterday") < order.index("forecast") < order.index("error")
        assert order.index("error") < order.index("updated")
        assert order[-1] == ONE_DAY_LABELS[-1]

    def test_its_words_follow_the_day(self) -> None:
        other = OneDay(
            day="2001-02-03",
            ewa=10.0,
            close=12.5,
            slope_before=1.2,
            intercept_before=0.0,
            forecast=12.0,
            error=0.5,
            sd=0.3,
            slope_after=1.23,
            intercept_after=0.02,
        )
        labels = scenes(other, ZeroStart.from_run())[0].labels
        assert labels[3:5] == ["yesterday: slope 1.200000,", "intercept 0.000000"]
        assert "forecast 12.00" in labels and "close 12.50" in labels and "error 0.50" in labels
        assert labels[-1] == (
            "slope +0.030000 × EWA 10.00 = +0.30, intercept +0.020000: line to 12.32, "
            "64% of the miss"
        )

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[0])
        for phrase in (
            "zoomed around 2007-05-15",
            "A black line, yesterday’s slope and intercept",
            "a numbered list of steps down the left side, each in its mark’s colour",
            "a thick grey tick on the black line above it is the forecast",
            "Two brass hairlines above and below the forecast",
            "A black dot higher up is EWC’s close",
            "a red bar from the forecast up to the dot",
            "a green line, the slope and intercept after the update",
            "Its intercept has barely changed",
            "that rise lifts the line by 0.38",
            "The finished drawing holds for twelve seconds.",
        ):
            assert phrase in alt, phrase
        assert "a little" not in alt
        assert "gutter" not in alt


# --- Lesson 2: two rows on a forecast of 0 ------------------------------------


class TestTheZeroStart:
    def test_it_is_the_runs(self, zero, run) -> None:
        _, y, f, result = run
        for k, row in enumerate(zero.rows):
            assert row.day == str(f.days[k].date()), SPEC
            assert (row.close, row.error, row.slope) == (y[k], f.error[k], f.slope[k]), SPEC
            assert row.forecast == y[k] - f.error[k]
            assert row.band == np.sqrt(f.variance[k])
        assert zero.units == result.trade.units[0]
        assert zero.first_return == result.trade.daily[1]
        assert np.flatnonzero(result.trade.daily)[0] == 1

    def test_its_figures(self, zero) -> None:
        one, two, three = zero.rows
        assert [row.day for row in zero.rows] == ["2006-04-26", "2006-04-27", "2006-04-28"]
        assert (one.forecast, two.forecast) == (0.0, 0.0), SPEC
        assert (one.error, two.error) == pytest.approx((22.95, 22.78), abs=5e-9), SPEC
        assert three.forecast == pytest.approx(22.088850, abs=5e-7), SPEC
        assert three.error == pytest.approx(0.851150, abs=5e-7), SPEC
        assert [row.band for row in zero.rows] == pytest.approx(
            [0.031623, 0.163213, 0.167334], abs=5e-7
        ), SPEC
        assert (one.slope, two.slope) == (0.0, pytest.approx(1.366666, abs=5e-7)), SPEC
        assert zero.units == -1.0, SPEC
        assert zero.first_return == pytest.approx(0.0074074, abs=5e-8), SPEC
        assert zero.first_return_day == "2006-04-27"

    def test_the_first_return_is_ewc_falling_under_a_short_alone(self, zero) -> None:
        """Row 1 holds −1 unit of EWC and 0 of EWA, so its return on row 2 is
        EWC's fall over EWC's price."""
        one, two, _ = zero.rows
        assert zero.first_return == pytest.approx((one.close - two.close) / one.close)

    def test_row_2_is_already_hedged(self, run) -> None:
        """Positions use the slope after each row's update, so row 2's short
        holds 1.366666 EWA shares against one EWC, not EWC alone."""
        x, y, f, result = run
        units = result.trade.units
        ewa_shares = units[:2] * -f.slope[:2]
        assert ewa_shares[0] == 0
        assert ewa_shares[1] == pytest.approx(1.366666, abs=5e-7)

        def earned(held: np.ndarray) -> float:
            """Row 3's return on ``held`` dollars of EWA and EWC from row 2."""
            moves = np.array([x[2] / x[1] - 1, y[2] / y[1] - 1])
            return float(held @ moves / np.abs(held).sum())

        hedged = units[1] * np.array([-f.slope[1] * x[1], y[1]])
        alone = units[1] * np.array([0.0, y[1]])
        assert result.trade.daily[2] == pytest.approx(earned(hedged), abs=1e-15)
        assert abs(result.trade.daily[2] - earned(alone)) > 0.005


class TestTheZeroStartSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Two rows on a forecast of 0"
        assert every[1].labels == ZERO_LABELS

    def test_row_3s_words_name_the_slope_its_forecast_uses(self, every, run) -> None:
        """Row 3's forecast is made from the slope and intercept row 2's update
        left, so the slope under its column is row 2's, read from the filter."""
        x, y, f, _ = run
        assert y[2] - f.error[2] == pytest.approx(f.slope[1] * x[2] + f.intercept[1], abs=1e-12)
        assert every[1].labels[-2:] == ["forecast uses", f"slope {f.slope[1]:.6f}"]
        assert f"{f.slope[1]:.6f}" == "1.366666", SPEC

    def test_only_row_1_says_ewc_alone(self, every) -> None:
        scene = every[1]
        alone = [s for s in scene.steps if isinstance(s, Label) and "alone" in s.text]
        assert [s.text for s in alone] == ["short EWC alone, 0 EWA shares"]
        assert alone[0].x < COLUMN_X[1] - 0.3
        assert "alone" not in " ".join(ZERO_LABELS[ZERO_LABELS.index("row 2, 2006-04-27") :])

    def test_its_colours(self, every) -> None:
        scene = every[1]
        for k in range(3):
            assert {s.gid: s.color for s in scene.strokes if s.gid.endswith(f"-{k}")} == {
                f"forecast-{k}": MUTED,
                f"close-{k}": INK,
                f"error-{k}": LOST,
                f"band-high-{k}": ACCENT,
                f"band-low-{k}": ACCENT,
            }
        colours = {
            "forecast": MUTED,
            "close": INK,
            "error": LOST,
            "band": ACCENT,
            "row": MUTED,
        }
        strip = {
            "slope 0 → 1.366666,",
            "after the forecast",
            "forecast uses",
            "slope 1.366666",
        }
        for text in ZERO_LABELS:
            label = _label(scene, text)
            word = text.split()[0]
            if word in colours and text not in strip:
                assert label.color == colours[word], text
        assert _label(scene, "short EWC alone, 0 EWA shares").color == LOST
        assert _label(scene, "+0.74% on 2006-04-27").color == GOOD
        for text in strip:
            assert _label(scene, text).color == INK, text

    def test_every_column_is_drawn_on_one_dollar_scale(self, every, zero) -> None:
        """Each dot, bar end and hairline sits at :func:`dollar_y` of its
        figure, one affine map for all three columns."""
        scene = every[1]
        assert dollar_y(1) - dollar_y(0) == pytest.approx(sketches.PER_DOLLAR)
        for k, row in enumerate(zero.rows):
            x = COLUMN_X[k]
            forecast, close = _stroke(scene, f"forecast-{k}"), _stroke(scene, f"close-{k}")
            bar = _stroke(scene, f"error-{k}")
            assert (forecast.x[0], forecast.y[0]) == pytest.approx(
                (x - DOT_OFFSET, dollar_y(row.forecast))
            )
            assert (close.x[0], close.y[0]) == pytest.approx((x + DOT_OFFSET, dollar_y(row.close)))
            assert bar.x == pytest.approx(np.full(bar.points, x))
            assert (bar.y[0], bar.y[-1]) == pytest.approx(
                (dollar_y(row.forecast), dollar_y(row.close))
            )
            for gid, sign in ((f"band-high-{k}", 1), (f"band-low-{k}", -1)):
                hair = _stroke(scene, gid)
                assert hair.y == pytest.approx(
                    np.full(hair.points, dollar_y(row.forecast + sign * row.band))
                )

    def test_the_band_is_nearly_invisible_beside_rows_1_and_2s_errors(self, every, zero) -> None:
        """On rows 1 and 2 the band's full height is under 2 percent of the bar."""
        for row in zero.rows[:2]:
            assert 2 * row.band < 0.02 * row.error

    def test_the_short_bar_keeps_its_labels_beside_it(self, every, zero) -> None:
        """Row 3's bar is a few pixels tall, so its labels stack downward from
        its close, and each dot sits beside the bar rather than on it."""
        scene, three = every[1], zero.rows[2]
        assert dollar_y(three.close) - dollar_y(three.forecast) < 0.1
        heights = [_label(scene, text).y for text in ZERO_LABELS[14:18]]
        assert heights == sorted(heights, reverse=True)
        assert ZERO_LABELS[14:18] == [
            "close 22.94",
            "error 0.85",
            "band ±0.167334",
            "forecast 22.09",
        ]
        assert _stroke(scene, "forecast-2").x[0] < COLUMN_X[2] < _stroke(scene, "close-2").x[0]

    def test_its_words_follow_the_rows(self) -> None:
        rows = (
            Row("2001-01-02", 0.0, 10.0, 10.0, 0.05, 0.0),
            Row("2001-01-03", 0.0, 10.5, 10.5, 0.1, 0.8),
            Row("2001-01-04", 8.0, 10.25, 2.25, 0.2, 0.9),
        )
        other = ZeroStart(rows, units=1.0, first_return=-0.012, first_return_day="2001-01-03")
        scene = scenes(OneDay.from_run(), other)[1]
        assert _label(scene, "long EWC alone, 0 EWA shares").color == GOOD
        assert _label(scene, "-1.20% on 2001-01-03").color == LOST
        assert "slope 0 → 0.800000," in scene.labels
        assert scene.labels[-2:] == ["forecast uses", "slope 0.800000"]
        assert "forecast 8.00" in scene.labels and "band ±0.200000" in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[1])
        for phrase in (
            "Three columns, the file’s first three rows",
            "a grey dot left of a red bar is the forecast",
            "a black dot right of it is EWC’s close",
            "the red bar runs the whole height",
            "Its two hairlines merge into one short brass tick",
            "Red words under it read",
            "Green words then appear under the first column",
            "the red bar between them is a few pixels tall",
            "The finished drawing holds for twelve seconds.",
        ):
            assert phrase in alt, phrase
        between = alt[alt.index("“row 2, 2006-04-27”") : alt.index("“+0.74%")]
        assert "alone" not in between
