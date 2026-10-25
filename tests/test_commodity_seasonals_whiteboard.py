"""The pins for the eight whiteboard GIFs in the commodity seasonals post.

Two sketches draw Lesson 1, its natural gas streaks and gasoline's two claims.
Five draw Lesson 2: the range the missing rows leave, a guessed price, what
Chan's 19 needs, how fill 2 carries June's move, and each fill's miss against
each year's move. One draws Lesson 4's numbered files. The scenes are built
from the natural gas and gasoline runs on the committed EIA files rather than
from a pinned copy of their figures. Most tests check the drawing against the
run, and a few check the run against literal dates, counts and labels the post
quotes, such as test_the_run_gives_these_dates_and_files.

1. The streak sketch draws a dot at each profitable year from 1994 to the
   first loss, a cross at that loss, a note naming the trade as natural gas's
   June contract, the first edition's release between 2008 and 2009, and
   brackets for Chan's counts of 13 and 14, from 1995 above the
   axis and from 1994 below it. What is pinned is that each mark sits at its
   year on one scale, that each bracket ends where
   :func:`chan.commodity_seasonals.runs_ending` says that count ends, and
   that other figures move the marks and the labels.
2. The gasoline sketch draws a dot at each profitable gasoline year from 1995
   to 2015, a cross at each loss, a span under the years with no row, the
   first edition's release, and brackets for the sidebar's claim and the main
   text's count. What is pinned is that each mark sits at its year on one
   scale, that no year without a row gets a mark, that the sidebar's bracket
   ends before the release and the first loss while the main text's covers
   every loss, and that other figures move the marks and the labels.
3. The range sketch draws gasoline's years and a scale of counts. What is
   pinned is that the files' range runs from the profitable years to those
   plus the missing ones, and that Chan's count sits at its top end.
4. The interpolation sketch draws the May contract around 1997's missing
   entry, the straight line across the gap and its guess, and a band of one
   typical miss either side of the guess, split at the exit price. What is
   pinned is that each settlement sits at its trading day and price on one
   scale, that the guess lies on the line, that the band spans the run's
   typical miss and splits where the exit price is, that the guess sits on
   the profit side while the band reaches the loss side, and that other
   figures move it.
5. The Chan's-19 sketch draws Chan's years and the files' as two bars. What
   is pinned is that each box spans its count, that the missing years fill
   exactly the gap between the files' profits and Chan's, and that both bars'
   losses line up.
6. The fill 2 sketch draws May's and June's prices around 1997's gap, June's
   rise and the same rise on May, and fill 2's band. What is pinned is that
   both arrows rise by June's change, that the guess is fill 2's, that the
   band spans fill 2's typical miss and splits at the exit price, and that
   May and June differ by mark as well as by ink.
7. The fill-miss sketch draws each missing year's move with fill 2 and a
   bar of one typical miss. What is pinned is that each dot and bar sit at the
   run's figures on one scale and that every bar crosses zero.
8. The calendar sketch draws the March to June contracts in 2008 and 2006,
   each bar ending at its last trading day, with a dashed line at each entry
   and exit. What is pinned is that June's number in each label is how many
   bars reach that line, that it equals the file the run reads, and that the
   March note follows the dates.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, every
sketch's slower pace, that two draws give the same bytes, and that
each committed GIF is a fresh draw, a comparison that runs only on macOS
arm64 with Comic Sans MS, as
``tests/test_usdcad_tests_whiteboard.py`` explains. The check that
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
from datetime import date, timedelta

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import commodity_seasonals as seasonals
from chan import commodity_seasonals_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.commodity_seasonals_whiteboard import (
    CALENDAR,
    CALENDAR_X,
    FIRST_EDITION,
    STREAK_AXIS_Y,
    FillTwoFigures,
    GasolineFigures,
    GuessFigures,
    StreakFigures,
    _bar_x,
    _cents_x,
    _chan_needs_gaps,
    _count_x,
    _day_x,
    _fill_misses,
    _fill_two_x,
    _fill_two_y,
    _gap_range,
    _gasoline_editions,
    _gasoline_x,
    _guess_x,
    _guess_y,
    _interpolation_guess,
    _june_file,
    _june_move_fill,
    _streak_start,
    _streak_x,
    gif_name,
    june_years,
    main,
    make_commodity_seasonals_whiteboards,
    scenes,
    sketch_timeline,
)
from chan.futures import ng_last_trade
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

POST = REPO_ROOT / "blog" / "commodity-seasonals-lessons.md"

#: Every GIF in the order :func:`make_commodity_seasonals_whiteboards` writes them.
GIFS = [
    "commodity_sketch_streak_start.gif",
    "commodity_sketch_gasoline_editions.gif",
    "commodity_sketch_gap_range.gif",
    "commodity_sketch_interpolation_guess.gif",
    "commodity_sketch_chan_needs_gaps.gif",
    "commodity_sketch_june_move_fill.gif",
    "commodity_sketch_fill_misses.gif",
    "commodity_sketch_june_file.gif",
]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "1. **They rule out the revised edition.**",
    "Gasoline’s main text says 19 profitable years",
    "EIA’s New York Harbor file holds no row",
    "Interpolating, which here means",
    "The losses say more than the gaps.",
    "1. **Fill 1, a straight line**",
    "Both fills guess a profit in all three years",
    "For gasoline that is always contract 1.",
)

STREAK_LABELS = [
    "1994",
    "1995",
    "2006",
    "2007",
    "2008",
    "2009",
    "loss",
    "dot: a profitable year",
    "natural gas, June contract",
    "first edition, Nov 2008",
    "13 from 1995, main text",
    "14 from 1995, sidebar",
    "13 from 1994",
    "14 from 1994",
]

GASOLINE_LABELS = [
    "1995",
    "2008",
    "2015",
    "no row",
    "first edition, Nov 2008",
    "sidebar: a profit every year since 1995",
    "main text: 19 of 21, as of 2015",
    "dot: a profitable year",
    "x: a loss, 2009 and 2012",
    "May contract",
]

RANGE_LABELS = [
    "1995",
    "2015",
    "no row: a profit or a loss?",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "the files allow 16 to 19",
    "Chan: 19",
    "profitable years of 21",
    "gasoline, May contract",
]

NEEDS_LABELS = [
    "19 profits",
    "Chan",
    "16 profits",
    "EIA",
    "2 losses",
    "2009, 2012",
    "no row",
    "1997 to 1999 must all be profits for Chan’s 19",
    "gasoline, May contract",
]

FILL_TWO_LABELS = [
    "May",
    "June",
    "dot: May   ring: June",
    "gasoline",
    "Apr 14, the entry: no May row",
    "June rose 0.9¢",
    "same rise on May: guess 0.621",
    "exit price 0.625",
    "0.630",
    "0.612",
    "fill 2’s typical miss either side",
    "entry here: a loss",
    "entry here: a profit",
]

MISS_LABELS = [
    "loss",
    "profit",
    "1997",
    "67%",
    "1998",
    "74%",
    "1999",
    "82%",
    "-1",
    "+1",
    "cents a gallon",
    "chance of profit",
    "dot: the year’s move with fill 2",
    "bar: fill 2’s typical miss either side",
    "gasoline, May contract",
]

GUESS_LABELS = [
    "gasoline, May contract, April 1997",
    "Apr 14, the entry: no row",
    "exit price 0.625",
    "straight-line guess 0.616",
    "0.635",
    "0.597",
    "one typical miss either side",
    "entry here: a loss",
    "entry here: a profit",
]

JUNE_LABELS = [
    "March",
    "April",
    "May",
    "June",
    "2008",
    "March still trading",
    "June is contract 4 on Feb 25",
    "contract 2 on Apr 15",
    "March",
    "April",
    "May",
    "June",
    "2006",
    "March has expired",
    "June is contract 3 on Feb 27",
    "contract 2 on Apr 13",
    "June’s number is how many bars each line crosses",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def streaks():
    return StreakFigures.from_run()


@pytest.fixture(scope="module")
def years():
    return june_years()


@pytest.fixture(scope="module")
def gasoline():
    return GasolineFigures.from_run()


@pytest.fixture(scope="module")
def guess():
    return GuessFigures.from_run()


@pytest.fixture(scope="module")
def fill_two():
    return FillTwoFigures.from_run()


@pytest.fixture(scope="module")
def every(streaks, years, gasoline, guess, fill_two):
    return scenes(streaks, years, gasoline, guess, fill_two)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, streaks, years, gasoline, guess, fill_two):
    return make_commodity_seasonals_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"),
        streaks=streaks,
        years=years,
        gasoline=gasoline,
        guess=guess,
        fill_two=fill_two,
    )


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


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_eight_in_the_order_the_post_reads_them(self, every) -> None:
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

    def test_each_sketch_of_one_trade_names_it(self, every) -> None:
        """A reader who meets a sketch before its paragraph can tell which
        commodity it draws, from its title or from one grey note. A title that
        names the commodity leaves the note only the contract. The calendar
        sketch draws several natural gas contracts and names each one, so it
        is the exception."""
        trades = {
            "streak_start": ("natural gas", "June contract"),
            "gasoline_editions": ("gasoline", "May contract"),
            "gap_range": ("gasoline", "May contract"),
            "interpolation_guess": ("gasoline", "May contract"),
            "chan_needs_gaps": ("gasoline", "May contract"),
            "fill_misses": ("gasoline", "May contract"),
            "june_move_fill": ("gasoline", "gasoline"),
        }
        assert set(trades) | {"june_file"} == {scene.slug for scene in every}
        for scene in every:
            if scene.slug not in trades:
                continue
            commodity, contract = trades[scene.slug]
            notes = [label for label in scene.labels if contract in label]
            assert len(notes) == 1, scene.slug
            assert _label(scene, notes[0]).color == MUTED, scene.slug
            in_title = commodity in scene.title.lower()
            assert (commodity in notes[0]) != in_title, scene.slug

    def test_every_pale_tint_has_a_green_edge(self, every) -> None:
        """No sketch draws a tint today. One that does would need the
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

    def test_every_sketch_builds_slowly_and_holds_twelve_seconds(self, every) -> None:
        """The pace the owner asked for, for each sketch in turn: each label alone
        for 0.9 s and the drawing for 12 s, the equity post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == (
            "streak_start",
            "gasoline_editions",
            "gap_range",
            "interpolation_guess",
            "chan_needs_gaps",
            "june_move_fill",
            "fill_misses",
            "june_file",
        )
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

    def test_the_alt_text_says_slow_exactly_when_the_sketch_is_paced(self, every) -> None:
        """A reader learns the pace from the alt text: "drawn slowly" and a
        twelve-second hold for each paced sketch, and neither for the rest."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(
        self, gifs, tmp_path, streaks, years, gasoline, guess, fill_two
    ) -> None:
        again = make_commodity_seasonals_whiteboards(
            out_dir=tmp_path,
            streaks=streaks,
            years=years,
            gasoline=gasoline,
            guess=guess,
            fill_two=fill_two,
        )
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
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
            ), f"{path.name}: redraw with: uv run python -m chan.commodity_seasonals_whiteboard"


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

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Each label is quoted after the one drawn before it, and a label drawn
        twice, such as the calendar's month names, is quoted twice."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2


