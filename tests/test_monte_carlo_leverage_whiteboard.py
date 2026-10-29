"""The pins for the two whiteboard GIFs in the Monte Carlo leverage post.

One sketches Lesson 4's point that the least of 100,000 draws sits deeper than
Chan's worst day because there are about 163 times as many draws, and one
Lesson 5's point that Box 8.6's loop keeps its leverage on the account near
f·D while the account falls through −0.5.

1. The least-draw sketch draws three rows of dots on one return scale: Chan's
   612 saved returns, the first 612 of the declared seed's draws and all
   100,000, each below −0.012. What is pinned is that every dot is one of those
   values at an affine function of it, that the dashed line sits at the saved
   returns' least and runs through all three rows, that the middle row stops
   short of it, that the red dot sits on the least draw, and the figures it
   prints: −0.022031, the chance of 0.091663, −0.043071, about 163 times as
   many and 1.9550 times as deep.
2. The loop sketch draws each CPPI form's leverage on its account, one point
   a day, from the day after the loop's account's high on day 169 to day 303,
   its first day below −0.5. What is pinned is that each point is that day's
   leverage, recomputed here by loops written out in this file, on one scale
   from 0 to f·D, that both lines start at f·D because both accounts set
   their high on day 169, and the figures it prints: 9.47, 3.46, −0.504523,
   −0.407605 and 0.946693.

Every figure a sketch prints is read from the run on Chan's committed returns,
so the tests recompute each through :mod:`chan.monte_carlo_leverage`'s own
functions rather than a frozen copy. Made-up figures check that the words and
title follow the data.

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

from chan import monte_carlo_leverage_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.monte_carlo_leverage import (
    CAP,
    DRAWS,
    SEED,
    D,
    draws,
    minimum_below,
    optimal_leverage,
    pearson_fit,
    read_returns,
)
from chan.monte_carlo_leverage_whiteboard import (
    CUTOFF,
    FEW_Y,
    HISTORY_Y,
    MANY_Y,
    SketchFigures,
    below,
    gif_name,
    leverage_on_account,
    leverage_y,
    main,
    make_monte_carlo_leverage_whiteboards,
    return_x,
    scenes,
    sketch_timeline,
    stretch_x,
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

POST = REPO_ROOT / "blog" / "monte-carlo-leverage-lessons.md"

#: Every GIF in the order :func:`make_monte_carlo_leverage_whiteboards` writes them.
GIFS = [
    "monte_carlo_leverage_sketch_least_draw.gif",
    "monte_carlo_leverage_sketch_loop_leverage.gif",
]

#: The paragraph each GIF follows, by its opening words: Lesson 4's paragraph
#: on the least draw, and Lesson 5's paragraph on Box 8.6.
LEAST_DRAW_PARAGRAPH = "The draws hold a worse day than the history"
LOOP_LEVERAGE_PARAGRAPH = "Box 8.6, the code printed beside that sentence"

LEAST_DRAW_LABELS = [
    "Chan’s 612 returns",
    "worst day −0.022031",
    "612 draws from the fit",
    "reach it with chance 0.091663",
    "−0.043071",
    "100,000 draws, about",
    "163 times as many",
    "least 1.9550 times as deep",
    "each dot a value below −0.012, to scale, draws from seed 20261012",
]

LOOP_LEVERAGE_LABELS = [
    "leverage on the account, from its high on day 169",
    "f·D = 10",
    "0",
    "day 170",
    "day 303",
    "Box 8.6’s loop: 9.47",
    "drawdown −0.504523, past −0.5",
    "the scheme on p. 263: 3.46",
    "drawdown −0.407605, above −0.5",
    "the loop’s 1 + drawdown of the unlevered returns to day 302: 0.946693",
]

#: The counts the least-draw alt text spells out, in words.
WORDS = {3: "three"}

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def run():
    """The saved returns, the fit, the declared seed's draws and ``f``, by the run's functions."""
    _, returns = read_returns()
    _, params = pearson_fit(returns)
    sim = draws(params, SEED)
    return {"returns": returns, "params": params, "sim": sim, "f": optimal_leverage(sim, CAP)}


@pytest.fixture(scope="module")
def figures():
    return SketchFigures.from_run()


@pytest.fixture(scope="module")
def every(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def least_draw(every):
    return every[0]


@pytest.fixture(scope="module")
def loop_leverage(every):
    return every[1]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_monte_carlo_leverage_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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


def _loop_leverage_by_hand(returns, leverage, d):
    """Box 8.6's lines 46 to 59 written out: each day's leverage is ``d·f·(1 + dd)``."""
    found, drawdown = [], 0.0
    for r in returns:
        found.append(d * leverage * (1 + drawdown))
        drawdown = min(0.0, (1 + drawdown) * (1 + r) - 1)
    return np.array(found)


def _scheme_leverage_by_hand(returns, leverage, d):
    """Location 3426's scheme written out: each day's leverage is ``f·sub / equity``.

    The subaccount starts at ``d``, earns ``f·R``, and is reset to ``d`` of the
    account at each new high, with the cash at ``1 − d`` of the last high.
    """
    found, equity, high, sub = [], 1.0, 1.0, d
    for r in returns:
        found.append(leverage * sub / equity)
        sub *= 1 + leverage * r
        equity = (1 - d) * high + sub
        if equity > high:
            high, sub = equity, d * equity
    return np.array(found)


def _account_by_hand(levers, returns):
    """The account's value each day from its daily leverage, starting at 1."""
    return np.cumprod(1 + levers * returns)


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
        """The post's chart has not moved to ``chan.palette``, so neither have its sketches."""
        inks = {INK, MUTED, ACCENT, GOOD, LOST}
        for scene in every:
            for step in scene.steps:
                assert step.color in inks, (scene.slug, getattr(step, "gid", None) or step.text)

    def test_the_chart_draws_in_the_shared_inks_too(self) -> None:
        """The rule the colour choice rests on: a post's sketches move to
        ``chan.palette`` when its chart does, and this chart has not."""
        source = (REPO_ROOT / "src" / "chan" / "monte_carlo_leverage_figures.py").read_text()
        assert "chan.palette" not in source
        assert "from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED" in source


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
        assert sketches.PACED == ("least_draw", "loop_leverage")
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
        again = make_monte_carlo_leverage_whiteboards(out_dir=tmp_path)
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
        assert not "monte_carlo_leverage.png".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.monte_carlo_leverage_whiteboard"


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
        (least,) = [k for k, p in enumerate(paragraphs) if p.startswith(LEAST_DRAW_PARAGRAPH)]
        (loop,) = [k for k, p in enumerate(paragraphs) if p.startswith(LOOP_LEVERAGE_PARAGRAPH)]
        for index, name in zip((least, loop), GIFS, strict=True):
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_the_least_draw_sketch_sits_in_lesson_4_and_the_loop_in_lesson_5(self) -> None:
        text = POST.read_text(encoding="utf-8")
        least, loop = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lesson_4 = text.index("## Lesson 4:")
        lesson_5 = text.index("## Lesson 5:")
        lesson_6 = text.index("## Lesson 6:")
        assert lesson_4 < least < lesson_5 < loop < lesson_6

    def test_each_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count("(../docs/figures/monte_carlo_leverage.png)") == 1

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
            f"[the whiteboard sketches]({base}src/chan/monte_carlo_leverage_whiteboard.py)"
            in footer
        )
        assert (
            f"[what the sketches draw]({base}tests/test_monte_carlo_leverage_whiteboard.py)"
            in footer
        )

    def test_the_module_says_neither_sketch_is_schematic(self) -> None:
        assert "Neither sketch is schematic." in (sketches.__doc__ or "")


