"""The pins for the one whiteboard GIF in the post on USD.CAD's holdout.

The GIF sketches the post's Lesson 1 and sits right after the paragraph that
opens "The t is 0.2670, far below 1.645". It sets the sum, above 0 with a check
mark, over a t gauge drawn to scale, so what is pinned is what a reader takes
from it: what it says and in which order, that each mark stands at an affine
function of its value, that the dot sits far left of the zone it falls short
of, that no label touches a line, leaves the board or touches another label in
the hand font or the fallback, and each file's size, frame count, loop and
timing.

Its sum and its t are read from the run on the committed vintage, which takes
a second, so the tests read the run itself rather than a frozen copy. The sum
is ``holdout.total_pnl`` and the t is the Newey-West t, which
``tests/test_usdcad_holdout.py`` pins under its ``SPEC`` as 0.11316189494446321
and 0.2670103469846707. The critical value is
:data:`chan.usdcad_holdout.NEWEY_WEST_CRITICAL`. A scene handed made-up
figures shows that every label follows them, and figures that would make the
words false are refused.

Two draws on one machine give the same bytes. Whether the committed GIF
equals a fresh draw depends on the font, as
``tests/test_usdcad_tests_whiteboard.py`` explains, so that comparison runs
only on macOS arm64 with Comic Sans MS.
"""

from __future__ import annotations

import hashlib
import logging
import math
import platform
import re
import warnings

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import usdcad_holdout_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.usdcad_holdout import NEWEY_WEST_CRITICAL, HoldoutRefused, read_holdout
from chan.usdcad_holdout_whiteboard import (
    GIF_PREFIX,
    LINE_X,
    _sign_and_t,
    gif_name,
    main,
    make_usdcad_holdout_whiteboards,
    scenes,
)
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    HOLD_MS,
    TITLE_MS,
    WIDTH,
    Frame,
    Label,
    clearances,
    hand_font,
    render,
    timeline,
)

POST = REPO_ROOT / "blog" / "usdcad-holdout-lessons.md"

GIFS = ["usdcad_holdout_sign_and_t.gif"]
STROKES = ["check", "line", "tick-zero", "tick-critical", "zone", "t"]
LABELS = [
    "sum 0.1132 > 0",
    "0",
    "1.645",
    "beats chance, one-sided 5%",
    "t = 0.2670",
    "mean daily P&L",
]

CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4

#: The figures ``tests/test_usdcad_holdout.py`` pins, at full precision.
TOTAL_PNL, T_NEWEY_WEST = 0.11316189494446321, 0.2670103469846707


@pytest.fixture(scope="module")
def holdout():
    return read_holdout()


@pytest.fixture(scope="module")
def drawn(holdout):
    return scenes(holdout)


@pytest.fixture(scope="module")
def frames(drawn):
    return [timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, holdout):
    return make_usdcad_holdout_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), holdout=holdout
    )


def _stroke(scene, gid: str):
    return next(s for s in scene.strokes if s.gid == gid)


def _x(scene, gid: str) -> float:
    """Where the upright stroke or dot ``gid`` stands on the board."""
    stroke = _stroke(scene, gid)
    assert np.ptp(stroke.x) == 0, gid
    return float(stroke.x[0])


def _named(scene, gid: str) -> list[Label]:
    return [s for s in scene.steps if isinstance(s, Label) and s.names == gid]


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


