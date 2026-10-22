"""The pins for the two whiteboard GIFs in the AUD.CAD rollover post.

One sketches Lesson 2's reason the 365-day reading overstates the year, and one
Lesson 3's reason the strategy earns rollover interest roughly on its net
position. Both print figures from the run on Chan's committed files, and the
tests here read that run rather than a copy of its figures. The vintage and the
specification are the ones ``tests/test_aud_cad_rollover.py`` states, and a
re-pin there moves the figures pinned in :class:`TestTheFigures`.

What is pinned for each sketch:

1. Its words, in order, and the ink of each mark.
2. Where each mark stands: the weekday each row triples, read from the
   script's rule, and the bar's parts to scale on the days held.
3. That other figures move the words and the marks, and that figures the
   words would misdescribe are refused.
4. That no label touches a line, leaves the board or touches another label,
   in the installed hand font and in the wider fallback.
5. Each file's size, frame count, loop and timing, and that it sits in the
   post right after the text it draws, with an alt text quoting its labels.

Two draws on one machine give the same bytes. Whether a committed GIF equals a
fresh draw depends on the font, as ``tests/test_usdcad_tests_whiteboard.py``
explains, so that comparison runs only on macOS arm64 with Comic Sans MS.
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

from chan import aud_cad_rollover as rollover
from chan import aud_cad_rollover_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.aud_cad_rollover import aud_cad_rollover, read_sources
from chan.aud_cad_rollover_whiteboard import (
    BAR_WIDTH,
    BAR_X,
    CELLS_X,
    CHECK_X,
    GIF_PREFIX,
    PACED,
    PACED_HOLD_MS,
    PAIRED_WIDTH,
    PRODUCT_ARROW,
    PRODUCT_Y,
    WEEK,
    RunFigures,
    cap,
    gif_name,
    main,
    make_aud_cad_rollover_whiteboards,
    scenes,
    sketch_timeline,
    week_days_paid,
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
)

POST = REPO_ROOT / "blog" / "aud-cad-rollover-lessons.md"

TITLES = ["Five trading days pay for seven", "Long and short days cancel"]
GIFS = ["aud_cad_rollover_five_pay_seven.gif", "aud_cad_rollover_long_short_cancel.gif"]

CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4

BRACE_WORDS = "5 trading days pay 7 days of interest"
LABELS = [
    [
        "AUD",
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "1",
        "1",
        "3",
        "1",
        "1",
        BRACE_WORDS,
        "CAD",
        "1",
        "1",
        "1",
        "3",
        "1",
        BRACE_WORDS,
        "average of AUD less CAD",
        "× 252 trading days",
        "3.26 percent",
        "the same average × 365 counts",
        "every weekend again",
        "4.73 percent",
        "365 / 252 is about 1.45,",
        "so 3.26 becomes 4.73",
        "the tripled day already paid for the weekend",
    ],
    [
        "510 days long: earn rollover interest",
        "707 days short: pay it",
        "cancel",
        "197 more days short:",
        "a net share of −16.2 percent",
        "× 3.26 percent a year",
        "−0.528 percent",
        "rollover added: −0.522 percent",
        "they cancel because long days see 3.290 and short days 3.287 percent a year",
        "what is left is the net position",
    ],
]
#: The ink of each label, in the order of :data:`LABELS`: green for what earns
#: or checks out, red for what pays or overstates, grey for context, brown for
#: the tripled days and the closing words, black for the rest.
LABEL_INKS = [
    [INK] * 6
    + [INK, INK, ACCENT, INK, INK, MUTED]
    + [INK, INK, INK, INK, ACCENT, INK, MUTED]
    + [GOOD, GOOD, GOOD, LOST, LOST, LOST, MUTED, MUTED, ACCENT],
    [GOOD, LOST, MUTED, LOST, LOST, INK, INK, GOOD, MUTED, ACCENT],
]
STROKE_INKS = [
    {
        "aud-row": INK,
        "aud-tripled": ACCENT,
        "aud-brace": MUTED,
        "cad-row": INK,
        "cad-tripled": ACCENT,
        "cad-brace": MUTED,
        "by-252": GOOD,
        "by-365": LOST,
    },
    {
        "long": GOOD,
        "short": LOST,
        "cancel": MUTED,
        "paired": MUTED,
        "leftover": LOST,
        "times-rate": INK,
        "checks-out": GOOD,
    },
]
STROKES = [
    [
        "aud-row",
        "aud-tripled",
        "aud-brace",
        "cad-row",
        "cad-tripled",
        "cad-brace",
        "by-252",
        "by-365",
    ],
    ["long", "short", "cancel", "paired", "leftover", "times-rate", "checks-out"],
]

#: Made-up figures, net short on 300 of 1,000 days, to show that the words and
#: the marks follow the figures rather than the committed run.
MOVED = RunFigures(
    long_days=350,
    short_days=650,
    rollover=0.041,
    over_365_days=0.041 * 365 / 252,
    rollover_drag=-0.0121,
    long_rate=0.0405,
    short_rate=0.0412,
)


@pytest.fixture(scope="module")
def result():
    sources = read_sources()
    return aud_cad_rollover(sources.closes[1], sources.aud[1], sources.cad[1])


@pytest.fixture(scope="module")
def figures(result) -> RunFigures:
    return RunFigures.from_run(result)


@pytest.fixture(scope="module")
def drawn(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def frames(drawn):
    return [sketch_timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, figures):
    return make_aud_cad_rollover_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), figures=figures
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


def _alt(scene) -> str:
    text = POST.read_text(encoding="utf-8")
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    return match.group(1)


class TestTheFigures:
    """The run's figures each sketch prints, at the values the run's own pins hold."""

    def test_the_days_held_each_way_are_the_lagged_positions(self, figures, result) -> None:
        """The position each day's return carries, over the rows after the first 20."""
        held = rollover.lag1(result.position)[rollover.SCRIPT_LOOKBACK :]
        assert (figures.long_days, figures.short_days, figures.held_days) == (510, 707, 1217)
        assert ((held > 0).sum(), (held < 0).sum(), len(held)) == (510, 707, 1217)

    def test_the_rates_and_the_rollover_added_are_the_runs(self, figures) -> None:
        assert figures.rollover == pytest.approx(0.0326416903, abs=1e-10)
        assert figures.over_365_days == pytest.approx(0.0472786388, abs=1e-10)
        assert figures.rollover_drag == pytest.approx(-0.0052212787, abs=1e-10)
        assert figures.long_rate == pytest.approx(0.0328995788, abs=1e-10)
        assert figures.short_rate == pytest.approx(0.0328677609, abs=1e-10)

    def test_the_net_share_times_the_rate_is_the_prediction(self, figures) -> None:
        assert figures.net_share == pytest.approx((510 - 707) / 1217)
        assert figures.predicted == pytest.approx(-0.0052838233, abs=1e-10)

    def test_the_365_day_reading_is_the_252_day_one_scaled(self, figures) -> None:
        ratio = rollover.DAYS_IN_YEAR / sketches.TRADING_DAYS
        assert figures.over_365_days == pytest.approx(figures.rollover * ratio, rel=1e-12)


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, drawn) -> None:
        assert [scene.title for scene in drawn] == TITLES

    def test_each_has_its_own_gif_named_for_it(self, drawn) -> None:
        assert [gif_name(scene) for scene in drawn] == GIFS
        assert all(name.startswith(GIF_PREFIX) for name in GIFS)

    def test_each_draws_its_strokes_in_order(self, drawn) -> None:
        assert [[s.gid for s in scene.strokes] for scene in drawn] == STROKES

    def test_each_says_what_it_should(self, drawn) -> None:
        assert [scene.labels for scene in drawn] == LABELS

    def test_each_label_and_stroke_is_in_the_ink_its_meaning_calls_for(self, drawn) -> None:
        for scene, labels, strokes in zip(drawn, LABEL_INKS, STROKE_INKS, strict=True):
            found = [s.color for s in scene.steps if isinstance(s, Label)]
            assert list(zip(scene.labels, found, strict=True)) == list(
                zip(scene.labels, labels, strict=True)
            ), scene.slug
            assert {s.gid: s.color for s in scene.strokes} == strokes, scene.slug

    def test_every_label_names_a_stroke_drawn_before_it(self, drawn) -> None:
        for scene in drawn:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if not isinstance(s, Label)]
                    assert step.names in earlier, (scene.title, step.text)

    def test_no_label_is_parsed_as_math(self, drawn) -> None:
        assert not [s.text for scene in drawn for s in scene.steps if getattr(s, "math", 0)]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, drawn) -> None:
        for scene in drawn:
            for stroke in scene.strokes:
                assert stroke.points >= stroke.frames, (scene.title, stroke.gid)

    def test_neither_draws_a_tint(self, drawn) -> None:
        """A tint would need a green edge, and neither sketch shades a region."""
        assert not [fill for scene in drawn for fill in scene.fills]


