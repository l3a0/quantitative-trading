"""The pins for the two whiteboard GIFs in the roll-return momentum post.

One sketches Lesson 2's claim that the declared rule is Example 6.1's
position, holding TU, with 341 window days taken out, days on which TU went
nowhere, so the two rules earn nearly the same while the declared rule swings
less. The other sketches Lesson 3's roll: Chan's continuous close switches to
the June 2012 contract on 2012-03-21, the 7th trading day before the March
contract's last price, with a change that matches neither contract's own,
while the rebuild gives that day to March and switches the day after. What is
pinned is what a reader takes from each.

1. The swing sketch reads its counts and figures from
   :class:`chan.roll_momentum_whiteboard.Swing`. The test derives them again
   from :func:`chan.roll_momentum.roll_momentum`'s rows, the volatility as a
   population standard deviation scaled by √252, rather than trusting the
   sketch's own reading. Its ticks are schematic, and the test holds what is
   not: the share of ticks drawn flat, that the green ticks are the brown ones
   where the rule is long, and that each bracket spans its own stretches.
2. The switch sketch reads its days, price changes and counts from
   :class:`chan.roll_momentum_whiteboard.Switch`. The test derives them again
   from the strip's contracts, the 2012-05-11 save and
   :func:`chan.roll_momentum.held_contracts`, and the counts from
   :func:`chan.roll_momentum.check_against_save`. Every mark sits at its own
   trading day on the axis.

A made-up set of figures for each shows the words follow the run. The rules
every sketch shares are pinned here too: labels clear of ink in the hand font
and the fallback, each GIF's size, frames, loop and timing, both sketches'
slower pace, that two draws give the same bytes, and that each committed GIF
is a fresh draw, a comparison that runs only on macOS arm64 with Comic Sans
MS, as ``tests/test_usdcad_tests_whiteboard.py`` explains. The check that
``docs/figures`` holds exactly the GIFs the modules draw lives in
``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS` from
here.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import platform
import re

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import roll_momentum as run
from chan import roll_momentum_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.matlab_helpers import backshift
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.roll_momentum_whiteboard import (
    AXIS_X0,
    AXIS_X1,
    DECLARED_Y,
    EXAMPLE_Y,
    NEW_Y,
    OLD_Y,
    SAVE_Y,
    TICKS,
    Swing,
    Switch,
    flat_ticks,
    gif_name,
    main,
    make_roll_momentum_whiteboards,
    scenes,
    sketch_timeline,
    stretches,
    switch_x,
    tick_x,
)
from chan.roll_returns import load_strip
from chan.tu_momentum import TRADING_DAYS, read_sources
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

POST = REPO_ROOT / "blog" / "roll-momentum-lessons.md"

#: Every GIF in the order :func:`make_roll_momentum_whiteboards` writes them.
GIFS = [
    "roll_momentum_sketch_less_swing.gif",
    "roll_momentum_sketch_switch_day.gif",
]

#: The paragraph each GIF follows, by its opening words. The second opens the
#: two-item list whose second item opens "Every disagreement sits on the roll day."
FOLLOWS = (
    "What differs is the risk.",
    "1. **The returns agree.**",
)

SPEC = (
    "TU strip inputdatadaily_tu_20120813/, chan-mat, raw, saved 2012-08-14, and the "
    "2012-05-11 save of TU's continuous close; the window 2009-01-02 to 2012-08-13; the "
    "declared rule on the column-unit roll return above 0.03, and the front contract rebuilt "
    "rolling 7 rows before its last price"
)

SWING_LABELS = [
    "Example 6.1’s rule",
    "holds TU every day",
    "the declared rule",
    "flat on 341 days",
    "TU on 341 flat days: −0.001244",
    "TU on 572 long days: 0.050629",
    "average annual return / annual volatility",
    "declared: 0.013661 / 0.007575 = 1.80",
    "Example 6.1: 0.013351 / 0.011156 = 1.20",
    "nearly the same return,",
    "a smaller swing",
]

SWITCH_LABELS = [
    "03-20",
    "03-21",
    "03-22",
    "03-30",
    "days to last price",
    "8",
    "7",
    "6",
    "0",
    "March 2012 contract",
    "June 2012 contract",
    "rebuild: March through 03-21, June from 03-22",
    "Chan’s continuous close",
    "March’s close less 0.1407",
    "03-21: switches to June’s close, +0.0625",
    "neither March’s +0.0547 nor June’s +0.0546",
    "30 of 1,999 changes differ, all on the 7th day before a last price",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def strip():
    return load_strip(run.ROOT)


@pytest.fixture(scope="module")
def save():
    return read_sources()[1]


@pytest.fixture(scope="module")
def result(strip):
    return run.roll_momentum(strip)


@pytest.fixture(scope="module")
def check(strip, result, save):
    return run.check_against_save(strip, result, save)


@pytest.fixture(scope="module")
def swing(result) -> Swing:
    return Swing.from_result(result)


@pytest.fixture(scope="module")
def switch(strip, save, check) -> Switch:
    return Switch.from_data(strip.contracts, save, check)


@pytest.fixture(scope="module")
def every(swing, switch):
    return scenes(swing, switch)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, swing, switch):
    return make_roll_momentum_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), swing=swing, switch=switch
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text, nth: int = 0):
    return [s for s in scene.steps if isinstance(s, Label) and s.text == text][nth]


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

    def test_neither_draws_a_tint(self, every) -> None:
        """No pale tint, so none needs the green edge the shared rules ask of one."""
        assert not [fill for scene in every for fill in scene.fills]

    def test_neither_draws_in_the_colour_kept_for_a_loss(self, every) -> None:
        """Nothing here is a loss or a refusal, so no mark is red."""
        for scene in every:
            colours = {s.color for s in scene.steps if not hasattr(s, "x0")}
            assert LOST not in colours, scene.slug


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
        assert sketches.PACED == ("less_swing", "switch_day")
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, swing, switch) -> None:
        again = make_roll_momentum_whiteboards(out_dir=tmp_path, swing=swing, switch=switch)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "roll_momentum.png").exists()

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
            ), f"{path.name}: redraw with: uv run python -m chan.roll_momentum_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys, swing, switch
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(sketches.Swing, "from_run", classmethod(lambda cls: swing))
        monkeypatch.setattr(sketches.Switch, "from_run", classmethod(lambda cls: switch))
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]

    def test_the_run_readers_give_the_same_figures(self, swing, switch) -> None:
        """``from_run`` reads the committed files the fixtures read."""
        assert Swing.from_run() == swing
        assert Switch.from_run() == switch


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = _paragraphs()
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_the_switch_sketch_follows_the_whole_list(self) -> None:
        """It sits after the list's second item, not between the lead-in and the list."""
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(FOLLOWS[1])]
        assert "\n2. **Every disagreement sits on the roll day.**" in paragraphs[index]

    def test_each_sits_in_its_lesson(self) -> None:
        text = POST.read_text(encoding="utf-8")
        swing, switch = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lessons = [text.index(f"## Lesson {n}:") for n in (2, 3, 4)]
        assert lessons[0] < swing < lessons[1] < switch < lessons[2]

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

    def test_each_alt_text_names_its_pace(self, every) -> None:
        for scene in every:
            alt = _alt(scene)
            assert "drawn slowly" in alt and "twelve seconds" in alt, scene.slug

    def test_no_alt_text_calls_chans_series_the_save(self, every) -> None:
        for scene in every:
            assert "save" not in _alt(scene), scene.slug

    def test_the_footer_links_the_sketch_code_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        code = f"[the whiteboard sketches]({base}src/chan/roll_momentum_whiteboard.py)"
        tests = f"[what the sketches draw]({base}tests/test_roll_momentum_whiteboard.py)"
        assert code in footer and tests in footer

    def test_the_module_says_which_parts_are_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "The first sketch is schematic in its ticks and figured in its words." in doc
        assert "The second is not schematic in its days or its numbers" in doc
        assert "Its rows are not prices to scale." in doc