class TestTheScene:
    def test_there_is_one_titled_the_sign_and_the_t(self, drawn) -> None:
        assert [scene.title for scene in drawn] == ["The sign and the t"]
        assert [gif_name(scene) for scene in drawn] == GIFS
        assert all(name.startswith(GIF_PREFIX) for name in GIFS)

    def test_it_draws_its_strokes_in_order(self, drawn) -> None:
        assert [s.gid for s in drawn[0].strokes] == STROKES

    def test_it_says_what_it_should(self, drawn) -> None:
        assert drawn[0].labels == LABELS

    def test_every_label_names_a_stroke_drawn_before_it(self, drawn) -> None:
        for scene in drawn:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if not isinstance(s, Label)]
                    assert step.names in earlier, step.text

    def test_no_label_is_parsed_as_math(self, drawn) -> None:
        assert not [s.text for scene in drawn for s in scene.steps if getattr(s, "math", 0)]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, drawn) -> None:
        for scene in drawn:
            for stroke in scene.strokes:
                assert stroke.points >= stroke.frames, stroke.gid

    def test_it_has_no_tint(self, drawn) -> None:
        """The zone is hatched in red rather than tinted, so no pale tint
        needs the green edge the equity seasonals post's tints carry."""
        assert not drawn[0].fills


class TestTheColours:
    def test_each_stroke_and_label_is_in_the_ink_its_meaning_calls_for(self, drawn) -> None:
        """The sum checks out in green, the gauge is black, the zone that
        would beat chance is red, and the run's t is brown."""
        scene = drawn[0]
        inks = {"check": GOOD, "line": INK, "tick-zero": INK, "tick-critical": INK}
        inks |= {"zone": LOST, "t": ACCENT}
        assert {s.gid: s.color for s in scene.strokes} == inks
        for step in scene.steps:
            if isinstance(step, Label):
                assert step.color == inks[step.names], step.text


class TestTheNumbersComeFromTheRun:
    def test_the_run_gives_the_figures_the_post_quotes(self, holdout) -> None:
        assert holdout.total_pnl == pytest.approx(TOTAL_PNL, abs=1e-9)
        assert holdout.newey_west.t_newey_west == pytest.approx(T_NEWEY_WEST, abs=1e-9)
        assert NEWEY_WEST_CRITICAL == 1.645

    def test_the_labels_print_the_runs_figures(self, holdout, drawn) -> None:
        labels = drawn[0].labels
        assert labels[0] == f"sum {holdout.total_pnl:.4f} > 0"
        assert labels[2] == f"{NEWEY_WEST_CRITICAL:.3f}"
        assert labels[4] == f"t = {holdout.newey_west.t_newey_west:.4f}"

    def test_the_level_is_the_normal_tail_past_the_critical_value(self) -> None:
        assert sketches._level(1.645) == "5%"
        assert sketches._level(2.326) == "1%"

    def test_other_figures_move_the_labels(self) -> None:
        assert _sign_and_t(0.05, 1.2, critical=2.326).labels == [
            "sum 0.0500 > 0",
            "0",
            "2.326",
            "beats chance, one-sided 1%",
            "t = 1.2000",
            "mean daily P&L",
        ]

    @pytest.mark.parametrize("total", [0.0, -0.02], ids=["zero", "below zero"])
    def test_a_sum_not_above_0_is_refused(self, total) -> None:
        """The check mark says the sum is above 0."""
        with pytest.raises(ValueError, match="checks the sum off as above 0"):
            _sign_and_t(total, 0.2)

    @pytest.mark.parametrize("t", [0.0, -0.3], ids=["zero", "below zero"])
    def test_a_t_not_above_0_is_refused(self, t) -> None:
        """The dot is drawn right of the 0 tick, as a positive sum implies."""
        with pytest.raises(ValueError, match="draws the t right of 0"):
            _sign_and_t(0.1, t)

    @pytest.mark.parametrize("t", [1.645, 2.1], ids=["on it", "past it"])
    def test_a_t_not_short_of_the_critical_value_is_refused(self, t) -> None:
        """The dot is drawn short of the zone, which would be false of a t inside it."""
        with pytest.raises(ValueError, match="short of its critical value of 1.645"):
            _sign_and_t(0.1, t)


