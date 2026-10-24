"""The pins for the one whiteboard GIF in the post on Chan's buy on gap.

The GIF sketches the strategy's first two rules and sits right after the
paragraph that opens "Chan gives a reason for rule 2". It draws PCS on
2011-01-06 to scale: the previous low, the dashed line one standard deviation
below it, and the 20-day average, with the open landing in the green band
between the last two and an arrow to the close. So what is pinned is what a
reader takes from it: what it says and in which order, that every price stands
at an affine function of its value, that the open sits inside the band and the
close under the dashed line and the low, that no label touches a line, leaves
the board or touches another label in the hand font or the fallback, and the
file's size, frame count, loop and timing. ``TestThePost`` reads the post
itself. It checks that the GIF sits right after that paragraph and is embedded
once, that its caption names the day and quotes the standard deviation and the
gain the run gives, and that its alt text quotes the title and every label in
drawing order.

Its figures are read from the run on the committed file, which takes a few
seconds, so the tests read the run itself rather than a frozen copy, and pin
its values here. A made-up day shows that every label follows the figures it
is handed, and a day whose figures would make the words false is refused.

Two draws on one machine give the same bytes. Whether the committed GIF
equals a fresh draw depends on the font, as
``tests/test_usdcad_tests_whiteboard.py`` explains, so that comparison runs
only on macOS arm64 with Comic Sans MS.
"""

from __future__ import annotations

import dataclasses
import hashlib
import logging
import math
import platform
import re
import warnings

import matplotlib
import numpy as np
import pandas as pd
import pytest
from PIL import Image

from chan import buy_on_gap_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.buy_on_gap import drop_qualifiers, entry_spread, read_sources, trailing_average
from chan.buy_on_gap_whiteboard import (
    AVERAGE_Y,
    AXIS_X,
    EXAMPLE_DAY,
    EXAMPLE_SYMBOL,
    GIF_PREFIX,
    INSET,
    LABEL_APART,
    LINES_END,
    LOW_Y,
    RIGHT_X,
    GapDay,
    _apart,
    _where_the_open_lands,
    gif_name,
    main,
    make_buy_on_gap_whiteboards,
    read_gap_day,
    scenes,
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
    render,
    timeline,
)
from chan.vintage import VintageUnavailable

POST = REPO_ROOT / "blog" / "buy-on-gap-lessons.md"

GIFS = ["buy_on_gap_where_the_open_lands.gif"]
STROKES = ["axis", "low", "entry", "average", "band-edge", "open", "zone", "sell"]
LABELS = [
    "price",
    "PCS on 2011-01-06, the only stock bought",
    "yesterday’s low 13.68",
    "low × (1 − 0.020967) 13.39",
    "20-day average 12.70",
    "an open in this band qualifies",
    "open 13.01",
    "not bought",
    "a large drop often carries bad news",
    "and is less likely to revert",
    "sell at the close 13.30",
]

CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4

#: PCS on 2011-01-06 as the run on the committed file gives it.
PREVIOUS_LOW, SPREAD, ENTRY = 13.68, 0.02096651480957532, 13.39317807740501
OPEN, AVERAGE, CLOSE = 13.01, 12.6985, 13.30
OPEN_TO_CLOSE = 0.022290545734050728

#: A made-up day whose figures keep every word true.
MADE_UP = GapDay(
    symbol="XYZ",
    day=pd.Timestamp("2009-03-02"),
    previous_low=50.0,
    spread=0.04,
    entry=48.0,
    open=46.5,
    average=45.0,
    close=47.25,
    bought=("XYZ",),
)


@pytest.fixture(scope="module")
def day():
    return read_gap_day()


@pytest.fixture(scope="module")
def drawn(day):
    return scenes(day)


@pytest.fixture(scope="module")
def frames(drawn):
    return [timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, day):
    return make_buy_on_gap_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"), day=day)


def _stroke(scene, gid: str):
    return next(s for s in scene.strokes if s.gid == gid)