# --- Lesson 1: the streak sketch -----------------------------------------------


class TestTheStreakFigures:
    def test_the_run_gives_profitable_years_to_2008_and_a_loss_in_2009(self, streaks) -> None:
        assert streaks.years == tuple((year, year < 2009) for year in range(1994, 2010))
        assert streaks.loss == 2009

    def test_each_count_ends_where_the_runs_streak_reaches_it(self, streaks) -> None:
        gas = seasonals.natural_gas_trades(*seasonals.NG_YEARS)
        for start in sketches.STARTS:
            runs = seasonals.runs_ending([t for t in gas if t.year >= start])
            for (count, _), end in zip(sketches.BOOK_COUNTS, streaks.ends[start], strict=True):
                assert runs[end] == count
                assert end - start + 1 == count

    def test_counted_from_1995_the_streaks_end_in_2007_and_2008_and_from_1994_a_year_earlier(
        self, streaks
    ) -> None:
        assert streaks.ends == {1995: (2007, 2008), 1994: (2006, 2007)}

    def test_the_book_counts_are_chans(self) -> None:
        assert sketches.BOOK_COUNTS == ((13, "main text"), (14, "sidebar"))
        assert sketches.STARTS == (1995, 1994)


class TestTheStreakSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "The start year decides where a streak ends"
        assert every[0].labels == STREAK_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert _stroke(scene, "profitable").color == GOOD
        assert _label(scene, "dot: a profitable year").color == GOOD
        assert _label(scene, "natural gas, June contract").color == MUTED
        assert _stroke(scene, "loss").color == LOST
        assert _label(scene, "loss").color == LOST
        release = _stroke(scene, "release")
        assert (release.color, release.dashed) == (MUTED, True)
        for start, color in ((1995, ACCENT), (1994, INK)):
            for count in (13, 14):
                gid = f"from-{start}-{count}"
                assert _stroke(scene, gid).color == color, gid
                (label,) = [s for s in scene.steps if isinstance(s, Label) and s.names == gid]
                assert label.color == color, gid

    def test_profitable_years_are_dots_and_the_loss_a_cross(self, every, streaks) -> None:
        """Colour is never the only cue: a profitable year is a dot and the loss
        a cross drawn as lines, each named by its own label."""
        scene = every[0]
        dots, cross = _stroke(scene, "profitable"), _stroke(scene, "loss")
        assert dots.dots > 0 and cross.dots == 0 and cross.points > 1
        won = [year for year, profitable in streaks.years if profitable]
        assert dots.x == pytest.approx([_streak_x(year, streaks) for year in won])
        assert set(dots.y) == {STREAK_AXIS_Y}
        assert cross.x.mean() == pytest.approx(_streak_x(streaks.loss, streaks))

    def test_years_sit_at_one_scale(self, every, streaks) -> None:
        xs = [_streak_x(year, streaks) for year, _ in streaks.years]
        assert np.diff(xs) == pytest.approx([xs[1] - xs[0]] * (len(xs) - 1))
        for year in ("1994", "1995", "2006", "2007", "2008", "2009"):
            assert _label(every[0], year).x == pytest.approx(_streak_x(int(year), streaks))

    def test_each_bracket_runs_from_its_start_to_its_end(self, every, streaks) -> None:
        scene = every[0]
        for start in sketches.STARTS:
            for (count, _), end in zip(sketches.BOOK_COUNTS, streaks.ends[start], strict=True):
                bracket = _stroke(scene, f"from-{start}-{count}")
                assert (bracket.x.min(), bracket.x.max()) == pytest.approx(
                    (_streak_x(start, streaks), _streak_x(end, streaks))
                )

    def test_1995_sits_above_the_axis_and_1994_below(self, every) -> None:
        scene = every[0]
        for count in (13, 14):
            assert _stroke(scene, f"from-1995-{count}").y.min() > STREAK_AXIS_Y
            assert _stroke(scene, f"from-1994-{count}").y.max() < STREAK_AXIS_Y
        # The longer streak sits further from the axis on each side.
        assert _stroke(scene, "from-1995-14").y.min() > _stroke(scene, "from-1995-13").y.max()
        assert _stroke(scene, "from-1994-14").y.max() < _stroke(scene, "from-1994-13").y.min()

    def test_the_release_sits_in_november_2008_after_every_bracket(self, every, streaks) -> None:
        scene = every[0]
        release = _stroke(scene, "release")
        assert FIRST_EDITION == (2008, 11)
        slot = _streak_x(2009, streaks) - _streak_x(2008, streaks)
        assert release.x[0] == pytest.approx(_streak_x(2008, streaks) + (10.5 / 12 - 0.5) * slot)
        assert set(release.x) == {release.x[0]}
        brackets = [s for s in scene.strokes if s.gid.startswith("from-")]
        assert max(b.x.max() for b in brackets) < release.x[0] < _streak_x(2009, streaks)

    def test_other_figures_move_the_marks_and_the_labels(self) -> None:
        made_up = StreakFigures(
            years=tuple((year, year != 2001) for year in range(1985, 2002)),
            ends={1995: (2000, 2001), 1994: (1999, 2000)},
        )
        scene = _streak_start(made_up)
        assert made_up.loss == 2001
        assert _stroke(scene, "from-1995-13").x.max() == pytest.approx(_streak_x(2000, made_up))
        assert _stroke(scene, "loss").x.mean() == pytest.approx(_streak_x(2001, made_up))
        assert {"1994", "1995", "1999", "2000", "2001"} <= set(scene.labels)
        assert "1985" not in scene.labels
        assert "2009" not in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every, streaks) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "a green dot" in alt and "a red cross" in alt and "dashed grey line" in alt
        assert "names the trade as “natural gas, June contract”" in alt
        for start, colour in ((1995, "brown"), (1994, "black")):
            assert f"two {colour} brackets start at {start}" in alt
            for (count, _), end in zip(sketches.BOOK_COUNTS, streaks.ends[start], strict=True):
                assert re.search(rf"“{count} from {start}[^”]*” ends at {end}", alt), (start, count)