# --- The figures, read from the run ----------------------------------------------


class TestTheLoopFigures:
    """The loop sketch's figures on the declared seed 20261012, with ``f`` the
    capped optimum, about 20, and D = 0.5, so f·D is about 10. A leverage or a
    drawdown is pinned at six decimals, as ``tests/test_monte_carlo_leverage.py``
    pins them."""

    def test_f_is_the_capped_optimum_and_d_the_script_s(self, figures, run) -> None:
        assert figures.loop.leverage == run["f"]
        assert figures.loop.d == D == 0.5
        assert figures.loop.full == pytest.approx(10.0, abs=5e-7)

    def test_the_stretch_runs_from_the_high_on_day_169_to_day_303(self, figures, run) -> None:
        """Day 303 is the day ``tests/test_monte_carlo_leverage_figures.py`` pins
        as the loop's first below −0.5, recomputed here from the loop by hand."""
        sim, f = run["sim"], run["f"]
        account = _account_by_hand(_loop_leverage_by_hand(sim, f, D), sim)
        drawdown = account / np.maximum.accumulate(account) - 1
        first = int(np.flatnonzero(drawdown < -0.5)[0]) + 1
        assert (
            (figures.loop.high_day, figures.loop.floor_day)
            == (169, 303)
            == (
                int(np.argmax(account[:first])) + 1,
                first,
            )
        )
        assert list(figures.loop.days) == list(range(170, 304))
        assert len(figures.loop.loop) == len(figures.loop.scheme) == 134

    def test_each_day_s_leverage_is_the_one_each_form_trades(self, figures, run) -> None:
        sim, f = run["sim"], run["f"]
        days = slice(figures.loop.high_day, figures.loop.floor_day)
        np.testing.assert_allclose(
            figures.loop.loop, _loop_leverage_by_hand(sim, f, D)[days], rtol=1e-9, atol=0
        )
        np.testing.assert_allclose(
            figures.loop.scheme, _scheme_leverage_by_hand(sim, f, D)[days], rtol=1e-9, atol=0
        )

    def test_both_accounts_set_their_high_on_day_169_so_both_lines_start_at_f_d(
        self, figures, run
    ) -> None:
        sim, f = run["sim"], run["f"]
        scheme = _account_by_hand(_scheme_leverage_by_hand(sim, f, D), sim)
        assert int(np.argmax(scheme[: figures.loop.floor_day])) + 1 == figures.loop.high_day
        assert figures.loop.loop[0] == pytest.approx(figures.loop.full, rel=1e-12)
        assert figures.loop.scheme[0] == pytest.approx(figures.loop.full, rel=1e-12)

    def test_on_day_303_the_loop_trades_9_47_and_the_scheme_3_46(self, figures) -> None:
        assert figures.loop.loop[-1] == pytest.approx(9.466931, abs=5e-7)
        assert figures.loop.scheme[-1] == pytest.approx(3.462047, abs=5e-7)
        assert figures.loop.multiplier == pytest.approx(0.946693, abs=5e-7)
        assert figures.loop.loop[-1] == pytest.approx(
            figures.loop.full * figures.loop.multiplier, rel=1e-12
        )

    def test_the_multiplier_is_one_plus_the_unlevered_drawdown_through_day_302(
        self, figures, run
    ) -> None:
        """Day 303's leverage reads the drawdown through the day before, as the loop
        sets it before the day's return, and not day 303's own."""
        unlevered = np.cumprod(1 + run["sim"])
        through = unlevered / np.maximum.accumulate(np.maximum(unlevered, 1.0))
        assert figures.loop.multiplier == pytest.approx(through[301], rel=1e-9)
        assert through[302] == pytest.approx(0.941142, abs=5e-7)

    def test_even_at_its_deepest_the_loop_trades_above_8_3(self, run) -> None:
        """The post's "barely cuts its leverage while the account falls", over all
        100,000 days rather than the sketch's stretch."""
        sim, f = run["sim"], run["f"]
        levers = _loop_leverage_by_hand(sim, f, D)
        account = _account_by_hand(levers, sim)
        deepest = int(np.argmin(account / np.maximum.accumulate(account) - 1))
        assert deepest + 1 == 37_071
        assert levers[deepest] == pytest.approx(8.342369, abs=5e-7)
        assert levers.min() == pytest.approx(8.317190, abs=5e-7)

    def test_the_loop_stays_near_f_d_over_the_whole_stretch(self, figures) -> None:
        """The alt text's "stays near 10": never below 9.45 of it."""
        assert min(figures.loop.loop) == pytest.approx(9.450657, abs=5e-7)
        assert min(figures.loop.loop) > 0.9 * figures.loop.full

    def test_on_day_303_one_account_is_past_the_floor_and_the_other_above(
        self, figures, run
    ) -> None:
        sim, f = run["sim"], run["f"]
        day = figures.loop.floor_day
        for levers, drawn in (
            (_loop_leverage_by_hand(sim, f, D), figures.loop.loop_drawdown),
            (_scheme_leverage_by_hand(sim, f, D), figures.loop.scheme_drawdown),
        ):
            account = _account_by_hand(levers, sim)[:day]
            assert drawn == pytest.approx(account[-1] / account.max() - 1, rel=1e-9)
        assert figures.loop.loop_drawdown == pytest.approx(-0.504523, abs=5e-7)
        assert figures.loop.scheme_drawdown == pytest.approx(-0.407605, abs=5e-7)

    def test_leverage_on_account_divides_by_the_day_s_return_and_refuses_zero(self) -> None:
        np.testing.assert_allclose(leverage_on_account([0.02, -0.03], [0.01, -0.01]), [2.0, 3.0])
        with pytest.raises(ValueError, match="return is 0"):
            leverage_on_account([0.0, 0.02], [0.0, 0.01])