class TestFiveDaysPayForSeven:
    def test_the_script_triples_aud_on_wednesday_and_cad_on_thursday(self) -> None:
        assert [day.strftime("%a") for day in WEEK] == ["Mon", "Tue", "Wed", "Thu", "Fri"]
        assert week_days_paid(rollover.AUD_TRIPLE_WEEKDAY) == (1, 1, 3, 1, 1)
        assert week_days_paid(rollover.CAD_TRIPLE_WEEKDAY) == (1, 1, 1, 3, 1)

    def test_each_row_prints_the_days_each_weekday_pays(self, drawn) -> None:
        labels = drawn[0].labels
        aud = labels[labels.index("AUD") + 6 : labels.index("AUD") + 11]
        cad = labels[labels.index("CAD") + 1 : labels.index("CAD") + 6]
        assert aud == [str(d) for d in week_days_paid(rollover.AUD_TRIPLE_WEEKDAY)]
        assert cad == [str(d) for d in week_days_paid(rollover.CAD_TRIPLE_WEEKDAY)]

    def test_the_tripled_box_sits_under_its_weekday_in_brown(self, drawn) -> None:
        scene = drawn[0]
        width = (CELLS_X[1] - CELLS_X[0]) / len(WEEK)
        for gid, weekday in (
            ("aud-tripled", rollover.AUD_TRIPLE_WEEKDAY),
            ("cad-tripled", rollover.CAD_TRIPLE_WEEKDAY),
        ):
            box = _stroke(scene, gid)
            assert box.color == ACCENT
            assert box.x.min() == pytest.approx(CELLS_X[0] + weekday * width)
            assert box.x.max() == pytest.approx(CELLS_X[0] + (weekday + 1) * width)
            header = _label(scene, WEEK[weekday].strftime("%a"))
            assert header.x == pytest.approx((box.x.min() + box.x.max()) / 2)
        threes = [s for s in scene.steps if isinstance(s, Label) and s.text == "3"]
        assert [s.color for s in threes] == [ACCENT, ACCENT]
        assert [s.names for s in threes] == ["aud-tripled", "cad-tripled"]

    def test_each_brace_spans_its_row_and_its_words_sit_under_it(self, drawn) -> None:
        scene = drawn[0]
        braces = [s for s in scene.steps if isinstance(s, Label) and s.text == BRACE_WORDS]
        for gid, words in zip(("aud-brace", "cad-brace"), braces, strict=True):
            brace, row = _stroke(scene, gid), _stroke(scene, gid.replace("brace", "row"))
            assert (brace.x.min(), brace.x.max()) == pytest.approx(CELLS_X)
            assert brace.y.max() < row.y.min()
            assert words.y < brace.y.min() and words.names == gid

    def test_252_is_green_and_365_red_with_the_closing_words_brown(self, drawn) -> None:
        scene = drawn[0]
        assert _stroke(scene, "by-252").color == GOOD
        assert _stroke(scene, "by-365").color == LOST
        for step in scene.steps:
            if isinstance(step, Label) and step.names in {"by-252"}:
                assert step.color == GOOD, step.text
        assert _label(scene, "4.73 percent").color == LOST
        assert _label(scene, "every weekend again").color == LOST
        assert scene.steps[-1].text == "the tripled day already paid for the weekend"
        assert scene.steps[-1].color == ACCENT

    def test_the_252_branch_sits_above_the_365_one(self, drawn) -> None:
        scene = drawn[0]
        assert _stroke(scene, "by-252").y.min() > _stroke(scene, "by-365").y.max()

    def test_both_branches_and_their_results_sit_between_the_rows(self, drawn) -> None:
        """Each multiplies the average of AUD less CAD, so neither sits level with
        one row, where it would read as that currency's figure."""
        scene = drawn[0]
        below_aud = _stroke(scene, "aud-row").y.min()
        above_cad = _stroke(scene, "cad-row").y.max()
        for gid, result in (("by-252", "3.26 percent"), ("by-365", "4.73 percent")):
            arrow = _stroke(scene, gid)
            assert above_cad < arrow.y.min() and arrow.y.max() < below_aud, gid
            assert above_cad < _label(scene, result).y < below_aud, result

    def test_words_beside_a_row_name_the_average_of_aud_less_cad(self, drawn) -> None:
        """Words level with one row read as that currency's figure, as an arrow
        does. The branches' words have no room between the rows, so wherever
        a branch's words sit beside a row, its top line, read first, names the
        average both branches multiply."""
        scene = drawn[0]
        rows = [_stroke(scene, gid).y for gid in ("aud-row", "cad-row")]
        for gid, opening in (
            ("by-252", "average of AUD less CAD"),
            ("by-365", "the same average × "),
        ):
            words = [
                s
                for s in scene.steps
                if isinstance(s, Label) and s.names == gid and not s.text.endswith(" percent")
            ]
            if any(row.min() <= w.y <= row.max() for w in words for row in rows):
                top = max(words, key=lambda w: w.y)
                assert words[0] is top and top.text.startswith(opening), (gid, top.text)

    def test_other_figures_move_the_percentages(self) -> None:
        labels = scenes(MOVED)[0].labels
        assert "4.10 percent" in labels and "5.94 percent" in labels
        assert "so 4.10 becomes 5.94" in labels

    def test_rows_that_pay_different_days_are_refused(self, monkeypatch, figures) -> None:
        monkeypatch.setattr(
            sketches,
            "week_days_paid",
            lambda weekday: (1, 1, 3, 1, 1) if weekday == 2 else (1,) * 5,
        )
        with pytest.raises(ValueError, match="pay 7 and 5 days"):
            scenes(figures)