# --- Lesson 1: the gasoline sketch ---------------------------------------------


class TestTheGasolineFigures:
    def test_the_run_gives_these_years(self, gasoline) -> None:
        assert [year for year, _ in gasoline.years] == list(range(1995, 2016))
        assert gasoline.lost == [2009, 2012]
        assert gasoline.gaps == [1997, 1998, 1999]
        assert len(gasoline.won) == 16

    def test_the_count_is_chans_and_spans_the_axis(self, gasoline) -> None:
        """Chan's 19 of 21 counts the 21 years the axis draws."""
        assert sketches.GASOLINE_COUNT == (19, 21)
        assert len(gasoline.years) == sketches.GASOLINE_COUNT[1]

    def test_no_loss_falls_in_the_first_editions_years(self, gasoline) -> None:
        assert min(gasoline.lost) > FIRST_EDITION[0]


class TestTheGasolineSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Gasoline’s two claims read as two editions"
        assert every[1].labels == GASOLINE_LABELS

    def test_its_colours(self, every, gasoline) -> None:
        scene = every[1]
        assert _stroke(scene, "profitable").color == GOOD
        assert _label(scene, "dot: a profitable year").color == GOOD
        for year in gasoline.lost:
            assert _stroke(scene, f"loss-{year}").color == LOST
        assert _label(scene, "x: a loss, 2009 and 2012").color == LOST
        assert _stroke(scene, "gap-0").color == MUTED
        assert _label(scene, "no row").color == MUTED
        release = _stroke(scene, "release")
        assert (release.color, release.dashed) == (MUTED, True)
        assert _stroke(scene, "sidebar").color == ACCENT
        assert _label(scene, "sidebar: a profit every year since 1995").color == ACCENT
        assert _stroke(scene, "main-text").color == INK
        assert _label(scene, "main text: 19 of 21, as of 2015").color == INK
        assert _label(scene, "May contract").color == MUTED

    def test_every_mark_sits_at_its_year_on_one_scale(self, every, gasoline) -> None:
        scene = every[1]
        dots = _stroke(scene, "profitable")
        assert list(dots.x) == pytest.approx([_gasoline_x(y, gasoline) for y in gasoline.won])
        for year in gasoline.lost:
            assert _stroke(scene, f"loss-{year}").x.mean() == pytest.approx(
                _gasoline_x(year, gasoline)
            )
        for year in ("1995", "2008", "2015"):
            assert _label(scene, year).x == pytest.approx(_gasoline_x(int(year), gasoline))

    def test_a_year_with_no_row_gets_no_mark_and_sits_under_the_span(self, every, gasoline) -> None:
        scene = every[1]
        marked = list(_stroke(scene, "profitable").x) + [
            _stroke(scene, f"loss-{year}").x.mean() for year in gasoline.lost
        ]
        span = _stroke(scene, "gap-0")
        for year in gasoline.gaps:
            x = _gasoline_x(year, gasoline)
            assert all(abs(m - x) > 0.1 for m in marked), year
            assert span.x.min() - 1e-9 <= x <= span.x.max() + 1e-9, year
        assert span.y.max() < sketches.GASOLINE_AXIS_Y
        note = _label(scene, "no row")
        assert note.x == pytest.approx((span.x.min() + span.x.max()) / 2)
        assert note.y < span.y.min()

    def test_the_sidebar_ends_before_the_release_and_the_main_text_covers_every_loss(
        self, every, gasoline
    ) -> None:
        scene = every[1]
        sidebar, main_text = _stroke(scene, "sidebar"), _stroke(scene, "main-text")
        release = _stroke(scene, "release").x[0]
        first_loss = _gasoline_x(min(gasoline.lost), gasoline)
        assert sidebar.x.min() == pytest.approx(_gasoline_x(1995, gasoline))
        assert sidebar.x.max() == pytest.approx(_gasoline_x(FIRST_EDITION[0], gasoline))
        assert sidebar.x.max() < release < first_loss
        assert main_text.x.min() == pytest.approx(_gasoline_x(1995, gasoline))
        assert main_text.x.max() == pytest.approx(_gasoline_x(2015, gasoline))
        assert main_text.x.max() >= _gasoline_x(max(gasoline.lost), gasoline)
        assert sketches.GASOLINE_AXIS_Y < sidebar.y.min() and sidebar.y.max() < main_text.y.min()

    def test_other_figures_move_the_marks_and_the_labels(self) -> None:
        outcomes = {1999: None, 2002: None, 2003: None, 2004: False, 2010: False}
        made_up = GasolineFigures(
            years=tuple((year, outcomes.get(year, True)) for year in range(1995, 2011))
        )
        scene = _gasoline_editions(made_up)
        assert "x: a loss, 2004 and 2010" in scene.labels
        assert "main text: 19 of 21, as of 2010" in scene.labels
        assert {"1995", "2008", "2010"} <= set(scene.labels)
        assert "2015" not in scene.labels
        assert scene.labels.count("no row") == 2
        assert _stroke(scene, "gap-1").x.max() == pytest.approx(_gasoline_x(2003, made_up))
        assert _stroke(scene, "main-text").x.max() == pytest.approx(_gasoline_x(2010, made_up))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "2009 and 2012 each have a red cross" in alt
        assert "Under 1997 to 1999, which have no mark" in alt
        assert (
            "a brown bracket, “sidebar: a profit every year since 1995”, runs from 1995 to 2008"
            in alt
        )
        assert "ends before the dashed line and before either cross" in alt
        assert "a black bracket, “main text: 19 of 21, as of 2015”, runs from 1995 to 2015" in alt


