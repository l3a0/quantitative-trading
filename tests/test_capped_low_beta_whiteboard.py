"""The pins for the whiteboard GIF in the capped low-beta post, in Lesson 5.

1. The break-even sketch draws each ceiling's yearly gap falling to 0 as a
   borrowing spread is charged, the black line at a ceiling of 2 and the brass
   line at 5. What is pinned is that every mark sits where its figure puts it
   under one affine map on each axis: each line runs straight from its gap at
   no spread to 0 at its break-even spread, each drop and tick sits at its
   break-even, and the zero line sits at a gap of 0. Also pinned are the words
   it prints, that the brass line falls about two and a half times as steeply
   and reaches 0 first, and that it passes under the black line before either
   reaches 0, a crossing the sketch leaves unlabelled.

The sketch is not schematic. The run reads committed vintages, so the tests
read it directly rather than a frozen copy of its figures, and a made-up set
of figures checks that the words follow the data. Every figure the sketch
prints is already pinned by ``tests/test_low_beta_capped.py`` at four places.
These tests pin it again at six, so a re-pin says which figure moved, though
the sketch prints four.

- **Vintages.** ``spx_20071123/``, the 500 stocks lifted from Chan's
  ``SPX_20071123.mat``, chan-mat adjusted, saved 2007-11-24. ``spy_chan.csv``,
  chan-xls adjusted, saved 2008-01-29. FRED's TB3MS, downloaded 2026-09-30.
- **Specification.** Entry 48's, as ``tests/test_low_beta_capped.py`` states
  it: Entry 45's portfolios unchanged, the low fifth levered by min(k, C) at
  the bill rate for C of 2 and 5, and d against the unlevered high fifth from
  December 2000 to October 2007. Every figure is exploratory and comes from a
  file built from survivors.

The lines are drawn straight between the run's endpoints, and one test holds
that the run's own charged gap departs from each straight line by under half a
pixel.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, the GIF's size, frames, loop and timing, its
slower pace, that two draws give the same bytes, and that the committed GIF is
a fresh draw, a comparison that runs only on macOS arm64 with Comic Sans MS,
as ``tests/test_usdcad_tests_whiteboard.py`` explains. The check that
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

from chan import capped_low_beta_whiteboard as sketches
from chan import low_beta_capped as lbc
from chan import low_beta_leverage as llb
from chan import usdcad_tests_whiteboard as whiteboard
from chan.capped_low_beta_whiteboard import (
    GAP,
    GAP_Y,
    SPREAD,
    SPREAD_X,
    TICK,
    BreakEvenFigures,
    CeilingLine,
    amount,
    g_y,
    gif_name,
    main,
    make_capped_low_beta_whiteboards,
    s_x,
    scenes,
    sketch_timeline,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, INK, MUTED
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

POST = REPO_ROOT / "blog" / "capped-low-beta-lessons.md"

#: Every GIF in the order :func:`make_capped_low_beta_whiteboards` writes them.
GIFS = ["capped_low_beta_sketch_break_even.gif"]

#: The opening words of the paragraph the GIF follows, and of the one after it.
BREAK_EVEN_FRAGMENT = "The run searched for the spread at which the gap’s point estimate"
NEXT_FRAGMENT = "Two cautions"

BREAK_EVEN_LABELS = [
    "gap a year",
    "yearly borrowing spread",
    "0",
    "ceiling 2: 0.0934",
    "borrows 1 per unit of capital",
    "0.0946",
    "ceiling 5: 0.1659",
    "borrows 2.5134",
    "0.0661",
    "steeper line: smaller spread erases it",
]

#: The unpatched read, kept before the ``gifs`` fixture and the command's test
#: patch :meth:`BreakEvenFigures.from_run` for speed, so a test can still run it.
FROM_RUN = BreakEvenFigures.from_run

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4

#: Board units up to pixels, the board's height in pixels over its height in units.
PX_PER_UNIT = HEIGHT / (whiteboard.YLIM[1] - whiteboard.YLIM[0])


@pytest.fixture(scope="module")
def portfolios():
    """The run's portfolios on the committed vintages."""
    _, closes, _, spy, _, bills = llb.read_sources()
    return llb.build_portfolios(closes, spy, bills)


