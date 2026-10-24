"""The pins for the two whiteboard GIFs in the spot and roll returns post.

One sketches the model's two readings, in "The model and the files", and one
Lesson 2's planted example. What is pinned is what a reader takes from each.

1. The model sketch is schematic: its slopes and expiries are made up, so no
   test here reads a figure off it. What is pinned is the model's algebra on
   the board. The spot line is c + αt, each contract line is
   c + αt − γ(T − t) with the same c and ends on the spot line at its own
   expiry, a held contract rises α + γ, and on the dashed day each later
   expiry sits lower by γ times its extra time to expiry.
2. The planted sketch draws the frame
   ``test_quarterly_contracts_triple_the_column_gamma_and_not_the_month_gamma``
   in ``tests/test_roll_returns.py`` builds. Its 0.03 and 0.09 are read from
   the two fits on that frame, and a second, made-up roll return shows the
   labels follow the run. The script's fit is drawn three times as steep as
   the fit in months, and both start at the same first price.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, the
model sketch's slower pace, that two draws give the same bytes, and that each
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

from chan import roll_returns_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED
from chan.roll_returns_whiteboard import (
    ALPHA,
    EXPIRIES,
    GAMMA,
    MODEL_ORIGIN,
    T0,
    T_START,
    C,
    Planted,
    contract_line,
    gif_name,
    main,
    make_roll_returns_whiteboards,
    month_x,
    planted,
    planted_frame,
    scenes,
    sketch_timeline,
    spot_line,
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
from tests import test_roll_returns as roll_test

POST = REPO_ROOT / "blog" / "roll-returns-lessons.md"

#: Every GIF in the order :func:`make_roll_returns_whiteboards` writes them.
GIFS = ["roll_returns_sketch_one_line.gif", "roll_returns_sketch_same_five_prices.gif"]

#: The paragraph each GIF follows, by its opening words. The model sketch
#: follows the two-item list of readings, and the planted sketch the planted
#: example's paragraph.
FOLLOWS = (
    "1. **Hold one contract.**",
    "A planted example shows how large the difference is.",
)

MODEL_LABELS = [
    "date t",
    "log price",
    "spot: rises at the spot return",
    "each contract ends at the spot",
    "hold one contract: spot return + roll return",
    "hold one day: each year to expiry sits one roll return lower",
    "roll return above 0: backwardation",
]

PLANTED_LABELS = [
    "Mar",
    "Jun",
    "Sep",
    "Dec",
    "Mar",
    "months from the nearest contract",
    "fit in months: 0.03 a year",
    "same prices, one column apart",
    "script’s fit: 0.09 a year, three times",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def every():
    return scenes()


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_roll_returns_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels_of(scene, gid):
    return [s for s in scene.steps if isinstance(s, Label) and s.names == gid]


def _slope(stroke) -> float:
    return float(np.polyfit(stroke.x, stroke.y, 1)[0])


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
        tints = [fill for scene in every for fill in scene.fills if fill.color == whiteboard.TINT]
        assert tints == []


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

    def test_only_the_model_sketch_builds_slowly_and_holds_twelve_seconds(self, every) -> None:
        """Each of its labels alone for 0.9 s and the drawing for 12 s, the
        equity post's slow pace. The planted sketch keeps the usual pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("one_line",)
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
        again = make_roll_returns_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        """No chart or sibling GIF starts like these, so the prefix check above
        reads only this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "roll_returns.png").exists()

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
            ), f"{path.name}: redraw with: uv run python -m chan.roll_returns_whiteboard"


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
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_the_model_sketch_follows_the_list_of_two_readings(self) -> None:
        """The list it follows is the one under "Two readings of that one line",
        whose second item holds one day."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(FOLLOWS[0])]
        assert paragraphs[index - 1].startswith("Two readings of that one line")
        assert "\n2. **Hold one day.**" in paragraphs[index]

    def test_the_model_sketch_sits_in_the_model_and_the_planted_one_in_lesson_2(self) -> None:
        text = POST.read_text(encoding="utf-8")
        model, planted_at = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        section = text.index("## The model and the files")
        lesson_1 = text.index("## Lesson 1:")
        lesson_2 = text.index("## Lesson 2:")
        lesson_3 = text.index("## Lesson 3:")
        assert section < model < lesson_1 < lesson_2 < planted_at < lesson_3

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Each label is quoted after the one drawn before it, and a label drawn
        more than once, such as the planted sketch's "Mar", is quoted each time."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_whether_it_is_schematic_and_slow(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        model, planted_scene = every
        assert "schematic and carries no figures from the run" in _alt(text, model)
        assert "schematic" not in _alt(text, planted_scene)
        for scene in every:
            alt = _alt(text, scene)
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_the_module_says_the_model_sketch_is_schematic(self) -> None:
        doc = sketches.__doc__ or ""
        assert "The model sketch is schematic and carries no figures from the run" in doc
        assert "the drop is drawn\nlarger than it is" in doc