# --- Lesson 2: same return, less swing ----------------------------------------


class TestTheSwing:
    def test_it_is_the_runs(self, result, swing) -> None:
        """Derived again from the run's rows, the volatility as a population
        standard deviation, which is what ``smartstd`` takes."""
        held = backshift(1, result.position)[result.window]
        market = result.market[result.window]
        flat = held == 0
        assert (swing.flat_days, swing.long_days) == (int(flat.sum()), int((held == 1).sum()))
        assert swing.flat_return == pytest.approx(np.prod(1 + market[flat]) - 1, abs=1e-15)
        assert swing.long_return == pytest.approx(np.prod(1 + market[~flat]) - 1, abs=1e-15)
        for daily, average, volatility, sharpe in (
            (
                result.daily[result.window],
                swing.declared_average,
                swing.declared_volatility,
                swing.declared_sharpe,
            ),
            (
                result.example_daily[result.window],
                swing.example_average,
                swing.example_volatility,
                swing.example_sharpe,
            ),
        ):
            assert average == pytest.approx(TRADING_DAYS * np.mean(daily), rel=1e-12)
            assert volatility == pytest.approx(
                math.sqrt(TRADING_DAYS) * np.std(daily, ddof=0), rel=1e-12
            )
            assert sharpe == pytest.approx(average / volatility, rel=1e-12)

    def test_its_figures_at_the_posts_precision(self, swing) -> None:
        assert (swing.flat_days, swing.long_days, swing.days) == (341, 572, 913), SPEC
        assert f"{swing.flat_return:.6f}" == "-0.001244", SPEC
        assert f"{swing.long_return:.6f}" == "0.050629", SPEC
        assert f"{swing.declared_average:.6f}" == "0.013661", SPEC
        assert f"{swing.declared_volatility:.6f}" == "0.007575", SPEC
        assert f"{swing.declared_sharpe:.2f}" == "1.80", SPEC
        assert f"{swing.example_average:.6f}" == "0.013351", SPEC
        assert f"{swing.example_volatility:.6f}" == "0.011156", SPEC
        assert f"{swing.example_sharpe:.2f}" == "1.20", SPEC

    def test_the_long_days_carry_the_declared_rules_whole_return(self, result, swing) -> None:
        """The words beside the green brackets are the declared rule's own
        compounded return over the window, not only TU's on those days."""
        whole = np.prod(1 + result.daily[result.window]) - 1
        assert swing.long_return == pytest.approx(whole, abs=1e-15)

    def test_the_closing_words_hold_on_the_run(self, swing) -> None:
        """ "Nearly the same return" and "a smaller swing" describe the run,
        and these bounds keep them true if a figure is re-pinned: the average
        returns sit within 3 percent of each other, and the declared rule's
        volatility is under three quarters of Example 6.1's."""
        assert abs(swing.declared_average / swing.example_average - 1) < 0.03, SPEC
        assert swing.declared_volatility / swing.example_volatility < 0.75, SPEC

    def test_the_window_opens_flat_as_the_sketch_does(self, result, every) -> None:
        assert result.held_position[0] == 0
        assert stretches_of(every[0])[0].startswith("flat")

    def test_a_rule_not_fully_long_is_refused(self, result) -> None:
        """The brown words say Example 6.1 holds TU every day, which is false
        unless every tranche is long on every window row."""
        positions = result.example_positions.copy()
        positions[np.flatnonzero(result.window)[100]] = 23
        with pytest.raises(ValueError, match="fully long"):
            Swing.from_result(dataclasses.replace(result, example_positions=positions))

    def test_a_short_declared_rule_is_refused(self, result) -> None:
        """The green row draws no short day, so a short one is refused."""
        position = result.position.copy()
        position[np.flatnonzero(result.window)[100]] = -1
        with pytest.raises(ValueError, match="short"):
            Swing.from_result(dataclasses.replace(result, position=position))


