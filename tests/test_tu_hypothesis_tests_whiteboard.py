"""The pins for the two whiteboard GIFs in the TU hypothesis tests post.

One sketches Lesson 4's point that the script's third test adds its shuffled
trades to the real positions rather than to ``pos_sim``, so it cannot fail,
and one Lesson 5's point that a drifting series keeps the rule long on most
days, so the rule collects the drift.

1. The wrong-array sketch draws the third test as written as boxes joined by
   arrows. What is pinned is which box each arrow leaves and enters, that only
   the arrow toward ``pos_sim`` is dashed and that it stops short of that box,
   and the figures it prints: the observed mean, every simulated mean 0, and
   the 10 draws run as written, each returning 0.
2. The mostly-long sketch draws two schematic random walks, with and without
   TU's drift. What is pinned is that both walks are built from TU's daily
   mean and standard deviation on one seed, that both lines share one scale,
   that each bracket spans its 250 days and ends in an arrow pointing the way
   the line moved over them, in green up and red down, that eight of ten point
   up with the drift and five without it, and the two shares of long days it
   prints.

Every figure a sketch prints is read from the run on Chan's committed file,
so the tests recompute each through :mod:`chan.tu_hypothesis_tests`'s and
:mod:`chan.tu_momentum`'s own functions rather than a frozen copy. Made-up
figures check that the words and title follow the data.

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

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import tu_hypothesis_tests as tests
from chan import tu_hypothesis_tests_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.tu_hypothesis_tests_whiteboard import (
    ARROW_RISE,
    DRIFTING_BRACKETS,
    DRIFTING_START,
    FLAT_BRACKETS,
    FLAT_START,
    MEANS_BOX,
    PER_RETURN,
    POS_BOX,
    POS_SIM_BOX,
    RET_SIM_BOX,
    TRADES_BOX,
    WALK_SEED,
    WINDOWS,
    SketchFigures,
    day_x,
    gif_name,
    long_share,
    main,
    make_tu_hypothesis_tests_whiteboards,
    scenes,
    sketch_timeline,
    walk,
    window_changes,
)
from chan.tu_momentum import (
    HOLD_DAYS,
    LOOKBACK,
    market_returns,
    positions,
    read_sources,
    signals,
    strategy_returns,
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
    timeline,
)

POST = REPO_ROOT / "blog" / "tu-hypothesis-tests-lessons.md"

#: Every GIF in the order :func:`make_tu_hypothesis_tests_whiteboards` writes them.
GIFS = [
    "tu_hypothesis_tests_sketch_wrong_array.gif",
    "tu_hypothesis_tests_sketch_mostly_long.gif",
]

#: The paragraph each GIF follows, by its opening words: Lesson 4's paragraph
#: on the script's third test, and Lesson 5's paragraph on the mechanism.
WRONG_ARRAY_PARAGRAPH = "The script writes the third test so that it returns 0 whatever the data."
MOSTLY_LONG_PARAGRAPH = "**The mechanism is the rule itself.**"

WRONG_ARRAY_LABELS = [
    "shuffled trades",
    "pos, the real positions",
    "added here",
    "pos_sim = zeros",
    "never reached",
    "ret_sim built from pos_sim = 0",
    "every simulated mean: 0",
    "observed mean 6.626644e-05 > 0",
    "10 draws run as written: every return 0",
]

MOSTLY_LONG_LABELS = [
    "schematic, with TU’s drift",
    "up: long",
    "down: short",
    "long on 0.804654",
    "of its entry days",
    "same noise, no drift",
    "long on 0.502401",
    "once the mean is removed",
    "shares from 1,000 simulated series",
    "long most days, so it collects the drift",
]

#: The counts the mostly-long alt text spells out, in words.
WORDS = {5: "five", 8: "eight", 10: "ten"}

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def strategy():
    """Example 6.1 on TU, through ``chan.tu_momentum``'s exported functions."""
    cl = read_sources()[1].to_numpy(dtype=float)
    market = market_returns(cl)
    longs, shorts = signals(cl, LOOKBACK)
    held = positions(longs, shorts, HOLD_DAYS)
    return {
        "closes": cl,
        "market": market,
        "longs": longs,
        "shorts": shorts,
        "held": held,
        "daily": strategy_returns(held, market, HOLD_DAYS),
    }