# --- Lesson 2: the range, the guess, Chan's 19 and the fill misses ---------------


def _span_ends(stroke) -> tuple[float, float]:
    return stroke.x.min(), stroke.x.max()


class TestTheRangeSketch:
    def test_its_words(self, every) -> None:
        assert every[2].title == "Three missing rows leave a range, not a count"
        assert every[2].labels == RANGE_LABELS

    def test_its_colours(self, every, gasoline) -> None:
        scene = every[2]
        assert _stroke(scene, "profitable").color == GOOD
        for year in gasoline.lost:
            assert _stroke(scene, f"loss-{year}").color == LOST
        assert _stroke(scene, "gaps").color == MUTED
        assert _stroke(scene, "range").color == ACCENT
        assert _label(scene, "the files allow 16 to 19").color == ACCENT
        assert _stroke(scene, "chan").color == INK
        assert _label(scene, "Chan: 19").color == INK

    def test_the_range_runs_from_the_files_profits_to_those_plus_the_gaps(
        self, every, gasoline
    ) -> None:
        scene = every[2]
        low, high = len(gasoline.won), len(gasoline.won) + len(gasoline.gaps)
        assert (low, high) == (16, 19)
        left, right = _span_ends(_stroke(scene, "range"))
        assert left == pytest.approx(_count_x(low, gasoline))
        assert right == pytest.approx(_count_x(high, gasoline))
        for n in range(low - 1, high + 2):
            assert _label(scene, str(n)).x == pytest.approx(_count_x(n, gasoline))

    def test_chans_count_sits_at_the_top_end(self, every, gasoline) -> None:
        chan = _stroke(every[2], "chan")
        assert list(chan.x) == pytest.approx(
            [_count_x(sketches.GASOLINE_COUNT[0], gasoline)] * len(chan.x)
        )
        assert chan.x[0] == pytest.approx(_span_ends(_stroke(every[2], "range"))[1])

    def test_other_figures_move_the_range_and_the_title(self) -> None:
        outcomes = {2000: None, 2001: None, 2004: False}
        made_up = GasolineFigures(
            years=tuple((year, outcomes.get(year, True)) for year in range(1995, 2011))
        )
        scene = _gap_range(made_up)
        assert scene.title == "Two missing rows leave a range, not a count"
        assert "the files allow 13 to 15" in scene.labels
        assert "profitable years of 16" in scene.labels
        assert [str(n) for n in range(12, 17)] == [
            label for label in scene.labels if label.isdigit() and len(label) == 2
        ]

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[2])
        assert "a red cross at 2009 and 2012" in alt
        assert "A grey span under 1997 to 1999, which have no mark" in alt
        assert "A brown bracket over 16 to 19" in alt
        assert "a black mark at 19, the bracket’s top end" in alt