def stretches_of(scene) -> list[str]:
    """The green row's strokes in drawing order, by their names."""
    return [s.gid for s in scene.strokes if re.fullmatch(r"(flat|long)-\d", s.gid)]


#: A made-up swing, so the words that should follow the run do.
OTHER_SWING = Swing(
    flat_days=100,
    long_days=1900,
    flat_return=0.0123456,
    long_return=-0.25,
    declared_average=0.02,
    declared_volatility=0.04,
    declared_sharpe=0.5,
    example_average=0.03,
    example_volatility=0.02,
    example_sharpe=1.5,
)


class TestTheSwingSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "Same return, less swing"
        assert every[0].labels == SWING_LABELS

    def test_its_words_follow_the_run(self, switch) -> None:
        labels = scenes(OTHER_SWING, switch)[0].labels
        assert [labels[k] for k in (3, 4, 5, 7, 8)] == [
            "flat on 100 days",
            "TU on 100 flat days: 0.012346",
            "TU on 1,900 long days: −0.250000",
            "declared: 0.020000 / 0.040000 = 0.50",
            "Example 6.1: 0.030000 / 0.020000 = 1.50",
        ]

    def test_its_colours(self, every) -> None:
        """Brown is Example 6.1's rule and green the declared rule, as in the
        post's chart. Grey marks the flat days."""
        scene = every[0]
        found = {s.gid: s.color for s in scene.strokes}
        assert found.pop("example") == ACCENT
        for gid, colour in found.items():
            assert colour == (MUTED if gid.startswith("flat") else GOOD), gid
        assert [_label(scene, text).color for text in SWING_LABELS] == [
            ACCENT,
            ACCENT,
            GOOD,
            MUTED,
            MUTED,
            GOOD,
            MUTED,
            GOOD,
            ACCENT,
            INK,
            INK,
        ]

    def test_each_rule_is_named_in_words_as_well_as_colour(self, every) -> None:
        """Brown and green can look alike, so each row and each fraction
        carries its rule's name."""
        scene = every[0]
        assert _labels_of(scene, "example")[:2] == SWING_LABELS[:2]
        assert SWING_LABELS[7].startswith("declared:")
        assert SWING_LABELS[8].startswith("Example 6.1:")

    def test_the_flat_share_of_ticks_is_the_flat_share_of_days(self, every, swing) -> None:
        scene = every[0]
        assert flat_ticks(swing) == round(TICKS * 341 / 913) == 18
        width = (sketches.ROW_X[1] - sketches.ROW_X[0]) / TICKS
        grey = sum(
            _stroke(scene, g).x.max() - _stroke(scene, g).x.min()
            for g in stretches_of(scene)
            if g.startswith("flat")
        )
        assert grey == pytest.approx(flat_ticks(swing) * width)

    def test_the_rows_alternate_flat_and_long_across_the_whole_row(self, every, swing) -> None:
        scene = every[0]
        names = stretches_of(scene)
        assert names == [f"{k}-{n}" for n in range(1, 4) for k in ("flat", "long")]
        edges = [(_stroke(scene, g).x.min(), _stroke(scene, g).x.max()) for g in names]
        assert edges[0][0] == pytest.approx(sketches.ROW_X[0])
        assert edges[-1][1] == pytest.approx(sketches.ROW_X[1])
        for (_, right), (left, _) in zip(edges, edges[1:], strict=False):
            assert right == pytest.approx(left)
        assert [kind for kind, _, _ in stretches(swing)] == ["flat", "long"] * 3

    def test_the_grey_stretches_are_flat_at_zero(self, every) -> None:
        scene = every[0]
        for gid in stretches_of(scene):
            if gid.startswith("flat"):
                assert set(_stroke(scene, gid).y) == {DECLARED_Y}, gid

    def test_the_green_ticks_are_the_brown_ones_where_the_rule_is_long(self, every) -> None:
        """Where the rule is long it earns TU's own return, so each green tick
        reaches as far as the brown tick above it, and the brown row ticks on
        every day the green row is flat."""
        scene = every[0]
        brown = _stroke(scene, "example")
        brown_ticks = {
            (round(x, 9), round(y - EXAMPLE_Y, 9))
            for x, y in zip(brown.x, brown.y, strict=True)
            if y != EXAMPLE_Y
        }
        green_ticks = set()
        for gid in stretches_of(scene):
            if gid.startswith("long"):
                stroke = _stroke(scene, gid)
                green_ticks |= {
                    (round(x, 9), round(y - DECLARED_Y, 9))
                    for x, y in zip(stroke.x, stroke.y, strict=True)
                    if y != DECLARED_Y
                }
        assert green_ticks and green_ticks < brown_ticks
        tops = {x for x, _ in brown_ticks} - {x for x, _ in green_ticks}
        assert len({round(tick_x(k), 9) for k in range(TICKS)} & tops) == 18

    def test_each_bracket_spans_its_own_stretch(self, every) -> None:
        scene = every[0]
        for n in range(1, 4):
            for kind, y in (
                ("flat", sketches.FLAT_BRACKET_Y),
                ("long", sketches.LONG_BRACKET_Y),
            ):
                part, bracket = _stroke(scene, f"{kind}-{n}"), _stroke(scene, f"{kind}-bracket-{n}")
                assert (bracket.x.min(), bracket.x.max()) == pytest.approx(
                    (part.x.min() + sketches.BRACKET_GAP, part.x.max() - sketches.BRACKET_GAP)
                ), (kind, n)
                assert np.median(bracket.y) == pytest.approx(y)
        assert DECLARED_Y > sketches.FLAT_BRACKET_Y > sketches.LONG_BRACKET_Y

    def test_the_words_sit_right_of_the_rows_at_their_heights(self, every) -> None:
        scene = every[0]
        for text, y in (
            (SWING_LABELS[0], EXAMPLE_Y),
            (SWING_LABELS[2], DECLARED_Y),
            (SWING_LABELS[4], sketches.FLAT_BRACKET_Y),
            (SWING_LABELS[5], sketches.LONG_BRACKET_Y),
        ):
            label = _label(scene, text)
            assert label.x > sketches.ROW_X[1] and label.ha == "left", text
            assert abs(label.y - y) < 0.2, text
        assert EXAMPLE_Y > DECLARED_Y

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[0])
        for phrase in (
            "A brown row of short up and down ticks",
            "a schematic stand-in for TU’s daily returns",
            "It is green where its ticks match the brown ones",
            "it flattens to a grey line in three stretches, the first at the start",
            "the number and places of the stretches are schematic",
            "the grey share of the row is about the share of window days the rule sits flat",
            "Green and grey words beside the row read “the declared rule” and “flat on 341 days”",
            "Grey brackets under the three grey stretches carry grey words reading",
            "green brackets under the three green stretches carry green words reading",
            "Grey words at the bottom left read “average annual return / annual volatility”",
            "then a green line reads “declared:",
            "and a brown one “Example 6.1:",
            "Black words at the bottom right read “nearly the same return,”",
            "the finished drawing holds for twelve seconds.",
        ):
            assert phrase in alt, phrase

    def test_each_rows_words_stack_name_over_claim(self, every) -> None:
        """The rule's name sits above its row's line and the claim below it,
        and the declared fraction sits above Example 6.1's."""
        scene = every[0]
        for name, claim, y in (
            (SWING_LABELS[0], SWING_LABELS[1], EXAMPLE_Y),
            (SWING_LABELS[2], SWING_LABELS[3], DECLARED_Y),
        ):
            assert _label(scene, name).y > y > _label(scene, claim).y, name
        caption, declared, example = (_label(scene, t) for t in SWING_LABELS[6:9])
        assert caption.y > declared.y > example.y
        assert caption.x == declared.x == example.x == sketches.ROW_X[0]
        assert caption.y < sketches.LONG_BRACKET_Y

    def test_each_bracket_has_an_upright_tick_at_each_end(self, every) -> None:
        scene = every[0]
        for stroke in scene.strokes:
            if "bracket" in stroke.gid:
                middle = np.median(stroke.y)
                for end in (stroke.x.min(), stroke.x.max()):
                    ys = stroke.y[np.isclose(stroke.x, end)]
                    assert ys.max() - middle == pytest.approx(0.1), stroke.gid
                    assert middle - ys.min() == pytest.approx(0.1), stroke.gid

    def test_the_grey_stretches_are_thicker_than_the_ticks(self, every) -> None:
        scene = every[0]
        grey = [s for s in scene.strokes if re.fullmatch(r"flat-\d", s.gid)]
        green = [s for s in scene.strokes if re.fullmatch(r"long-\d", s.gid)]
        assert {s.width for s in grey} == {3.0}
        assert all(s.width < 3.0 for s in green)