@pytest.fixture(scope="module")
def figures():
    return SketchFigures.from_run()


@pytest.fixture(scope="module")
def every(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def wrong_array(every):
    return every[0]


@pytest.fixture(scope="module")
def mostly_long(every):
    return every[1]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_tu_hypothesis_tests_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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


def _inside(x: float, y: float, box: tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = box
    return x0 <= x <= x1 and y0 <= y <= y1


def _windows(scene, name: str):
    return [s for s in scene.strokes if s.gid.startswith(f"{name}-window-")]


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
        tints = [fill for scene in every for fill in scene.fills if fill.color == whiteboard.TINT]
        assert tints == []

    def test_every_colour_is_a_shared_ink(self, every) -> None:
        """The post's chart has not moved to ``chan.palette``, so neither have its sketches."""
        inks = {INK, MUTED, ACCENT, GOOD, LOST}
        for scene in every:
            for step in scene.steps:
                assert step.color in inks, (scene.slug, getattr(step, "gid", None) or step.text)


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
        assert sketches.PACED == ("wrong_array", "mostly_long")
        for scene in every:
            frames = sketch_timeline(scene)
            paced = scene.slug in sketches.PACED
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            assert labels, scene.slug
            assert {f.ms for f in labels} == {
                sketches.PACED_LABEL_MS if paced else whiteboard.LABEL_MS
            }, scene.slug
            assert frames[-1].ms == (sketches.PACED_HOLD_MS if paced else HOLD_MS)
            assert [(f.done, f.partial) for f in frames] == [
                (f.done, f.partial) for f in timeline(scene)
            ]

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_tu_hypothesis_tests_whiteboards(out_dir=tmp_path)
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
        assert not "tu_hypothesis_tests.png".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.tu_hypothesis_tests_whiteboard"


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
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (wrong,) = [k for k, p in enumerate(paragraphs) if p.startswith(WRONG_ARRAY_PARAGRAPH)]
        (mostly,) = [k for k, p in enumerate(paragraphs) if p.startswith(MOSTLY_LONG_PARAGRAPH)]
        for index, name in zip((wrong, mostly), GIFS, strict=True):
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_the_wrong_array_sketch_sits_in_lesson_4_and_the_mostly_long_in_lesson_5(
        self,
    ) -> None:
        text = POST.read_text(encoding="utf-8")
        wrong, mostly = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lesson_4 = text.index("## Lesson 4:")
        lesson_5 = text.index("## Lesson 5:")
        after = text.index("## What this replication cannot say")
        assert lesson_4 < wrong < lesson_5 < mostly < after

    def test_each_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count("(../docs/figures/tu_hypothesis_tests.png)") == 1

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
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_the_footer_links_the_sketch_code_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        assert (
            f"[the whiteboard sketches]({base}src/chan/tu_hypothesis_tests_whiteboard.py)" in footer
        )
        assert (
            f"[what the sketches draw]({base}tests/test_tu_hypothesis_tests_whiteboard.py)"
            in footer
        )

    def test_the_module_says_the_second_sketch_is_schematic(self) -> None:
        assert "The second sketch's lines are schematic." in (sketches.__doc__ or "")

    def test_the_drawing_itself_says_the_lines_are_schematic(self, mostly_long) -> None:
        """A Substack reader does not see the alt text, so the frame says it."""
        assert mostly_long.labels[0].startswith("schematic")


# --- The figures, read from the run ----------------------------------------------


class TestTheFigures:
    def test_the_long_shares_are_the_second_tests_first_1000_series(self, strategy) -> None:
        """The same draws and the same signal as
        ``tests/test_tu_hypothesis_tests.py::test_a_drifting_series_is_long_on_most_signal_days``,
        which pins the two shares, recomputed here through the run's own sampler."""
        moments = tests.script_moments(strategy["market"])
        params = tests.pearson_iv_parameters(
            moments.mean, moments.std, moments.skewness, moments.kurtosis
        )
        uniforms = np.random.default_rng(tests.RETURNS_SEED).random((1_000, 2_000))
        simulated = tests.pearson_iv_draws(params, uniforms)
        found = SketchFigures.from_run()
        for draws, share in (
            (simulated, found.drifting_share),
            (simulated - moments.mean, found.flat_share),
        ):
            cl_sim = np.cumprod(1 + draws, axis=1) - 1
            longs = cl_sim[:, LOOKBACK:] > cl_sim[:, :-LOOKBACK]
            shorts = cl_sim[:, LOOKBACK:] < cl_sim[:, :-LOOKBACK]
            expected = (longs.sum(axis=1) / (longs.sum(axis=1) + shorts.sum(axis=1))).mean()
            assert share == expected

    def test_the_first_1000_series_are_the_first_batch_of_the_second_test(self) -> None:
        """The run draws its 10,000 series in batches of 1,000 from one generator,
        so the first batch is the 1,000 series the shares read."""
        assert sketches.SHARE_SERIES == tests.RETURNS_BATCH == 1_000

    def test_long_share_counts_long_days_over_long_and_short_days(self) -> None:
        """A made-up series up 3 days, flat 1 and down 2, with a lookback of 1.

        Its price moves up, up, up, flat, down, down, so of the five days with
        a day before them three are long, one is neither and two are short.
        """
        returns = np.array([[0.0, 0.01, 0.01, 0.01, 0.0, -0.01, -0.01]])
        assert long_share(returns, lookback=1) == 3 / 5

    def test_the_observed_mean_is_the_strategy_s(self, figures, strategy) -> None:
        assert figures.observed_mean == float(strategy["daily"].mean())
        assert figures.observed_mean > 0

    def test_the_as_written_draws_are_the_run_s(self, figures, strategy) -> None:
        written = tests.randomized_trades_as_written(
            strategy["longs"], strategy["shorts"], strategy["held"], strategy["market"]
        )
        assert figures.as_written_means == tuple(written.means)
        assert figures.largest_return == written.largest_return == 0.0
        assert figures.as_written_draws == tests.AS_WRITTEN_DRAWS

    def test_the_lines_carry_tu_s_daily_mean_and_standard_deviation(
        self, figures, strategy
    ) -> None:
        moments = tests.script_moments(strategy["market"])
        assert (figures.daily_mean, figures.daily_std) == (moments.mean, moments.std)
        z = np.random.default_rng(WALK_SEED).standard_normal(LOOKBACK * WINDOWS)
        np.testing.assert_array_equal(
            walk(figures, drift=True),
            np.concatenate([[0.0], np.cumsum(moments.std * z + moments.mean)]),
        )
        np.testing.assert_array_equal(
            walk(figures, drift=False), np.concatenate([[0.0], np.cumsum(moments.std * z)])
        )

    def test_over_250_days_the_drift_is_about_0_87_noise_standard_deviations(self, figures) -> None:
        """The figure the module docstring and README give for why the lines are noisy."""
        ratio = LOOKBACK * figures.daily_mean / (math.sqrt(LOOKBACK) * figures.daily_std)
        assert round(ratio, 2) == 0.87

    def test_eight_of_ten_windows_rise_with_the_drift_and_five_without(self, figures) -> None:
        assert len(window_changes(figures, drift=True)) == WINDOWS == 10
        assert int((window_changes(figures, drift=True) > 0).sum()) == 8
        assert int((window_changes(figures, drift=False) > 0).sum()) == 5
        assert (window_changes(figures, drift=True) != 0).all()
        assert (window_changes(figures, drift=False) != 0).all()


# --- Lesson 4: the shuffled trades land in the wrong place ------------------------


class TestTheWrongArraySketch:
    def test_its_words(self, wrong_array) -> None:
        assert wrong_array.labels == WRONG_ARRAY_LABELS
        assert wrong_array.title == "The shuffled trades land in the wrong place"

    def test_its_numbers_are_read_from_the_run(self, wrong_array, figures) -> None:
        labels = wrong_array.labels
        assert f"observed mean {figures.observed_mean:.6e} > 0" in labels
        assert f"{tests.AS_WRITTEN_DRAWS} draws run as written: every return 0" in labels

    def test_its_colours(self, wrong_array) -> None:
        colours = {s.gid: s.color for s in wrong_array.strokes}
        assert colours == {
            "trades": ACCENT,
            "pos": INK,
            "added": INK,
            "pos-sim": MUTED,
            "never": LOST,
            "feeds": MUTED,
            "ret-sim": MUTED,
            "averaged": MUTED,
            "means": LOST,
        }
        words = {s.text: s.color for s in wrong_array.steps if isinstance(s, Label)}
        assert words == {
            "shuffled trades": ACCENT,
            "pos, the real positions": INK,
            "added here": INK,
            "pos_sim = zeros": MUTED,
            "never reached": LOST,
            "ret_sim built from pos_sim = 0": MUTED,
            "every simulated mean: 0": LOST,
            "observed mean 6.626644e-05 > 0": GOOD,
            "10 draws run as written: every return 0": INK,
        }

    def test_each_box_holds_its_words(self, wrong_array) -> None:
        for gid, box, text in (
            ("trades", TRADES_BOX, "shuffled trades"),
            ("pos", POS_BOX, "pos, the real positions"),
            ("pos-sim", POS_SIM_BOX, "pos_sim = zeros"),
            ("ret-sim", RET_SIM_BOX, "ret_sim built from pos_sim = 0"),
            ("means", MEANS_BOX, "every simulated mean: 0"),
        ):
            stroke = _stroke(wrong_array, gid)
            x0, y0, x1, y1 = box
            np.testing.assert_allclose(
                (stroke.x.min(), stroke.y.min(), stroke.x.max(), stroke.y.max()), box, atol=1e-12
            )
            label = _label(wrong_array, text)
            assert (label.names, label.x, label.y) == (gid, (x0 + x1) / 2, (y0 + y1) / 2)

    def test_each_arrow_leaves_one_box_and_points_into_the_next(self, wrong_array) -> None:
        """The shaft starts at the first point, and its tip is the point farthest
        from there, since the head's two strokes run back toward the start."""
        gap = sketches.ARROW_GAP + 1e-9

        def near(point: tuple[float, float], box: tuple[float, float, float, float]) -> bool:
            x0, y0, x1, y1 = box
            return x0 - gap <= point[0] <= x1 + gap and y0 - gap <= point[1] <= y1 + gap

        for gid, source, target in (
            ("added", TRADES_BOX, POS_BOX),
            ("feeds", POS_SIM_BOX, RET_SIM_BOX),
            ("averaged", RET_SIM_BOX, MEANS_BOX),
        ):
            stroke = _stroke(wrong_array, gid)
            start = (stroke.x[0], stroke.y[0])
            far = int(np.argmax(np.hypot(stroke.x - start[0], stroke.y - start[1])))
            tip = (stroke.x[far], stroke.y[far])
            assert not _inside(*start, source) and not _inside(*tip, target), gid
            assert near(start, source) and near(tip, target), gid
            assert not near(start, target) and not near(tip, source), gid

    def test_only_the_arrow_toward_pos_sim_is_dashed_and_it_stops_short(self, wrong_array) -> None:
        dashed = [s.gid for s in wrong_array.strokes if s.dashed]
        assert dashed == ["never"]
        never = _stroke(wrong_array, "never")
        assert never.y.min() > POS_SIM_BOX[3] + 0.2
        assert never.y.max() < TRADES_BOX[1]
        assert POS_SIM_BOX[0] < never.x.min() and never.x.max() < POS_SIM_BOX[2]
        assert never.y[0] > never.y[-1]

    def test_the_words_follow_made_up_figures(self, figures) -> None:
        made_up = replace(
            figures,
            observed_mean=-2.5e-05,
            as_written_means=(0.0, 0.0, 1.0e-04),
            largest_return=3.0e-03,
        )
        labels = scenes(made_up)[0].labels
        assert "ret_sim built from pos_sim = not 0" in labels
        assert "not every simulated mean is 0" in labels
        assert "observed mean -2.500000e-05 ≤ 0" in labels
        assert "3 draws run as written: largest return 3.000000e-03" in labels

    def test_its_alt_text_says_what_the_picture_shows(self, wrong_array) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), wrong_array)
        for words in (
            "brass box labelled “shuffled trades”",
            "black box to its right labelled “pos, the real positions”",
            "black arrow from the first box into the second labelled “added here”",
            "grey box under the shuffled trades",
            "dashed red arrow points down from the shuffled trades toward it but stops short",
            "grey box labelled “ret_sim built from pos_sim = 0”",
            "red box labelled “every simulated mean: 0”",
            "Green words to the left of the red box",
            "A grey arrow runs from that box into a wide grey box",
            "a grey arrow runs down from that into a red box",
        ):
            assert words in alt, words