class TestTheGuessFigures:
    def test_it_reads_the_runs_fill_and_the_prices_around_it(self, guess) -> None:
        assert guess.fill == seasonals.gap_fills()[0]
        days = [day for day, _ in guess.prices]
        assert (days[0], days[-1]) == (date(1997, 4, 7), date(1997, 4, 25))
        missing = [
            day
            for day in (date(1997, 4, 7) + timedelta(days=k) for k in range(19))
            if seasonals.is_trading_day(day) and day not in days
        ]
        assert missing == [date(1997, 4, d) for d in (11, 14, 16, 18)]
        assert len(days) == 11
        assert guess.top == pytest.approx(guess.fill.linear + guess.fill.linear_error)
        assert guess.bottom == pytest.approx(guess.fill.linear - guess.fill.linear_error)


class TestTheInterpolationSketch:
    def test_its_words(self, every) -> None:
        assert every[3].title == "Interpolating turns a gap into a guess"
        assert every[3].labels == GUESS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[3]
        assert _stroke(scene, "prices").color == INK
        exit_line = _stroke(scene, "exit")
        assert (exit_line.color, exit_line.dashed) == (MUTED, True)
        assert _stroke(scene, "line").color == ACCENT
        assert _stroke(scene, "guess").color == ACCENT
        assert _label(scene, "straight-line guess 0.616").color == ACCENT
        assert _stroke(scene, "loss-zone").color == LOST
        assert _label(scene, "entry here: a loss").color == LOST
        assert _stroke(scene, "profit-zone").color == GOOD
        assert _label(scene, "entry here: a profit").color == GOOD

    def test_each_price_sits_at_its_trading_day_and_price(self, every, guess) -> None:
        prices = _stroke(every[3], "prices")
        assert list(prices.x) == pytest.approx([_guess_x(d, guess) for d, _ in guess.prices])
        assert list(prices.y) == pytest.approx([_guess_y(p, guess) for _, p in guess.prices])
        steps = np.diff(prices.x)
        gap = list(prices.x).index(_guess_x(guess.fill.before, guess))
        assert steps[gap] == pytest.approx(3 * steps[0])

    def test_the_guess_lies_on_the_line(self, every, guess) -> None:
        scene = every[3]
        line, dot = _stroke(scene, "line"), _stroke(scene, "guess")
        x0, x1, y0, y1 = line.x[0], line.x[-1], line.y[0], line.y[-1]
        on_line = y0 + (dot.x[0] - x0) * (y1 - y0) / (x1 - x0)
        assert dot.y[0] == pytest.approx(on_line)
        assert dot.x[0] == pytest.approx(_guess_x(guess.fill.day, guess))
        assert dot.y[0] == pytest.approx(_guess_y(guess.fill.linear, guess))

    def test_the_band_is_one_typical_miss_either_side_split_at_the_exit(self, every, guess) -> None:
        scene = every[3]
        loss, profit = _stroke(scene, "loss-zone"), _stroke(scene, "profit-zone")
        exit_y = _guess_y(guess.fill.other, guess)
        assert (loss.y.min(), loss.y.max()) == pytest.approx((exit_y, _guess_y(guess.top, guess)))
        assert (profit.y.min(), profit.y.max()) == pytest.approx(
            (_guess_y(guess.bottom, guess), exit_y)
        )
        exit_line = _stroke(scene, "exit")
        assert list(exit_line.y) == pytest.approx([exit_y] * len(exit_line.y))

    def test_the_guess_is_a_profit_and_the_band_reaches_a_loss(self, guess) -> None:
        assert guess.bottom < guess.fill.linear < float(guess.fill.other) < guess.top

    def test_other_figures_move_the_guess_and_the_band(self, guess) -> None:
        moved = dataclasses.replace(guess.fill, linear=0.600, linear_error=0.010)
        scene = _interpolation_guess(GuessFigures(prices=guess.prices, fill=moved))
        assert "straight-line guess 0.600" in scene.labels
        assert {"0.610", "0.590"} <= set(scene.labels)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[3])
        assert "settlements one trading day apart" in alt
        assert "The guess sits in the green part, and the band reaches into the red" in alt