def _y(scene, gid: str) -> float:
    """The height of the level or dot ``gid``."""
    stroke = _stroke(scene, gid)
    assert np.ptp(stroke.y) == 0, gid
    return float(stroke.y[0])


def _tip(scene) -> tuple[float, float]:
    """Where the arrow to the close ends: the shaft's second point, where the
    head is drawn."""
    arrow = _stroke(scene, "sell")
    tip = int(np.argmax(arrow.x))
    return float(arrow.x[tip]), float(arrow.y[tip])


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
    def test_there_is_one_titled_where_the_open_has_to_land(self, drawn) -> None:
        assert [scene.title for scene in drawn] == ["Where the open has to land"]
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

    def test_only_the_entry_line_is_dashed(self, drawn) -> None:
        assert [s.gid for s in drawn[0].strokes if s.dashed] == ["entry"]

    def test_every_pale_tint_has_a_green_edge(self, drawn) -> None:
        """The tint alone stands 1.29 to 1 against the white board, under WCAG
        2.1's 3 to 1 for a graphical object, so the band gets a green edge that
        runs round it."""
        assert sketches.TINT_EDGE >= 1.0
        (fill,) = drawn[0].fills
        assert fill.color == whiteboard.TINT
        edge = _stroke(drawn[0], "band-edge")
        assert edge.color == GOOD and edge.width == sketches.TINT_EDGE
        assert (edge.x.min(), edge.x.max()) == pytest.approx((fill.x0, fill.x1))
        assert (edge.y.min(), edge.y.max()) == pytest.approx((fill.y0, fill.y1))


class TestTheColours:
    def test_each_stroke_and_label_is_in_the_ink_its_meaning_calls_for(self, drawn) -> None:
        """The axis and the note are grey context, the three levels black, the
        band where an open qualifies green, the zone that is not red, and the open and
        its path to the close brown."""
        scene = drawn[0]
        inks = {"axis": MUTED, "low": INK, "entry": INK, "average": INK}
        inks |= {"band-edge": GOOD, "open": ACCENT, "zone": LOST, "sell": ACCENT}
        assert {s.gid: s.color for s in scene.strokes} == inks
        for step in scene.steps:
            if isinstance(step, Label):
                assert step.color == {**inks, "band": GOOD}[step.names], step.text


