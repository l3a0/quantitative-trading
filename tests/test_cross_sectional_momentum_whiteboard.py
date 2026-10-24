"""The pins for the two whiteboard GIFs in the cross-sectional momentum post.

One sketches how the strategy's 25 overlapping cohorts make one unit of
capital, and one Lesson 1's two annual returns from one window. Every number
either one prints comes from the run, so the tests here recompute each figure
from :mod:`chan.cross_sectional_momentum` on the committed closes, apart from
the sketch module, and build the expected labels from what they find rather
than from typed values.

1. The cohorts sketch draws one bar per cohort, each one trading day later and
   one row lower than the last, a dashed line on the one day every bar covers,
   the arithmetic that makes the picks held one unit of capital, and a red
   stretch of the axis under the 2007 window's days short of a full book.
   What is pinned is that each bar spans the days its cohort is held, that the
   dashed line cuts every bar and only on that day, that the counts match the
   script's formations, positions and divisor, and that the sketch counts
   picks rather than positions, since a stock long in one cohort and short in
   another nets out of the positions.
2. The returns sketch draws the window's daily returns as a row of bars, then
   the two paths from them to the script's two annual figures. What is pinned
   is that each bar's height is in proportion to its return, that each path's
   arithmetic gives the figure it ends on, and that the book's 37 percent is
   not on it, because the post holds the book's figures back until Lesson 2.

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

from chan import cross_sectional_momentum as momentum
from chan import cross_sectional_momentum_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.cross_sectional_momentum_whiteboard import (
    AXIS_Y,
    DAILY_TALLEST,
    DAILY_X,
    DAILY_Y,
    GIF_PREFIX,
    HALF,
    Cohorts,
    Returns,
    _cohorts,
    _two_returns,
    cohort_y,
    day_x,
    gif_name,
    main,
    make_cross_sectional_momentum_whiteboards,
    scenes,
    sketch_timeline,
    spelled,
)
from chan.matlab_helpers import backshift
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

POST = REPO_ROOT / "blog" / "cross-sectional-momentum-lessons.md"

#: Every GIF in the order :func:`make_cross_sectional_momentum_whiteboards` writes them.
GIFS = ["cross_sectional_momentum_cohorts.gif", "cross_sectional_momentum_two_returns.gif"]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "1. **The ranking.** Each stock’s return over the last 252 trading days",
    "None of the five prints what the comment says.",
)

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


# --- What the run gives, recomputed apart from the sketch module ----------------


@dataclasses.dataclass(frozen=True)
class Run:
    """The closes and what the script computes on them, read once for the module."""

    closes: pd.DataFrame
    values: np.ndarray
    days: pd.DatetimeIndex
    longs: np.ndarray
    shorts: np.ndarray
    lagged: np.ndarray
    held: np.ndarray
    daily: np.ndarray


@pytest.fixture(scope="module")
def run() -> Run:
    _, closes = momentum.read_closes()
    values = closes.to_numpy(dtype=float)
    longs, shorts = momentum.formations(momentum.ranking_returns(values))
    positions = momentum.overlapping_positions(longs, shorts)
    return Run(
        closes=closes,
        values=values,
        days=pd.DatetimeIndex(closes.index),
        longs=longs,
        shorts=shorts,
        lagged=np.nan_to_num(backshift(1, positions)),
        held=momentum.cohorts_held(len(values)),
        daily=momentum.script_as_printed(values),
    )


@pytest.fixture(scope="module")
def figures(run):
    return sketches.cohort_figures(run.closes), sketches.return_figures(run.closes)


@pytest.fixture(scope="module")
def every(figures):
    return scenes(*figures)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, figures):
    return make_cross_sectional_momentum_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), figures=figures
    )


def _window(run: Run) -> tuple[pd.DatetimeIndex, np.ndarray]:
    return momentum.window_returns(run.daily, run.days, "2007")


def _cohort_labels(n: int, longs: int, shorts: int, held: int, short_days: int) -> list[str]:
    picks = longs + shorts
    return [
        "trading days",
        f"{longs} long",
        f"{shorts} short",
        f"one cohort: one day’s {picks} picks",
        f"{n} cohorts held",
        f"{n} cohorts × {picks} picks",
        f"= {held:,} picks held",
        f"divide by 2 · {longs} · {n} = {held:,}",
        "one unit of capital",
        f"first {short_days} days of 2007:",
        f"fewer than {n}",
    ]


def _return_labels(n: int, total: float, growth: float, arithmetic: float, apr: float):
    return [
        f"2007: {n} days",
        f"add the {n} returns: {total:.4f}",
        f"× 252/{n}",
        f"{arithmetic:.4f}, Avg Ann Ret",
        f"multiply the 1 + r: {growth:.4f}",
        f"^(252/{n}), less 1",
        f"{apr:.4f}, APR",
    ]


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _labels_of(scene, gid):
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
        assert all(name.startswith(GIF_PREFIX) for name in GIFS)

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
        assert sketches.PACED == ("cohorts", "two_returns")
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

    def test_two_draws_give_the_same_bytes(self, gifs, figures, tmp_path) -> None:
        again = make_cross_sectional_momentum_whiteboards(out_dir=tmp_path, figures=figures)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_only_other_file_under_the_prefix_is_the_posts_chart(self) -> None:
        """The post's chart starts with the same prefix and is a PNG, so the
        glob for GIFs above reads only this module's sketches."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert sorted(name for name in names if name.startswith(GIF_PREFIX)) == [
            "cross_sectional_momentum_cumulative_returns.png"
        ]

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
            ), f"{path.name}: redraw with: uv run python -m {sketches.__name__}"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys, figures
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(sketches, "read_figures", lambda: figures)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]

    def test_a_missing_vintage_reaches_the_reader_as_one_line(self, monkeypatch) -> None:
        from chan.vintage import VintageUnavailable

        def refuse():
            raise VintageUnavailable("no closes here")

        monkeypatch.setattr(sketches, "read_figures", refuse)
        with pytest.raises(SystemExit, match="no closes here"):
            main()


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = _paragraphs()
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_gif_has_an_italic_caption_after_it(self) -> None:
        paragraphs = _paragraphs()
        for name in GIFS:
            (index,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{name})" in p]
            caption = paragraphs[index + 1]
            assert caption.startswith("*") and caption.endswith("*"), name
            assert "\n" not in caption, name

    def test_the_cohorts_sketch_sits_in_the_strategy_and_the_returns_in_lesson_1(self) -> None:
        text = POST.read_text(encoding="utf-8")
        cohorts, returns = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        strategy = text.index("## The strategy and the file")
        lesson_1 = text.index("## Lesson 1:")
        lesson_2 = text.index("## Lesson 2:")
        assert strategy < cohorts < text.index("The data is [one file]") < lesson_1
        assert lesson_1 < returns < text.index("Four things bear on which side") < lesson_2

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_says_it_is_slow_and_from_the_run(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            assert "drawn slowly stroke by stroke" in alt, scene.slug
            assert "The finished drawing holds for twelve seconds." in alt, scene.slug
            assert "come from the run" in alt, scene.slug
            assert "schematic" not in alt, scene.slug

    def test_no_alt_text_or_caption_carries_a_dash_or_a_semicolon(self) -> None:
        paragraphs = _paragraphs()
        for name in GIFS:
            (index,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{name})" in p]
            for block in paragraphs[index : index + 2]:
                assert "—" not in block and ";" not in block, name

    def test_the_module_says_the_figures_come_from_the_run(self) -> None:
        assert "is read from the run on the committed" in (sketches.__doc__ or "")


# --- The strategy: twenty-five cohorts make one portfolio ------------------------


def _bars(scene, side: str):
    return [s for s in scene.strokes if s.gid.startswith("cohort-") and s.gid.endswith(side)]


class TestTheCohortCounts:
    """Each count the sketch prints, measured on the run apart from the module."""

    def test_each_cohort_is_the_top_n_long_and_the_top_n_short(self, run, figures) -> None:
        cohorts, _ = figures
        formed = run.longs.any(axis=1)
        assert set(run.longs.sum(axis=1)[formed]) == {momentum.TOP_N} == {cohorts.longs}
        assert set(run.shorts.sum(axis=1)[formed]) == {momentum.TOP_N}
        assert cohorts.picks == 2 * momentum.TOP_N
        assert int(np.flatnonzero(formed)[0]) == momentum.LOOKBACK

    def test_a_full_day_holds_hold_days_cohorts(self, run, figures) -> None:
        cohorts, _ = figures
        assert int(run.held.max()) == momentum.HOLD_DAYS == cohorts.hold_days

    def test_every_full_day_holds_the_same_count_of_picks(self, run, figures) -> None:
        """A pick is one stock marked by one cohort. On a full day the cohorts
        held are the formations of the last ``HOLD_DAYS`` rows."""
        cohorts, _ = figures
        marks = (run.longs | run.shorts).sum(axis=1)
        full = np.flatnonzero(run.held == momentum.HOLD_DAYS)
        found = {int(marks[t - momentum.HOLD_DAYS : t].sum()) for t in full}
        assert found == {momentum.HOLD_DAYS * 2 * momentum.TOP_N} == {cohorts.picks_held}

    def test_the_picks_are_not_the_positions(self, run, figures) -> None:
        """A stock long in one cohort and short in another nets out of the
        positions, so on some full days the positions sum to less than the
        picks. The sketch says picks for that reason."""
        cohorts, _ = figures
        full = np.flatnonzero(run.held == momentum.HOLD_DAYS)
        netted = np.abs(run.lagged[full]).sum(axis=1)
        assert netted.max() == cohorts.picks_held
        assert netted.min() < cohorts.picks_held
        assert "positions" not in " ".join(
            label for scene in scenes(*figures) for label in scene.labels
        )

    def test_the_divisor_is_the_one_the_script_divides_by(self, run, figures) -> None:
        cohorts, _ = figures
        longs, shorts = run.longs, run.shorts
        positions = momentum.overlapping_positions(longs, shorts)
        assert np.array_equal(
            momentum.daily_returns(positions, run.values, cohorts.divisor), run.daily
        )
        assert not np.array_equal(
            momentum.daily_returns(positions, run.values, cohorts.divisor + 1), run.daily
        )

    def test_the_2007_window_opens_on_one_cohort_and_fills_a_day_at_a_time(
        self, run, figures
    ) -> None:
        cohorts, _ = figures
        window, _ = _window(run)
        start = run.days.get_loc(window[0])
        assert cohorts.opens == window[0] == run.days[momentum.LOOKBACK + 1]
        assert cohorts.held_at_open == int(run.held[start]) == 1
        inside = run.held[start : start + len(window)]
        assert cohorts.short_days == int((inside < momentum.HOLD_DAYS).sum())
        assert list(inside[: cohorts.short_days + 1]) == list(range(1, momentum.HOLD_DAYS + 1))

    def test_the_labels_print_the_runs_counts(self, run, every) -> None:
        window, _ = _window(run)
        start = run.days.get_loc(window[0])
        inside = run.held[start : start + len(window)]
        assert every[0].labels == _cohort_labels(
            int(run.held.max()),
            int(run.longs[momentum.LOOKBACK].sum()),
            int(run.shorts[momentum.LOOKBACK].sum()),
            int(run.held.max()) * 2 * momentum.TOP_N,
            int((inside < run.held.max()).sum()),
        )

    def test_the_title_spells_the_count(self, every, figures) -> None:
        assert (
            every[0].title
            == f"{spelled(figures[0].hold_days).capitalize()} cohorts make one portfolio"
        )
        assert every[0].title == "Twenty-five cohorts make one portfolio"


class TestSpelledCounts:
    @pytest.mark.parametrize(
        ("count", "words"),
        [
            (1, "one"),
            (9, "nine"),
            (10, "ten"),
            (13, "thirteen"),
            (20, "twenty"),
            (24, "twenty-four"),
            (25, "twenty-five"),
            (99, "ninety-nine"),
        ],
    )
    def test_each_count_in_words(self, count, words) -> None:
        assert spelled(count) == words

    @pytest.mark.parametrize("count", [0, 100])
    def test_a_count_outside_one_to_ninety_nine_is_refused(self, count) -> None:
        with pytest.raises(ValueError, match="from 1 to 99"):
            spelled(count)


class TestTheCohortsSketch:
    def test_its_colours(self, every, figures) -> None:
        """Grey context, green longs, red shorts and the red warning of a short
        book, the brass line the sketch points at, and black arithmetic."""
        scene, n = every[0], figures[0].hold_days
        assert _stroke(scene, "axis").color == MUTED
        assert _stroke(scene, "held").color == ACCENT and _stroke(scene, "held").dashed
        assert _stroke(scene, "ramp").color == LOST
        assert all(bar.color == GOOD for bar in _bars(scene, "-long"))
        assert all(bar.color == LOST for bar in _bars(scene, "-short"))
        labels = scene.labels
        inks = [MUTED, GOOD, LOST, INK, ACCENT, INK, INK, INK, INK, LOST, LOST]
        assert [_label(scene, text).color for text in labels] == inks
        assert _label(scene, f"{n} cohorts held").names == "held"

    def test_one_bar_per_cohort_each_a_day_later_and_a_row_lower(self, every, figures) -> None:
        scene, n = every[0], figures[0].hold_days
        longs, shorts = _bars(scene, "-long"), _bars(scene, "-short")
        assert len(longs) == len(shorts) == n
        for k, (green, red) in enumerate(zip(longs, shorts, strict=True)):
            for bar in (green, red):
                assert (bar.x.min(), bar.x.max()) == pytest.approx((day_x(k), day_x(k + n)))
            assert set(np.round(green.y, 9)) == {round(cohort_y(k) + HALF, 9)}
            assert set(np.round(red.y, 9)) == {round(cohort_y(k) - HALF, 9)}
        assert np.diff([cohort_y(k) for k in range(n)]) == pytest.approx(
            [-sketches.PITCH] * (n - 1)
        )
        assert sketches.PITCH > 2 * HALF

    def test_the_first_cohort_draws_first_and_the_rest_one_at_a_time(self, every, figures) -> None:
        n = figures[0].hold_days
        gids = [s.gid for s in every[0].strokes if s.gid.startswith("cohort-")]
        assert gids == [f"cohort-{k}-{side}" for k in range(n) for side in ("long", "short")]

    def test_the_long_label_sits_above_the_short_label_left_of_the_first_bar(self, every) -> None:
        """Colour is never the only cue: the green line is the upper one and
        its words sit above, and the red line's sit below."""
        scene = every[0]
        long_, short = (_labels_of(scene, f"cohort-0-{side}")[0] for side in ("long", "short"))
        assert long_.y > cohort_y(0) > short.y
        assert long_.ha == short.ha == "right"
        assert long_.x < day_x(0) and short.x < day_x(0)

    def test_the_dashed_line_cuts_every_bar_and_only_on_one_day(self, every, figures) -> None:
        """The first cohort's last day is the last cohort's first, and that is
        the one day every cohort is held."""
        scene, n = every[0], figures[0].hold_days
        line = _stroke(scene, "held")
        (x,) = set(np.round(line.x, 9))
        for bar in _bars(scene, "-long") + _bars(scene, "-short"):
            assert bar.x.min() < x < bar.x.max(), bar.gid
        first, last = _bars(scene, "-long")[0], _bars(scene, "-long")[-1]
        assert x + sketches.DX > first.x.max() and x - sketches.DX < last.x.min()
        assert line.y.max() > cohort_y(0) + HALF and line.y.min() < AXIS_Y
        assert _label(scene, f"{n} cohorts held").x == pytest.approx(x)

    def test_the_red_stretch_covers_the_days_short_of_a_full_book(self, every, figures) -> None:
        cohorts = figures[0]
        ramp = _stroke(every[0], "ramp")
        assert set(np.round(ramp.y, 9)) == {AXIS_Y}
        assert (ramp.x.min(), ramp.x.max()) == pytest.approx((day_x(0), day_x(cohorts.short_days)))
        assert ramp.x.max() < _stroke(every[0], "held").x[0]
        axis = _stroke(every[0], "axis")
        assert axis.x.min() < ramp.x.min() and axis.x.max() > _bars(every[0], "-long")[-1].x.max()

    def test_made_up_counts_move_the_title_and_labels(self) -> None:
        made_up = Cohorts(
            hold_days=20,
            longs=30,
            picks=60,
            picks_held=1200,
            divisor=1200,
            opens=pd.Timestamp("2009-01-02"),
            held_at_open=1,
            short_days=19,
        )
        scene = _cohorts(made_up)
        assert scene.title == "Twenty cohorts make one portfolio"
        assert scene.labels == _cohort_labels(20, 30, 30, 1200, 19)
        assert len(_bars(scene, "-long")) == 20

    @pytest.mark.parametrize(
        ("change", "match"),
        [
            ({"held_at_open": 2}, "opens on 2 cohorts"),
            ({"short_days": 23}, "23 days short of 25"),
            ({"picks_held": 2400}, "and it divides by"),
            ({"divisor": 100}, "and it divides by 100"),
        ],
        ids=["opens on two", "fills unevenly", "picks", "divisor"],
    )
    def test_counts_that_would_make_the_drawing_false_are_refused(
        self, figures, change, match
    ) -> None:
        with pytest.raises(ValueError, match=match):
            _cohorts(dataclasses.replace(figures[0], **change))

    def test_its_alt_text_says_what_the_picture_shows(self, every, figures) -> None:
        n = figures[0].hold_days
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert f"One bar {n} days long appears at the top left, a green line over a red line" in alt
        assert f"{spelled(n - 1).capitalize()} more bars follow" in alt
        assert "each starting one day later and one row lower" in alt
        assert f"a staircase of {n}" in alt
        assert f"A brown dashed line drops through all {n} bars" in alt
        assert "on the day the first bar ends and the last begins" in alt
        assert "a red stretch covers the axis from the first bar’s start to the dashed line" in alt
        assert "positions" not in alt


# --- Lesson 1: add, or multiply ------------------------------------------------


class TestTheReturnFigures:
    def test_the_figures_are_the_scripts_over_2007(self, run, figures) -> None:
        _, returns = figures
        _, r = _window(run)
        printed = momentum.window_figures(run.daily, run.days, "2007")
        assert returns.daily == pytest.approx(tuple(r), abs=0)
        assert (returns.total, returns.growth) == pytest.approx((r.sum(), np.prod(1 + r)))
        assert returns.arithmetic == printed.arithmetic_annual
        assert returns.compounded == printed.compounded_apr
        assert returns.trading_days == momentum.TRADING_DAYS == 252

    def test_adding_then_scaling_gives_the_arithmetic_figure(self, figures) -> None:
        _, returns = figures
        assert returns.total * 252 / returns.days == pytest.approx(returns.arithmetic, rel=1e-12)

    def test_multiplying_then_raising_gives_the_compounded_figure(self, figures) -> None:
        _, returns = figures
        assert returns.growth ** (252 / returns.days) - 1 == pytest.approx(
            returns.compounded, rel=1e-12
        )

    def test_the_labels_print_the_runs_figures(self, run, every) -> None:
        _, r = _window(run)
        printed = momentum.window_figures(run.daily, run.days, "2007")
        assert every[1].labels == _return_labels(
            len(r), r.sum(), np.prod(1 + r), printed.arithmetic_annual, printed.compounded_apr
        )

    def test_the_labels_match_what_the_script_prints(self, every) -> None:
        """The two annual figures print as the script's own print lines format
        them, which the post's Lesson 1 table quotes."""
        labels = every[1].labels
        assert labels[3].split(",")[0] == "0.3200"
        assert labels[6].split(",")[0] == "0.3726"


class TestTheReturnsSketch:
    def test_its_title(self, every) -> None:
        assert every[1].title == "Add, or multiply: two annual returns, one window"

    def test_its_colours(self, every) -> None:
        """The daily bars are grey context, the added path black and the
        multiplied path brass, every label in its path's ink."""
        scene = every[1]
        assert {s.gid: s.color for s in scene.strokes} == {
            "daily": MUTED,
            "add": INK,
            "multiply": ACCENT,
        }
        inks = [MUTED, INK, INK, INK, ACCENT, ACCENT, ACCENT]
        assert [_label(scene, text).color for text in scene.labels] == inks

    def test_each_daily_bar_stands_at_its_return(self, every, figures) -> None:
        """Every third point is a bar's tip, at the baseline plus a height in
        proportion to that day's return, and the bars stand evenly spaced."""
        _, returns = figures
        daily = _stroke(every[1], "daily")
        r = np.asarray(returns.daily)
        tips = daily.y[1::3]
        assert len(tips) == returns.days
        assert tips - DAILY_Y == pytest.approx(DAILY_TALLEST * r / np.abs(r).max())
        assert daily.y[0::3] == pytest.approx([DAILY_Y] * returns.days)
        assert daily.x[1::3] == pytest.approx(np.linspace(*DAILY_X, returns.days))
        assert (tips > DAILY_Y).any() and (tips < DAILY_Y).any()

    def test_each_path_reads_left_to_right_on_its_own_row(self, every) -> None:
        scene = every[1]
        for gid, first, result in (
            ("add", "add the", "Avg Ann Ret"),
            ("multiply", "multiply the", "APR"),
        ):
            arrow = _stroke(scene, gid)
            start = next(s for s in scene.labels if s.startswith(first))
            end = next(s for s in scene.labels if s.endswith(result))
            assert _label(scene, start).x < arrow.x.min() < arrow.x.max() < _label(scene, end).x
            assert _label(scene, start).y == pytest.approx(arrow.y[0])
            assert _label(scene, end).y == pytest.approx(arrow.y[0])
        assert _stroke(scene, "add").y[0] > _stroke(scene, "multiply").y[0]

    def test_the_books_figures_are_not_on_it(self, every) -> None:
        """Lesson 2 brings in the book's 37 percent, so this sketch carries none
        of the book's figures."""
        words = " ".join([every[1].title, *every[1].labels])
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        for text in (words, alt):
            for figure in (r"(?<![.\d])37\b", r"\bpercent\b", r"\b4\.1\b", r"\bbook\b"):
                assert not re.search(figure, text), figure

    def test_made_up_returns_move_the_labels(self) -> None:
        daily = (0.01, -0.005, 0.02, 0.0)
        r = np.asarray(daily)
        made_up = Returns(
            daily=daily,
            total=float(r.sum()),
            growth=float(np.prod(1 + r)),
            arithmetic=float(252 * r.mean()),
            compounded=float(np.prod(1 + r) ** (252 / 4) - 1),
            trading_days=252,
        )
        scene = _two_returns(made_up)
        assert scene.labels == _return_labels(
            4, r.sum(), np.prod(1 + r), 252 * r.mean(), np.prod(1 + r) ** 63 - 1
        )

    def test_a_window_that_lost_is_refused(self, figures) -> None:
        """The sketch's arrows run to two positive figures."""
        with pytest.raises(ValueError, match="draws a window that gained"):
            _two_returns(dataclasses.replace(figures[1], total=-0.1, growth=0.9))

    def test_its_alt_text_says_what_the_picture_shows(self, every, figures) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "one for each daily return, rises above and dips below a baseline" in alt
        assert "Below it, in black," in alt and "Under that, in brown," in alt