class TestTheChanNeedsGapsSketch:
    def test_its_words(self, every) -> None:
        assert every[4].title == "Chan’s 19 needs all three gaps to be profits"
        assert every[4].labels == NEEDS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[4]
        for gid in ("chan-won", "files-won"):
            assert _stroke(scene, gid).color == GOOD, gid
        for gid in ("chan-lost", "files-lost"):
            assert _stroke(scene, gid).color == LOST, gid
        gap = _stroke(scene, "files-gap")
        assert (gap.color, gap.dashed) == (MUTED, True)
        assert _stroke(scene, "needs").color == ACCENT
        assert _label(scene, "1997 to 1999 must all be profits for Chan’s 19").color == ACCENT

    def test_each_box_spans_its_count(self, every, gasoline) -> None:
        scene = every[4]
        won = len(gasoline.won)
        spans = {
            "chan-won": (0, 19),
            "chan-lost": (19, 21),
            "files-won": (0, won),
            "files-gap": (won, won + len(gasoline.gaps)),
            "files-lost": (won + len(gasoline.gaps), 21),
        }
        for gid, (a, b) in spans.items():
            assert _span_ends(_stroke(scene, gid)) == pytest.approx(
                (_bar_x(a, gasoline), _bar_x(b, gasoline))
            ), gid

    def test_the_missing_years_fill_the_gap_to_chans_profits(self, every) -> None:
        scene = every[4]
        assert _span_ends(_stroke(scene, "files-gap"))[1] == pytest.approx(
            _span_ends(_stroke(scene, "chan-won"))[1]
        )
        assert _span_ends(_stroke(scene, "files-lost")) == pytest.approx(
            _span_ends(_stroke(scene, "chan-lost"))
        )

    def test_other_figures_move_the_boxes_and_the_labels(self) -> None:
        outcomes = {2000: None, 2001: None, 2004: False, 2007: False}
        made_up = GasolineFigures(
            years=tuple((year, outcomes.get(year, True)) for year in range(1995, 2016))
        )
        scene = _chan_needs_gaps(made_up)
        assert scene.title == "Chan’s 19 needs all two gaps to be profits"
        assert {"17 profits", "2004, 2007"} <= set(scene.labels)
        assert "2000 to 2001 must all be profits for Chan’s 19" in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[4])
        assert "two bars of 21 years" in alt
        assert "both bars end in the same two losses" in alt
        assert "sits under the last three of Chan’s profits" in alt


class TestTheFillTwoSketch:
    def test_its_words(self, every) -> None:
        assert every[5].title == "Fill 2 carries June’s move across the gap"
        assert every[5].labels == FILL_TWO_LABELS

    def test_its_colours_and_marks(self, every, fill_two) -> None:
        scene = every[5]
        may = _stroke(scene, "may")
        assert (may.color, may.dots) == (INK, 6.0)
        for k in range(len(fill_two.june)):
            ring = _stroke(scene, f"june-{k}")
            assert (ring.color, ring.dots) == (MUTED, 0.0), k
            assert len(ring.x) > 1 and ring.x[0] == pytest.approx(ring.x[-1]), k
        assert _stroke(scene, "june-rise").color == MUTED
        assert _stroke(scene, "may-rise").color == ACCENT
        assert _stroke(scene, "guess").color == ACCENT
        assert _stroke(scene, "loss-zone").color == LOST
        assert _stroke(scene, "profit-zone").color == GOOD
        exit_line = _stroke(scene, "exit")
        assert (exit_line.color, exit_line.dashed) == (MUTED, True)

    def test_it_reads_the_runs_fill_two_and_both_contracts(self, fill_two) -> None:
        fill = seasonals.gap_fills()[0]
        assert fill_two.fill == fill
        assert fill_two.window == (date(1997, 4, 7), date(1997, 4, 17))
        june = dict(fill_two.june)
        may = dict(fill_two.may)
        assert fill.day not in may and fill.day in june
        assert float(may[fill.base] + june[fill.day] - june[fill.base]) == pytest.approx(fill.june)

    def test_each_mark_sits_at_its_trading_day_and_price(self, every, fill_two) -> None:
        scene = every[5]
        may = _stroke(scene, "may")
        assert list(may.x) == pytest.approx([_fill_two_x(d, fill_two) for d, _ in fill_two.may])
        assert list(may.y) == pytest.approx([_fill_two_y(p, fill_two) for _, p in fill_two.may])
        for k, (d, p) in enumerate(fill_two.june):
            ring = _stroke(scene, f"june-{k}")
            assert (ring.x.min() + ring.x.max()) / 2 == pytest.approx(
                _fill_two_x(d, fill_two), abs=1e-6
            ), k
            assert (ring.y.min() + ring.y.max()) / 2 == pytest.approx(
                _fill_two_y(p, fill_two), abs=1e-6
            ), k

    def test_both_arrows_rise_by_junes_change(self, every, fill_two) -> None:
        """The brown arrow is the grey one carried onto May: same start day,
        same end day, same rise."""
        scene = every[5]
        fill, june, may = fill_two.fill, dict(fill_two.june), dict(fill_two.may)
        grey, brown = _stroke(scene, "june-rise"), _stroke(scene, "may-rise")
        assert (grey.x[0], brown.x[0]) == pytest.approx((_fill_two_x(fill.base, fill_two),) * 2)
        assert grey.y[0] == pytest.approx(_fill_two_y(june[fill.base], fill_two))
        assert brown.y[0] == pytest.approx(_fill_two_y(may[fill.base], fill_two))
        tip = lambda stroke: max(range(len(stroke.x)), key=lambda i: stroke.x[i])  # noqa: E731
        grey_rise = grey.y[tip(grey)] - grey.y[0]
        brown_rise = brown.y[tip(brown)] - brown.y[0]
        assert grey_rise == pytest.approx(brown_rise)
        assert brown.y[tip(brown)] == pytest.approx(_fill_two_y(fill.june, fill_two))
        assert _stroke(scene, "guess").y[0] == pytest.approx(_fill_two_y(fill.june, fill_two))

    def test_the_band_is_fill_twos_miss_split_at_the_exit(self, every, fill_two) -> None:
        scene = every[5]
        loss, profit = _stroke(scene, "loss-zone"), _stroke(scene, "profit-zone")
        exit_y = _fill_two_y(fill_two.fill.other, fill_two)
        assert (loss.y.min(), loss.y.max()) == pytest.approx(
            (exit_y, _fill_two_y(fill_two.top, fill_two))
        )
        assert (profit.y.min(), profit.y.max()) == pytest.approx(
            (_fill_two_y(fill_two.bottom, fill_two), exit_y)
        )
        assert fill_two.bottom < fill_two.fill.june < float(fill_two.fill.other) < fill_two.top
        assert (fill_two.bottom, fill_two.top) == pytest.approx((0.612063, 0.629937), abs=1e-6)

    def test_other_figures_move_the_guess_and_the_band(self, fill_two) -> None:
        moved = dataclasses.replace(fill_two.fill, june_error=0.002)
        scene = _june_move_fill(dataclasses.replace(fill_two, fill=moved))
        assert {"0.623", "0.619"} <= set(scene.labels)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[5])
        assert "Black dots are the May gasoline contract’s settlements and grey rings" in alt
        assert "a brown arrow of the same rise starts at May’s April 8 price" in alt
        assert "The guess sits in the green part just under the line" in alt