# --- The model: one line, read two ways ----------------------------------------


class TestTheModelSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "One line, read two ways"
        assert every[0].labels == MODEL_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        for gid, ink in (
            ("x-axis", MUTED),
            ("y-axis", MUTED),
            ("spot", INK),
            *((f"contract-{t}", MUTED) for t in EXPIRIES),
            *((f"contract-{t}-end", MUTED) for t in EXPIRIES),
            ("held", ACCENT),
            ("day", INK),
            ("day-spot", INK),
            *((f"day-{t}", INK) for t in EXPIRIES),
        ):
            assert _stroke(scene, gid).color == ink, gid
        for text, ink in zip(
            MODEL_LABELS, (MUTED, MUTED, INK, MUTED, ACCENT, GOOD, GOOD), strict=True
        ):
            assert _label(scene, text).color == ink, text
        assert _stroke(scene, "day").dashed

    def test_each_label_names_the_stroke_it_sits_beside(self, every) -> None:
        scene = every[0]
        for gid, texts in (
            ("x-axis", ["date t"]),
            ("y-axis", ["log price"]),
            ("spot", ["spot: rises at the spot return"]),
            (f"contract-{EXPIRIES[-1]}-end", ["each contract ends at the spot"]),
            ("held", ["hold one contract: spot return + roll return"]),
            ("day", MODEL_LABELS[-2:]),
        ):
            assert [label.text for label in _labels_of(scene, gid)] == texts, gid

    def test_the_slopes_say_backwardation_with_a_small_spot_return(self) -> None:
        assert 0 < ALPHA < GAMMA

    def test_the_spot_line_is_c_plus_alpha_t(self, every) -> None:
        spot = _stroke(every[0], "spot")
        assert spot.y == pytest.approx(C + ALPHA * spot.x)
        assert _slope(spot) == pytest.approx(ALPHA)

    def test_each_contract_is_its_model_line_and_rises_alpha_plus_gamma(self, every) -> None:
        scene = every[0]
        for expiry in EXPIRIES:
            line = _stroke(scene, f"contract-{expiry}")
            assert line.y == pytest.approx(C + ALPHA * line.x - GAMMA * (expiry - line.x))
            assert _slope(line) == pytest.approx(ALPHA + GAMMA)
            assert line.x[0] == pytest.approx(T_START)

    def test_each_contract_ends_on_the_spot_line_at_its_own_expiry(self, every) -> None:
        """The spot line shares the model's c, so at t = T the contract and the
        spot are one price, and the grey dot marks it."""
        scene = every[0]
        for expiry in EXPIRIES:
            line, dot = (
                _stroke(scene, f"contract-{expiry}"),
                _stroke(scene, f"contract-{expiry}-end"),
            )
            assert (line.x[-1], line.y[-1]) == pytest.approx((expiry, spot_line(expiry)))
            assert (dot.x[0], dot.y[0]) == pytest.approx((expiry, spot_line(expiry)))
            assert contract_line(expiry, expiry) == pytest.approx(spot_line(expiry))

    def test_the_lowest_contract_clears_the_axis(self, every) -> None:
        scene = every[0]
        lowest = min(_stroke(scene, f"contract-{t}").y.min() for t in EXPIRIES)
        assert lowest - MODEL_ORIGIN[1] >= 0.3

    def test_the_brass_arrow_retraces_the_latest_contract(self, every) -> None:
        scene = every[0]
        held, line = _stroke(scene, "held"), _stroke(scene, f"contract-{EXPIRIES[-1]}")
        tip = int(np.flatnonzero(np.isclose(held.x, held.x.max()))[0])
        assert held.y[: tip + 1] == pytest.approx(contract_line(held.x[: tip + 1], EXPIRIES[-1]))
        assert (held.x[0], held.y[0]) == pytest.approx((line.x[0], line.y[0]))
        assert (held.x[tip], held.y[tip]) == pytest.approx((line.x[-1], line.y[-1]))
        assert tip < held.points - 1, "an arrowhead follows the shaft"
        assert held.width > line.width

    def test_the_dashed_day_crosses_every_line_with_a_dot_at_each(self, every) -> None:
        scene = every[0]
        day = _stroke(scene, "day")
        assert set(day.x) == {T0}
        assert day.y.min() == pytest.approx(MODEL_ORIGIN[1])
        assert day.y.max() > spot_line(T0)
        for expiry in EXPIRIES:
            assert T_START < T0 < expiry
        dot = _stroke(scene, "day-spot")
        assert (dot.x[0], dot.y[0]) == pytest.approx((T0, spot_line(T0)))
        for expiry in EXPIRIES:
            dot = _stroke(scene, f"day-{expiry}")
            assert (dot.x[0], dot.y[0]) == pytest.approx((T0, contract_line(T0, expiry)))

    def test_on_the_day_each_later_expiry_sits_lower_by_gamma_per_unit_of_expiry(
        self, every
    ) -> None:
        """The one-day reading: the dots on the dashed line fall on a line of
        slope −γ against expiry, with the spot at expiry t₀."""
        scene = every[0]
        expiries = np.array([T0, *EXPIRIES])
        heights = np.array(
            [_stroke(scene, "day-spot").y[0], *(_stroke(scene, f"day-{t}").y[0] for t in EXPIRIES)]
        )
        assert np.all(np.diff(heights) < 0)
        assert float(np.polyfit(expiries, heights, 1)[0]) == pytest.approx(-GAMMA)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "A black line rising gently from left to right" in alt
        assert "each climbs more steeply than the spot line until it meets it" in alt
        assert "retraced in brown with an arrowhead" in alt
        assert "the spot highest and each later contract lower" in alt


