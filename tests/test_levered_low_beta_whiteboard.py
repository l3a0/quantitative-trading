"""The pins for the two whiteboard GIFs in the levered low-beta post, both in Lesson 3.

1. The ruin line sketch draws two levered lines through the point (rf, rf),
   one at June 2001's k and one at the smallest k that ruins June, against a
   floor at −1. What is pinned is that every mark sits where its figure puts
   it under one affine map on each axis: each line's points satisfy
   rf + k × (r − rf), the grey line meets the floor at June's low fifth return
   and the black one at June's ruin line, each drop and tick sits at its
   meeting, and the red dot sits on the black line at June's levered return,
   below the floor. Also pinned are the words it prints and that the black
   line is the steeper.
2. The months sketch draws a bell curve with the low fifth's mean and
   standard deviation, June's line, the curve's tail left of it, and the 83
   months as a strip of dots. What is pinned is the curve's shape and peak,
   that the shading stays left of the line and under the curve, that each dot
   sits at its month's return, that the red ones are exactly the 13 at or
   below the line, and that no two dots in one row touch.

Neither sketch is schematic. The run reads committed vintages, so the tests
read it directly rather than a frozen copy of its figures, and a made-up set
of figures checks that the words follow the data. Every figure the sketches
print is already pinned by ``tests/test_low_beta_leverage.py``, and these
tests pin it again at the precision the sketches draw it.

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
from statistics import NormalDist

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import levered_low_beta_whiteboard as sketches
from chan import low_beta_leverage as llb
from chan import usdcad_tests_whiteboard as whiteboard
from chan.levered_low_beta_whiteboard import (
    AXIS_Y,
    CURVE_HEIGHT,
    DOT_APART,
    LEVERED,
    ROW_STEP,
    RUIN_R,
    RUIN_X,
    RUIN_Y,
    STRIP_TOP,
    TAIL_AXIS_Y,
    TICK,
    Y_TICKS,
    RuinFigures,
    gif_name,
    lev_y,
    main,
    make_levered_low_beta_whiteboards,
    r_x,
    scenes,
    sketch_timeline,
    tail_x,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import INK, LOST, MUTED
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

POST = REPO_ROOT / "blog" / "levered-low-beta-lessons.md"

#: Every GIF in the order :func:`make_levered_low_beta_whiteboards` writes them.
GIFS = ["levered_low_beta_sketch_ruin_line.gif", "levered_low_beta_sketch_months_past.gif"]

#: A fragment of the paragraph each GIF follows. The review round that added
#: the sketches was free to reword both paragraphs' openings, so each is found
#: by words likely to survive that.
RUIN_FRAGMENT = "the line sat at −0.0144"
MONTHS_FRAGMENT = "13 fell at or below June"

RUIN_LABELS = [
    "levered month",
    "0",
    "−1",
    "−2",
    "low fifth’s month",
    "whole capital lost",
    "every line turns on rf = 0.0029",
    "−0.0403",
    "k = 23.2017, the least that ruins June",
    "−0.0144",
    "June’s k = 58.0262",
    "June: −2.5053",
    "steeper line: smaller loss ruins",
]

MONTHS_LABELS = [
    "bell curve: mean 0.0109, sd 0.0292",
    "June’s line, −0.0144",
    "0.1931 of the curve",
    "about one month in five",
    "13 of 83 at or below",
    "the low fifth’s 83 monthly returns",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def portfolios():
    """The run's portfolios on the committed vintages."""
    _, closes, _, spy, _, bills = llb.read_sources()
    return llb.build_portfolios(closes, spy, bills)


@pytest.fixture(scope="module")
def figures(portfolios):
    return RuinFigures.from_portfolios(portfolios)


@pytest.fixture(scope="module")
def every(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, figures, monkeypatch_module):
    monkeypatch_module.setattr(RuinFigures, "from_run", classmethod(lambda cls, d=None: figures))
    return make_levered_low_beta_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


@pytest.fixture(scope="module")
def monkeypatch_module():
    with pytest.MonkeyPatch.context() as patch:
        yield patch


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


def _alt(text: str, scene) -> str:
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


def _r_of(x):
    """The low fifth return at a board position across, the inverse of :func:`r_x`."""
    (r0, r1), (x0, x1) = RUIN_R, RUIN_X
    return r0 + (np.asarray(x) - x0) * (r1 - r0) / (x1 - x0)