class TestTheGauge:
    @pytest.mark.parametrize("figures", [None, (0.05, 1.2, 2.326)], ids=["run", "made up"])
    def test_every_mark_stands_at_an_affine_function_of_its_value(self, drawn, figures) -> None:
        """The board distance between any two marks over the gap between their
        values is one number, so the line is a ruler rather than a sketch."""
        if figures is None:
            scene, values = drawn[0], [0.0, T_NEWEY_WEST, NEWEY_WEST_CRITICAL]
        else:
            total, t, critical = figures
            scene, values = _sign_and_t(total, t, critical=critical), [0.0, t, critical]
        xs = [_x(scene, gid) for gid in ("tick-zero", "t", "tick-critical")]
        slopes = [
            (xs[j] - xs[i]) / (values[j] - values[i])
            for i in range(len(xs))
            for j in range(i + 1, len(xs))
        ]
        assert slopes[0] > 0
        assert slopes == pytest.approx([slopes[0]] * len(slopes), rel=1e-12)
        line = _stroke(scene, "line")
        assert line.x.min() < min(xs) and max(xs) < line.x.max()

    def test_the_dot_sits_on_the_line_far_left_of_the_zone(self, drawn) -> None:
        """Right of the 0 tick, and nearer it than the zone by more than four to one."""
        scene = drawn[0]
        zero, dot, edge = (_x(scene, g) for g in ("tick-zero", "t", "tick-critical"))
        assert _stroke(scene, "t").y[0] == _stroke(scene, "line").y[0]
        assert zero < dot < edge
        assert edge - dot > 4 * (dot - zero)

    def test_the_zone_runs_from_the_critical_tick_to_the_line_end_above_it(self, drawn) -> None:
        scene = drawn[0]
        zone, line = _stroke(scene, "zone"), _stroke(scene, "line")
        assert zone.x.min() == pytest.approx(_x(scene, "tick-critical"))
        assert zone.x.max() == line.x.max() == LINE_X[1]
        assert zone.y.min() > line.y[0], "the zone sits above the line"

    def test_each_tick_and_the_dot_carry_their_labels_above_or_below_them(self, drawn) -> None:
        """The values on the ticks sit under the line, and the t over its dot."""
        scene = drawn[0]
        level = _stroke(scene, "line").y[0]
        for gid, texts in (("tick-zero", ["0"]), ("tick-critical", ["1.645"])):
            named = _named(scene, gid)
            assert [s.text for s in named] == texts
            assert all(s.x == pytest.approx(_x(scene, gid)) and s.y < level for s in named)
        named = _named(scene, "t")
        assert [s.text for s in named] == ["t = 0.2670", "mean daily P&L"]
        assert all(s.x == pytest.approx(_x(scene, "t")) and s.y > level for s in named)

    def test_the_sum_and_its_check_sit_over_the_gauge(self, drawn) -> None:
        """The sum's words end where its check mark starts, both above every
        mark on the gauge."""
        scene = drawn[0]
        check, (words,) = _stroke(scene, "check"), _named(scene, "check")
        assert words.ha == "right" and words.x < check.x.min()
        above = max(s.y.max() for s in scene.strokes if s.gid != "check")
        assert check.y.min() > above and words.y > above


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, drawn, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            found = clearances(scene)
            assert set(found) == {*scene.labels, scene.title}
            for text, pixels in found.items():
                assert pixels >= CLEAR_PX, (text, round(pixels, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_sits_inside_the_board(
        self, drawn, monkeypatch, fallback
    ) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            for text, box in _boxes(scene):
                inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                assert inside >= INSIDE_PX, (text, round(inside, 1))

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
                    assert gap >= APART_LABELS_PX, (one, other, round(gap, 1))

    def test_no_glyph_falls_back_to_an_empty_box(self, drawn, caplog) -> None:
        with warnings.catch_warnings(record=True) as caught, caplog.at_level(logging.WARNING):
            warnings.simplefilter("always")
            for scene in drawn:
                render(scene, timeline(scene)[-1:])
        messages = [str(w.message) for w in caught] + [r.getMessage() for r in caplog.records]
        assert not [m for m in messages if "glyph" in m.lower()], messages


class TestTheGifs:
    def test_there_is_one_named_for_its_scene(self, gifs) -> None:
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

    def test_each_opens_on_its_title_and_holds_its_drawing_four_seconds(
        self, drawn, frames
    ) -> None:
        for scene, steps in zip(drawn, frames, strict=True):
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            assert (steps[-1].done, steps[-1].ms) == (len(scene.steps), HOLD_MS)
            assert HOLD_MS == 4000

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, holdout) -> None:
        again = make_usdcad_holdout_whiteboards(out_dir=tmp_path, holdout=holdout)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_these_gifs_and_no_others(self) -> None:
        """A GIF left behind by a renamed or retired scene fails here. It reads
        this module's prefix, and ``tests/test_equity_seasonals_whiteboard.py``
        holds that every GIF in the folder is one a module draws."""
        assert {path.name for path in FIGURES_DIR.glob(f"{GIF_PREFIX}*.gif")} == set(GIFS)

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
            ), f"{path.name}: redraw with: uv run python -m chan.usdcad_holdout_whiteboard"