# --- Lesson 2: same five prices, three times the slope -------------------------


class TestThePlantedFigures:
    def test_the_frame_is_the_one_the_roll_return_test_builds(self) -> None:
        """The frame
        ``test_quarterly_contracts_triple_the_column_gamma_and_not_the_month_gamma``
        builds, read from that test module's own days, columns and curve, so
        the two cannot drift apart."""
        frame = planted_frame()
        expected = np.tile(roll_test._curve(0.03, np.arange(6.0) * 3), (len(roll_test.DAYS), 1))
        assert list(frame.columns) == list(roll_test.QUARTERLY)
        assert frame.index.equals(roll_test.DAYS)
        np.testing.assert_allclose(frame.to_numpy(), expected, rtol=1e-15)

    def test_a_frame_whose_days_disagree_is_refused(self, monkeypatch) -> None:
        """Every day of the planted frame carries one curve, so one γ. A frame
        whose second day has another curve has no single figure to print."""
        frame = planted_frame()
        frame.iloc[1] = planted_frame(0.05).iloc[1]
        monkeypatch.setattr(sketches, "planted_frame", lambda gamma=0.03: frame)
        with pytest.raises(ValueError, match="one γ on every day"):
            planted()

    def test_the_two_fits_give_0_03_and_0_09(self) -> None:
        run = planted()
        assert run.month_gamma == pytest.approx(0.03, rel=1e-12)
        assert run.column_gamma == pytest.approx(0.09, rel=1e-12)
        assert run.times == 3

    def test_it_reads_the_five_nearest_months_and_their_names(self) -> None:
        run = planted()
        assert run.months == (0, 3, 6, 9, 12)
        assert run.names == ("Mar", "Jun", "Sep", "Dec", "Mar")

    def test_the_prices_fall_from_50_00_to_48_52_as_the_docstring_says(self) -> None:
        prices = np.exp(planted().log_prices)
        assert (f"{prices[0]:.2f}", f"{prices[-1]:.2f}") == ("50.00", "48.52")
        assert "from 50.00 to 48.52" in " ".join((sketches.__doc__ or "").split())

    def test_a_made_up_roll_return_moves_the_labels_and_keeps_three_times(self) -> None:
        """The figures follow the run: a planted γ of 0.05 prints 0.05 and 0.15,
        and the quarterly spacing still makes it three times."""
        run = planted(0.05)
        assert run.month_gamma == pytest.approx(0.05, rel=1e-12)
        assert run.column_gamma == pytest.approx(0.15, rel=1e-12)
        scene = scenes(run)[1]
        assert scene.title == "Same five prices, three times the slope"
        assert "fit in months: 0.05 a year" in scene.labels
        assert "script’s fit: 0.15 a year, three times" in scene.labels

    def test_a_different_ratio_changes_the_word(self) -> None:
        run = Planted(
            months=(0, 2, 4, 6, 8),
            names=("Mar", "May", "Jul", "Sep", "Nov"),
            log_prices=tuple(np.log(50.0) - 0.04 / 12 * np.array([0, 2, 4, 6, 8])),
            month_gamma=0.04,
            column_gamma=0.08,
        )
        scene = scenes(run)[1]
        assert scene.title == "Same five prices, two times the slope"
        assert scene.labels[:5] == ["Mar", "May", "Jul", "Sep", "Nov"]
        assert scene.labels[-1] == "script’s fit: 0.08 a year, two times"

    def test_a_ratio_that_is_not_a_whole_number_is_refused(self) -> None:
        run = Planted((0, 3, 6, 9, 12), ("Mar",) * 5, (0.0,) * 5, 0.03, 0.07)
        with pytest.raises(ValueError, match="not a whole number"):
            _ = run.times


class TestThePlantedSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Same five prices, three times the slope"
        assert every[1].labels == PLANTED_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[1]
        for gid, ink in (
            ("axis", MUTED),
            ("prices", INK),
            ("months-fit", GOOD),
            *((f"slide-{k}", MUTED) for k in range(1, 5)),
            ("columns", LOST),
            ("script-fit", LOST),
        ):
            assert _stroke(scene, gid).color == ink, gid
        for text in PLANTED_LABELS[:6]:
            assert _label(scene, text).color == MUTED, text
        assert _label(scene, "fit in months: 0.03 a year").color == GOOD
        assert _label(scene, "same prices, one column apart").color == MUTED
        assert _label(scene, "script’s fit: 0.09 a year, three times").color == LOST

    def test_each_cloud_comes_before_its_fit_and_the_slides_before_the_red_dots(
        self, every
    ) -> None:
        gids = [s.gid for s in every[1].strokes]
        assert gids.index("prices") + 1 == gids.index("months-fit")
        assert gids.index("months-fit") < gids.index("slide-1")
        assert gids.index("slide-4") < gids.index("columns")
        assert gids.index("columns") + 1 == gids.index("script-fit")

    def test_each_label_names_the_stroke_it_sits_beside(self, every) -> None:
        scene = every[1]
        assert [label.text for label in _labels_of(scene, "axis")] == PLANTED_LABELS[:6]
        assert [label.text for label in _labels_of(scene, "months-fit")] == [PLANTED_LABELS[6]]
        assert [label.text for label in _labels_of(scene, "slide-4")] == [PLANTED_LABELS[7]]
        assert [label.text for label in _labels_of(scene, "script-fit")] == [PLANTED_LABELS[8]]

    def test_the_dots_are_dots_and_the_fits_are_lines(self, every) -> None:
        scene = every[1]
        for cloud in ("prices", "columns"):
            assert _stroke(scene, cloud).dots > 0, cloud
        for line in ("months-fit", "script-fit"):
            assert _stroke(scene, line).dots == 0, line

    def test_the_month_names_sit_under_their_months(self, every) -> None:
        scene = every[1]
        names = [
            s
            for s in scene.steps
            if isinstance(s, Label) and s.text in {"Mar", "Jun", "Sep", "Dec"}
        ]
        assert [n.x for n in names] == pytest.approx(list(month_x(np.array(planted().months))))
        axis = _stroke(scene, "axis")
        assert all(n.y < axis.y.min() for n in names)

    def test_the_axis_ticks_every_month_from_0_to_12(self, every) -> None:
        axis = _stroke(every[1], "axis")
        top = axis.y.max()
        ticks = sorted(
            {round(float(x), 9) for x, y in zip(axis.x, axis.y, strict=True) if y < top - 1e-9}
        )
        assert ticks == pytest.approx(list(month_x(np.arange(13))))

    def test_the_prices_sit_at_their_months_and_fall_evenly(self, every) -> None:
        prices = _stroke(every[1], "prices")
        assert prices.x == pytest.approx(month_x(np.array([0, 3, 6, 9, 12])))
        steps = np.diff(prices.y)
        assert np.all(steps < 0)
        assert steps == pytest.approx([steps[0]] * 4)

    def test_the_drop_is_drawn_larger_than_it_is(self, every) -> None:
        """The true fall is 3 percent of the price, and the board's height is
        4.7, so drawn to scale it would be a flat row."""
        prices = _stroke(every[1], "prices")
        drawn = prices.y[0] - prices.y[-1]
        true = planted().log_prices[0] - planted().log_prices[-1]
        assert drawn > 10 * true

    def test_the_red_dots_are_the_same_prices_one_column_apart(self, every) -> None:
        scene = every[1]
        prices, columns = _stroke(scene, "prices"), _stroke(scene, "columns")
        assert columns.y == pytest.approx(prices.y)
        assert columns.x == pytest.approx(month_x(np.arange(5)))

    def test_each_grey_arrow_slides_a_dot_left_at_its_height(self, every) -> None:
        scene = every[1]
        prices, columns = _stroke(scene, "prices"), _stroke(scene, "columns")
        for k in range(1, 5):
            arrow = _stroke(scene, f"slide-{k}")
            tip = int(np.flatnonzero(np.isclose(arrow.x, arrow.x.min()))[0])
            shaft_y = arrow.y[: tip + 1]
            assert shaft_y == pytest.approx([prices.y[k]] * (tip + 1)), k
            assert prices.x[k] - 0.3 < arrow.x[0] < prices.x[k], k
            assert columns.x[k] < arrow.x[tip] < columns.x[k] + 0.3, k

    def test_each_line_is_the_least_squares_fit_of_its_dots(self, every) -> None:
        scene = every[1]
        for cloud, line in (("prices", "months-fit"), ("columns", "script-fit")):
            dots, fit = _stroke(scene, cloud), _stroke(scene, line)
            slope, intercept = np.polyfit(dots.x, dots.y, 1)
            assert fit.y == pytest.approx(intercept + slope * fit.x), line
            assert (fit.x.min(), fit.x.max()) == pytest.approx((dots.x.min(), dots.x.max()))

    def test_the_scripts_fit_is_three_times_as_steep_and_starts_at_the_same_point(
        self, every
    ) -> None:
        scene = every[1]
        in_months, scripts = _stroke(scene, "months-fit"), _stroke(scene, "script-fit")
        assert _slope(scripts) / _slope(in_months) == pytest.approx(3.0)
        assert _slope(in_months) < 0
        assert (scripts.x[0], scripts.y[0]) == pytest.approx((in_months.x[0], in_months.y[0]))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "Five black dots sit at those five months, falling evenly" in alt
        assert "drawn far larger than the true fall from 50.00 to 48.52" in alt
        assert "slide the four later dots left at the same heights" in alt
        assert "three times as steep as the green one and starting from the same first dot" in alt