def _v_of(y):
    """The levered return at a board height, the inverse of :func:`lev_y`."""
    (v0, v1), (y0, y1) = LEVERED, RUIN_Y
    return v0 + (np.asarray(y) - y0) * (v1 - v0) / (y1 - y0)


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

    def test_each_draws_its_strokes_in_order(self, every) -> None:
        assert [s.gid for s in every[0].strokes] == [
            "y-axis",
            "x-axis",
            "floor",
            "pivot",
            "ruinous",
            "ruinous-drop",
            "asked",
            "asked-drop",
            "month",
        ]
        assert [s.gid for s in every[1].strokes] == [
            "axis",
            "curve",
            "line",
            "tail",
            "months",
            "past",
        ]

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
        """Neither sketch draws a tint today. The months sketch shades its tail
        with red strokes instead. A tint would need the green edge the equity
        seasonals module's ``_tinted`` draws, since the tint alone stands 1.29
        to 1 against the board."""
        assert [fill for scene in every for fill in scene.fills] == []


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
        assert sketches.PACED == ("ruin_line", "months_past")
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
        again = make_levered_low_beta_whiteboards(out_dir=tmp_path)
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
        assert not "low_beta_leverage.png".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.levered_low_beta_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys, figures
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(RuinFigures, "from_run", classmethod(lambda cls, d=None: figures))
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_the_footer_links_the_sketch_code_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        assert f"[the whiteboard sketches]({base}src/chan/levered_low_beta_whiteboard.py)" in footer
        assert (
            f"[what the sketches draw]({base}tests/test_levered_low_beta_whiteboard.py)" in footer
        )

    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (ruin,) = [k for k, p in enumerate(paragraphs) if RUIN_FRAGMENT in p]
        (months,) = [k for k, p in enumerate(paragraphs) if MONTHS_FRAGMENT in p]
        for index, name in zip((ruin, months), GIFS, strict=True):
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_both_sit_in_lesson_3_before_the_chart(self) -> None:
        text = POST.read_text(encoding="utf-8")
        ruin, months = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lesson_3 = text.index("## Lesson 3:")
        chart = text.index("(../docs/figures/low_beta_leverage.png)")
        lesson_4 = text.index("## Lesson 4:")
        assert lesson_3 < ruin < months < chart < lesson_4

    def test_each_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count("(../docs/figures/low_beta_leverage.png)") == 1

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

    def test_the_module_says_neither_is_schematic(self) -> None:
        assert "Neither sketch is schematic." in (sketches.__doc__ or "")


# --- The figures, read from the run ----------------------------------------------


class TestTheFigures:
    def test_the_month_is_the_runs_first_ruin(self, figures, portfolios) -> None:
        first = llb.ruined_months(portfolios)[0]
        assert figures.month == str(first.held_to.date()) == "2001-06-29"
        assert figures.name == "June"
        assert figures.leverage == first.leverage
        assert figures.levered == first.levered

    def test_junes_figures(self, figures) -> None:
        """The figures the round that commissioned the sketches verified, to six places."""
        assert round(figures.rf, 7) == 0.0029083
        assert round(figures.leverage, 6) == 58.026192
        assert round(figures.line, 6) == -0.014375
        assert round(figures.low, 6) == -0.040317
        assert round(figures.levered, 6) == -2.505311
        assert round(figures.ruinous, 6) == 23.201703

    def test_they_agree_with_the_runs_own_helpers(self, figures, portfolios) -> None:
        month = figures.month
        assert figures.line == float(llb.ruin_line(portfolios.rf, portfolios.leverage).loc[month])
        assert figures.ruinous == float(
            llb.ruinous_leverage(portfolios.low, portfolios.rf).loc[month]
        )
        assert figures.returns == tuple(float(r) for r in portfolios.low)

    def test_the_two_lines_meet_minus_1_where_the_post_says(self, figures) -> None:
        """The leverage that ruins June meets −1 at June's own return, and
        June's leverage at June's ruin line."""
        assert figures.rf + figures.ruinous * (figures.low - figures.rf) == pytest.approx(llb.RUIN)
        assert figures.rf + figures.leverage * (figures.line - figures.rf) == pytest.approx(
            llb.RUIN
        )
        assert figures.rf + figures.leverage * (figures.low - figures.rf) == pytest.approx(
            figures.levered
        )

    def test_the_months_figures(self, figures) -> None:
        assert len(figures.returns) == 83
        assert (round(figures.mean, 4), round(figures.sd, 4)) == (0.0109, 0.0292)
        assert figures.sd == pytest.approx(float(np.std(figures.returns, ddof=1)))
        assert figures.reached == 13
        assert round(figures.chance, 4) == 0.1931
        assert figures.chance == NormalDist(figures.mean, figures.sd).cdf(figures.line)

    def test_a_month_exactly_on_the_line_counts(self, figures) -> None:
        """The post says at or below, so a return equal to the line is in."""
        on = replace(figures, returns=(figures.line, figures.line + 0.01))
        assert on.reached == 1


