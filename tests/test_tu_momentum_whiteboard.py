"""The pins for the two whiteboard GIFs in the TU momentum post.

One sketches the correlation table's point that keeping every 25th day tiles
the future returns while the past returns still overlap, and one Lesson 1's
point that the later save keeps 69 other days from the same closes.

1. The table sketch draws the first three kept pairs of the 250/25 cell on the
   2012-05-11 save to scale, with a row of 69 dots that is not to scale. What
   is pinned is each bar's length and place in trading days, measured on the
   rendered frame too, since round caps carry each bar's ink past its line.
   Each future bar starts where the one before ends, with no pixel column of
   ink shared, and the bracket covers exactly the days the first two pasts
   share. Also pinned are the dates and counts it prints, that a cell whose
   hold is not shorter than its lookback is refused, and the facts behind its
   two closing lines: consecutive kept pasts share 225 of their 250 daily
   changes and consecutive kept futures share none.
2. The saves sketch draws the first four kept days of each save to scale.
   What is pinned is that each tick sits at its day, that each later tick
   falls four trading days after an earlier one and before the next, and the
   counts and correlations it prints: 1,996 shared closes, all equal, 69
   kept days in each with none shared, and 0.2719 against 0.2870.

Neither sketch is schematic. The run reads committed vintages, so the tests
read it directly rather than a frozen copy of its figures, and a made-up set
of figures checks that the words follow the data. The 225 shared days, the
four trading days between the saves' first days, the dates of the kept days
after the first, the count of kept days the saves share and the later save's
0.29 at the book's precision had no pin before this module.

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
from scipy.stats import pearsonr

from chan import tu_momentum as tu
from chan import tu_momentum_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.matlab_helpers import backshift, fwdshift
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, INK, MUTED
from chan.tu_momentum_whiteboard import (
    BAR_WIDTH,
    BRACKET_Y,
    CAP,
    DOTS_X,
    LOWER_Y,
    PAIR_YS,
    PAIRS,
    SHOWN,
    TICK_HALF,
    UPPER_Y,
    SaveFigures,
    day_x,
    gif_name,
    kept_rows,
    main,
    make_tu_momentum_whiteboards,
    scenes,
    sketch_timeline,
    tick_scale,
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

POST = REPO_ROOT / "blog" / "tu-momentum-lessons.md"

#: Every GIF in the order :func:`make_tu_momentum_whiteboards` writes them.
GIFS = ["tu_momentum_sketch_futures_tile.gif", "tu_momentum_sketch_no_shared_day.gif"]

#: The paragraph each GIF follows: the correlation table's paragraph on
#: overlapping windows by its opening words, and Lesson 1's paragraph on the
#: later data file by a fragment, since its opening words are free to change.
TILE_PARAGRAPH = "Neighbouring days share almost all of their windows."
SAVES_FRAGMENT = "shift alone moves the 250/25 correlation"

TILE_LABELS = [
    "trading days, to scale",
    "past 250 days",
    "future 25 days",
    "first kept day, 2005-06-01",
    "2005-07-07, one hold later",
    "225 of 250 days shared",
    "2005-08-11, two holds later",
    "69 kept days, every 25th, dots not to scale",
    "future returns: no overlap",
    "past returns: still overlap",
]

SAVES_LABELS = [
    "file ending 2012-05-11",
    "2005-06-01",
    "file ending 2012-05-17",
    "2005-06-07",
    "each 4 trading days later",
    "first 4 kept days of each",
    "1,996 closes in both files, every one equal",
    "69 kept days in each, none shared",
    "250/25 correlation: 0.2719 on the earlier, 0.2870 on the later",
    "at the book’s two decimals: 0.27 against 0.29",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def saves():
    """Both saves' closes, read through the replication's own readers."""
    return tu.read_sources()[1], tu.read_later_save()[1]


@pytest.fixture(scope="module")
def figures():
    return SaveFigures.from_run()


@pytest.fixture(scope="module")
def every(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_tu_momentum_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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


def _alt(text: str, scene) -> str:
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


def _inked(stroke) -> tuple[float, float]:
    """Where a bar's ink starts and ends across, its line extended by the round cap."""
    return float(stroke.x.min()) - CAP, float(stroke.x.max()) + CAP


