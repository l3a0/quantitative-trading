"""The pins for the low-beta holdout post's three whiteboard GIFs, two in Lesson 1 and one in 5.

1. The bound sketch draws, on one axis of the yearly gap, a black bracket from
   the measured gap to the one-sided upper bound and a brass bracket from 0 to
   Y. What is pinned is that every mark sits where its figure puts it under one
   affine map: the red dot at the gap, each bracket's legs at its two figures,
   the brass join at 1.645 standard errors, and the hatching from the bound to
   the axis's end. Also pinned are that the black bracket is exactly as long as
   the brass bracket's first piece, the two brackets sit on opposite sides of
   the axis, the join carries no figure, and the words it prints.
2. The dropped-month sketch draws, on its own axis of the yearly gap, five
   rows: the gap over every month, then the gap without the lowest month, the
   second lowest, the highest, and the lowest and highest together. What is
   pinned is that each dot sits at its figure under one affine map, each
   arrow starts at the gap and points at its row's dot, the dashed upright
   stands at 0 through every row, a dot's ink and its printed figure follow
   its sign, and the row labels name the months the run read. Figures whose
   lowest or second-lowest month leaves the gap's sign unchanged are refused,
   since the title would then be false.
3. The look-ahead sketch is schematic. What is pinned is its order of events:
   stock A runs past both dates, stock B's series stops strictly between them,
   the old rule's arrow points from the next month-end back to the formation,
   and the new rule's cash line runs flat from B's last close to the month-end.
   Also pinned is that no label claims the formation now sees only its own
   date, since the post names two exclusions that still read the next
   month-end.

The first two sketches' figures need the owner's archive, so they are pinned
here as :data:`PINNED` and :data:`PINNED_DROPPED`, every test here runs
without the archive, and ``test_the_whiteboard_draws_this_runs_figures`` and
``test_the_whiteboard_draws_this_runs_dropped_months`` in
``tests/test_low_beta_holdout.py`` hold that the run gives them. A made-up
second set of figures for each checks that the words and marks follow the
data.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, every
sketch's slower pace, that two draws give the same bytes, and that each
committed GIF is a fresh draw, a comparison that runs only on macOS arm64
with Comic Sans MS, as ``tests/test_usdcad_tests_whiteboard.py`` explains.
The check that ``docs/figures`` holds exactly the GIFs the modules draw lives
in ``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS`
from here.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import math
import platform
import re
from dataclasses import replace
from datetime import date

import matplotlib
import numpy as np
import pandas as pd
import pytest
from ithildincore import whiteboard
from ithildincore.whiteboard import (
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
from PIL import Image

from chan import low_beta_holdout_whiteboard as sketches
from chan.archive import ArchiveUnavailable
from chan.low_beta_holdout import HoldoutRefused
from chan.low_beta_holdout_whiteboard import (
    ABOVE_Y,
    AXIS_Y,
    BELOW_Y,
    DROP_AXIS_Y,
    DROP_X,
    DROPS,
    FIGURE_X,
    FORMED_X,
    GAP_X,
    GAPS,
    NEXT_X,
    ROWS_Y,
    BoundFigures,
    DroppedFigures,
    drop_x,
    gap_x,
    gif_name,
    main,
    make_low_beta_holdout_whiteboards,
    scenes,
    sketch_timeline,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED

POST = REPO_ROOT / "blog" / "low-beta-holdout-lessons.md"

#: Every GIF in the order :func:`make_low_beta_holdout_whiteboards` returns them.
GIFS = [
    "low_beta_holdout_sketch_bound_and_y.gif",
    "low_beta_holdout_sketch_dropped_months.gif",
    "low_beta_holdout_sketch_look_ahead.gif",
]
#: The GIFs a redraw cannot write without the owner's archive.
ARCHIVE_GIFS = {
    "low_beta_holdout_sketch_bound_and_y.gif",
    "low_beta_holdout_sketch_dropped_months.gif",
}

#: The registered run's yearly gap, its yearly Newey-West standard error and Y,
#: as ``test_the_whiteboard_draws_this_runs_figures`` in
#: ``tests/test_low_beta_holdout.py`` holds the run gives them. The vintage and
#: the specification are that file's ``SPEC``: IVV's members, their Alpha
#: Vantage ``adjusted_close`` series downloaded 2026-10-05, SPY's downloaded
#: 2026-10-11, the committed calendar and TB3MS, under issue 275's plan with
#: issue 526's changes and both amendments of 2026-10-11, over 208 holding
#: months from January 2009 to April 2026. A re-pin there moves these figures.
PINNED = BoundFigures(
    gap=-0.058965291602502266,
    error=0.11853562090407452,
    detectable=0.2947506749400717,
)

#: Twelve times the mean of d over all 208 holding months and over the months
#: left when the lowest, the second lowest, the highest, and the lowest and
#: highest together are dropped, with those three months, as
#: ``test_the_whiteboard_draws_this_runs_dropped_months`` in
#: ``tests/test_low_beta_holdout.py`` holds the run gives them, on the same
#: vintages and specification as :data:`PINNED`. The write-up measured these
#: after the run, so they decide nothing.
PINNED_DROPPED = DroppedFigures(
    months=208,
    gap=-0.058965291602502266,
    lowest=date(2024, 12, 31),
    second=date(2026, 3, 31),
    highest=date(2025, 2, 28),
    without_lowest=0.03132642815124606,
    without_second=0.007890177777331676,
    without_highest=-0.09471610660305997,
    without_lowest_and_highest=-0.004159625175752438,
)

#: A fragment of the paragraph each GIF follows, keyed on words a review round
#: is unlikely to reword: the end of Lesson 1's bound paragraph, the opening of
#: its dropped-month paragraph and the opening of Lesson 5's holding-month
#: paragraph.
BOUND_FRAGMENT = "from a deficit of the same size."
DROP_FRAGMENT = "Either of two months sets the sign of the gap on its own."
LOOK_FRAGMENT = "The holding month changed most."

BOUND_LABELS = [
    "gap a year",
    "0",
    "measured gap",
    "−0.0590",
    "1.645 × 0.1185",
    "upper bound 0.1360",
    "advantages the data reject",
    "the gap found four times in five",
    "Y 0.2948",
    "the same 1.645 × 0.1185",
    "0.8416 × 0.1185",
    "same standard error, different starting points",
]

DROP_LABELS = [
    "gap a year",
    "0",
    "all 208 months",
    "−0.0590",
    "without Dec 2024",
    "+0.0313",
    "without Mar 2026",
    "+0.0079",
    "without Feb 2025",
    "−0.0947",
    "without Dec 2024 and Feb 2025",
    "−0.0042",
    "dropping a month is not a test",
]

LOOK_LABELS = [
    "formation",
    "next month-end",
    "stock A",
    "stock B’s series stops",
    "old rule: drop B, read from the future",
    "new rule: B’s return to its last close, then cash",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def every():
    return scenes(PINNED, PINNED_DROPPED)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_low_beta_holdout_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), figures=PINNED, dropped=PINNED_DROPPED
    )


def _stroke(scene, gid):
    (found,) = [s for s in scene.strokes if s.gid == gid]
    return found


def _label(scene, text):
    (found,) = [s for s in scene.steps if isinstance(s, Label) and s.text == text]
    return found


def _font(monkeypatch, fallback: bool) -> None:
    if fallback:
        monkeypatch.setattr(whiteboard, "hand_font", lambda: whiteboard.FALLBACK_FONT)


def _boxes(scene):
    with matplotlib.rc_context(whiteboard.style()):
        canvas, artists = whiteboard.new_board(scene)
        whiteboard.show(scene, artists, Frame(len(scene.steps), 0, 0))
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


def _gap_of(x):
    """The gap a year at a board position across, the inverse of :func:`gap_x`."""
    (v0, v1), (x0, x1) = GAPS, GAP_X
    return v0 + (np.asarray(x) - x0) * (v1 - v0) / (x1 - x0)


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_three_in_the_order_the_post_reads_them(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

    def test_each_draws_its_strokes_in_order(self, every) -> None:
        assert [s.gid for s in every[0].strokes] == ["axis", "gap", "bound", "reject", "y", "join"]
        assert [s.gid for s in every[1].strokes] == [
            "axis",
            "zero",
            "row-0",
            "arrow-1",
            "row-1",
            "arrow-2",
            "row-2",
            "arrow-3",
            "row-3",
            "arrow-4",
            "row-4",
        ]
        assert [s.gid for s in every[2].strokes] == [
            "time",
            "formed",
            "next",
            "a",
            "b",
            "b-last",
            "old",
            "cash",
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
        """No sketch draws a tint. The bound sketch hatches its rejected
        zone with red strokes instead. A tint would need the green edge the
        equity seasonals module's ``_tinted`` draws, since the tint alone
        stands 1.29 to 1 against the board."""
        assert [fill for scene in every for fill in scene.fills] == []

    def test_no_two_labels_in_a_scene_share_their_words(self, every) -> None:
        """:func:`clearances` keys its result by a label's words, so two labels
        with the same words would hide one of them from the clearance test."""
        for scene in every:
            assert len(set(scene.labels)) == len(scene.labels), scene.slug


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

    def test_every_sketch_builds_slowly_and_holds_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("bound_and_y", "dropped_months", "look_ahead")
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
        again = make_low_beta_holdout_whiteboards(
            out_dir=tmp_path, figures=PINNED, dropped=PINNED_DROPPED
        )
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
        assert not "low_beta_holdout.png".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.low_beta_holdout_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(sketches, "read_figures", lambda: (PINNED, PINNED_DROPPED))
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]

    @pytest.mark.parametrize(
        "refusal",
        [ArchiveUnavailable("no archive here"), HoldoutRefused("SPY is a member ticker")],
        ids=["no archive", "run refused"],
    )
    def test_without_the_archive_it_names_the_gifs_it_left(
        self, monkeypatch, refusal, tmp_path
    ) -> None:
        """It draws into a scratch folder, because a draw into the figures
        folder would overwrite the committed GIFs that the byte test compares."""

        def refuse(*args, **kwargs):
            raise refusal

        before = {path.name: path.read_bytes() for path in FIGURES_DIR.glob("*.gif")}
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(sketches.low_beta_holdout, "read_holdout", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == (
            "low_beta_holdout_sketch_bound_and_y.gif, low_beta_holdout_sketch_dropped_months.gif "
            f"were not redrawn: {refusal}"
        )
        assert sorted(p.name for p in tmp_path.glob("*.gif")) == sorted(set(GIFS) - ARCHIVE_GIFS)
        assert {path.name: path.read_bytes() for path in FIGURES_DIR.glob("*.gif")} == before

    def test_the_archive_slugs_are_the_archive_gifs(self) -> None:
        assert {f"{sketches.GIF_PREFIX}{slug}.gif" for slug in sketches.ARCHIVE_SLUGS} == (
            ARCHIVE_GIFS
        )

    def test_it_catches_every_refusal_the_run_turns_into_one_line(self) -> None:
        """The two tests above raise two of the refusals. This one holds that the
        tuple the command catches is the one ``chan.low_beta_holdout.main``
        catches, read from that function's source, so a refusal added there or
        dropped here fails."""
        tree = ast.parse(inspect.getsource(sketches.low_beta_holdout.main))
        (handler,) = [node for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler)]
        caught = {getattr(sketches.low_beta_holdout, name.id) for name in handler.type.elts}
        assert len(caught) == 9
        assert set(sketches.REFUSALS) == caught


class TestThePost:
    def test_the_footer_links_the_sketch_code_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        assert f"[the whiteboard sketches]({base}src/chan/low_beta_holdout_whiteboard.py)" in footer
        assert (
            f"[what the sketches draw]({base}tests/test_low_beta_holdout_whiteboard.py)" in footer
        )

    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (bound,) = [k for k, p in enumerate(paragraphs) if BOUND_FRAGMENT in p]
        (drop,) = [k for k, p in enumerate(paragraphs) if p.startswith(DROP_FRAGMENT)]
        (look,) = [k for k, p in enumerate(paragraphs) if p.startswith(LOOK_FRAGMENT)]
        for index, name in zip((bound, drop, look), GIFS, strict=True):
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_sits_in_its_lesson(self) -> None:
        text = POST.read_text(encoding="utf-8")
        bound, drop, look = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        assert text.index("## Lesson 1:") < bound < drop < text.index("## Lesson 2:")
        assert text.index("## Lesson 5:") < look < text.index("## What this holdout cannot say")

    def test_each_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count("(../docs/figures/low_beta_holdout.png)") == 1

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

    def test_the_module_says_which_is_schematic(self) -> None:
        doc = sketches.__doc__ or ""
        assert "The first two sketches are drawn to scale, and the third is schematic." in doc


# --- Lesson 1: Y and the upper bound -------------------------------------------------


class TestTheBoundFigures:
    def test_the_pinned_figures_print_as_the_post_does(self) -> None:
        f = PINNED
        assert (sketches.four(f.gap), sketches.four(f.error)) == ("−0.0590", "0.1185")
        assert (sketches.four(f.bound), sketches.four(f.detectable)) == ("0.1360", "0.2948")

    def test_the_bound_is_the_gap_plus_1_645_standard_errors(self) -> None:
        """Written out rather than read from the module's constants, so a wrong
        constant there fails."""
        assert PINNED.bound == pytest.approx(PINNED.gap + 1.645 * PINNED.error, abs=1e-15)
        assert PINNED.reach == pytest.approx(1.645 * PINNED.error, abs=1e-15)

    def test_y_is_1_645_plus_0_8416_of_the_same_standard_errors(self) -> None:
        assert PINNED.detectable == pytest.approx((1.645 + 0.8416) * PINNED.error, abs=1e-12)

    def test_the_unlabelled_join_is_a_figure_the_post_does_not_state(self) -> None:
        """1.645 × 0.1185 is 0.1950. The post never prints it, so the sketch
        draws the join and prints nothing there."""
        join = sketches.four(PINNED.reach)
        assert join == "0.1950"
        assert join not in POST.read_text(encoding="utf-8")
        assert not [text for text in scenes(PINNED, PINNED_DROPPED)[0].labels if join in text]

    def test_from_verdict_reads_the_yearly_figures(self) -> None:
        class Stub:
            gap, standard_error, detectable = -0.06, 0.01, 0.3

        found = BoundFigures.from_verdict(Stub())
        assert (found.gap, found.detectable) == (-0.06, 0.3)
        assert found.error == pytest.approx(0.12, abs=1e-15)


class TestTheBoundSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "Y and the upper bound"
        assert every[0].labels == BOUND_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert _stroke(scene, "axis").color == MUTED
        for gid in ("gap", "reject"):
            assert _stroke(scene, gid).color == LOST, gid
        assert _stroke(scene, "bound").color == INK
        for gid in ("y", "join"):
            assert _stroke(scene, gid).color == ACCENT, gid
        for text in ("gap a year", "0", "1.645 × 0.1185", "the same 1.645 × 0.1185"):
            assert _label(scene, text).color == MUTED, text
        assert _label(scene, "0.8416 × 0.1185").color == MUTED
        for text in ("measured gap", "−0.0590", "advantages the data reject"):
            assert _label(scene, text).color == LOST, text
        for text in ("upper bound 0.1360", "same standard error, different starting points"):
            assert _label(scene, text).color == INK, text
        for text in ("the gap found four times in five", "Y 0.2948"):
            assert _label(scene, text).color == ACCENT, text

    def test_the_gap_dot_sits_on_the_axis_at_the_gap(self, every) -> None:
        dot = _stroke(every[0], "gap")
        assert (dot.points, dot.frames) == (1, 1)
        assert dot.y[0] == AXIS_Y
        assert _gap_of(dot.x[0]) == pytest.approx(PINNED.gap)

    def test_the_axis_ticks_zero(self, every) -> None:
        axis = _stroke(every[0], "axis")
        assert (axis.x.min(), axis.x.max()) == pytest.approx(GAP_X)
        below = axis.x[axis.y < AXIS_Y]
        assert len(below) and _gap_of(below) == pytest.approx(0.0, abs=1e-12)

    def test_the_black_bracket_runs_from_the_gap_to_the_bound_above_the_axis(self, every) -> None:
        bracket = _stroke(every[0], "bound")
        assert _gap_of(bracket.x.min()) == pytest.approx(PINNED.gap)
        assert _gap_of(bracket.x.max()) == pytest.approx(PINNED.bound)
        assert bracket.y.min() == AXIS_Y and bracket.y.max() == ABOVE_Y
        assert (bracket.y[0], bracket.y[-1]) == (AXIS_Y, AXIS_Y)

    def test_the_brass_bracket_runs_from_0_to_y_below_the_axis(self, every) -> None:
        bracket = _stroke(every[0], "y")
        assert _gap_of(bracket.x.min()) == pytest.approx(0.0, abs=1e-12)
        assert _gap_of(bracket.x.max()) == pytest.approx(PINNED.detectable)
        assert bracket.y.max() == AXIS_Y and bracket.y.min() == BELOW_Y
        assert (bracket.y[0], bracket.y[-1]) == (AXIS_Y, AXIS_Y)

    def test_the_join_sits_1_645_standard_errors_from_0_on_the_brass_bar(self, every) -> None:
        join = _stroke(every[0], "join")
        assert np.ptp(join.x) == 0
        assert _gap_of(join.x[0]) == pytest.approx(1.645 * PINNED.error)
        assert join.y.min() < BELOW_Y < join.y.max()

    def test_the_black_bracket_is_as_long_as_the_brass_bars_first_piece(self, every) -> None:
        """The two brackets share one standard error. Only their starts differ,
        by the 0.0590 between the gap and 0."""
        scene = every[0]
        black = _stroke(scene, "bound")
        first = _stroke(scene, "join").x[0] - _stroke(scene, "y").x.min()
        assert np.ptp(black.x) == pytest.approx(first)
        shift = _gap_of(_stroke(scene, "y").x.min()) - _gap_of(black.x.min())
        assert shift == pytest.approx(-PINNED.gap)

    def test_the_hatching_runs_from_the_bound_to_the_axis_end_above_the_axis(self, every) -> None:
        hatch = _stroke(every[0], "reject")
        assert _gap_of(hatch.x.min()) == pytest.approx(PINNED.bound)
        assert hatch.x.max() == pytest.approx(GAP_X[1])
        assert AXIS_Y < hatch.y.min() and hatch.y.max() <= ABOVE_Y + 0.1

    def test_each_figure_label_sits_beside_its_mark(self, every) -> None:
        scene = every[0]
        bound, y_end = gap_x(PINNED.bound), gap_x(PINNED.detectable)
        upper = _label(scene, "upper bound 0.1360")
        assert (upper.ha, upper.y > ABOVE_Y) == ("right", True)
        assert float(bound) - 0.3 < upper.x < float(bound)
        y_label = _label(scene, "Y 0.2948")
        assert (y_label.ha, BELOW_Y < y_label.y < AXIS_Y) == ("right", True)
        assert float(y_end) - 0.3 < y_label.x < float(y_end)
        for text in ("measured gap", "−0.0590"):
            label = _label(scene, text)
            assert (label.ha, label.y < AXIS_Y) == ("right", True), text
            assert float(gap_x(PINNED.gap)) - 0.3 < label.x < float(gap_x(PINNED.gap)), text

    def test_made_up_figures_move_the_words_and_marks(self) -> None:
        made_up = replace(PINNED, gap=-0.0400, error=0.0900, detectable=(1.645 + 0.8416) * 0.09)
        scene = scenes(made_up, PINNED_DROPPED)[0]
        assert "−0.0400" in scene.labels
        assert "1.645 × 0.0900" in scene.labels and "0.8416 × 0.0900" in scene.labels
        assert f"upper bound {sketches.four(-0.04 + 1.645 * 0.09)}" in scene.labels
        assert f"Y {sketches.four(made_up.detectable)}" in scene.labels
        assert _gap_of(_stroke(scene, "bound").x.max()) == pytest.approx(made_up.bound)

    @pytest.mark.parametrize(
        "changes",
        [
            {"gap": 0.01},
            {"gap": -0.2},
            {"detectable": 0.4},
            {"detectable": 0.1},
        ],
        ids=["a positive gap", "a gap off the axis", "Y off the axis", "Y below the bound"],
    )
    def test_figures_the_drawing_would_misdescribe_are_refused(self, changes) -> None:
        with pytest.raises(ValueError, match="the sketch draws a negative gap"):
            scenes(replace(PINNED, **changes), PINNED_DROPPED)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "A black bracket rises from the red dot" in alt
        assert "A brass bracket hangs below the axis from 0" in alt
        assert "the same length as the black bracket" in alt
        assert "carries no figure" in alt


# --- Lesson 1: either of two months sets the sign -----------------------------------


def _drop_of(x):
    """The gap a year at a board position across, the inverse of :func:`drop_x`."""
    (v0, v1), (x0, x1) = DROPS, DROP_X
    return v0 + (np.asarray(x) - x0) * (v1 - v0) / (x1 - x0)


#: Each row's figure in :data:`PINNED_DROPPED`, top to bottom.
ROW_VALUES = [
    PINNED_DROPPED.gap,
    PINNED_DROPPED.without_lowest,
    PINNED_DROPPED.without_second,
    PINNED_DROPPED.without_highest,
    PINNED_DROPPED.without_lowest_and_highest,
]
#: Each row's label, top to bottom.
ROW_LABELS = DROP_LABELS[2:12:2]


class TestTheDroppedFigures:
    def test_the_pinned_figures_print_as_the_post_does(self) -> None:
        printed = [sketches.signed(value) for value in ROW_VALUES]
        assert printed == ["−0.0590", "+0.0313", "+0.0079", "−0.0947", "−0.0042"]
        text = POST.read_text(encoding="utf-8")
        for figure in printed[1:]:
            assert figure in text, figure

    def test_the_gap_is_the_bound_sketchs_gap(self) -> None:
        """Both sketches in Lesson 1 start from the same −0.0590."""
        assert PINNED_DROPPED.gap == pytest.approx(PINNED.gap, abs=1e-15)

    def test_from_differences_reads_the_months_and_the_means(self) -> None:
        """Made-up d over six months, so which month is dropped follows the data."""
        index = pd.to_datetime(
            ["2020-01-31", "2020-02-29", "2020-03-31", "2020-04-30", "2020-05-31", "2020-06-30"]
        )
        d = pd.Series([0.01, -0.30, 0.20, -0.10, 0.02, 0.03], index=index)
        found = DroppedFigures.from_differences(d)
        assert found.months == 6
        assert (found.lowest, found.second, found.highest) == (
            date(2020, 2, 29),
            date(2020, 4, 30),
            date(2020, 3, 31),
        )
        assert found.gap == pytest.approx(12 * d.mean())
        assert found.without_lowest == pytest.approx(12 * d.drop(index[1]).mean())
        assert found.without_second == pytest.approx(12 * d.drop(index[3]).mean())
        assert found.without_highest == pytest.approx(12 * d.drop(index[2]).mean())
        assert found.without_lowest_and_highest == pytest.approx(
            12 * d.drop([index[1], index[2]]).mean()
        )


class TestTheDroppedMonthsSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Either of two months sets the sign"
        assert every[1].labels == DROP_LABELS

    def test_its_colours(self, every) -> None:
        """Each dot and its printed figure are red below zero and green above
        it, and the arrows are black, since row 2's crosses zero."""
        scene = every[1]
        for gid in ("axis", "zero"):
            assert _stroke(scene, gid).color == MUTED, gid
        assert _stroke(scene, "zero").dashed
        for row, value in enumerate(ROW_VALUES):
            ink = LOST if value < 0 else GOOD
            assert _stroke(scene, f"row-{row}").color == ink, row
            assert _label(scene, sketches.signed(value)).color == ink, row
        for row in range(1, 5):
            assert _stroke(scene, f"arrow-{row}").color == INK, row
        for text in ("gap a year", "0"):
            assert _label(scene, text).color == MUTED, text
        for text in [*ROW_LABELS, "dropping a month is not a test"]:
            assert _label(scene, text).color == INK, text

    def test_each_row_label_and_figure_sit_in_its_dots_row(self, every) -> None:
        scene = every[1]
        for text, value, y in zip(ROW_LABELS, ROW_VALUES, ROWS_Y, strict=True):
            assert _label(scene, text).y == y, text
            assert _label(scene, sketches.signed(value)).y == y, text

    def test_each_dot_sits_in_its_row_at_its_figure(self, every) -> None:
        scene = every[1]
        for row, (value, y) in enumerate(zip(ROW_VALUES, ROWS_Y, strict=True)):
            dot = _stroke(scene, f"row-{row}")
            assert (dot.points, dot.frames) == (1, 1)
            assert dot.y[0] == y
            assert _drop_of(dot.x[0]) == pytest.approx(value)

    def test_the_rows_run_top_to_bottom_above_the_axis(self) -> None:
        assert list(ROWS_Y) == sorted(ROWS_Y, reverse=True)
        assert min(ROWS_Y) > DROP_AXIS_Y

    def test_each_arrow_starts_at_the_gap_and_points_at_its_rows_dot(self, every) -> None:
        scene = every[1]
        start = float(drop_x(PINNED_DROPPED.gap))
        for row in range(1, 5):
            arrow, dot = _stroke(scene, f"arrow-{row}"), _stroke(scene, f"row-{row}")
            assert (arrow.x[0], arrow.y[0]) == pytest.approx((start, ROWS_Y[row]))
            shaft = int(np.argmax(np.abs(arrow.x - start)))
            tip = arrow.x[shaft]
            assert arrow.y[shaft] == pytest.approx(ROWS_Y[row])
            # The head points towards the dot and stops just short of it,
            # between the gap and the dot rather than past the dot.
            assert min(start, dot.x[0]) < tip < max(start, dot.x[0]), row
            assert abs(dot.x[0] - tip) <= 0.2, row

    def test_dropping_the_lowest_month_moves_the_gap_further_than_the_highest(self, every) -> None:
        """The paragraph's "less far", drawn as two arrow lengths."""
        scene = every[1]
        start = float(drop_x(PINNED_DROPPED.gap))
        lowest = abs(_stroke(scene, "row-1").x[0] - start)
        highest = abs(_stroke(scene, "row-3").x[0] - start)
        assert lowest > 2 * highest

    def test_the_dashed_upright_stands_at_0_through_every_row_over_its_label(self, every) -> None:
        upright = _stroke(every[1], "zero")
        assert np.ptp(upright.x) == 0
        assert _drop_of(upright.x[0]) == pytest.approx(0.0, abs=1e-12)
        assert upright.y.min() == DROP_AXIS_Y and upright.y.max() > max(ROWS_Y)
        zero = _label(every[1], "0")
        assert (zero.x, zero.ha) == (pytest.approx(upright.x[0]), "center")
        assert zero.y < DROP_AXIS_Y

    def test_the_axis_runs_along_the_bottom(self, every) -> None:
        axis = _stroke(every[1], "axis")
        assert (axis.x.min(), axis.x.max()) == pytest.approx(DROP_X)
        assert np.ptp(axis.y) == 0 and axis.y[0] == DROP_AXIS_Y

    def test_the_figures_stand_in_a_column_at_the_right_edge(self, every) -> None:
        scene = every[1]
        for value, y in zip(ROW_VALUES, ROWS_Y, strict=True):
            label = _label(scene, sketches.signed(value))
            assert (label.x, label.y, label.ha) == (FIGURE_X, y, "right")
        assert FIGURE_X > DROP_X[1]

    def test_the_closing_label_comes_last(self, every) -> None:
        assert every[1].steps[-1].text == "dropping a month is not a test"

    def test_made_up_figures_move_the_words_and_marks(self) -> None:
        made_up = DroppedFigures(
            months=120,
            gap=0.0200,
            lowest=date(2019, 6, 30),
            second=date(2011, 8, 31),
            highest=date(2015, 1, 31),
            without_lowest=-0.0400,
            without_second=-0.0300,
            without_highest=0.0100,
            without_lowest_and_highest=0.0050,
        )
        scene = scenes(PINNED, made_up)[1]
        assert scene.labels[2:12] == [
            "all 120 months",
            "+0.0200",
            "without Jun 2019",
            "−0.0400",
            "without Aug 2011",
            "−0.0300",
            "without Jan 2015",
            "+0.0100",
            "without Jun 2019 and Jan 2015",
            "+0.0050",
        ]
        assert _stroke(scene, "row-0").color == GOOD
        assert _stroke(scene, "row-1").color == LOST
        assert _drop_of(_stroke(scene, "row-3").x[0]) == pytest.approx(0.0100)

    @pytest.mark.parametrize(
        "changes",
        [
            {"without_lowest": -0.0200},
            {"without_second": -0.0010},
            {"without_highest": -0.2000},
            {"without_lowest": 0.0600},
        ],
        ids=[
            "the lowest month leaves the sign",
            "the second lowest leaves the sign",
            "a figure off the axis left",
            "a figure off the axis right",
        ],
    )
    def test_figures_the_title_would_misdescribe_are_refused(self, changes) -> None:
        with pytest.raises(ValueError, match="either of two months sets the sign"):
            scenes(PINNED, replace(PINNED_DROPPED, **changes))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "a black arrow starts from that same position" in alt
        assert "red below zero and green above it" in alt
        assert "less than half as far" in alt
        assert "just touching the upright on its left" in alt