@pytest.fixture(scope="module")
def figures(portfolios):
    return BreakEvenFigures.from_portfolios(portfolios)


@pytest.fixture(scope="module")
def every(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def monkeypatch_module():
    with pytest.MonkeyPatch.context() as patch:
        yield patch


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, figures, monkeypatch_module):
    monkeypatch_module.setattr(
        BreakEvenFigures, "from_run", classmethod(lambda cls, d=None: figures)
    )
    return make_capped_low_beta_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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


def _s_of(x):
    """The yearly spread at a board position across, the inverse of :func:`s_x`."""
    (s0, s1), (x0, x1) = SPREAD, SPREAD_X
    return s0 + (np.asarray(x) - x0) * (s1 - s0) / (x1 - x0)


def _g_of(y):
    """The yearly gap at a board height, the inverse of :func:`g_y`."""
    (g0, g1), (y0, y1) = GAP, GAP_Y
    return g0 + (np.asarray(y) - y0) * (g1 - g0) / (y1 - y0)


def _distance(stroke, label) -> float:
    """How far a label's anchor sits from a straight stroke, in board units."""
    t = np.linspace(0.0, 1.0, 2001)
    x = stroke.x[0] + t * (stroke.x[-1] - stroke.x[0])
    y = stroke.y[0] + t * (stroke.y[-1] - stroke.y[0])
    return float(np.min(np.hypot(x - label.x, y - label.y)))