class TestTheLeastFigures:
    def test_the_rows_are_the_values_below_minus_0_012(self, figures, run) -> None:
        returns, sim = run["returns"], run["sim"]
        assert CUTOFF == -0.012
        for found, values in (
            (figures.least.history, returns),
            (figures.least.few, sim[: len(returns)]),
            (figures.least.many, sim),
        ):
            assert sorted(found) == sorted(v for v in values if v < CUTOFF)
            assert list(found) == sorted(found, reverse=True)

    def test_its_counts(self, figures) -> None:
        assert figures.least.history_count == 612
        assert figures.least.many_count == DRAWS == 100_000
        assert figures.least.times_as_many == 163
        assert (len(figures.least.history), len(figures.least.few), len(figures.least.many)) == (
            3,
            3,
            377,
        )

    def test_its_least_values_and_chance(self, figures, run) -> None:
        """The figures ``TestWhatThePostMeasured`` in
        ``tests/test_monte_carlo_leverage.py`` pins, recomputed here."""
        returns, sim = run["returns"], run["sim"]
        assert figures.least.history_least == float(returns.min()) == figures.least.history[-1]
        assert figures.least.many_least == float(sim.min()) == figures.least.many[-1]
        assert figures.least.history_least == pytest.approx(-0.022031, abs=5e-7)
        assert figures.least.many_least == pytest.approx(-0.043071, abs=5e-7)
        assert figures.least.times_as_deep == pytest.approx(1.9550, abs=5e-5)
        assert figures.least.chance == minimum_below(run["params"], float(returns.min()), 612)
        assert figures.least.chance == pytest.approx(0.091663, abs=5e-7)

    def test_the_cutoff_sits_where_the_fit_s_tail_turns_thinner(self, figures) -> None:
        """The module docstring and README: as many of the first 612 draws as of
        Chan's 612 returns sit below −0.012, and only his reach past −0.015."""
        assert len(figures.least.few) == len(figures.least.history) == 3
        assert [v for v in figures.least.history if v < -0.015] != []
        assert [v for v in figures.least.few if v < -0.015] == []

    def test_the_first_612_draws_stop_short_of_chan_s_worst_day(self, figures) -> None:
        assert figures.least.few[-1] > figures.least.history_least
        assert figures.least.few[-1] == pytest.approx(-0.013818, abs=5e-7)

    def test_below_keeps_the_values_under_the_cutoff_shallowest_first(self) -> None:
        values = [-0.02, 0.01, -0.005, -0.011, -0.012, -0.0125]
        assert below(values, cutoff=-0.01) == (-0.011, -0.012, -0.0125, -0.02)
        assert below(values) == (-0.0125, -0.02)