# --- Lesson 5: what the formation cannot know ---------------------------------------


class TestTheLookAheadSketch:
    def test_its_words(self, every) -> None:
        assert every[2].title == "What the formation cannot know"
        assert every[2].labels == LOOK_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[2]
        for gid in ("time", "formed", "next"):
            assert _stroke(scene, gid).color == MUTED, gid
        for gid in ("formed", "next"):
            assert _stroke(scene, gid).dashed, gid
        for gid in ("a", "b", "b-last"):
            assert _stroke(scene, gid).color == INK, gid
        assert _stroke(scene, "old").color == LOST
        assert _stroke(scene, "cash").color == GOOD
        for text in LOOK_LABELS[:2]:
            assert _label(scene, text).color == MUTED, text
        for text in LOOK_LABELS[2:4]:
            assert _label(scene, text).color == INK, text
        assert _label(scene, LOOK_LABELS[4]).color == LOST
        assert _label(scene, LOOK_LABELS[5]).color == GOOD

    def test_stock_a_trades_past_both_dates(self, every) -> None:
        a = _stroke(every[2], "a")
        assert a.x.min() < FORMED_X and a.x.max() > NEXT_X

    def test_stock_bs_series_stops_strictly_between_the_dates(self, every) -> None:
        """The case the new rule changed. A series ending on the formation day
        itself is one of the two exclusions the post says still look ahead,
        so B stops after the formation, not on it."""
        scene = every[2]
        b, last = _stroke(scene, "b"), _stroke(scene, "b-last")
        assert b.x.min() < FORMED_X < b.x.max() < NEXT_X
        assert (last.x[0], last.y[0]) == (b.x[-1], b.y[-1])

    def test_the_old_rule_points_from_the_next_month_end_back_to_the_formation(self, every) -> None:
        old = _stroke(every[2], "old")
        assert (old.x[0], old.x.min()) == pytest.approx((NEXT_X, FORMED_X))
        tip = int(np.argmin(old.x))
        assert old.x[tip + 1] > FORMED_X, "the arrow's head sits at the formation"

    def test_the_new_rule_holds_b_flat_from_its_last_close_to_the_month_end(self, every) -> None:
        scene = every[2]
        cash, last = _stroke(scene, "cash"), _stroke(scene, "b-last")
        assert np.ptp(cash.y) == 0 and cash.y[0] == last.y[0]
        assert (cash.x.min(), cash.x.max()) == pytest.approx((last.x[0], NEXT_X))

    def test_it_carries_no_figures(self, every) -> None:
        assert not [text for text in every[2].labels if re.search(r"\d", text)]

    def test_no_label_says_the_formation_now_sees_only_its_own_date(self, every) -> None:
        """Two exclusions still read the next month-end, which the paragraph
        after the sketch says, so a closing label claiming the look-ahead is
        gone would contradict the post."""
        words = " ".join(every[2].labels).lower()
        assert "left tick" not in words and "only" not in words

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[2])
        assert "schematic" in alt
        assert "stops between the two dates" in alt
        assert "points from the next month-end back to the formation" in alt