class TestTheNumbersComeFromTheRun:
    def test_the_day_is_pcs_on_2011_01_06(self, day) -> None:
        assert (EXAMPLE_SYMBOL, EXAMPLE_DAY) == ("PCS", pd.Timestamp("2011-01-06"))
        assert (day.symbol, day.day) == (EXAMPLE_SYMBOL, EXAMPLE_DAY)

    def test_the_run_gives_the_figures_the_sketch_and_the_post_quote(self, day) -> None:
        assert day.previous_low == pytest.approx(PREVIOUS_LOW, abs=1e-9)
        assert day.spread == pytest.approx(SPREAD, abs=1e-12)
        assert day.entry == pytest.approx(ENTRY, abs=1e-9)
        assert day.open == pytest.approx(OPEN, abs=1e-9)
        assert day.average == pytest.approx(AVERAGE, abs=1e-9)
        assert day.close == pytest.approx(CLOSE, abs=1e-9)
        assert day.open_to_close == pytest.approx(OPEN_TO_CLOSE, abs=1e-12)
        assert f"{day.spread:.6f}" == "0.020967"
        assert f"{day.open_to_close:.6f}" == "0.022291"

    def test_pcs_is_the_only_stock_bought_that_day(self, day) -> None:
        assert day.bought == ("PCS",)

    def test_bought_is_read_from_the_run_on_another_day(self) -> None:
        from chan.buy_on_gap import buy_on_gap

        _, frames = read_sources()
        positions = buy_on_gap(frames["Open"], frames["Low"], frames["Close"]).positions
        t = frames["Open"].index.get_loc(EXAMPLE_DAY)
        j = frames["Open"].columns.get_loc(EXAMPLE_SYMBOL)
        other = next(
            k for k in range(t + 1, len(positions)) if positions[k].any() and not positions[k, j]
        )
        day = read_gap_day(day=frames["Open"].index[other])
        assert EXAMPLE_SYMBOL not in day.bought and len(day.bought) >= 1

    def test_the_dashed_line_is_the_price_the_run_compares_the_open_against(self) -> None:
        """Read back through ``drop_qualifiers``, which takes the same
        ``entry_price``: PCS qualifies that day, an open one step under the
        dashed line still does, and nudging its open up to the dashed line takes
        it out, as nudging it down to the average does. The first two hold the
        line from below and the third from above."""
        _, frames = read_sources()
        op, lo, cl = (frames[k].to_numpy(dtype=float) for k in ("Open", "Low", "Close"))
        spread, average = entry_spread(cl), trailing_average(cl)
        t = frames["Open"].index.get_loc(EXAMPLE_DAY)
        j = frames["Open"].columns.get_loc(EXAMPLE_SYMBOL)
        assert drop_qualifiers(op, lo, spread, average)[0][t, j]
        day = read_gap_day()
        under = op.copy()
        under[t, j] = np.nextafter(day.entry, -np.inf)
        assert drop_qualifiers(under, lo, spread, average)[0][t, j]
        for price in (day.entry, day.average):
            moved = op.copy()
            moved[t, j] = price
            assert not drop_qualifiers(moved, lo, spread, average)[0][t, j], price

    def test_the_dashed_line_is_read_through_entry_price(self, monkeypatch) -> None:
        """The sketch calls the run's own ``entry_price`` rather than a copy of
        its formula, so a change to the formula reaches the drawing."""
        calls = []

        def marked(lows, spread):
            calls.append(1)
            return np.full(np.shape(lows), 13.5)

        monkeypatch.setattr(sketches, "entry_price", marked)
        assert read_gap_day().entry == 13.5
        assert calls == [1]

    def test_the_labels_print_the_days_figures(self, day, drawn) -> None:
        labels = drawn[0].labels
        assert labels[1] == f"{day.symbol} on {day.day.date()}, the only stock bought"
        assert labels[2] == f"yesterday’s low {day.previous_low:.2f}"
        assert labels[3] == f"low × (1 − {day.spread:.6f}) {day.entry:.2f}"
        assert labels[4] == f"20-day average {day.average:.2f}"
        assert labels[6] == f"open {day.open:.2f}"
        assert labels[10] == f"sell at the close {day.close:.2f}"

    def test_other_figures_move_the_labels(self) -> None:
        labels = _where_the_open_lands(MADE_UP).labels
        assert labels[1:5] == [
            "XYZ on 2009-03-02, the only stock bought",
            "yesterday’s low 50.00",
            "low × (1 − 0.040000) 48.00",
            "20-day average 45.00",
        ]
        assert (labels[6], labels[10]) == ("open 46.50", "sell at the close 47.25")
        assert [labels[0], labels[5], *labels[7:10]] == [
            LABELS[0],
            LABELS[5],
            *LABELS[7:10],
        ]

    def test_a_day_with_another_stock_bought_is_refused(self) -> None:
        """The note says the stock is the only one bought that day."""
        for bought in (("XYZ", "ABC"), ("ABC",), ()):
            with pytest.raises(ValueError, match="the one stock bought that day"):
                _where_the_open_lands(dataclasses.replace(MADE_UP, bought=bought))

    @pytest.mark.parametrize("entry", [50.0, 51.0], ids=["on the low", "above it"])
    def test_a_dashed_line_not_below_the_low_is_refused(self, entry) -> None:
        with pytest.raises(ValueError, match="dashed line below the previous low"):
            _where_the_open_lands(dataclasses.replace(MADE_UP, entry=entry))

    @pytest.mark.parametrize(
        "opened",
        [48.0, 49.0, 45.0, 44.0],
        ids=["on the dashed line", "above it", "on the average", "below it"],
    )
    def test_an_open_not_strictly_inside_the_band_is_refused(self, opened) -> None:
        """``bog.m``'s two comparisons are strict, so an open on either line does
        not qualify, and the sketch says an open in the band does."""
        with pytest.raises(ValueError, match="open strictly between the dashed line"):
            _where_the_open_lands(dataclasses.replace(MADE_UP, open=opened, close=47.9))

    @pytest.mark.parametrize(
        "closed",
        [46.5, 46.0, 48.0, 49.0],
        ids=["at the open", "below it", "on the dashed line", "above it"],
    )
    def test_a_close_not_between_the_open_and_the_dashed_line_is_refused(self, closed) -> None:
        """The arrow rises to the close and ends under the dashed line."""
        with pytest.raises(ValueError, match="close above the open and under the dashed"):
            _where_the_open_lands(dataclasses.replace(MADE_UP, close=closed))


