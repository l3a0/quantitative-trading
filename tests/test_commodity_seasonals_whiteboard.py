"""The pins for the two whiteboard GIFs in the commodity seasonals post.

One sketches Lesson 1's streaks and one Lesson 4's numbered files. Both read
the natural gas run on the committed EIA files, so every test here reads the
run itself rather than a pinned copy of its figures.

1. The streak sketch draws a dot at each profitable year from 1994 to the
   first loss, a cross at that loss, the first edition's release between 2008
   and 2009, and brackets for Chan's counts of 13 and 14, from 1995 above the
   axis and from 1994 below it. What is pinned is that each mark sits at its
   year on one scale, that each bracket ends where
   :func:`chan.commodity_seasonals.runs_ending` says that count ends, and
   that other figures move the marks and the labels.
2. The calendar sketch draws the March to June contracts in 2008 and 2006,
   each bar ending at its last trading day, with a dashed line at each entry
   and exit. What is pinned is that June's number in each label is how many
   bars reach that line, that it equals the file the run reads, and that the
   March note follows the dates.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, that two
draws give the same bytes, and that each committed GIF is a fresh draw, a
comparison that runs only on macOS arm64 with Comic Sans MS, as
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
from datetime import date

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
    StreakFigures,
    _day_x,
    _june_file,
    _streak_start,
    _streak_x,
    gif_name,
    june_years,
    main,
    make_commodity_seasonals_whiteboards,
    scenes,
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
GIFS = ["commodity_sketch_streak_start.gif", "commodity_sketch_june_file.gif"]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "Read as first-edition figures counted from 1995",
    "For gasoline the answer is simple.",
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
    "first edition, Nov 2008",
    "13 from 1995, main text",
    "14 from 1995, sidebar",
    "13 from 1994",
    "14 from 1994",
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
    "contract 1 is whichever contract stops trading next",
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
def every(streaks, years):
    return scenes(streaks, years)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, streaks, years):
    return make_commodity_seasonals_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), streaks=streaks, years=years
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
            steps = timeline(scene)
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(path) == [f.ms for f in steps], path.name

    def test_each_opens_on_its_title_and_holds_its_drawing(self, every) -> None:
        for scene in every:
            steps = timeline(scene)
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            assert steps[-1].ms == HOLD_MS, scene.slug

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, streaks, years) -> None:
        again = make_commodity_seasonals_whiteboards(out_dir=tmp_path, streaks=streaks, years=years)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, every) -> None:
        for name, scene in zip(GIFS, every, strict=True):
            steps = timeline(scene)
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
        for start, colour in ((1995, "brown"), (1994, "black")):
            assert f"two {colour} brackets start at {start}" in alt
            for (count, _), end in zip(sketches.BOOK_COUNTS, streaks.ends[start], strict=True):
                assert re.search(rf"“{count} from {start}[^”]*” ends at {end}", alt), (start, count)


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


class TestTheJuneSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Which file holds the June contract"
        assert every[1].labels == JUNE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[1]
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
        scene = every[1]
        for f in years:
            for month, last in zip(("march", "april", "may"), f.last_trade, strict=False):
                bar = _stroke(scene, f"{f.year}-{month}")
                assert bar.x.max() == pytest.approx(_day_x(last)), (f.year, month)
                assert bar.x.min() == pytest.approx(CALENDAR_X[0])
            assert _stroke(scene, f"{f.year}-june").x.max() > CALENDAR_X[1]
            assert f.last_trade[3] > CALENDAR[1].replace(year=f.year)

    def test_june_is_numbered_by_the_bars_each_line_crosses(self, every, years) -> None:
        scene = every[1]
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
        scene = every[1]
        for f in years:
            rows = [_stroke(scene, f"{f.year}-{m}").y[0] for m in ("march", "april", "may", "june")]
            for moment in ("entry", "exit"):
                line = _stroke(scene, f"{f.year}-{moment}")
                assert line.y.max() > max(rows) and line.y.min() < min(rows)

    def test_march_is_drawn_still_trading_in_2008_and_expired_in_2006(self, every, years) -> None:
        scene = every[1]
        still, expired = years
        assert _stroke(scene, "2008-march").x.max() > _stroke(scene, "2008-entry").x[0]
        assert _stroke(scene, "2006-march").x.max() < _stroke(scene, "2006-entry").x[0]
        assert (still.march_trading, expired.march_trading) == (True, False)

    def test_the_years_are_stacked_and_their_rows_ordered_by_expiry(self, every) -> None:
        scene = every[1]
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

    def test_it_closes_on_contract_1_being_whichever_stops_trading_next(self, every) -> None:
        last = every[1].steps[-1]
        assert (last.text, last.color) == (
            "contract 1 is whichever contract stops trading next",
            INK,
        )

    def test_its_alt_text_says_what_the_picture_shows(self, every, years) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        still, expired = years
        for f in years:
            assert f"March’s bar ends on {f.last_trade[0]:%B} {f.last_trade[0].day}" in alt
        assert "crosses all four bars" in alt
        assert "crosses only April, May and June" in alt
        assert alt.count("crosses May and June") == 2
        assert (still.entry_number, expired.entry_number) == (4, 3)