# --- Lesson 5: drift makes the rule mostly long -----------------------------------


class TestTheMostlyLongSketch:
    def test_its_words(self, mostly_long) -> None:
        assert mostly_long.labels == MOSTLY_LONG_LABELS
        assert mostly_long.title == "Drift makes the rule mostly long"

    def test_its_shares_are_read_from_the_run(self, mostly_long, figures) -> None:
        labels = mostly_long.labels
        assert f"long on {figures.drifting_share:.6f}" in labels
        assert f"long on {figures.flat_share:.6f}" in labels
        assert f"shares from {sketches.SHARE_SERIES:,} simulated series" in labels

    def test_its_colours(self, mostly_long, figures) -> None:
        assert _stroke(mostly_long, "drifting-line").color == ACCENT
        assert _stroke(mostly_long, "flat-line").color == INK
        for name, drift in (("drifting", True), ("flat", False)):
            changes = window_changes(figures, drift)
            for stroke, change in zip(_windows(mostly_long, name), changes, strict=True):
                assert stroke.color == (GOOD if change > 0 else LOST), stroke.gid
        words = {s.text: s.color for s in mostly_long.steps if isinstance(s, Label)}
        assert words == {
            "schematic, with TU’s drift": ACCENT,
            "up: long": GOOD,
            "down: short": LOST,
            "long on 0.804654": ACCENT,
            "of its entry days": ACCENT,
            "same noise, no drift": INK,
            "long on 0.502401": INK,
            "once the mean is removed": INK,
            "shares from 1,000 simulated series": MUTED,
            "long most days, so it collects the drift": INK,
        }

    def test_both_lines_are_their_walks_on_one_scale(self, mostly_long, figures) -> None:
        for name, drift, start in (("drifting", True, DRIFTING_START), ("flat", False, FLAT_START)):
            line = _stroke(mostly_long, f"{name}-line")
            level = walk(figures, drift)
            days = np.arange(0, len(level), sketches.EVERY)
            np.testing.assert_allclose(line.y, start + PER_RETURN * level[days], rtol=0, atol=1e-12)
            np.testing.assert_allclose(
                line.x, [day_x(figures, d) for d in days], rtol=0, atol=1e-12
            )
            assert days[-1] == LOOKBACK * WINDOWS
            assert np.isclose(line.x[-1], sketches.LINE_X[1]), name

    def test_each_bracket_spans_its_250_days(self, mostly_long, figures) -> None:
        """The bracket's level part runs from its window's first day to its last."""
        gap = sketches.BRACKET_GAP
        for name, level in (("drifting", DRIFTING_BRACKETS), ("flat", FLAT_BRACKETS)):
            for k, stroke in enumerate(_windows(mostly_long, name)):
                flat = stroke.x[np.isclose(stroke.y, level)]
                start = day_x(figures, k * LOOKBACK) + gap
                end = day_x(figures, (k + 1) * LOOKBACK) - gap
                assert np.isclose(flat.min(), start) and np.isclose(flat.max(), end), stroke.gid
                assert np.isclose(stroke.x[0], start), stroke.gid

    def test_each_row_of_brackets_sits_under_its_line(self, mostly_long) -> None:
        for name, level in (("drifting", DRIFTING_BRACKETS), ("flat", FLAT_BRACKETS)):
            line = _stroke(mostly_long, f"{name}-line")
            assert level + ARROW_RISE < line.y.min(), name
            for stroke in _windows(mostly_long, name):
                assert stroke.y.max() < line.y.min(), stroke.gid
        flat_line = _stroke(mostly_long, "flat-line")
        tops = [s.y.min() for s in _windows(mostly_long, "drifting")]
        assert flat_line.y.max() < min(tops)

    def test_each_arrow_points_the_way_its_window_moved(self, mostly_long, figures) -> None:
        """The head's tip is the point farthest from the bracket's level, at the window's end."""
        for name, drift, level in (
            ("drifting", True, DRIFTING_BRACKETS),
            ("flat", False, FLAT_BRACKETS),
        ):
            changes = window_changes(figures, drift)
            for k, (stroke, change) in enumerate(
                zip(_windows(mostly_long, name), changes, strict=True)
            ):
                far = int(np.argmax(np.abs(stroke.y - level)))
                tip = stroke.y[far] - level
                assert np.isclose(abs(tip), ARROW_RISE), stroke.gid
                assert np.sign(tip) == np.sign(change), stroke.gid
                end = day_x(figures, (k + 1) * LOOKBACK) - sketches.BRACKET_GAP
                assert np.isclose(stroke.x[far], end), stroke.gid

    def test_the_words_follow_made_up_figures(self, figures) -> None:
        made_up = replace(figures, drifting_share=0.45, flat_share=0.25)
        scene = scenes(made_up)[1]
        assert scene.title == "Drift does not make the rule mostly long"
        assert "long on 0.450000" in scene.labels
        assert "long on 0.250000" in scene.labels
        assert scene.labels[-1] == "not long most days, so it misses the drift"

    def test_the_title_reads_the_drifting_share_and_not_the_flat_one(self, figures) -> None:
        """The run's two shares both sit above a half, so only made-up shares on
        opposite sides of it tell the two apart."""
        for drifting, flat, title in (
            (0.45, 0.55, "Drift does not make the rule mostly long"),
            (0.55, 0.45, "Drift makes the rule mostly long"),
        ):
            made_up = replace(figures, drifting_share=drifting, flat_share=flat)
            assert scenes(made_up)[1].title == title

    def test_a_made_up_drift_moves_the_arrows(self, figures) -> None:
        """With no drift the top line draws the flat line's arrows, five up."""
        made_up = replace(figures, daily_mean=0.0)
        windows = _windows(scenes(made_up)[1], "drifting")
        assert [s.color for s in windows].count(GOOD) == 5

    def test_its_alt_text_says_what_the_picture_shows(self, mostly_long, figures) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), mostly_long)
        up = int((window_changes(figures, drift=True) > 0).sum())
        flat_up = int((window_changes(figures, drift=False) > 0).sum())
        assert "Both lines are schematic random walks" in alt
        assert "the upper one with TU’s daily mean as well" in alt
        assert "not TU’s closes and not the run’s simulated series" in alt
        assert "noisy brass line rises" in alt
        assert f"{WORDS[WINDOWS]} brackets each 250 days long end in an arrow" in alt
        assert (
            "up in green where the line ends the 250 days higher"
            " and down in red where it ends lower"
        ) in alt
        assert f"{WORDS[up]} of the {WORDS[WINDOWS]} point up" in alt
        assert f"{WORDS[flat_up]} of its {WORDS[WINDOWS]} arrows point up" in alt
        assert f"{WORDS[WINDOWS - flat_up]} down" in alt
        assert "black line with the same noise and no drift" in alt
        for words in (
            "“up: long” in green and “down: short” in red",
            "brass words beside the line",
            "wanders level",
            "Black words beside it",
            "Grey words at the bottom right",
        ):
            assert words in alt, words