class TestTheFillMissesSketch:
    def test_its_words(self, every) -> None:
        assert every[6].title == "Each fill misses by more than the year moved"
        assert every[6].labels == MISS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[6]
        zero = _stroke(scene, "zero")
        assert (zero.color, zero.dashed) == (MUTED, True)
        assert _label(scene, "loss").color == LOST
        assert _label(scene, "profit").color == GOOD
        for year in (1997, 1998, 1999):
            assert _stroke(scene, f"move-{year}").color == ACCENT
            assert _stroke(scene, f"miss-{year}").color == INK

    def test_each_dot_and_bar_sit_at_the_runs_figures(self, every) -> None:
        scene = every[6]
        for fill in seasonals.gap_fills():
            move, miss = 100 * fill.move(fill.june), 100 * fill.june_error
            assert _stroke(scene, f"move-{fill.year}").x[0] == pytest.approx(_cents_x(move))
            assert _span_ends(_stroke(scene, f"miss-{fill.year}")) == pytest.approx(
                (_cents_x(move - miss), _cents_x(move + miss))
            )

    def test_every_bar_crosses_zero_and_every_dot_is_a_profit(self, every) -> None:
        scene = every[6]
        zero = _stroke(scene, "zero").x[0]
        for year in (1997, 1998, 1999):
            left, right = _span_ends(_stroke(scene, f"miss-{year}"))
            assert left < zero < right, year
            assert _stroke(scene, f"move-{year}").x[0] > zero, year

    def test_other_figures_move_the_rows(self) -> None:
        fills = seasonals.gap_fills()
        sure = dataclasses.replace(fills[0], june_error=0.001)
        scene = _fill_misses((sure, *fills[1:]))
        left, _ = _span_ends(_stroke(scene, "miss-1997"))
        assert left > _stroke(scene, "zero").x[0]
        assert "100%" in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[6])
        assert "a black bar of one typical miss either side reaches across zero" in alt
        assert "a brown dot right of zero" in alt


# --- Lesson 4: the calendar sketch ---------------------------------------------


def _reaches(scene, tag: str, x: float) -> list[str]:
    """The months whose bar in year ``tag`` reaches the vertical line at ``x``."""
    return [
        month
        for month in ("march", "april", "may", "june")
        if _stroke(scene, f"{tag}-{month}").x.max() >= x
    ]


class TestTheJuneYears:
    def test_the_run_gives_these_dates_and_files(self, years) -> None:
        still, expired = years
        assert (still.year, still.entry, still.last_trade[0]) == (
            2008,
            date(2008, 2, 25),
            date(2008, 2, 27),
        )
        assert (expired.year, expired.entry, expired.last_trade[0]) == (
            2006,
            date(2006, 2, 27),
            date(2006, 2, 24),
        )
        assert (still.entry_number, still.exit_number) == (4, 2)
        assert (expired.entry_number, expired.exit_number) == (3, 2)
        assert (still.exit, expired.exit) == (date(2008, 4, 15), date(2006, 4, 13))

    def test_each_number_is_the_file_the_trade_reads(self, years) -> None:
        for f in years:
            trade = seasonals.natural_gas_trade(f.year)
            assert trade.entry_symbol == seasonals.NATURAL_GAS[f.entry_number]
            assert trade.exit_symbol == seasonals.NATURAL_GAS[f.exit_number]
            assert f.last_trade == tuple(ng_last_trade(f.year, month) for month in (3, 4, 5, 6))

    def test_each_number_counts_the_contracts_still_trading(self, years) -> None:
        """A contract still trades on its own last day, so June's number is how
        many of the four have a last trading day on or after the day."""
        for f in years:
            for day, number in ((f.entry, f.entry_number), (f.exit, f.exit_number)):
                assert sum(last >= day for last in f.last_trade) == number

    def test_2007_is_left_out_because_its_entry_is_marchs_last_day(self) -> None:
        trade = seasonals.natural_gas_trade(2007)
        assert trade.entry_day == ng_last_trade(2007, 3)

    def test_march_still_trades_on_its_own_last_day(self) -> None:
        """2007 enters on March's last trading day, where the run reads June as
        contract 4, so its note would call March still trading."""
        f = sketches.JuneYear.from_run(2007)
        assert f.entry == f.last_trade[0]
        assert (f.march_trading, f.entry_number) == (True, 4)