class TestTheScale:
    @pytest.mark.parametrize("made_up", [False, True], ids=["run", "made up"])
    def test_every_price_stands_at_an_affine_function_of_its_value(
        self, day, drawn, made_up
    ) -> None:
        """The board distance between any two prices over the gap between
        them is one number, so the levels are a ruler rather than a sketch."""
        figures, scene = (MADE_UP, _where_the_open_lands(MADE_UP)) if made_up else (day, drawn[0])
        prices = [figures.previous_low, figures.entry, figures.open, figures.average, figures.close]
        heights = [*(_y(scene, g) for g in ("low", "entry", "open", "average")), _tip(scene)[1]]
        slopes = [
            (heights[j] - heights[i]) / (prices[j] - prices[i])
            for i in range(len(prices))
            for j in range(i + 1, len(prices))
        ]
        assert slopes[0] > 0
        assert slopes == pytest.approx([slopes[0]] * len(slopes), rel=1e-9)
        assert (_y(scene, "average"), _y(scene, "low")) == pytest.approx((AVERAGE_Y, LOW_Y))

    def test_the_open_lands_inside_the_band(self, drawn) -> None:
        scene = drawn[0]
        (band,) = scene.fills
        dot = _stroke(scene, "open")
        assert band.x0 < dot.x[0] < band.x1
        assert band.y0 < dot.y[0] < band.y1
        assert _y(scene, "average") < band.y0 and band.y1 < _y(scene, "entry")

    def test_the_band_and_the_zone_stand_just_inside_their_lines(self, drawn) -> None:
        """The band runs from just above the average to just under the dashed
        line, and the zone from just under the average down, so neither edge
        draws over a line."""
        scene = drawn[0]
        (band,) = scene.fills
        zone = _stroke(scene, "zone")
        average, entry = _y(scene, "average"), _y(scene, "entry")
        assert (band.y0, band.y1) == pytest.approx((average + INSET, entry - INSET))
        assert zone.y.max() == pytest.approx(average - INSET)
        assert band.x0 == zone.x.min() == AXIS_X + INSET
        assert band.x1 == zone.x.max() == LINES_END

    def test_the_arrow_rises_and_ends_under_the_dashed_line_and_the_low(self, drawn) -> None:
        """The close gains on the open and stays under the previous low, and
        the drawing shows both."""
        scene = drawn[0]
        dot, (x, y) = _stroke(scene, "open"), _tip(scene)
        assert x > dot.x[0] and y > dot.y[0]
        assert y < _y(scene, "entry") < _y(scene, "low")
        (band,) = scene.fills
        assert band.y0 < y < band.y1

    def test_the_level_labels_stand_right_of_the_lines(self, drawn) -> None:
        """Each level's label starts right of where the lines end, at its
        line's height unless another label above pushed it down."""
        scene = drawn[0]
        for gid in ("low", "entry", "average", "sell"):
            (label,) = _named(scene, gid)
            assert label.ha == "left" and label.x == RIGHT_X > LINES_END
        (low,), (entry,), (average,) = (_named(scene, g) for g in ("low", "entry", "average"))
        assert low.y == _y(scene, "low") and average.y == _y(scene, "average")
        assert entry.y == pytest.approx(min(_y(scene, "entry"), low.y - LABEL_APART))

    def test_the_close_label_sits_under_the_dashed_lines_label(self, drawn) -> None:
        """The close is too near the dashed line on this scale for both labels
        to stand at their own heights, so the close's moves down."""
        scene = drawn[0]
        (entry,), (sell,) = (_named(scene, g) for g in ("entry", "sell"))
        assert sell.y == pytest.approx(entry.y - LABEL_APART)
        assert sell.y < _tip(scene)[1]

    def test_apart_moves_a_label_only_down_and_only_when_it_must(self) -> None:
        assert _apart([3.0, 2.0, 1.9, 0.5], 0.36) == pytest.approx([3.0, 2.0, 1.64, 0.5])
        assert _apart([3.0, 2.9, 2.8], 0.36) == pytest.approx([3.0, 2.64, 2.28])


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
        """The multiplication sign, the typographic minus and the curly apostrophe are all drawn."""
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, day) -> None:
        again = make_buy_on_gap_whiteboards(out_dir=tmp_path, day=day)
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
        system, machine, font = platform.system(), platform.machine(), whiteboard.hand_font()
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
            ), f"{path.name}: redraw with: uv run python -m chan.buy_on_gap_whiteboard"