# --- Lesson 3: where the rebuild and Chan's continuous close switch -----------


class TestTheSwitch:
    def test_it_is_the_runs(self, strip, save, check, switch) -> None:
        """Derived again from the strip's contracts and the save's close."""
        contracts = strip.contracts
        march, june = contracts["TU-2012H"], contracts["TU-2012M"]
        held = run.held_contracts(contracts)
        assert str(march.last_valid_index().date()) == switch.last == "2012-03-30", SPEC
        assert (switch.before, switch.switch, switch.after) == (
            "2012-03-20",
            "2012-03-21",
            "2012-03-22",
        ), SPEC
        assert switch.days == tuple(
            str(d.date()) for d in contracts.loc["2012-03-19":"2012-03-30"].index
        )
        assert (held["2012-03-21"], held["2012-03-22"]) == ("TU-2012H", "TU-2012M")
        assert (switch.old, switch.new) == ("TU-2012H", "TU-2012M")
        assert (switch.rebuild_switch, switch.rebuild_after) == ("TU-2012H", "TU-2012M")
        assert switch.shift == pytest.approx(march["2012-03-20"] - save["2012-03-20"], abs=1e-12)
        assert save["2012-03-21"] == june["2012-03-21"]
        assert switch.save_change == pytest.approx(
            save["2012-03-21"] - save["2012-03-20"], abs=1e-12
        )
        assert switch.old_change == pytest.approx(
            march["2012-03-21"] - march["2012-03-20"], abs=1e-12
        )
        assert switch.new_change == pytest.approx(
            june["2012-03-21"] - june["2012-03-20"], abs=1e-12
        )
        assert (switch.changes, switch.differ, switch.on_roll_row) == (
            check.changes,
            check.beyond_rounding,
            check.beyond_rounding_on_jump_row,
        )

    def test_its_figures_at_the_files_precision(self, switch) -> None:
        assert f"{switch.shift:.4f}" == "0.1407", SPEC
        assert f"{switch.save_change:+.4f}" == "+0.0625", SPEC
        assert f"{switch.old_change:+.4f}" == "+0.0547", SPEC
        assert f"{switch.new_change:+.4f}" == "+0.0546", SPEC
        assert (switch.changes, switch.differ, switch.on_roll_row) == (1999, 30, 30), SPEC

    def test_the_counts_under_the_dates_are_days_to_the_last_price(self, switch) -> None:
        assert (
            [
                switch.before_last(d)
                for d in (switch.before, switch.switch, switch.after, switch.last)
            ]
            == [run.ROLL_ROWS + 1, run.ROLL_ROWS, run.ROLL_ROWS - 1, 0]
            == [8, 7, 6, 0]
        )

    def test_chans_change_matches_neither_contracts_own(self, switch) -> None:
        """The words say neither, so both gaps are past the files' rounding."""
        for own in (switch.old_change, switch.new_change):
            assert abs(switch.save_change - own) > run.SAVE_ROUNDING

    def test_chans_close_sits_below_march_on_the_day_before(self, save, strip, switch) -> None:
        """It is shifted, never on the March line: 0.1407 below March's close."""
        march = strip.contracts["TU-2012H"]
        assert save["2012-03-20"] < march["2012-03-20"]
        assert switch.shift > 100 * run.SAVE_ROUNDING

    def test_a_save_off_the_new_contract_is_refused(self, strip, save, check) -> None:
        """The words say Chan's close switches to June's on 03-21."""
        moved = save.copy()
        moved["2012-03-21"] += 0.01
        with pytest.raises(ValueError, match="does not equal"):
            Switch.from_data(strip.contracts, moved, check)

    def test_a_roll_the_rebuild_does_not_make_is_refused(
        self, strip, save, check, monkeypatch
    ) -> None:
        """The words say the rebuild gives the switch day to March and the next
        day to June, which a roll a row later would make false."""
        original = run.held_contracts
        monkeypatch.setattr(run, "held_contracts", lambda c: original(c, 6))
        with pytest.raises(ValueError, match="does not roll"):
            Switch.from_data(strip.contracts, save, check)

    def test_a_roll_a_row_earlier_is_refused(self, strip, save, check, monkeypatch) -> None:
        """A rebuild already on June on the switch day would make "March
        through 03-21" false, though it still rolls between two contracts."""
        original = run.held_contracts
        monkeypatch.setattr(run, "held_contracts", lambda c: original(c, 8))
        with pytest.raises(ValueError, match="does not roll"):
            Switch.from_data(strip.contracts, save, check)