class TestTheJuneSketch:
    def test_its_words(self, every) -> None:
        assert every[7].title == "Which file holds the June contract"
        assert every[7].labels == JUNE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[7]
        for tag in ("2008", "2006"):
            assert _stroke(scene, f"{tag}-june").color == ACCENT
            for month in ("march", "april", "may"):
                assert _stroke(scene, f"{tag}-{month}").color == INK
            for moment in ("entry", "exit"):
                line = _stroke(scene, f"{tag}-{moment}")
                assert (line.color, line.dashed) == (MUTED, True)
        for step in scene.steps:
            if not isinstance(step, Label):
                continue
            if re.fullmatch(r"(June is )?contract \d on \w+ \d+", step.text) or step.text == "June":
                assert step.color == ACCENT, step.text
            elif step.text in {"March", "April", "May"} or step.text.startswith("March "):
                assert step.color == MUTED, step.text

    def test_the_calendar_is_one_scale_of_days(self) -> None:
        assert _day_x(CALENDAR[0]) == pytest.approx(CALENDAR_X[0])
        assert _day_x(CALENDAR[1]) == pytest.approx(CALENDAR_X[1])
        per_day = _day_x(date(2008, 3, 2)) - _day_x(date(2008, 3, 1))
        assert _day_x(date(2008, 4, 15)) - _day_x(date(2008, 2, 25)) == pytest.approx(50 * per_day)
        # Month and day decide the place, not the year.
        assert _day_x(date(2006, 4, 13)) == _day_x(date(2008, 4, 13))

    def test_each_bar_ends_at_its_last_trading_day_and_june_runs_off(self, every, years) -> None:
        scene = every[7]
        for f in years:
            for month, last in zip(("march", "april", "may"), f.last_trade, strict=False):
                bar = _stroke(scene, f"{f.year}-{month}")
                assert bar.x.max() == pytest.approx(_day_x(last)), (f.year, month)
                assert bar.x.min() == pytest.approx(CALENDAR_X[0])
            june = _stroke(scene, f"{f.year}-june")
            assert june.x.min() == pytest.approx(CALENDAR_X[0])
            # The shaft runs flat along June's row from the calendar's start
            # past its end, so a shortened shaft bends away from the row.
            shaft = june.x <= CALENDAR_X[1]
            assert june.y[shaft] == pytest.approx([june.y[0]] * int(shaft.sum()))
            assert june.x.max() > CALENDAR_X[1]
            assert f.last_trade[3] > CALENDAR[1].replace(year=f.year)

    def test_june_is_numbered_by_the_bars_each_line_crosses(self, every, years) -> None:
        scene = every[7]
        for f in years:
            tag = str(f.year)
            for moment, day, number in (
                ("entry", f.entry, f.entry_number),
                ("exit", f.exit, f.exit_number),
            ):
                line = _stroke(scene, f"{tag}-{moment}")
                assert line.x == pytest.approx([_day_x(day)] * line.points)
                crossed = _reaches(scene, tag, line.x[0])
                assert crossed[-1] == "june" and len(crossed) == number, (tag, moment)
                (label,) = [
                    s
                    for s in scene.steps
                    if isinstance(s, Label) and s.names == line.gid and " on " in s.text
                ]
                assert label.text.endswith(f"contract {number} on {day:%b} {day.day}")
                assert label.x == pytest.approx(line.x[0])

    def test_each_line_spans_its_years_four_bars(self, every, years) -> None:
        scene = every[7]
        for f in years:
            rows = [_stroke(scene, f"{f.year}-{m}").y[0] for m in ("march", "april", "may", "june")]
            for moment in ("entry", "exit"):
                line = _stroke(scene, f"{f.year}-{moment}")
                assert line.y.max() > max(rows) and line.y.min() < min(rows)

    def test_march_is_drawn_still_trading_in_2008_and_expired_in_2006(self, every, years) -> None:
        scene = every[7]
        still, expired = years
        assert _stroke(scene, "2008-march").x.max() > _stroke(scene, "2008-entry").x[0]
        assert _stroke(scene, "2006-march").x.max() < _stroke(scene, "2006-entry").x[0]
        assert (still.march_trading, expired.march_trading) == (True, False)

    def test_the_years_are_stacked_and_their_rows_ordered_by_expiry(self, every) -> None:
        scene = every[7]
        for tag in ("2008", "2006"):
            rows = [_stroke(scene, f"{tag}-{m}").y[0] for m in ("march", "april", "may", "june")]
            assert rows == sorted(rows, reverse=True)
        assert _stroke(scene, "2006-entry").y.max() < _stroke(scene, "2008-entry").y.min()

    def test_other_figures_move_the_bars_the_note_and_the_numbers(self, years) -> None:
        still, expired = years
        swapped = (
            dataclasses.replace(still, entry=date(2008, 2, 28), entry_number=3),
            dataclasses.replace(expired, entry=date(2006, 2, 23), entry_number=4),
        )
        scene = _june_file(*swapped)
        assert "March has expired" in scene.labels[:8]
        assert "March still trading" in scene.labels[8:]
        assert "June is contract 3 on Feb 28" in scene.labels
        assert "June is contract 4 on Feb 23" in scene.labels
        assert len(_reaches(scene, "2008", _stroke(scene, "2008-entry").x[0])) == 3

    def test_it_closes_on_the_rule_it_draws(self, every) -> None:
        last = every[7].steps[-1]
        assert (last.text, last.color) == ("June’s number is how many bars each line crosses", INK)

    def test_its_alt_text_says_what_the_picture_shows(self, every, years) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[7])
        still, expired = years
        for f in years:
            assert f"March’s bar ends on {f.last_trade[0]:%B} {f.last_trade[0].day}" in alt
        assert "crosses all four bars" in alt
        assert "crosses only April, May and June" in alt
        assert alt.count("crosses May and June") == 2
        assert (still.entry_number, expired.entry_number) == (4, 3)