# --- Lesson 4: the least of many draws goes deeper --------------------------------


class TestTheLeastDrawSketch:
    def test_its_words(self, least_draw) -> None:
        assert least_draw.labels == LEAST_DRAW_LABELS
        assert least_draw.title == "The least of many draws goes deeper"

    def test_its_numbers_are_read_from_the_run(self, least_draw, figures) -> None:
        least = figures.least
        labels = least_draw.labels
        assert f"worst day {least.history_least:.6f}".replace("-", "−") in labels
        assert f"reach it with chance {least.chance:.6f}" in labels
        assert f"{least.many_least:.6f}".replace("-", "−") in labels
        assert f"least {least.times_as_deep:.4f} times as deep" in labels
        assert f"each dot a value below −0.012, to scale, draws from seed {SEED}" in labels

    def test_its_colours(self, least_draw) -> None:
        colours = {s.gid: s.color for s in least_draw.strokes}
        assert colours == {
            "history": ACCENT,
            "worst": ACCENT,
            "few": INK,
            "many": INK,
            "many-least": LOST,
        }
        words = {s.text: s.color for s in least_draw.steps if isinstance(s, Label)}
        assert words == {
            "Chan’s 612 returns": ACCENT,
            "worst day −0.022031": ACCENT,
            "612 draws from the fit": INK,
            "reach it with chance 0.091663": INK,
            "−0.043071": LOST,
            "100,000 draws, about": INK,
            "163 times as many": INK,
            "least 1.9550 times as deep": LOST,
            "each dot a value below −0.012, to scale, draws from seed 20261012": MUTED,
        }

    def test_each_dot_sits_at_its_value_on_one_scale(self, least_draw, figures) -> None:
        low, high = sketches.RETURN_RANGE
        per = (sketches.ROW_X[1] - sketches.ROW_X[0]) / (high - low)
        for gid, values, y in (
            ("history", figures.least.history, HISTORY_Y),
            ("few", figures.least.few, FEW_Y),
            ("many", figures.least.many, MANY_Y),
        ):
            row = _stroke(least_draw, gid)
            assert row.dots > 0, gid
            np.testing.assert_allclose(
                row.x, sketches.ROW_X[0] + per * (np.array(values) - low), rtol=0, atol=1e-12
            )
            np.testing.assert_array_equal(row.y, np.full(len(values), y))
        assert HISTORY_Y > FEW_Y > MANY_Y
        assert sketches.ROW_X[0] < return_x(figures.least.many_least)
        assert return_x(max(figures.least.many)) < sketches.ROW_X[1]

    def test_the_dashed_line_sits_at_chan_s_worst_day_through_every_row(
        self, least_draw, figures
    ) -> None:
        line = _stroke(least_draw, "worst")
        assert line.dashed
        np.testing.assert_allclose(line.x, return_x(figures.least.history_least), atol=1e-12)
        assert line.y.max() > HISTORY_Y and line.y.min() < MANY_Y
        label = _label(least_draw, "worst day −0.022031")
        assert label.x == return_x(figures.least.history_least) and label.y > line.y.max()

    def test_only_the_bottom_row_reaches_past_the_line(self, least_draw, figures) -> None:
        worst = return_x(figures.least.history_least)
        assert _stroke(least_draw, "few").x.min() > worst
        assert _stroke(least_draw, "many").x.min() < worst
        assert _stroke(least_draw, "history").x.min() == pytest.approx(worst, abs=1e-12)

    def test_the_red_dot_and_its_figure_sit_on_the_least_draw(self, least_draw, figures) -> None:
        dot = _stroke(least_draw, "many-least")
        x = return_x(figures.least.many_least)
        assert (dot.points, dot.frames, float(dot.x[0]), float(dot.y[0])) == (1, 1, x, MANY_Y)
        label = _label(least_draw, "−0.043071")
        assert (label.x, label.ha) == (x, "center") and label.y < MANY_Y

    def test_the_words_follow_made_up_figures(self, figures) -> None:
        made_up = replace(
            figures,
            least=replace(
                figures.least,
                history=(-0.012, -0.05),
                history_count=500,
                history_least=-0.05,
                many_count=50_000,
                many_least=-0.04,
                chance=0.5,
            ),
        )
        scene = scenes(made_up)[0]
        assert scene.title == "The least of many draws goes no deeper"
        for words in (
            "Chan’s 500 returns",
            "worst day −0.050000",
            "500 draws from the fit",
            "reach it with chance 0.500000",
            "−0.040000",
            "50,000 draws, about",
            "100 times as many",
            "least 0.8000 times as deep",
        ):
            assert words in scene.labels, words
        assert _label(scene, "least 0.8000 times as deep").color == INK
        rounded = replace(
            figures, least=replace(figures.least, history_count=500, many_count=50_300)
        )
        assert "101 times as many" in scenes(rounded)[0].labels

    def test_the_words_beside_each_row_read_top_down(self, least_draw) -> None:
        first = _label(least_draw, "612 draws from the fit")
        second = _label(least_draw, "reach it with chance 0.091663")
        assert first.y > FEW_Y > second.y
        ys = [
            _label(least_draw, t).y
            for t in ("100,000 draws, about", "163 times as many", "least 1.9550 times as deep")
        ]
        assert ys[0] > ys[1] > ys[2] and ys[0] > MANY_Y > ys[2]

    def test_its_alt_text_says_what_the_picture_shows(self, least_draw, figures) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), least_draw)
        for words in (
            "Three rows of dots share one return scale",
            "each dot is a return or a draw below −0.012, placed at its value",
            "a dense black band near −0.012",
            "The top row, in brass,",
            "its leftmost dot sits on a dashed brass line",
            "runs down through the rows below",
            "The middle row is the first 612 of the declared seed’s draws",
            f"its {WORDS[len(figures.least.few)]} dots all sit right of the dashed line",
            "The bottom row is all 100,000 draws",
            "a red dot marks its least",
            "then in red",
            "A grey note at the bottom",
        ):
            assert words in alt, words