def _lines(figures):
    return (("low", figures.low), ("high", figures.high))


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_is_one_in_the_order_the_post_reads_it(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

    def test_it_draws_its_strokes_in_order(self, every) -> None:
        assert [s.gid for s in every[0].strokes] == [
            "gap-axis",
            "spread-axis",
            "zero",
            "low",
            "low-drop",
            "high",
            "high-drop",
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
        """The sketch draws no tint today. A tint would need the green edge the
        equity seasonals module's ``_tinted`` draws, since the tint alone stands
        1.29 to 1 against the board."""
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

    def test_it_builds_slowly_and_holds_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("break_even",)
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
            plain = timeline(scene)
            for k, frame in enumerate(frames[:-1]):
                if frame not in labels:
                    assert frame.ms == plain[k].ms, (scene.slug, k)

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_capped_low_beta_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_chart(self) -> None:
        """No chart or sibling GIF starts like this one, so the prefix check above
        reads only this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert not "low_beta_capped.png".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.capped_low_beta_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys, figures
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(BreakEvenFigures, "from_run", classmethod(lambda cls, d=None: figures))
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_the_footer_links_the_sketch_code_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        assert f"[the whiteboard sketch]({base}src/chan/capped_low_beta_whiteboard.py)" in footer
        assert f"[what the sketch draws]({base}tests/test_capped_low_beta_whiteboard.py)" in footer

    def test_the_gif_follows_the_paragraph_it_draws(self) -> None:
        """Right after the paragraph that finds the break-even spreads, and right
        before the one that opens on the two cautions."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (found,) = [k for k, p in enumerate(paragraphs) if p.startswith(BREAK_EVEN_FRAGMENT)]
        embed = paragraphs[found + 1]
        assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", embed)
        assert paragraphs[found + 2].startswith(NEXT_FRAGMENT)

    def test_it_sits_in_lesson_5(self) -> None:
        text = POST.read_text(encoding="utf-8")
        embed = text.index(f"(../docs/figures/{GIFS[0]})")
        assert text.index("## Lesson 5:") < embed < text.index("## What this test cannot say")

    def test_the_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count("(../docs/figures/low_beta_capped.png)") == 1

    def test_the_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_the_alt_text_says_it_is_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "drawn slowly" in alt, scene.slug
            assert "twelve seconds" in alt, scene.slug

    def test_the_module_says_it_is_not_schematic(self) -> None:
        assert "The sketch is not schematic." in (sketches.__doc__ or "")


# --- The figures, read from the run ----------------------------------------------


class TestTheFigures:
    def test_the_redraw_reads_the_same_figures_from_the_committed_vintages(
        self, figures, tmp_path
    ) -> None:
        """The path ``main`` and :func:`scenes` take by default, run unpatched,
        and the data folder it is handed reaches the read."""
        assert FROM_RUN() == figures
        with pytest.raises(VintageUnavailable):
            FROM_RUN(tmp_path)

    def test_they_are_the_two_ceilings_in_order(self, figures) -> None:
        assert (figures.low.ceiling, figures.high.ceiling) == lbc.CEILINGS == (2.0, 5.0)

    def test_the_runs_figures(self, figures) -> None:
        """The figures Lesson 5 and Lesson 3 quote, to six places."""
        assert round(figures.low.gap, 6) == 0.093436
        assert round(figures.high.gap, 6) == 0.16593
        assert round(figures.low.spread, 6) == 0.09457
        assert round(figures.high.spread, 6) == 0.066134
        assert figures.low.borrowed == 1.0
        assert round(figures.high.borrowed, 6) == 2.51339

    def test_they_agree_with_the_runs_own_helpers(self, figures, portfolios) -> None:
        for line in (figures.low, figures.high):
            capped = lbc.cap(portfolios, line.ceiling)
            assert line.gap == lbc.capped(portfolios, line.ceiling).gap
            assert line.spread == lbc.break_even_spread(capped)
            assert line.borrowed == float(capped.leverage.mean()) - 1

    def test_each_spread_brings_the_charged_gap_to_0(self, figures, portfolios) -> None:
        for line in (figures.low, figures.high):
            capped = lbc.cap(portfolios, line.ceiling)
            assert lbc.charged_gap(capped, 0.0) == pytest.approx(line.gap, abs=1e-12)
            assert lbc.charged_gap(capped, line.spread) == pytest.approx(0.0, abs=1e-9)

    def test_a_straight_line_is_faithful_to_the_charged_gap(self, figures, portfolios) -> None:
        """Across each line's span the run's charged gap sits within 0.0005 a
        year of the straight line, under half a pixel on the board, which is
        what lets the sketch draw each line straight between its endpoints.
        The largest departure is about 0.00034, at a ceiling of 5 near the
        middle of its span, as the module docstring says."""
        pixel = (GAP[1] - GAP[0]) / ((GAP_Y[1] - GAP_Y[0]) * PX_PER_UNIT)
        worst = {}
        for line in (figures.low, figures.high):
            capped = lbc.cap(portfolios, line.ceiling)
            spreads = np.linspace(0.0, line.spread, 21)
            departures = np.array(
                [
                    abs(lbc.charged_gap(capped, s) - line.gap * (1 - s / line.spread))
                    for s in spreads
                ]
            )
            assert departures.max() < 0.0005, line.ceiling
            assert departures.max() < pixel / 2, line.ceiling
            worst[line.ceiling] = (departures.max(), spreads[departures.argmax()] / line.spread)
        assert round(worst[5.0][0], 5) == 0.00034
        assert worst[5.0][1] == pytest.approx(0.5)
        assert worst[2.0][0] < worst[5.0][0]

    def test_the_brass_line_falls_about_two_and_a_half_times_as_steeply(self, figures) -> None:
        assert round(figures.high.slope / figures.low.slope, 1) == 2.5

    def test_the_brass_line_reaches_0_first_and_crosses_the_black_one_before(self, figures) -> None:
        """The larger lead breaks even at the smaller spread, so the two lines
        cross at a spread below both break-evens and a gap above 0."""
        low, high = figures.low, figures.high
        assert high.gap > low.gap and high.spread < low.spread
        crossing = (high.gap - low.gap) / (high.slope - low.slope)
        assert 0 < crossing < high.spread
        assert low.gap - low.slope * crossing > 0

    def test_a_ceiling_with_no_lead_refuses(self, portfolios) -> None:
        """A line needs a gap above 0 to break even from, so a ceiling whose gap
        is 0 or below at no spread raises rather than drawing a line to nowhere."""
        losing = replace(portfolios, low=portfolios.low - 0.2)
        with pytest.raises(ValueError, match="0 or below with no spread"):
            CeilingLine.from_portfolios(losing, 2.0)

    def test_amount_prints_a_whole_number_as_a_digit(self) -> None:
        assert (amount(1.0), amount(2.0), amount(2.5133899)) == ("1", "2", "2.5134")


# --- Lesson 5: who breaks even first ---------------------------------------------


class TestTheBreakEvenSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "Who breaks even first"
        assert every[0].labels == BREAK_EVEN_LABELS

    def test_each_label_names_the_stroke_it_describes(self, every) -> None:
        named = [(s.text, s.names) for s in every[0].steps if isinstance(s, Label)]
        assert [names for _, names in named] == [
            "gap-axis",
            "spread-axis",
            "zero",
            "low",
            "low",
            "low-drop",
            "high",
            "high",
            "high-drop",
            "high",
        ]

    def test_its_colours(self, every) -> None:
        scene = every[0]
        for gid in ("gap-axis", "spread-axis", "zero", "low-drop", "high-drop"):
            assert _stroke(scene, gid).color == MUTED, gid
        for gid in ("low-drop", "high-drop"):
            assert _stroke(scene, gid).dashed, gid
        for gid in ("low", "high", "zero"):
            assert not _stroke(scene, gid).dashed, gid
        assert _stroke(scene, "low").color == INK
        assert _stroke(scene, "high").color == ACCENT
        for text in BREAK_EVEN_LABELS[:3]:
            assert _label(scene, text).color == MUTED, text
        for text in BREAK_EVEN_LABELS[3:6]:
            assert _label(scene, text).color == INK, text
        for text in BREAK_EVEN_LABELS[6:]:
            assert _label(scene, text).color == ACCENT, text

    def test_each_line_runs_straight_from_its_gap_to_0_at_its_spread(self, every, figures) -> None:
        """Every point of each line, read back through the inverse maps, sits on
        the straight line from (0, gap) to (spread, 0)."""
        scene = every[0]
        for gid, line in _lines(figures):
            stroke = _stroke(scene, gid)
            s, g = _s_of(stroke.x), _g_of(stroke.y)
            assert (s[0], g[0]) == pytest.approx((0.0, line.gap), abs=1e-12), gid
            assert (s[-1], g[-1]) == pytest.approx((line.spread, 0.0), abs=1e-12), gid
            assert g == pytest.approx(line.gap * (1 - s / line.spread), abs=1e-12), gid

    def test_the_brass_line_is_the_steeper_on_the_board(self, every) -> None:
        def slope(stroke):
            return (stroke.y[-1] - stroke.y[0]) / (stroke.x[-1] - stroke.x[0])

        scene = every[0]
        assert slope(_stroke(scene, "high")) < slope(_stroke(scene, "low")) < 0
        assert _stroke(scene, "high").x.max() < _stroke(scene, "low").x.max()

    def test_the_lines_cross_unlabelled_before_either_reaches_0(self, every, figures) -> None:
        """The brass line starts above the black one and ends left of it on the
        zero line, so it passes under it on the way. No label names the crossing
        or prints a figure for it, since the post states none."""
        scene = every[0]
        low, high = _stroke(scene, "low"), _stroke(scene, "high")
        xs = np.linspace(SPREAD_X[0], high.x.max(), 400)
        above = np.interp(xs, high.x, high.y) - np.interp(xs, low.x, low.y)
        assert above[0] > 0 and above[-1] < 0
        assert np.count_nonzero(np.diff(np.sign(above))) == 1
        at = xs[np.argmax(above < 0)]
        crossing = Label("", float(at), float(np.interp(at, low.x, low.y)), names="low")
        for label in scene.steps:
            if isinstance(label, Label):
                assert np.hypot(label.x - crossing.x, label.y - crossing.y) > 0.6, label.text
        printed = {sketches.four(line.gap) for _, line in _lines(figures)}
        printed |= {sketches.four(line.spread) for _, line in _lines(figures)}
        numbers = {n for text in scene.labels for n in re.findall(r"\d\.\d{4}", text)}
        assert numbers <= printed | {sketches.four(figures.high.borrowed)}

    def test_the_zero_line_is_at_a_gap_of_0_across_the_window(self, every) -> None:
        zero = _stroke(every[0], "zero")
        assert set(np.round(zero.y, 12)) == {round(float(g_y(0.0)), 12)}
        assert (zero.x.min(), zero.x.max()) == pytest.approx(SPREAD_X)
        assert _label(every[0], "0").y == pytest.approx(g_y(0.0))

    def test_the_window_holds_both_lines(self, figures) -> None:
        for _, line in _lines(figures):
            assert GAP[0] < 0 < line.gap < GAP[1]
            assert SPREAD[0] == 0 < line.spread < SPREAD[1]

    def test_each_drop_falls_from_its_break_even_to_the_spread_axis(self, every, figures) -> None:
        scene = every[0]
        for drop, gid, line in (
            ("low-drop", "low", figures.low),
            ("high-drop", "high", figures.high),
        ):
            x = float(s_x(line.spread))
            stroke = _stroke(scene, drop)
            assert set(np.round(stroke.x, 12)) == {round(x, 12)}, drop
            assert (stroke.y.max(), stroke.y.min()) == pytest.approx((g_y(0.0), GAP_Y[0])), drop
            ends = _stroke(scene, gid)
            assert (ends.x[-1], ends.y[-1]) == pytest.approx((x, g_y(0.0))), gid

    def test_each_break_even_has_a_tick_and_its_label_on_the_spread_axis(
        self, every, figures
    ) -> None:
        scene = every[0]
        axis = _stroke(scene, "spread-axis")
        ticks = sorted(
            {round(float(x), 12) for x, y in zip(axis.x, axis.y, strict=True) if y < GAP_Y[0]}
        )
        assert ticks == pytest.approx(sorted(s_x([figures.low.spread, figures.high.spread])))
        assert axis.y.min() == pytest.approx(GAP_Y[0] - TICK)
        for text, line in (("0.0946", figures.low), ("0.0661", figures.high)):
            label = _label(scene, text)
            assert (label.x, label.ha) == (pytest.approx(s_x(line.spread)), "center"), text
            assert label.y < GAP_Y[0] - TICK

    def test_each_ceilings_label_sits_at_its_gap_left_of_the_axis(self, every, figures) -> None:
        scene = every[0]
        for text, line in (("ceiling 2: 0.0934", figures.low), ("ceiling 5: 0.1659", figures.high)):
            label = _label(scene, text)
            assert label.y == pytest.approx(g_y(line.gap)), text
            assert (label.ha, label.x < SPREAD_X[0]) == ("right", True), text

    def test_each_borrowing_label_sits_beside_its_own_line(self, every) -> None:
        """Nearer its own line than the other, so position names the line as
        well as colour does."""
        scene = every[0]
        low, high = _stroke(scene, "low"), _stroke(scene, "high")
        for text, own, other in (
            ("borrows 1 per unit of capital", low, high),
            ("borrows 2.5134", high, low),
        ):
            label = _label(scene, text)
            assert _distance(own, label) < _distance(other, label), text

    def test_made_up_figures_move_the_words(self, figures) -> None:
        made_up = replace(
            figures,
            low=replace(figures.low, ceiling=1.5, gap=0.0712, spread=0.0583, borrowed=1.5),
            high=replace(figures.high, ceiling=4.0, gap=0.1204, spread=0.0412, borrowed=3.0),
        )
        labels = scenes(made_up)[0].labels
        assert "ceiling 1.5: 0.0712" in labels and "ceiling 4: 0.1204" in labels
        assert "borrows 1.5000 per unit of capital" in labels
        assert "borrows 3" in labels
        assert "0.0583" in labels and "0.0412" in labels

    def test_its_alt_text_says_what_the_picture_shows(self, every, figures) -> None:
        scene = every[0]
        alt = _alt(POST.read_text(encoding="utf-8"), scene)
        assert "A grey line across the board just above the bottom axis" in alt
        assert g_y(0.0) > GAP_Y[0]
        assert "A black line starts on the upright axis" in alt
        assert "falls gently to the zero line" in alt
        assert "a dashed grey drop falls to the bottom axis" in alt
        assert "a second dashed drop" in alt
        for gid in ("low-drop", "high-drop"):
            assert _stroke(scene, gid).dashed and _stroke(scene, gid).color == MUTED, gid
        assert "A brass line starts higher" in alt
        assert figures.high.gap > figures.low.gap
        assert "about two and a half times as steeply" in alt
        assert "passes under the black line partway across" in alt
        assert "reaches the zero line first, further left" in alt
        assert figures.high.spread < figures.low.spread