class TestThePost:
    def test_the_gif_follows_the_paragraph_on_chans_reason_for_rule_2(self, day) -> None:
        """Keyed on the paragraph's opening words, then the caption right after."""
        paragraphs = _paragraphs()
        (index,) = [
            k for k, p in enumerate(paragraphs) if p.startswith("Chan gives a reason for rule 2")
        ]
        embed = paragraphs[index + 1]
        assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", embed)
        caption = paragraphs[index + 2]
        assert caption.startswith("*") and caption.endswith("*") and "\n" not in caption
        assert caption.startswith(f"*{day.symbol} on {day.day.date()}, the only stock")
        assert "drawn to scale" in caption
        assert f"one standard deviation of its daily returns, {day.spread:.6f}," in caption
        assert f"gained {100 * day.open_to_close:.1f} percent by the close" in caption
        assert "below the previous low and still above the 20-day average" in caption
        assert "without getting back to that low" in caption

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
        assert "drawn to scale" in alt
        assert "A pale green band with a green edge fills the space between" in alt
        assert "A brown dot lands inside the band" in alt
        assert "a brown arrow rises from the dot to the right" in alt
        assert "A red hatched zone below the average" in alt
        assert "ends inside the band, just under the dashed line and well under" in alt
        assert alt.endswith("holds for four seconds before it redraws.")


class TestTheCommand:
    def test_it_writes_every_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []

        def draw(**kwargs):
            drawn.append(kwargs)
            return [FIGURES_DIR / name for name in GIFS]

        monkeypatch.setattr(sketches, "make_buy_on_gap_whiteboards", draw)
        main()
        assert drawn == [{}]
        assert capsys.readouterr().out.splitlines() == [
            f"wrote {FIGURES_DIR / name}" for name in GIFS
        ]

    def test_drawing_with_no_out_dir_writes_the_committed_paths(self, monkeypatch, day) -> None:
        saved = []
        monkeypatch.setattr(sketches, "read_gap_day", lambda: day)
        monkeypatch.setattr(sketches, "render", lambda scene, frames: [Image.new("P", (1, 1))])
        monkeypatch.setattr(Image.Image, "save", lambda self, path, **kw: saved.append(path))
        paths = make_buy_on_gap_whiteboards()
        assert paths == saved == [FIGURES_DIR / name for name in GIFS]

    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        refusal = VintageUnavailable("the committed file's hash does not match its manifest")

        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(sketches, "read_gap_day", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
