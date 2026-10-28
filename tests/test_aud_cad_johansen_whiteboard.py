"""The pins for the two whiteboard GIFs in the AUD.USD against CAD.USD post.

One sketches Lesson 2's reason a constant scale on one leg's closes moves no
return, and one Lesson 4's reading of the share the chart's top panel plots.
The figures they print come from the run on Chan's committed files, and the
tests here read that run rather than a copy of its figures. The vintage and the
specification are the ones ``tests/test_aud_cad_johansen.py`` states, and a
re-pin there moves the figures pinned in :class:`TestTheFigures`.

The scale sketch is schematic apart from its two scales and its count of
returns. The share sketch draws the last day's hedge from the run and the two
other cases, a spread and a hedge held both ways, as schematic bars.

What is pinned for each sketch:

1. Its words, in order, and the ink of each mark.
2. Where each mark stands: the doubled bars twice the plain ones, the last
   day's dollars to scale, the dot and the dashed mark at their shares on the
   line, and the band from 0 to 1 with its edge.
3. That other figures move the words and the marks, and that figures the
   words would misdescribe are refused.
4. That no label touches a line, leaves the board or touches another label,
   in the installed hand font and in the wider fallback.
5. Each file's size, frame count, loop, timing and palette, and that it sits in
   the post right after the text it draws, with an alt text quoting its labels.

Two draws on one machine give the same bytes. Whether a committed GIF equals a
fresh draw depends on the font, as ``tests/test_usdcad_tests_whiteboard.py``
explains, so that comparison runs only on macOS arm64 with Comic Sans MS.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import platform
import re

import matplotlib
import numpy as np
import pandas as pd
import pytest
from PIL import Image

from chan import aud_cad_johansen as johansen
from chan import aud_cad_johansen_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.aud_cad_johansen import aud_cad, cross_rates, read_sources
from chan.aud_cad_johansen_whiteboard import (
    AXIS_Y,
    CLOSES_BASE,
    DOLLARS_LENGTH,
    DOLLARS_X,
    DOUBLED_X,
    GIF_PREFIX,
    PACED,
    PACED_HOLD_MS,
    PLAIN_X,
    SHARE_X,
    RunFigures,
    gif_name,
    main,
    make_aud_cad_johansen_whiteboards,
    scenes,
    share_x,
    sketch_timeline,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    HOLD_MS,
    REJECT_TINT,
    TINT,
    TITLE_MS,
    WIDTH,
    Frame,
    Label,
    clearances,
    hand_font,
)

POST = REPO_ROOT / "blog" / "aud-cad-johansen-lessons.md"

TITLES = ["Doubling a price changes no return", "What the top panel’s share means"]
GIFS = ["aud_cad_johansen_no_return_moves.gif", "aud_cad_johansen_share.gif"]

CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4

LABELS = [
    [
        "yesterday",
        "today",
        "AUD.USD",
        "× 2",
        "yesterday",
        "today",
        "AUD.USD × 2",
        "today ÷ yesterday:",
        "the same percent change",
        "the weight w halves:",
        "w × close = (w ÷ 2) × (2 × close),",
        "the same dollars held",
        "every return identical",
        "AUD.USD × 2, CAD.USD × 0.37: all 612 still match",
    ],
    [
        "AUD.USD: 1 unit × its close, long",
        "CAD.USD: −0.7797 units × its close, short",
        "the last day, 2012-04-26: 1 to −0.7622 in dollars",
        "−1",
        "0",
        "1",
        "CAD.USD’s share, −0.4325",
        "AUD.USD long",
        "CAD.USD short",
        "at −0.5, equal dollars",
        "against each other:",
        "a spread",
        "held the same way",
        "CAD.USD short",
        "AUD.USD short",
        "long both, or short both:",
        "a bet on the US dollar",
    ],
]
#: The ink of each label, in the order of :data:`LABELS`: green for what is
#: bought or checks out, red for what is shorted or held the same way, grey for
#: context, brass for the doubling and the closing words and for the last day.
LABEL_INKS = [
    [MUTED, MUTED, INK, ACCENT, MUTED, MUTED, INK, INK, GOOD, INK, INK, GOOD, GOOD, ACCENT],
    [GOOD, LOST, ACCENT, MUTED, MUTED, MUTED, ACCENT, GOOD, LOST, INK, INK, INK]
    + [LOST, LOST, LOST, LOST, LOST],
]
STROKE_INKS = [
    {
        "plain-yesterday": INK,
        "plain-today": INK,
        "times": ACCENT,
        "doubled-yesterday": INK,
        "doubled-today": INK,
        "same-change": GOOD,
        "same-dollars": GOOD,
        "same-return": GOOD,
    },
    {
        "aud-dollars": GOOD,
        "cad-dollars": LOST,
        "axis": MUTED,
        "last-day": ACCENT,
        "equal": MUTED,
        "spread-aud": GOOD,
        "spread-cad": LOST,
        "same-way-edge": LOST,
        "same-base": MUTED,
        "same-cad": LOST,
        "same-aud": LOST,
    },
]
STROKES = [
    [
        "plain-yesterday",
        "plain-today",
        "times",
        "doubled-yesterday",
        "doubled-today",
        "same-change",
        "same-dollars",
        "same-return",
    ],
    [
        "aud-dollars",
        "cad-dollars",
        "axis",
        "last-day",
        "equal",
        "spread-aud",
        "spread-cad",
        "same-way-edge",
        "same-base",
        "same-cad",
        "same-aud",
    ],
]
#: Each bar's stroke and the label that names it: its currency and its side.
BARS = {
    "spread-aud": ("AUD.USD long", GOOD),
    "spread-cad": ("CAD.USD short", LOST),
    "same-cad": ("CAD.USD short", LOST),
    "same-aud": ("AUD.USD short", LOST),
}

#: Made-up figures, a last day nearer a spread and a smaller scale on CAD.USD,
#: to show that the words and the marks follow the figures rather than the run.
MOVED = RunFigures(
    last_day=pd.Timestamp("2015-06-30"),
    cad_units=-0.9123456,
    cad_dollars=-0.8765432,
    share=-0.8765432 / 1.8765432,
    test_days=500,
    scales=(2.0, 0.5),
)


@pytest.fixture(scope="module")
def result():
    sources = read_sources()
    return aud_cad(cross_rates(sources.audusd[1], sources.usdcad[1]))


@pytest.fixture(scope="module")
def figures(result) -> RunFigures:
    return RunFigures.from_run(result)


@pytest.fixture(scope="module")
def drawn(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def frames(drawn):
    return [sketch_timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, figures):
    return make_aud_cad_johansen_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), figures=figures
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _labels(scene, names):
    return [s for s in scene.steps if isinstance(s, Label) and s.names == names]


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


def _alt(scene) -> str:
    text = POST.read_text(encoding="utf-8")
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    return match.group(1)


def _length(stroke) -> float:
    return float(math.hypot(stroke.x[-1] - stroke.x[0], stroke.y[-1] - stroke.y[0]))


class TestTheFigures:
    """The run's figures the sketches print, at the values the run's own pins hold."""

    def test_the_last_days_hedge_and_share_are_the_runs(self, figures) -> None:
        assert figures.last_day == pd.Timestamp("2012-04-26")
        assert figures.cad_units == pytest.approx(-0.7796733233, abs=1e-10)
        assert figures.cad_dollars == pytest.approx(-0.7622442800, abs=1e-10)
        assert figures.share == pytest.approx(-0.4325417813, abs=1e-10)

    def test_the_share_is_the_dollar_ratio_over_the_gross(self, figures) -> None:
        """1 to −0.7622 in dollars is a share of −0.7622 over 1.7622."""
        ratio = figures.cad_dollars
        assert figures.share == pytest.approx(ratio / (1 + abs(ratio)), abs=1e-12)

    def test_the_scales_are_the_ones_the_runs_test_puts_on_the_legs(self, figures) -> None:
        assert figures.scales == johansen.SCALE_CHECK == (2.0, 0.37)
        assert figures.test_days == 612


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, drawn) -> None:
        assert [scene.title for scene in drawn] == TITLES

    def test_each_has_its_own_gif_named_for_it(self, drawn) -> None:
        assert [gif_name(scene) for scene in drawn] == GIFS
        assert all(name.startswith(GIF_PREFIX) for name in GIFS)

    def test_each_draws_its_strokes_in_order(self, drawn) -> None:
        assert [[s.gid for s in scene.strokes] for scene in drawn] == STROKES

    def test_each_says_what_it_should(self, drawn) -> None:
        assert [scene.labels for scene in drawn] == LABELS

    def test_each_label_and_stroke_is_in_the_ink_its_meaning_calls_for(self, drawn) -> None:
        for scene, labels, strokes in zip(drawn, LABEL_INKS, STROKE_INKS, strict=True):
            found = [s.color for s in scene.steps if isinstance(s, Label)]
            assert list(zip(scene.labels, found, strict=True)) == list(
                zip(scene.labels, labels, strict=True)
            ), scene.slug
            assert {s.gid: s.color for s in scene.strokes} == strokes, scene.slug

    def test_every_label_names_a_stroke_drawn_before_it(self, drawn) -> None:
        for scene in drawn:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if not isinstance(s, Label)]
                    assert step.names in earlier, (scene.title, step.text)

    def test_no_label_is_parsed_as_math(self, drawn) -> None:
        assert not [s.text for scene in drawn for s in scene.steps if getattr(s, "math", 0)]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, drawn) -> None:
        for scene in drawn:
            for stroke in scene.strokes:
                assert stroke.points >= stroke.frames, (scene.title, stroke.gid)

    def test_every_pale_tint_has_an_edge_in_its_own_ink(self, drawn) -> None:
        """The tint alone stands 1.29 to 1 against the white board, under WCAG
        2.1's 3 to 1 for a graphical object, so each tint gets a box round it in
        the ink it is a blend of: green round the green tint, red round the red."""
        own = {TINT: GOOD, REJECT_TINT: LOST}
        fills = [(scene, fill) for scene in drawn for fill in scene.fills]
        assert [fill.color for _, fill in fills] == [REJECT_TINT]
        for scene, fill in fills:
            edge = _stroke(scene, f"{fill.gid}-edge")
            assert edge.color == own[fill.color]
            assert (edge.x.min(), edge.x.max()) == pytest.approx((fill.x0, fill.x1))
            assert (edge.y.min(), edge.y.max()) == pytest.approx((fill.y0, fill.y1))
            assert scene.steps.index(edge) == scene.steps.index(fill) + 1

    def test_every_bar_carries_its_currency_and_its_side(self, drawn) -> None:
        """Green and red look alike to a reader with red-green colour blindness,
        so each bar's words name the currency and whether it is long or short,
        and the side matches the bar's ink."""
        share = drawn[1]
        for gid, (words, ink) in BARS.items():
            (label,) = _labels(share, gid)
            assert (label.text, label.color, _stroke(share, gid).color) == (words, ink, ink)
        for gid, side in (("aud-dollars", "long"), ("cad-dollars", "short")):
            label = _labels(share, gid)[0]
            assert label.text.startswith(gid[:3].upper() + ".USD:") and label.text.endswith(side)