class TestThePost:
    def test_the_gif_follows_the_paragraph_on_the_t(self) -> None:
        """Keyed on the paragraph's opening words, then the caption right after."""
        paragraphs = _paragraphs()
        (index,) = [
            k for k, p in enumerate(paragraphs) if p.startswith("The t is 0.2670, far below 1.645")
        ]
        embed = paragraphs[index + 1]
        assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", embed)
        caption = paragraphs[index + 2]
        assert caption.startswith("*") and caption.endswith("*")
        assert "drawn to scale" in caption
        assert f"the t falls far short of {NEWEY_WEST_CRITICAL:.3f}" in caption

    def test_it_is_embedded_once(self) -> None:
        assert POST.read_text(encoding="utf-8").count(f"docs/figures/{GIFS[0]})") == 1

    def test_the_alt_text_quotes_its_title_and_labels_in_drawing_order(self, drawn) -> None:
        text = POST.read_text(encoding="utf-8")
        scene = drawn[0]
        match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
        assert match
        alt = match.group(1)
        assert alt.startswith(f"An animated whiteboard sketch titled “{scene.title}”")
        places = [alt.find(f"“{label}”") for label in scene.labels]
        assert -1 not in places, [w for w, at in zip(scene.labels, places, strict=True) if at < 0]
        assert places == sorted(places)
        assert "A green check mark comes first" in alt
        assert (
            "A red hatched zone above the line runs from the 1.645 tick to the line’s right end"
            in alt
        )
        assert "A brown dot lands on the line just right of the 0 tick, far left of the zone" in alt
        assert alt.endswith("holds for four seconds before it redraws.")


class TestTheCommand:
    def test_it_writes_every_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []

        def draw(**kwargs):
            drawn.append(kwargs)
            return [FIGURES_DIR / name for name in GIFS]

        monkeypatch.setattr(sketches, "make_usdcad_holdout_whiteboards", draw)
        main()
        assert drawn == [{}]
        assert capsys.readouterr().out.splitlines() == [
            f"wrote {FIGURES_DIR / name}" for name in GIFS
        ]

    def test_drawing_with_no_out_dir_writes_the_committed_paths(self, monkeypatch, holdout) -> None:
        saved = []
        monkeypatch.setattr(sketches, "read_holdout", lambda: holdout)
        monkeypatch.setattr(sketches, "render", lambda scene, frames: [Image.new("P", (1, 1))])
        monkeypatch.setattr(Image.Image, "save", lambda self, path, **kw: saved.append(path))
        paths = make_usdcad_holdout_whiteboards()
        assert paths == saved == [FIGURES_DIR / name for name in GIFS]

    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        refusal = HoldoutRefused("the vintage's rows are out of date order")

        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(sketches, "read_holdout", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