def _x_at(days: float, f: RunFigures) -> float:
    return BAR_X[0] + (BAR_X[1] - BAR_X[0]) * days / f.held_days


@pytest.fixture(params=["run", "moved"])
def either(request, figures) -> RunFigures:
    return figures if request.param == "run" else MOVED


class TestLongAndShortDaysCancel:
    def test_the_bar_is_to_scale_on_the_days_held(self, either) -> None:
        scene = scenes(either)[1]
        long, short = _stroke(scene, "long"), _stroke(scene, "short")
        # The ink runs half the line's width past each end, as a round cap.
        reach = cap(BAR_WIDTH)
        assert reach == pytest.approx(BAR_WIDTH * 100 / 72 / 2 / 68)
        assert (long.x.min() - reach, long.x.max() + reach) == pytest.approx(
            (BAR_X[0], _x_at(either.long_days, either))
        )
        assert (short.x.min() - reach, short.x.max() + reach) == pytest.approx(
            (_x_at(either.long_days, either), BAR_X[1])
        )
        assert set(long.y) == set(short.y)

    def test_the_paired_days_are_the_long_ones_and_as_many_short(self, either) -> None:
        scene = scenes(either)[1]
        paired, cancel = _stroke(scene, "paired"), _stroke(scene, "cancel")
        end = _x_at(2 * either.long_days, either)
        reach = cap(PAIRED_WIDTH)
        assert (paired.x.min() - reach, paired.x.max() + reach) == pytest.approx((BAR_X[0], end))
        assert (cancel.x.min(), cancel.x.max()) == pytest.approx((BAR_X[0], end))
        # The bracket's middle tick sits where the long days end.
        middle = _x_at(either.long_days, either)
        assert np.isclose(cancel.x, middle).sum() >= 3
        # Thin enough that the colours of the days it pairs show either side of it.
        assert paired.width <= _stroke(scene, "long").width / 2

    def test_the_leftover_runs_from_the_pairs_to_the_end(self, either) -> None:
        scene = scenes(either)[1]
        leftover = _stroke(scene, "leftover")
        assert (leftover.x.min(), leftover.x.max()) == pytest.approx(
            (_x_at(2 * either.long_days, either), BAR_X[1])
        )

    def test_long_is_green_short_red_the_pairs_grey_and_the_check_green(self, drawn) -> None:
        scene = drawn[1]
        inks = {s.gid: s.color for s in scene.strokes}
        assert inks == {
            "long": GOOD,
            "short": LOST,
            "cancel": MUTED,
            "paired": MUTED,
            "leftover": LOST,
            "times-rate": INK,
            "checks-out": GOOD,
        }
        for step in scene.steps:
            if isinstance(step, Label) and step.names in {"long", "short", "cancel", "leftover"}:
                assert step.color == inks[step.names], step.text
        assert _label(scene, "rollover added: −0.522 percent").color == GOOD
        assert scene.steps[-1].text == "what is left is the net position"
        assert scene.steps[-1].color == ACCENT

    def test_the_product_arrow_points_from_the_rate_to_the_result(self, drawn) -> None:
        scene = drawn[1]
        arrow = _stroke(scene, "times-rate")
        start, end = PRODUCT_ARROW
        assert (arrow.x[0], arrow.x.max()) == pytest.approx((start, end))
        assert set(np.round(arrow.y[: np.argmax(arrow.x) + 1], 9)) == {PRODUCT_Y}
        rate, result = _label(scene, "× 3.26 percent a year"), _label(scene, "−0.528 percent")
        assert (rate.ha, rate.y) == ("right", PRODUCT_Y) and rate.x < start
        assert (result.ha, result.y) == ("right", PRODUCT_Y) and result.x > end

    def test_the_check_sits_on_the_row_it_marks_left_of_its_words(self, drawn) -> None:
        scene = drawn[1]
        check, added = _stroke(scene, "checks-out"), _label(scene, "rollover added: −0.522 percent")
        assert check.y.min() < added.y < check.y.max()
        assert check.x.min() == CHECK_X
        assert PRODUCT_ARROW[0] - 2 < check.x.min() and check.x.max() < added.x - 3.5

    def test_the_two_results_end_together_so_their_figures_line_up(self, drawn) -> None:
        scene = drawn[1]
        predicted = _label(scene, "−0.528 percent")
        added = _label(scene, "rollover added: −0.522 percent")
        assert (predicted.ha, added.ha) == ("right", "right")
        assert predicted.x == added.x
        assert predicted.y > added.y

    def test_other_figures_move_the_words(self) -> None:
        labels = scenes(MOVED)[1].labels
        assert labels[:5] == [
            "350 days long: earn rollover interest",
            "650 days short: pay it",
            "cancel",
            "300 more days short:",
            "a net share of −30.0 percent",
        ]
        assert "× 4.10 percent a year" in labels
        assert "−1.230 percent" in labels
        assert "rollover added: −1.210 percent" in labels
        assert (
            "they cancel because long days see 4.050 and short days 4.120 percent a year" in labels
        )

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_the_leftover_words_hang_under_the_short_half_from_the_bars_end(
        self, either, monkeypatch, fallback
    ) -> None:
        """Red is the only ink tying them to the leftover span, and to a reader who
        cannot tell red from grey their place has to do it. Two lines, each ending at
        the bar's right end, keep them clear of the long half and of the grey label."""
        _font(monkeypatch, fallback)
        scene = scenes(either)[1]
        words = [s for s in scene.steps if isinstance(s, Label) and s.names == "leftover"]
        assert [w.text for w in words] == [
            f"{either.short_days - either.long_days:,} more days short:",
            f"a net share of {100 * either.net_share:.1f} percent".replace("-", "−"),
        ]
        assert all((w.ha, w.x, w.color) == ("right", BAR_X[1], LOST) for w in words)
        assert words[0].y > words[1].y > PRODUCT_Y
        to_px = WIDTH / (whiteboard.XLIM[1] - whiteboard.XLIM[0])
        middle = (_x_at(either.long_days, either) - whiteboard.XLIM[0]) * to_px
        boxes = dict(_boxes(scene))
        for w in words:
            assert boxes[w.text].x0 > middle, (w.text, round(boxes[w.text].x0), round(middle))

    @pytest.mark.parametrize("long_days", [707, 800])
    def test_a_net_long_or_flat_run_is_refused(self, figures, long_days) -> None:
        """The words say more days are short, which these figures would make false."""
        with pytest.raises(ValueError, match="more days are short"):
            scenes(dataclasses.replace(figures, long_days=long_days))


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, drawn, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            found = clearances(scene)
            assert set(found) == {*scene.labels, scene.title}
            for text, pixels in found.items():
                assert pixels >= CLEAR_PX, (scene.title, text, round(pixels, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_sits_inside_the_board(
        self, drawn, monkeypatch, fallback
    ) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            for text, box in _boxes(scene):
                inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                assert inside >= INSIDE_PX, (scene.title, text, round(inside, 1))

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
                    assert gap >= APART_LABELS_PX, (scene.title, one, other, round(gap, 1))


class TestTheGifs:
    def test_there_is_one_named_for_each_scene(self, gifs) -> None:
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

    def test_each_opens_on_its_title_and_holds_its_drawing(self, drawn, frames) -> None:
        for scene, steps in zip(drawn, frames, strict=True):
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            hold = PACED_HOLD_MS if scene.slug in PACED else HOLD_MS
            assert steps[-1].ms == hold, scene.slug

    def test_only_the_cancel_sketch_builds_slowly(self, drawn) -> None:
        """It prints nine of the run's figures, more than the usual pace lets a reader take in."""
        assert [scene.slug in PACED for scene in drawn] == [False, True]
        assert PACED_HOLD_MS == 12000

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, figures) -> None:
        again = make_aud_cad_rollover_whiteboards(out_dir=tmp_path, figures=figures)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
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
            ), f"{path.name}: redraw with: uv run python -m chan.aud_cad_rollover_whiteboard"