def _px(x: float) -> float:
    """The pixel column a board position falls at."""
    return x * WIDTH / (whiteboard.XLIM[1] - whiteboard.XLIM[0])


def _ink_columns(frame: np.ndarray, color: str, y: float) -> np.ndarray:
    """The pixel columns left of the dates that hold ``color`` within a bar's reach of ``y``."""
    row = round(HEIGHT - y * HEIGHT / (whiteboard.YLIM[1] - whiteboard.YLIM[0]))
    band = frame[row - 6 : row + 7, : int(_px(sketches.DATES_X)) - 5]
    rgb = np.array([round(v * 255) for v in matplotlib.colors.to_rgb(color)])
    return np.flatnonzero((np.abs(band - rgb).sum(axis=-1) <= 3).any(axis=0))


def _ticks(stroke) -> list[float]:
    """Where a line of ticks has its upright ticks, read from the points that reach above it."""
    top = stroke.y.max()
    return sorted({float(x) for x, y in zip(stroke.x, stroke.y, strict=True) if y == top})


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

    def test_both_sketches_build_slowly_and_hold_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("futures_tile", "no_shared_day")
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
        again = make_tu_momentum_whiteboards(out_dir=tmp_path)
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
        assert not "tu_momentum.png".startswith(sketches.GIF_PREFIX)

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
            ), f"{path.name}: redraw with: uv run python -m chan.tu_momentum_whiteboard"


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
        (tile,) = [k for k, p in enumerate(paragraphs) if p.startswith(TILE_PARAGRAPH)]
        (saves,) = [k for k, p in enumerate(paragraphs) if SAVES_FRAGMENT in p]
        for index, name in zip((tile, saves), GIFS, strict=True):
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_the_tile_sketch_sits_in_the_table_section_and_the_saves_in_lesson_1(self) -> None:
        text = POST.read_text(encoding="utf-8")
        tile, saves = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        table = text.index("### The correlation table")
        rule = text.index("### The rule")
        lesson_1 = text.index("## Lesson 1:")
        lesson_2 = text.index("## Lesson 2:")
        assert table < tile < rule < lesson_1 < saves < lesson_2

    def test_each_gif_is_embedded_once_and_the_chart_still_is(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name
        assert text.count("(../docs/figures/tu_momentum.png)") == 1

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
        assert f"[the whiteboard sketches]({base}src/chan/tu_momentum_whiteboard.py)" in footer
        assert f"[what the sketches draw]({base}tests/test_tu_momentum_whiteboard.py)" in footer

    def test_the_module_says_neither_is_schematic(self) -> None:
        assert "Neither sketch is schematic." in (sketches.__doc__ or "")


# --- The figures, read from the run ----------------------------------------------


class TestTheFigures:
    def test_the_cell_is_the_traded_one(self, figures) -> None:
        assert (figures.lookback, figures.hold) == (tu.LOOKBACK, tu.HOLD_DAYS) == (250, 25)
        assert (figures.step, figures.overlap) == (25, 225)

    def test_kept_rows_are_the_rows_the_correlation_runs_on(self, saves) -> None:
        """For every cell of the table, the past and future returns on the kept
        rows give :func:`chan.tu_momentum.correlation`'s coefficient, p-value
        and row count exactly."""
        for closes in saves:
            cl = closes.to_numpy(dtype=float)
            for lookback in tu.PERIODS:
                for hold in tu.PERIODS:
                    rows = kept_rows(cl, lookback, hold)
                    with np.errstate(invalid="ignore", divide="ignore"):
                        before = backshift(lookback, cl)
                        past = ((cl - before) / before)[rows]
                        future = ((fwdshift(hold, cl) - cl) / cl)[rows]
                    cell = tu.correlation(cl, lookback, hold)
                    found = pearsonr(past, future)
                    assert (float(found[0]), float(found[1]), len(rows)) == (
                        cell.coefficient,
                        cell.p_value,
                        cell.rows,
                    ), (lookback, hold)

    def test_each_save_keeps_69_days_25_rows_apart_from_row_250(self, figures) -> None:
        for kept in (figures.earlier, figures.later):
            assert len(kept.rows) == len(kept.days) == 69
            assert kept.rows[0] == 250
            assert set(np.diff(kept.rows)) == {25}

    def test_the_kept_days_and_correlations(self, figures) -> None:
        assert figures.earlier.save == "2012-05-11"
        assert figures.later.save == "2012-05-17"
        assert figures.earlier.days[:SHOWN] == (
            "2005-06-01",
            "2005-07-07",
            "2005-08-11",
            "2005-09-16",
        )
        assert figures.later.days[:SHOWN] == (
            "2005-06-07",
            "2005-07-13",
            "2005-08-17",
            "2005-09-22",
        )
        assert round(figures.earlier.coefficient, 6) == 0.271855
        assert round(figures.later.coefficient, 6) == 0.287046

    def test_the_saves_share_1996_equal_closes_and_no_kept_day(self, figures, saves) -> None:
        earlier, later = saves
        assert (figures.shared, figures.equal, figures.shared_kept) == (1996, 1996, 0)
        assert str(later.index[0].date()) == "2004-06-07"
        assert figures.offset == 4

    def test_each_later_kept_day_is_the_offset_on_in_the_earlier_saves_days(
        self, figures, saves
    ) -> None:
        """What lets the saves sketch draw both rows on one scale: the later
        save's row r is the earlier save's row r + 4, wherever both exist."""
        earlier, _ = saves
        for row, day in zip(figures.later.rows, figures.later.days, strict=True):
            if row + figures.offset < len(earlier):
                assert str(earlier.index[row + figures.offset].date()) == day

    def test_consecutive_kept_pasts_share_225_daily_changes_and_futures_none(self, figures) -> None:
        """A past return over rows r − 250 to r spans the daily changes into
        rows r − 249 to r, and a future return over r to r + 25 those into
        r + 1 to r + 25. Taken one kept row apart, two pasts share 225 of
        their 250 changes and two futures share none, only the close at the
        boundary."""
        rows = figures.earlier.rows
        for one, next_ in zip(rows, rows[1:], strict=False):
            past = set(range(one - figures.lookback + 1, one + 1))
            past_next = set(range(next_ - figures.lookback + 1, next_ + 1))
            future = set(range(one + 1, one + figures.hold + 1))
            future_next = set(range(next_ + 1, next_ + figures.hold + 1))
            assert len(past & past_next) == figures.overlap == 225
            assert future & future_next == set()
            assert max(future) == next_


# --- The correlation table: future returns end to end, past returns overlap ------


class TestTheTileSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "Future returns end to end, past returns overlap"
        assert every[0].labels == TILE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert _stroke(scene, "axis").color == MUTED
        for k in range(1, PAIRS + 1):
            assert _stroke(scene, f"past-{k}").color == ACCENT
            assert _stroke(scene, f"future-{k}").color == INK
        for gid in ("join-1", "join-2", "bracket-left", "bracket-right"):
            assert _stroke(scene, gid).color == MUTED, gid
        for gid in ("join-1", "join-2"):
            assert _stroke(scene, gid).dashed, gid
        assert not any(_stroke(scene, g).dashed for g in ("bracket-left", "bracket-right"))
        assert _stroke(scene, "kept-days").color == INK
        assert _label(scene, "past 250 days").color == ACCENT
        assert _label(scene, "future 25 days").color == INK
        assert _label(scene, "225 of 250 days shared").color == MUTED
        assert _label(scene, "trading days, to scale").color == MUTED
        for text in (
            "first kept day, 2005-06-01",
            "2005-07-07, one hold later",
            "2005-08-11, two holds later",
            "69 kept days, every 25th, dots not to scale",
            "future returns: no overlap",
        ):
            assert _label(scene, text).color == INK, text
        assert _label(scene, "past returns: still overlap").color == ACCENT

    def test_each_bar_is_drawn_to_scale_at_its_days(self, every, figures) -> None:
        """Past bar k's ink runs from 250 days before kept row k to it, and
        future bar k's from it to 25 days after, at one scale for every bar.
        Each line stops :data:`CAP` inside its days, since its round cap
        carries the ink that far past the line's end."""
        scene = every[0]
        first = figures.earlier.rows[0] - figures.lookback
        for k in range(PAIRS):
            day = figures.earlier.rows[k] - first
            past, future = _stroke(scene, f"past-{k + 1}"), _stroke(scene, f"future-{k + 1}")
            assert _inked(past) == pytest.approx((day_x(day - figures.lookback), day_x(day)))
            assert _inked(future) == pytest.approx((day_x(day), day_x(day + figures.hold)))
            assert set(past.y) == set(future.y) == {PAIR_YS[k]}
            past_ink, future_ink = _inked(past), _inked(future)
            assert past_ink[1] - past_ink[0] == pytest.approx(10 * (future_ink[1] - future_ink[0]))

    def test_the_cap_is_half_the_bar_width_on_the_board(self) -> None:
        """5 points wide at 100 dpi is about 6.9 pixels, so each round cap
        reaches about 3.5 pixels, 0.051 of a board unit, past its line."""
        pixels_per_unit = WIDTH / (whiteboard.XLIM[1] - whiteboard.XLIM[0])
        assert CAP * pixels_per_unit == pytest.approx(BAR_WIDTH / 2 * whiteboard.DPI / 72)
        assert CAP == pytest.approx(0.0511, abs=1e-4)
        assert whiteboard._style()["lines.solid_capstyle"] == "round"

    def test_the_drawn_ink_covers_each_bars_days_and_futures_share_no_column(
        self, every, figures
    ) -> None:
        """Rendered, each bar's ink starts and ends within a pixel of its days,
        and no pixel column holds ink of two neighbouring futures."""
        scene = every[0]
        frame = np.asarray(
            whiteboard.render(scene, [Frame(len(scene.steps), 0, 0)])[0].convert("RGB")
        ).astype(int)
        first = figures.earlier.rows[0] - figures.lookback
        futures = []
        for k in range(PAIRS):
            day = figures.earlier.rows[k] - first
            past = _ink_columns(frame, ACCENT, PAIR_YS[k])
            future = _ink_columns(frame, INK, PAIR_YS[k])
            futures.append(set(future.tolist()))
            for columns, start, end in (
                (past, day - figures.lookback, day),
                (future, day, day + figures.hold),
            ):
                assert abs(columns.min() - _px(day_x(start))) <= 1, (k, start)
                assert abs(columns.max() + 1 - _px(day_x(end))) <= 1, (k, end)
        for one, next_ in zip(futures, futures[1:], strict=False):
            assert not one & next_

    def test_each_future_starts_where_the_one_before_ends(self, every) -> None:
        scene = every[0]
        for k in range(1, PAIRS):
            before, after = _stroke(scene, f"future-{k}"), _stroke(scene, f"future-{k + 1}")
            assert _inked(after)[0] == pytest.approx(_inked(before)[1])
            join = _stroke(scene, f"join-{k}")
            assert set(np.round(join.x, 12)) == {round(_inked(after)[0], 12)}
            assert join.y.max() < PAIR_YS[k - 1] and join.y.min() > PAIR_YS[k]

    def test_each_past_lies_over_all_but_one_hold_of_the_one_before(self, every, figures) -> None:
        scene = every[0]
        for k in range(1, PAIRS):
            before = _inked(_stroke(scene, f"past-{k}"))
            after = _inked(_stroke(scene, f"past-{k + 1}"))
            assert before[1] - after[0] == pytest.approx(figures.overlap * sketches.PER_DAY)
            assert after[0] - before[0] == pytest.approx(figures.step * sketches.PER_DAY)

    def test_the_bracket_covers_the_days_the_first_two_pasts_share(self, every) -> None:
        scene = every[0]
        left, right = _stroke(scene, "bracket-left"), _stroke(scene, "bracket-right")
        first, second = _inked(_stroke(scene, "past-1")), _inked(_stroke(scene, "past-2"))
        assert left.x.min() == pytest.approx(second[0])
        assert right.x.max() == pytest.approx(first[1])
        assert PAIR_YS[1] < BRACKET_Y < PAIR_YS[0]
        words = _label(scene, "225 of 250 days shared")
        assert left.x.max() < words.x < right.x.min() and words.y == BRACKET_Y

    def test_the_axis_runs_under_every_bar(self, every) -> None:
        scene = every[0]
        axis = _stroke(scene, "axis")
        bars = [_inked(s) for s in scene.strokes if s.gid.startswith(("past-", "future-"))]
        assert axis.x.min() == pytest.approx(min(b[0] for b in bars))
        assert axis.x.max() == pytest.approx(max(b[1] for b in bars))
        assert set(axis.y) == {sketches.AXIS_Y} and sketches.AXIS_Y < min(PAIR_YS)

    def test_one_dot_for_each_kept_day_evenly_spaced(self, every, figures) -> None:
        dots = _stroke(every[0], "kept-days")
        assert dots.dots > 0 and dots.points == len(figures.earlier.rows) == 69
        assert (dots.x.min(), dots.x.max()) == pytest.approx(DOTS_X)
        assert np.diff(dots.x) == pytest.approx([np.diff(dots.x)[0]] * 68)

    def test_made_up_cell_and_counts_move_the_words(self, figures) -> None:
        """Another cell with the hold shorter than the lookback, and saves
        keeping different counts, change every word that prints the cell, the
        step, the overlap or a count."""
        earlier = replace(
            figures.earlier, rows=figures.earlier.rows[:60], days=figures.earlier.days[:60]
        )
        later = replace(figures.later, rows=figures.later.rows[:58], days=figures.later.days[:58])
        made_up = replace(figures, lookback=120, hold=20, earlier=earlier, later=later)
        tile, saves = (scene.labels for scene in scenes(made_up))
        assert "past 120 days" in tile
        assert "future 20 days" in tile
        assert "100 of 120 days shared" in tile
        assert "60 kept days, every 20th, dots not to scale" in tile
        assert "60 and 58 kept days, none shared" in saves
        assert "120/20 correlation: 0.2719 on the earlier, 0.2870 on the later" in saves

    @pytest.mark.parametrize(("lookback", "hold"), [(100, 120), (60, 60)])
    def test_a_hold_as_long_as_the_lookback_is_refused(self, figures, lookback, hold) -> None:
        """Then the pasts would tile and the futures overlap, so the title and
        the closing lines would be false."""
        with pytest.raises(ValueError, match="hold shorter than the lookback"):
            scenes(replace(figures, lookback=lookback, hold=hold))

    def test_its_alt_text_says_what_the_picture_shows(self, every, figures) -> None:
        scene = every[0]
        alt = _alt(POST.read_text(encoding="utf-8"), scene)
        assert figures.hold * 10 == figures.lookback
        assert "A grey line under where the bars go" in alt
        assert "a black bar one tenth as long" in alt
        assert figures.step == figures.hold
        assert "A second pair below starts one hold to the right" in alt
        assert PAIR_YS[1] < PAIR_YS[0]
        assert "Its black bar begins exactly where the first black bar ends" in alt
        assert "runs from where the second starts to where the first ends" in alt
        assert "Under the axis, a row of black dots" in alt
        assert sketches.DOTS_Y < sketches.AXIS_Y
        assert (
            "with “future returns: no overlap” in black on the left and "
            "“past returns: still overlap” in brass on the right"
        ) in alt
        left = _label(scene, "future returns: no overlap")
        right = _label(scene, "past returns: still overlap")
        assert (left.ha, right.ha) == ("left", "right") and left.x < right.x


# --- Lesson 1: same closes, no kept day shared ----------------------------------


class TestTheSavesSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Same closes, no kept day shared"
        assert every[1].labels == SAVES_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert _stroke(scene, "upper-ticks").color == INK
        assert _stroke(scene, "lower-ticks").color == ACCENT
        for k in range(1, SHOWN + 1):
            link = _stroke(scene, f"link-{k}")
            assert (link.color, link.dashed) == (MUTED, True)
        for text in ("file ending 2012-05-11", "2005-06-01"):
            assert _label(scene, text).color == INK
        for text in ("file ending 2012-05-17", "2005-06-07"):
            assert _label(scene, text).color == ACCENT
        for text in ("each 4 trading days later", "first 4 kept days of each"):
            assert _label(scene, text).color == MUTED
        for text in SAVES_LABELS[-4:]:
            assert _label(scene, text).color == INK, text

    def test_each_tick_sits_at_its_day_on_one_scale(self, every, figures) -> None:
        """Upper tick k at the earlier save's kept row k, lower tick k at the
        later save's kept row k plus the four rows between the saves' first
        days, both through one affine map."""
        scene = every[1]
        origin, per_day = tick_scale(figures)
        upper = _ticks(_stroke(scene, "upper-ticks"))
        lower = _ticks(_stroke(scene, "lower-ticks"))
        assert upper == pytest.approx([origin + per_day * r for r in figures.earlier.rows[:SHOWN]])
        assert lower == pytest.approx(
            [origin + per_day * (r + figures.offset) for r in figures.later.rows[:SHOWN]]
        )
        assert _stroke(scene, "upper-ticks").y.max() == pytest.approx(UPPER_Y + TICK_HALF)
        assert _stroke(scene, "lower-ticks").y.max() == pytest.approx(LOWER_Y + TICK_HALF)

    def test_each_lower_tick_falls_between_two_upper_ones(self, every, figures) -> None:
        scene = every[1]
        upper = _ticks(_stroke(scene, "upper-ticks"))
        lower = _ticks(_stroke(scene, "lower-ticks"))
        _, per_day = tick_scale(figures)
        for k, x in enumerate(lower):
            assert x - upper[k] == pytest.approx(figures.offset * per_day)
            if k + 1 < len(upper):
                assert upper[k] < x < upper[k + 1]
        assert not set(np.round(upper, 9)) & set(np.round(lower, 9))

    def test_each_link_joins_an_upper_tick_to_the_lower_one_after_it(self, every) -> None:
        scene = every[1]
        upper = _ticks(_stroke(scene, "upper-ticks"))
        lower = _ticks(_stroke(scene, "lower-ticks"))
        for k in range(SHOWN):
            link = _stroke(scene, f"link-{k + 1}")
            assert (link.x[0], link.x[-1]) == pytest.approx((upper[k], lower[k]))
            assert link.y[0] < UPPER_Y - TICK_HALF and link.y[-1] > LOWER_Y + TICK_HALF

    def test_made_up_figures_move_the_words(self, figures) -> None:
        """A made-up offset, shared count, kept-day overlap and pair of
        correlations each change the words that print them."""
        later = replace(
            figures.later,
            coefficient=0.31234,
            days=(figures.earlier.days[0], *figures.later.days[1:]),
        )
        made_up = replace(figures, later=later, offset=3, shared=1990, equal=1989)
        labels = scenes(made_up)[1].labels
        assert "each 3 trading days later" in labels
        assert "1,990 closes in both files, 1,989 equal" in labels
        assert "69 kept days in each, 1 shared" in labels
        assert "250/25 correlation: 0.2719 on the earlier, 0.3123 on the later" in labels
        assert "at the book’s two decimals: 0.27 against 0.31" in labels
        assert scenes(made_up)[1].title == "Some closes differ, 1 kept day shared"

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert (
            "four upright ticks, one for each of the first four days the 250/25 cell keeps" in alt
        )
        assert "A black line with four upright ticks" in alt
        assert "Below it, a brass line with four ticks" in alt
        assert "with “2005-06-01” over its first tick" in alt
        assert "with “2005-06-07” under its first tick" in alt
        assert "Each brass tick sits a short way right of a black tick" in alt
        assert "so no brass tick lines up with a black one" in alt
        assert "Dashed grey links join each black tick to the brass tick after it" in alt
        scene = every[1]
        upper, lower = _stroke(scene, "upper-ticks"), _stroke(scene, "lower-ticks")
        assert (upper.color, lower.color) == (INK, ACCENT) and LOWER_Y < UPPER_Y
        assert len(_ticks(upper)) == len(_ticks(lower)) == SHOWN
        assert _label(scene, "2005-06-01").y > upper.y.max()
        assert _label(scene, "2005-06-07").y < lower.y.min()
        assert all(b > t for t, b in zip(_ticks(upper), _ticks(lower), strict=True))