class TestTheHelpers:
    @pytest.mark.parametrize(
        ("n", "word"),
        [
            (1, "1st"),
            (2, "2nd"),
            (3, "3rd"),
            (4, "4th"),
            (7, "7th"),
            (11, "11th"),
            (12, "12th"),
            (13, "13th"),
            (21, "21st"),
            (22, "22nd"),
            (23, "23rd"),
            (111, "111th"),
        ],
    )
    def test_ordinal(self, n, word) -> None:
        assert sketches._ordinal(n) == word

    def test_change_signs_every_value(self) -> None:
        assert [sketches._change(v) for v in (0.0625, 0.0, -0.0123)] == [
            "+0.0625",
            "+0.0000",
            "−0.0123",
        ]


#: A made-up switch, so the words that should follow the run do.
OTHER_SWITCH = Switch(
    old="TU-2010Z",
    new="TU-2011H",
    days=("2010-12-15", "2010-12-16", "2010-12-17", "2010-12-20", "2010-12-21"),
    before="2010-12-16",
    switch="2010-12-17",
    after="2010-12-20",
    last="2010-12-21",
    rebuild_switch="TU-2010Z",
    rebuild_after="TU-2011H",
    shift=0.25,
    save_change=-0.0123,
    old_change=0.0001,
    new_change=-0.02,
    changes=2345,
    differ=12,
    on_roll_row=11,
)


class TestTheSwitchSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "The rebuild and Chan’s continuous close switch"
        assert every[1].labels == SWITCH_LABELS

    def test_its_words_follow_the_run(self, swing) -> None:
        labels = scenes(swing, OTHER_SWITCH)[1].labels
        assert labels == [
            "12-16",
            "12-17",
            "12-20",
            "12-21",
            "days to last price",
            "3",
            "2",
            "1",
            "0",
            "December 2010 contract",
            "March 2011 contract",
            "rebuild: December through 12-17, March from 12-20",
            "Chan’s continuous close",
            "December’s close less 0.2500",
            "12-17: switches to March’s close, −0.0123",
            "neither December’s +0.0001 nor March’s −0.0200",
            "12 of 2,345 changes differ, 11 on the 7th day before a last price",
        ]

    def test_its_colours(self, every) -> None:
        """Chan's continuous close is brown, the series Example 6.1 trades and
        the one the sketch points at, and its switching change is brown too,
        never the red kept for a loss."""
        scene = every[1]
        assert {s.gid: s.color for s in scene.strokes} == {
            "axis": MUTED,
            "old": MUTED,
            "new": MUTED,
            "rebuild-old": INK,
            "rebuild-new": INK,
            "save-before": ACCENT,
            "guide-before": MUTED,
            "save-switch": ACCENT,
            "guide-switch": MUTED,
            "save-after": ACCENT,
        }
        assert [_label(scene, text).color for text in SWITCH_LABELS] == [MUTED] * 11 + [
            INK,
            ACCENT,
            ACCENT,
            ACCENT,
            INK,
            INK,
        ]

    def test_the_axis_ticks_once_on_every_trading_day(self, every, switch) -> None:
        """The alt text says one tick a day."""
        axis = _stroke(every[1], "axis")
        tops = np.round(axis.x[axis.y > sketches.AXIS_Y + 1e-9], 9)
        assert sorted(set(tops)) == pytest.approx([switch_x(switch, d) for d in switch.days])
        assert axis.y.min() == sketches.AXIS_Y
        assert axis.y.max() == pytest.approx(sketches.AXIS_Y + 0.08)
        assert (axis.x.min(), axis.x.max()) == pytest.approx((AXIS_X0, AXIS_X1))

    def test_switch_x_is_affine_in_the_count_of_trading_days(self, switch) -> None:
        xs = np.array([switch_x(switch, d) for d in switch.days])
        assert (xs[0], xs[-1]) == pytest.approx((AXIS_X0, AXIS_X1))
        assert np.diff(xs) == pytest.approx(np.full(len(xs) - 1, xs[1] - xs[0]))

    def test_every_date_and_count_sits_under_its_own_day(self, every, switch) -> None:
        scene = every[1]
        dates = (switch.before, switch.switch, switch.after, switch.last)
        for date, text, count in zip(dates, SWITCH_LABELS[:4], SWITCH_LABELS[5:9], strict=True):
            for label in (_label(scene, text), _label(scene, count)):
                assert label.ha == "center", text
                assert label.x == pytest.approx(switch_x(switch, date)), text
            assert _label(scene, text).y > _label(scene, count).y > sketches.CLOSING_Y

    def test_the_rebuild_reads_march_through_the_switch_day_and_june_after(
        self, every, switch
    ) -> None:
        scene = every[1]
        x = lambda d: switch_x(switch, d)  # noqa: E731
        old, new = _stroke(scene, "rebuild-old"), _stroke(scene, "rebuild-new")
        assert set(old.y) == {OLD_Y} and set(new.y) == {NEW_Y}
        assert (old.x.min(), old.x.max()) == pytest.approx((AXIS_X0, x(switch.switch)))
        assert (new.x.min(), new.x.max()) == pytest.approx((x(switch.after), AXIS_X1))
        assert old.width > _stroke(scene, "old").width

    def test_the_contract_lines_run_the_axis_and_march_ends_at_its_last_price(
        self, every, switch
    ) -> None:
        scene = every[1]
        old, new = _stroke(scene, "old"), _stroke(scene, "new")
        assert (old.x.min(), old.x.max()) == pytest.approx((AXIS_X0, switch_x(switch, switch.last)))
        assert (new.x.min(), new.x.max()) == pytest.approx((AXIS_X0, AXIS_X1))
        assert old.y.max() > OLD_Y > old.y.min()  # the end tick

    def test_chans_close_is_its_own_line_never_on_march(self, every, switch) -> None:
        scene = every[1]
        x = lambda d: switch_x(switch, d)  # noqa: E731
        parts = [_stroke(scene, g) for g in ("save-before", "save-switch", "save-after")]
        for part in parts:
            assert set(part.y) == {SAVE_Y}, part.gid
        assert NEW_Y < SAVE_Y < OLD_Y
        spans = [(p.x.min(), p.x.max()) for p in parts]
        assert spans == pytest.approx(
            [
                (AXIS_X0, x(switch.before)),
                (x(switch.before), x(switch.switch)),
                (x(switch.switch), AXIS_X1),
            ]
        )
        assert parts[1].width > parts[0].width == parts[2].width

    def test_the_guides_tie_chans_close_to_march_then_june(self, every, switch) -> None:
        scene = every[1]
        before, after = _stroke(scene, "guide-before"), _stroke(scene, "guide-switch")
        assert np.allclose(before.x, switch_x(switch, switch.before))
        assert np.allclose(after.x, switch_x(switch, switch.switch))
        assert SAVE_Y < before.y.min() < before.y.max() < OLD_Y
        assert NEW_Y < after.y.min() < after.y.max() < SAVE_Y
        assert before.dashed and after.dashed

    def test_the_words_sit_beside_what_they_name(self, every, switch) -> None:
        scene = every[1]
        shift = _label(scene, SWITCH_LABELS[13])
        assert shift.ha == "right" and shift.x < switch_x(switch, switch.before)
        assert SAVE_Y < shift.y < OLD_Y
        for text in SWITCH_LABELS[14:16]:
            label = _label(scene, text)
            assert label.ha == "left" and label.x > switch_x(switch, switch.switch), text
            assert SAVE_Y < label.y < OLD_Y, text
        rebuild = _label(scene, SWITCH_LABELS[11])
        assert rebuild.y > OLD_Y
        for text, y in zip(SWITCH_LABELS[9:11], (OLD_Y, NEW_Y), strict=True):
            label = _label(scene, text)
            assert label.y == y and label.x < AXIS_X0, text
        assert _label(scene, SWITCH_LABELS[12]).y == SAVE_Y

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[1])
        for phrase in (
            "A grey axis of TU’s trading days runs along the bottom from 2012-03-19 to 2012-03-30, "
            "one tick a day",
            "A thick black line covers the March line from 03-19 to 03-21",
            "a second thick black line covers the June line from 03-22 to 03-30",
            "a brown line labelled “Chan’s continuous close” runs to 03-20",
            "a dashed grey guide rises to the March line",
            "The brown line thickens from 03-20 to 03-21",
            "a second dashed grey guide drops to the June line",
            "each contract’s own change that day",
            "with grey dates under four ticks",
            "Grey words under the dates read “days to last price”",
            "with black words above reading “rebuild:",
            "with brown words reading “March’s close less 0.1407”",
            "Brown words beside it read “03-21: switches to June’s close, +0.0625”",
            "black words under them read “neither March’s +0.0547 nor June’s +0.0546”",
            "Black words at the bottom read “30 of 1,999 changes differ",
            "The rows say which contract each series reads rather than drawing prices to scale",
            "every mark sits at its own trading day",
            "the finished drawing holds for twelve seconds.",
        ):
            assert phrase in alt, phrase
        assert "spans" not in alt