# --- Lesson 3: the ruin line ------------------------------------------------------


class TestTheRuinSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "The ruin line"
        assert every[0].labels == RUIN_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        for gid in ("y-axis", "x-axis", "ruinous", "ruinous-drop", "asked-drop"):
            assert _stroke(scene, gid).color == MUTED, gid
        for gid in ("ruinous-drop", "asked-drop"):
            assert _stroke(scene, gid).dashed, gid
        assert not _stroke(scene, "ruinous").dashed
        for gid in ("floor", "month"):
            assert _stroke(scene, gid).color == LOST, gid
        for gid in ("asked", "pivot"):
            assert _stroke(scene, gid).color == INK, gid
        for text in RUIN_LABELS[:5]:
            assert _label(scene, text).color == MUTED, text
        assert _label(scene, "k = 23.2017, the least that ruins June").color == MUTED
        for text in ("whole capital lost", "June: −2.5053"):
            assert _label(scene, text).color == LOST, text
        for text in (
            "every line turns on rf = 0.0029",
            "−0.0403",
            "−0.0144",
            "June’s k = 58.0262",
            "steeper line: smaller loss ruins",
        ):
            assert _label(scene, text).color == INK, text

    def test_the_axes_scales_differ_by_about_a_hundred(self) -> None:
        """A board unit across is about a hundredth of a board unit up, which is
        why the alt text calls the bottom axis far finer."""
        across = (RUIN_R[1] - RUIN_R[0]) / (RUIN_X[1] - RUIN_X[0])
        up = (LEVERED[1] - LEVERED[0]) / (RUIN_Y[1] - RUIN_Y[0])
        assert 80 < up / across < 130

    def test_each_levered_line_is_rf_plus_k_times_the_excess(self, every, figures) -> None:
        """Every point of each line, read back through the inverse maps, gives
        rf + k × (r − rf) for its own k."""
        scene = every[0]
        for gid, k in (("ruinous", figures.ruinous), ("asked", figures.leverage)):
            stroke = _stroke(scene, gid)
            r, v = _r_of(stroke.x), _v_of(stroke.y)
            assert v == pytest.approx(figures.rf + k * (r - figures.rf), abs=1e-9), gid
            assert r.min() >= RUIN_R[0] - 1e-12 and r.max() <= RUIN_R[1] + 1e-12, gid
            assert v.min() >= LEVERED[0] - 1e-9 and v.max() <= LEVERED[1] + 1e-9, gid

    def test_the_black_line_is_the_steeper(self, every) -> None:
        def slope(stroke):
            return (stroke.y[-1] - stroke.y[0]) / (stroke.x[-1] - stroke.x[0])

        scene = every[0]
        assert slope(_stroke(scene, "asked")) > slope(_stroke(scene, "ruinous")) > 0

    def test_both_lines_pass_through_the_pivot(self, every, figures) -> None:
        scene = every[0]
        pivot = _stroke(scene, "pivot")
        assert (pivot.x[0], pivot.y[0]) == pytest.approx((r_x(figures.rf), lev_y(figures.rf)))
        for gid in ("ruinous", "asked"):
            stroke = _stroke(scene, gid)
            assert stroke.x.min() < pivot.x[0] < stroke.x.max(), gid
            assert np.interp(pivot.x[0], stroke.x, stroke.y) == pytest.approx(pivot.y[0]), gid

    def test_the_floor_is_at_minus_1_across_the_window(self, every) -> None:
        floor = _stroke(every[0], "floor")
        assert set(np.round(floor.y, 12)) == {round(float(lev_y(llb.RUIN)), 12)}
        assert (floor.x.min(), floor.x.max()) == pytest.approx(RUIN_X)

    def test_each_drop_falls_from_its_lines_meeting_with_the_floor(self, every, figures) -> None:
        scene = every[0]
        floor_y = float(lev_y(llb.RUIN))
        for drop, line, r in (
            ("ruinous-drop", "ruinous", figures.low),
            ("asked-drop", "asked", figures.line),
        ):
            x = float(r_x(r))
            stroke = _stroke(scene, drop)
            assert set(np.round(stroke.x, 12)) == {round(x, 12)}, drop
            assert (stroke.y.max(), stroke.y.min()) == pytest.approx((floor_y, AXIS_Y)), drop
            meets = _stroke(scene, line)
            assert np.interp(floor_y, meets.y, meets.x) == pytest.approx(x), line

    def test_each_meeting_has_a_tick_and_its_label_on_the_bottom_axis(self, every, figures) -> None:
        scene = every[0]
        axis = _stroke(scene, "x-axis")
        ticks = sorted(
            {round(float(x), 12) for x, y in zip(axis.x, axis.y, strict=True) if y < AXIS_Y}
        )
        assert ticks == pytest.approx(sorted((r_x(figures.low), r_x(figures.line))))
        for text, r in (("−0.0403", figures.low), ("−0.0144", figures.line)):
            label = _label(scene, text)
            assert (label.x, label.ha) == (pytest.approx(r_x(r)), "center"), text
            assert label.y < AXIS_Y - TICK

    def test_each_y_tick_and_its_label_sit_at_its_value(self, every) -> None:
        scene = every[0]
        axis = _stroke(scene, "y-axis")
        nubs = sorted(
            {round(float(y), 12) for x, y in zip(axis.x, axis.y, strict=True) if x < RUIN_X[0]}
        )
        assert nubs == pytest.approx(sorted(lev_y(v) for v in Y_TICKS))
        for v, text in zip(Y_TICKS, ("0", "−1", "−2"), strict=True):
            assert _label(scene, text).y == pytest.approx(lev_y(v)), text

    def test_the_red_dot_is_junes_month_on_the_black_line_below_the_floor(
        self, every, figures
    ) -> None:
        scene = every[0]
        dot, asked = _stroke(scene, "month"), _stroke(scene, "asked")
        assert dot.points == 1
        assert (dot.x[0], dot.y[0]) == pytest.approx((r_x(figures.low), lev_y(figures.levered)))
        assert np.interp(dot.x[0], asked.x, asked.y) == pytest.approx(dot.y[0])
        assert dot.y[0] < lev_y(llb.RUIN)
        assert dot.x[0] == pytest.approx(_stroke(scene, "ruinous-drop").x[0])
        assert LEVERED[0] < figures.levered

    def test_made_up_figures_move_the_words(self, figures) -> None:
        made_up = replace(
            figures,
            month="2001-09-28",
            rf=0.0021,
            leverage=31.5098,
            line=-0.0296,
            low=-0.0337,
            levered=-1.1278,
            ruinous=27.9461,
        )
        labels = scenes(made_up)[0].labels
        assert "every line turns on rf = 0.0021" in labels
        assert "−0.0337" in labels and "−0.0296" in labels
        assert "k = 27.9461, the least that ruins September" in labels
        assert "September’s k = 31.5098" in labels
        assert "September: −1.1278" in labels

    def test_its_alt_text_says_what_the_picture_shows(self, every, figures) -> None:
        scene = every[0]
        alt = _alt(POST.read_text(encoding="utf-8"), scene)
        assert "a grey axis along the bottom, on a far finer scale" in alt
        assert "A red line across the board at −1" in alt
        assert "A black dot near the top right marks the point every levered line passes" in alt
        pivot = _stroke(scene, "pivot")
        assert pivot.x[0] > np.mean(RUIN_X) and pivot.y[0] > np.mean(RUIN_Y)
        assert "A grey line rises gently through that dot" in alt
        assert "A steeper black line through the same dot meets the red line further right" in alt
        assert _stroke(scene, "asked-drop").x[0] > _stroke(scene, "ruinous-drop").x[0]
        assert "meets the red line further right, nearer zero," in alt
        assert abs(figures.line) < abs(figures.low)
        assert "on the first drop and well below the red line" in alt