class TestThePost:
    def test_each_gif_follows_the_text_it_draws(self) -> None:
        """The five-days sketch right after Lesson 2's list of the two readings,
        before the paragraph that says the reproduction picks neither, and the cancel
        sketch right after the paragraph on the net position."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name, following in zip(
            ("1. **The AUD rate alone, 4.66 percent.**", "**Net position explains the cost.**"),
            GIFS,
            ("**This reproduction picks neither.**", "**The two APRs differ by more than"),
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name
            assert paragraphs[index + 2].startswith(following), name
        listed = paragraphs[
            [k for k, p in enumerate(paragraphs) if p.startswith("1. **The AUD")][0]
        ]
        assert "\n2. **The difference over 365 days, 4.73 percent.**" in listed

    def test_each_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"](../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_its_title_and_labels_in_order(self, drawn) -> None:
        for scene in drawn:
            alt = _alt(scene)
            place = alt.index(f"“{scene.title}”")
            for text in dict.fromkeys(scene.labels):
                if text in {"1", "3", "Mon", "Tue", "Wed", "Thu", "Fri"}:
                    assert f"“{text}”" in alt, (scene.slug, text)
                    continue
                place = alt.index(f"“{text}”", place) + 1

    def test_each_alt_text_says_how_it_builds(self, drawn) -> None:
        for scene in drawn:
            alt = _alt(scene)
            if scene.slug in PACED:
                assert "drawn slowly" in alt and "holds for twelve seconds" in alt
            else:
                assert "drawn slowly" not in alt and "twelve seconds" not in alt

    def test_the_cancel_sketchs_alt_text_says_the_bar_is_grouped_by_side(self, drawn) -> None:
        alt = _alt(drawn[1])
        assert "to scale, with the days grouped by side rather than by date" in alt

    def test_each_alt_text_names_each_marks_ink_and_the_days_held(self, drawn, figures) -> None:
        """The label-order test skips the words between quotes, so these are held here."""
        for scene, phrases in zip(
            drawn,
            (
                [
                    "outlined in brown and holds “3”",
                    "A grey brace",
                    "a green arrow labelled “average of AUD less CAD”",
                    "a red arrow labelled “the same average × 365",
                    "A grey note",
                    "a brown line closes",
                ],
                [
                    f"the {figures.held_days:,} days the rule holds a position",
                    f"a green part labelled “{figures.long_days:,} days long",
                    f"a red part labelled “{figures.short_days:,} days short",
                    "A grey bracket",
                    "a thinner grey line",
                    "A red bracket",
                    "a green tick",
                    "A grey note",
                    "a brown line closes",
                ],
            ),
            strict=True,
        ):
            alt = _alt(scene)
            for phrase in phrases:
                assert phrase in alt, (scene.slug, phrase)

    def test_the_five_days_alt_text_names_the_tripled_days(self, drawn) -> None:
        alt = _alt(drawn[0])
        assert "“AUD”" in alt and "except Wednesday, which is outlined in brown" in alt
        assert "“CAD”" in alt and "except that Thursday is the box outlined in brown" in alt


class TestTheCommand:
    def test_it_writes_both_gifs_into_the_figures_folder(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.iterdir()) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]