# --- Lesson 5: Box 8.6's loop barely cuts its leverage ----------------------------


class TestTheLoopLeverageSketch:
    def test_its_words(self, loop_leverage) -> None:
        assert loop_leverage.labels == LOOP_LEVERAGE_LABELS
        assert loop_leverage.title == "Box 8.6’s loop barely cuts its leverage"

    def test_its_numbers_are_read_from_the_run(self, loop_leverage, figures) -> None:
        loop = figures.loop
        labels = loop_leverage.labels
        assert f"Box 8.6’s loop: {loop.loop[-1]:.2f}" in labels
        assert f"the scheme on p. 263: {loop.scheme[-1]:.2f}" in labels
        assert f"drawdown {loop.loop_drawdown:.6f}, past −0.5".replace("-0", "−0") in labels
        assert f"drawdown {loop.scheme_drawdown:.6f}, above −0.5".replace("-0", "−0") in labels
        assert (
            f"the loop’s 1 + drawdown of the unlevered returns to day 302: {loop.multiplier:.6f}"
            in labels
        )

    def test_its_colours(self, loop_leverage) -> None:
        colours = {s.gid: s.color for s in loop_leverage.strokes}
        assert colours == {"axes": MUTED, "loop": LOST, "scheme": GOOD}
        words = {s.text: s.color for s in loop_leverage.steps if isinstance(s, Label)}
        assert words == {
            "leverage on the account, from its high on day 169": MUTED,
            "f·D = 10": MUTED,
            "0": MUTED,
            "day 170": MUTED,
            "day 303": MUTED,
            "Box 8.6’s loop: 9.47": LOST,
            "drawdown −0.504523, past −0.5": LOST,
            "the scheme on p. 263: 3.46": GOOD,
            "drawdown −0.407605, above −0.5": GOOD,
            "the loop’s 1 + drawdown of the unlevered returns to day 302: 0.946693": INK,
        }

    def test_each_line_is_its_leverage_day_by_day_on_one_scale(
        self, loop_leverage, figures
    ) -> None:
        per = sketches.PER_LEVERAGE
        days = np.arange(figures.loop.days[0], figures.loop.days[-1] + 1)
        across = (sketches.LAST_X - sketches.AXIS_X) / (days[-1] - days[0])
        for gid, values in (("loop", figures.loop.loop), ("scheme", figures.loop.scheme)):
            line = _stroke(loop_leverage, gid)
            np.testing.assert_allclose(
                line.y, sketches.AXIS_Y + per * np.array(values), rtol=0, atol=1e-12
            )
            np.testing.assert_allclose(
                line.x, sketches.AXIS_X + across * (days - days[0]), rtol=0, atol=1e-12
            )
            assert not line.dashed, gid

    def test_the_axis_runs_from_0_to_f_d_and_its_ticks_sit_there(
        self, loop_leverage, figures
    ) -> None:
        axes = _stroke(loop_leverage, "axes")
        assert axes.x.min() == sketches.AXIS_X and axes.x.max() == sketches.LAST_X
        assert axes.y.min() == sketches.AXIS_Y == leverage_y(0.0)
        assert axes.y.max() > leverage_y(figures.loop.full)
        assert _label(loop_leverage, "f·D = 10").y == leverage_y(figures.loop.full)
        assert _label(loop_leverage, "0").y == leverage_y(0.0)
        assert _label(loop_leverage, "day 170").x == pytest.approx(stretch_x(figures.loop, 170))
        assert _label(loop_leverage, "day 303").x == pytest.approx(stretch_x(figures.loop, 303))
        assert _label(loop_leverage, "day 170").ha == "left"
        assert _label(loop_leverage, "day 303").ha == "right"

    def test_each_line_s_words_sit_at_its_end(self, loop_leverage, figures) -> None:
        for text, values in (
            ("Box 8.6’s loop: 9.47", figures.loop.loop),
            ("the scheme on p. 263: 3.46", figures.loop.scheme),
        ):
            label = _label(loop_leverage, text)
            assert label.y == leverage_y(values[-1]), text
            assert label.x > sketches.LAST_X, text

    def test_the_words_follow_made_up_figures(self, figures) -> None:
        made_up = replace(
            figures,
            loop=replace(
                figures.loop,
                high_day=40,
                floor_day=44,
                loop=(10.0, 9.0, 8.0, 7.5),
                scheme=(10.0, 5.0, 2.0, 1.25),
                loop_drawdown=-0.45,
                scheme_drawdown=-0.6,
                multiplier=0.75,
            ),
        )
        labels = scenes(made_up)[1].labels
        for words in (
            "leverage on the account, from its high on day 40",
            "day 41",
            "day 44",
            "Box 8.6’s loop: 7.50",
            "drawdown −0.450000, above −0.5",
            "the scheme on p. 263: 1.25",
            "drawdown −0.600000, past −0.5",
            "the loop’s 1 + drawdown of the unlevered returns to day 43: 0.750000",
        ):
            assert words in labels, words

    def test_its_alt_text_says_what_the_picture_shows(self, loop_leverage) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), loop_leverage)
        for words in (
            "Two grey axes sit under the caption",
            "The upright one has",
            "The flat one runs from",
            "at its top",
            "at its foot",
            "the first day the loop’s account is below −0.5",
            "one point a day, both start at 10",
            "The red line stays near 10",
            "The green line falls as it goes",
            "A black note at the bottom",
        ):
            assert words in alt, words