# --- Lesson 3: how many months reach June's line ---------------------------------


class TestTheMonthsSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Thirteen of 83 months past June’s line"
        assert every[1].labels == MONTHS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert _stroke(scene, "axis").color == MUTED
        assert _stroke(scene, "curve").color == INK
        for gid in ("line", "tail", "past"):
            assert _stroke(scene, gid).color == LOST, gid
        assert _stroke(scene, "months").color == INK
        for text in MONTHS_LABELS[1:5]:
            assert _label(scene, text).color == LOST, text
        for text in (MONTHS_LABELS[0], MONTHS_LABELS[5]):
            assert _label(scene, text).color == INK, text

    def test_the_curve_is_the_bell_curve_of_the_months(self, every, figures) -> None:
        """Its peak sits over the mean at :data:`CURVE_HEIGHT`, and one standard
        deviation either side it stands at e^(−1/2) of that."""
        curve = _stroke(every[1], "curve")
        r = sketches.TAIL_R[0] + (curve.x - sketches.TAIL_X[0]) * (
            sketches.TAIL_R[1] - sketches.TAIL_R[0]
        ) / (sketches.TAIL_X[1] - sketches.TAIL_X[0])
        z = (r - figures.mean) / figures.sd
        assert curve.y == pytest.approx(TAIL_AXIS_Y + CURVE_HEIGHT * np.exp(-0.5 * z**2))
        assert curve.y.max() <= TAIL_AXIS_Y + CURVE_HEIGHT
        assert curve.x[np.argmax(curve.y)] == pytest.approx(tail_x(figures.mean), abs=0.07)
        for side in (-1, 1):
            at = figures.mean + side * figures.sd
            assert sketches.curve_y(figures, at) == pytest.approx(
                TAIL_AXIS_Y + CURVE_HEIGHT * math.exp(-0.5)
            )

    def test_the_line_sits_at_junes_line(self, every, figures) -> None:
        line = _stroke(every[1], "line")
        assert set(np.round(line.x, 12)) == {round(float(tail_x(figures.line)), 12)}
        dots = _stroke(every[1], "months").y.tolist() + _stroke(every[1], "past").y.tolist()
        assert line.y.min() < min(dots) and line.y.max() > TAIL_AXIS_Y + CURVE_HEIGHT * 0.69

    def test_each_hatch_reaches_the_curve(self, every, figures) -> None:
        """Each upright hatch rises from the axis to the curve itself, not short of it."""
        tail = _stroke(every[1], "tail")
        xs = np.round(tail.x, 9)
        uprights = [x for x in np.unique(xs) if (xs == x).sum() > 2]
        assert len(uprights) >= 10
        (r0, r1), (x0, x1) = sketches.TAIL_R, sketches.TAIL_X
        for x in uprights:
            r = r0 + (x - x0) * (r1 - r0) / (x1 - x0)
            top = float(sketches.curve_y(figures, r))
            assert tail.y[xs == x].max() == pytest.approx(top, abs=1e-9)

    def test_a_month_on_the_line_is_drawn_red(self, figures) -> None:
        """At or below, as the post says, so a return equal to the line is a red dot."""
        on = replace(figures, returns=(*figures.returns, figures.line))
        past = _stroke(scenes(on)[1], "past")
        assert past.points == on.reached == 14
        assert np.isclose(past.x, tail_x(figures.line)).any()

    def test_the_dots_are_drawn_left_to_right(self, every) -> None:
        for gid in ("months", "past"):
            assert np.all(np.diff(_stroke(every[1], gid).x) >= 0), gid

    def test_the_shading_stays_left_of_the_line_and_under_the_curve(self, every, figures) -> None:
        scene = every[1]
        tail = _stroke(scene, "tail")
        assert tail.x.max() < tail_x(figures.line)
        assert tail.y.min() == pytest.approx(TAIL_AXIS_Y)
        tops = tail.y > TAIL_AXIS_Y + 1e-9
        r = sketches.TAIL_R[0] + (tail.x - sketches.TAIL_X[0]) * (
            sketches.TAIL_R[1] - sketches.TAIL_R[0]
        ) / (sketches.TAIL_X[1] - sketches.TAIL_X[0])
        # The pen joins two hatch tops with a straight chord, and the tail is
        # convex, so the chord rides above the curve by under a pixel.
        pixel = 10 / 680  # the board is 10 units across, drawn 680 pixels wide
        assert np.all(tail.y[tops] <= sketches.curve_y(figures, r[tops]) + pixel)
        assert tail.x.max() > tail_x(figures.line) - 0.1

    def test_one_dot_for_each_month_at_its_return(self, every, figures) -> None:
        scene = every[1]
        months, past = _stroke(scene, "months"), _stroke(scene, "past")
        assert months.dots > 0 and past.dots > 0
        assert months.points + past.points == len(figures.returns) == 83
        drawn = sorted(np.concatenate([months.x, past.x]).tolist())
        assert drawn == pytest.approx(sorted(tail_x(np.array(figures.returns)).tolist()))

    def test_the_red_dots_are_the_13_at_or_below_the_line(self, every, figures) -> None:
        scene = every[1]
        months, past = _stroke(scene, "months"), _stroke(scene, "past")
        line_x = float(tail_x(figures.line))
        expected = tail_x(np.array([r for r in figures.returns if r <= figures.line]))
        assert sorted(past.x.tolist()) == pytest.approx(sorted(expected.tolist()))
        assert past.points == figures.reached == 13
        assert past.x.max() <= line_x < months.x.min()

    def test_no_two_dots_in_a_row_touch_and_the_strip_sits_under_the_axis(self, every) -> None:
        scene = every[1]
        xs = np.concatenate([_stroke(scene, g).x for g in ("months", "past")])
        ys = np.concatenate([_stroke(scene, g).y for g in ("months", "past")])
        assert ys.max() == pytest.approx(STRIP_TOP) and STRIP_TOP < TAIL_AXIS_Y
        for y in np.unique(np.round(ys, 9)):
            row = np.sort(xs[np.round(ys, 9) == y])
            assert np.all(np.diff(row) >= DOT_APART - 1e-12), y
        rows = np.round((STRIP_TOP - ys) / ROW_STEP, 9)
        assert np.all(rows == np.round(rows))

    def test_a_dot_moves_down_only_where_the_row_above_is_taken(self) -> None:
        xs = np.array([0.0, 0.05, 0.3, 0.32, 0.34, 1.0])
        assert sketches.strip_rows(xs).tolist() == [0, 1, 0, 1, 2, 0]

    def test_made_up_figures_move_the_words(self, figures) -> None:
        """Dropping two of the months at or below the line changes the count in
        the title and the labels, and the mean, deviation and chance with them."""
        kept = [r for r in figures.returns if r <= figures.line][2:]
        rest = [r for r in figures.returns if r > figures.line]
        made_up = replace(figures, returns=tuple(kept + rest))
        scene = scenes(made_up)[1]
        assert scene.title == "Eleven of 81 months past June’s line"
        assert "11 of 81 at or below" in scene.labels
        assert "the low fifth’s 81 monthly returns" in scene.labels
        curve = f"bell curve: mean {sketches.four(made_up.mean)}, sd {sketches.four(made_up.sd)}"
        assert curve in scene.labels
        assert f"{sketches.four(made_up.chance)} of the curve" in scene.labels
        assert made_up.chance != figures.chance
        rare = replace(made_up, returns=tuple(r + 0.03 for r in made_up.returns))
        assert "about one month in" in scenes(rare)[1].labels[3]
        assert scenes(rare)[1].labels[3] != "about one month in five"

    def test_its_alt_text_says_what_the_picture_shows(self, every, figures) -> None:
        scene = every[1]
        alt = _alt(POST.read_text(encoding="utf-8"), scene)
        assert "a black bell curve rises from it" in alt
        assert "A red upright line left of the curve’s peak" in alt
        assert tail_x(figures.line) < tail_x(figures.mean)
        assert "The part of the curve left of it is shaded with red upright strokes" in alt
        assert "Under the axis sit dots, one for each month, in order of return" in alt
        assert "stacked in short columns where they would overlap" in alt
        ys = np.concatenate([_stroke(scene, g).y for g in ("months", "past")])
        assert len(np.unique(np.round(ys, 9))) > 1
        assert "The dots right of the red line come first, in black" in alt
        assert "Then the dots at or left of it appear in red" in alt
        steps = [s for s in scene.steps if not isinstance(s, Label)]
        gids = [s.gid for s in steps]
        assert gids.index("months") < gids.index("past")