class TestNoReturnMoves:
    def test_the_doubled_bars_are_twice_the_plain_ones_on_one_baseline(self, drawn) -> None:
        scene = drawn[0]
        for day, plain_x, doubled_x in zip(("yesterday", "today"), PLAIN_X, DOUBLED_X, strict=True):
            plain, doubled = _stroke(scene, f"plain-{day}"), _stroke(scene, f"doubled-{day}")
            assert plain.y[0] == doubled.y[0] == CLOSES_BASE
            assert set(plain.x) == {plain_x} and set(doubled.x) == {doubled_x}
            assert _length(doubled) == pytest.approx(2 * _length(plain), rel=1e-12)
        assert _length(_stroke(scene, "plain-today")) > _length(_stroke(scene, "plain-yesterday"))

    def test_the_closing_words_follow_the_figures(self) -> None:
        labels = scenes(MOVED)[0].labels
        assert labels[-1] == "AUD.USD × 2, CAD.USD × 0.5: all 500 still match"

    def test_a_scale_other_than_2_on_aud_usd_is_refused(self, figures) -> None:
        """The title says the price doubles, which another scale would make false."""
        with pytest.raises(ValueError, match="says it doubles"):
            scenes(dataclasses.replace(figures, scales=(3.0, 0.37)))


class TestTheShare:
    def test_the_line_runs_from_minus_1_to_1_to_scale(self, drawn) -> None:
        axis = _stroke(drawn[1], "axis")
        assert (axis.x.min(), axis.x.max()) == SHARE_X
        assert set(axis.y) == {AXIS_Y}
        assert (share_x(-1.0), share_x(0.0), share_x(1.0)) == (
            SHARE_X[0],
            sum(SHARE_X) / 2,
            SHARE_X[1],
        )
        ticks = {s.text: s.x for s in _labels(drawn[1], "axis")}
        assert ticks == {"−1": share_x(-1.0), "0": share_x(0.0), "1": share_x(1.0)}

    def test_the_last_days_dot_sits_at_its_share_on_the_line(self, drawn, figures) -> None:
        dot = _stroke(drawn[1], "last-day")
        assert (dot.x[0], dot.y[0]) == (pytest.approx(share_x(figures.share)), AXIS_Y)
        (words,) = _labels(drawn[1], "last-day")
        assert words.x == dot.x[0]

    def test_the_last_days_bars_are_its_dollars_to_scale(self, drawn, figures) -> None:
        aud, cad = _stroke(drawn[1], "aud-dollars"), _stroke(drawn[1], "cad-dollars")
        assert aud.x[0] == cad.x[0] == DOLLARS_X
        assert _length(aud) == pytest.approx(DOLLARS_LENGTH)
        assert _length(cad) / _length(aud) == pytest.approx(-figures.cad_dollars, rel=1e-12)

    def test_the_equal_pair_stands_on_the_dashed_mark_at_minus_half(self, drawn) -> None:
        scene = drawn[1]
        equal = _stroke(scene, "equal")
        assert equal.dashed and set(equal.x) == {share_x(-0.5)}
        assert equal.y[0] == AXIS_Y
        aud, cad = _stroke(scene, "spread-aud"), _stroke(scene, "spread-cad")
        assert set(aud.x) == set(cad.x) == {share_x(-0.5)}
        assert aud.y[0] == cad.y[0]
        assert aud.y[-1] > aud.y[0] > cad.y[-1] > equal.y[-1]
        assert _length(aud) == pytest.approx(_length(cad))

    def test_the_band_runs_from_0_to_1_on_the_line(self, drawn) -> None:
        (band,) = drawn[1].fills
        assert (band.x0, band.x1, band.y0) == (share_x(0.0), share_x(1.0), AXIS_Y)
        assert band.color == REJECT_TINT

    def test_the_pair_held_the_same_way_hangs_short_on_one_side(self, drawn) -> None:
        """A short AUD.USD bar and a tall CAD.USD bar, both below their baseline,
        drawn above the band."""
        scene = drawn[1]
        base = _stroke(scene, "same-base")
        (band,) = scene.fills
        cad, aud = _stroke(scene, "same-cad"), _stroke(scene, "same-aud")
        for bar in (cad, aud):
            assert bar.y[0] == base.y[0]
            assert bar.y[-1] < bar.y[0]
            assert band.x0 < bar.x[0] < band.x1 and bar.y[-1] > band.y1
            assert base.x.min() < bar.x[0] < base.x.max()
        assert _length(cad) > 2 * _length(aud)

    def test_the_band_says_long_both_or_short_both(self, drawn) -> None:
        """On the 90 days the hedge held both legs one way it was long both on 28
        and short both on 62, so the words name both and the bars draw the 62."""
        words = [s.text for s in _labels(drawn[1], "same-way")]
        assert words == ["held the same way", "long both, or short both:", "a bet on the US dollar"]

    def test_the_90_days_held_one_way_were_long_both_on_28_and_short_both_on_62(
        self, result
    ) -> None:
        held = result.positions[result.training :]
        same = result.dollar_split > 0
        assert int(same.sum()) == 90
        assert int((same & (held > 0).all(axis=1)).sum()) == 28
        assert int((same & (held < 0).all(axis=1)).sum()) == 62

    def test_other_figures_move_the_words_and_the_marks(self) -> None:
        scene = scenes(MOVED)[1]
        assert scene.labels[1] == "CAD.USD: −0.9123 units × its close, short"
        assert scene.labels[2] == "the last day, 2015-06-30: 1 to −0.8765 in dollars"
        assert scene.labels[6] == "CAD.USD’s share, −0.4671"
        assert _stroke(scene, "last-day").x[0] == pytest.approx(share_x(MOVED.share))
        cad = _stroke(scene, "cad-dollars")
        assert _length(cad) == pytest.approx(DOLLARS_LENGTH * 0.8765432)

    @pytest.mark.parametrize("share", [0.0, 0.3, -1.0])
    def test_a_last_day_held_the_same_way_or_all_in_one_leg_is_refused(
        self, figures, share
    ) -> None:
        """The sketch draws the last day long AUD.USD and short CAD.USD."""
        with pytest.raises(ValueError, match="draws it below 0"):
            scenes(dataclasses.replace(figures, share=share))


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, drawn, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            found = clearances(scene)
            assert set(found) == {*scene.labels, scene.title}
            for text, pixels in found.items():
                assert pixels >= CLEAR_PX, (scene.title, text, round(pixels, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_sits_inside_the_board(
        self, drawn, monkeypatch, fallback
    ) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            for text, box in _boxes(scene):
                inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                assert inside >= INSIDE_PX, (scene.title, text, round(inside, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_no_two_labels_touch(self, drawn, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
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

    def test_each_is_680_by_320_and_loops_forever(self, gifs, frames) -> None:
        for path, steps in zip(gifs, frames, strict=True):
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(path) == [f.ms for f in steps], path.name

    def test_each_opens_on_its_title_and_holds_its_drawing(self, drawn, frames) -> None:
        for scene, steps in zip(drawn, frames, strict=True):
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            hold = PACED_HOLD_MS if scene.slug in PACED else HOLD_MS
            assert steps[-1].ms == hold, scene.slug

    def test_only_the_share_sketch_builds_slowly(self, drawn) -> None:
        """It draws three ideas and seventeen labels, more than the usual pace lets
        a reader take in."""
        assert [scene.slug in PACED for scene in drawn] == [False, True]
        assert PACED_HOLD_MS == 12000

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, figures) -> None:
        again = make_aud_cad_johansen_whiteboards(out_dir=tmp_path, figures=figures)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, frames) -> None:
        for name, steps in zip(GIFS, frames, strict=True):
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
            ), f"{path.name}: redraw with: uv run python -m chan.aud_cad_johansen_whiteboard"

    def test_each_carries_the_shared_inks_the_chart_draws_in(self) -> None:
        """The post has not moved to chan.palette, so neither have its sketches."""
        for name in GIFS:
            assert _gif_palette(FIGURES_DIR / name) == _ink_palette(whiteboard.INKS), name


class TestThePost:
    def test_each_gif_follows_the_text_it_draws(self) -> None:
        """The scale sketch right after Lesson 2's paragraph on the invisible
        scale, and the share sketch right after Lesson 4's paragraph on the top
        panel."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            ("A scale is invisible to them.", "That day’s hedge is one of 612."),
            GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"](../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_its_title_and_labels_in_order(self, drawn) -> None:
        for scene in drawn:
            alt = _alt(scene)
            place = alt.index(f"“{scene.title}”")
            for text in scene.labels:
                place = alt.index(f"“{text}”", place) + 1

    def test_each_alt_text_says_how_it_builds(self, drawn) -> None:
        for scene in drawn:
            alt = _alt(scene)
            if scene.slug in PACED:
                assert "drawn slowly" in alt and "holds for twelve seconds" in alt
            else:
                assert "drawn slowly" not in alt and "twelve seconds" not in alt

    def test_each_alt_text_names_each_marks_ink_and_says_what_is_schematic(self, drawn) -> None:
        """The label-order test skips the words between quotes, so these are held here."""
        for scene, phrases in zip(
            drawn,
            (
                [
                    "two black bars",
                    "a brass arrow",
                    "twice as tall",
                    "green check",
                    "in brass",
                    "The bars are schematic",
                ],
                [
                    "a green bar",
                    "a red bar about three quarters as long",
                    "a brass dot",
                    "a dashed grey mark",
                    "a green bar above and a red bar below",
                    "A pale red band with a red edge",
                    "both hanging below a grey baseline",
                    "The equal bars and the band’s bars are schematic",
                ],
            ),
            strict=True,
        ):
            alt = _alt(scene)
            for phrase in phrases:
                assert phrase in alt, (scene.slug, phrase)


class TestTheCommand:
    def test_it_writes_both_gifs_into_the_figures_folder(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.iterdir()) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]
        for name in GIFS:
            assert _gif_palette(tmp_path / name) == _ink_palette(whiteboard.INKS), name


def _ink_palette(inks) -> list[int]:
    """The leading entries of the renderer's palette for ``inks``: white, then each ink's blends."""
    flat = whiteboard.palette(inks).getpalette()
    return flat[: 3 * (1 + len(inks) * len(whiteboard.BLENDS))]


def _gif_palette(path) -> list[int]:
    with Image.open(path) as gif:
        return gif.getpalette()[: len(_ink_palette(whiteboard.INKS))]


def test_the_band_ink_is_the_shared_red_not_the_palettes() -> None:
    """The chart draws in the shared inks, so the band's tint is the shared red."""
    from chan import palette

    assert REJECT_TINT != palette.REJECT_TINT
    assert np.allclose(
        matplotlib.colors.to_rgb(REJECT_TINT),
        whiteboard._blend(LOST, whiteboard.BLENDS[-1]),
        atol=0.5 / 255,
    )
    assert sketches.REJECT_TINT is REJECT_TINT
