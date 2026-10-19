"""The pins for the twenty-one whiteboard GIFs in the equity-seasonals post.

Two sketch the post's opening section, two its section "The two strategies",
seven the rules its first lesson lists, one rule each, one the split that its
second lesson discusses, three its check of Chan's five-year claim, three its
lesson on survivorship bias, and three its question on whether the January
effect survived the book. The opening's timeline places each source's years to
scale, from Chan's committed files and the registered runs' constants, and its
verdicts sketch draws the two registered runs' figures to scale. Those figures
are pinned here as :data:`PINNED`, the values
``tests/test_equity_seasonals.py`` pins, so every test here runs without the
owner's archive. ``test_the_whiteboard_draws_these_runs_verdicts`` and
``test_the_whiteboard_draws_these_runs_ranges`` in
``tests/test_equity_seasonals.py`` hold that the runs give :data:`PINNED` and
:data:`PINNED_RANGES`.

The strategy sketches are schematic and read no data, so what is pinned for
them is what a reader takes from them.

1. Which way each strategy bets: Example 7.6 buys the lowest-ranked tenth and
   shorts the highest and points its losers up and its winners down, and
   Example 7.7 does the reverse and points each the way it already went.
2. Its timing: January is one twelfth of the year past the year's last close,
   and the same-month trade ranks and holds the same calendar month in two
   strips, a year apart, then moves on a month.
3. That each sketch names its bet in the post's own words, "mean reversion"
   and "seasonal momentum".
4. That no label touches a line, leaves the frame or touches another label,
   in the installed hand font and in the wider fallback.
5. Each file's size, frame count, loop and timing, and that it sits in the
   post right after the paragraph it draws.

The rule sketches print figures from :class:`RuleFigures`, whose defaults
``tests/test_equity_seasonals.py`` derives from Chan's files. What is pinned
here is that each label prints its figure, that the marks stand where the
figures put them, and that other figures move both. Each rule sketch closes
the rule it draws in the post.

The split sketch prints figures from :class:`SplitFigures`, whose defaults
``TestTheYearsInsideTheSplit`` derives. What is pinned for it is that each
bar and bracket stands to one scale on the file's figures and on other ones,
that each bar and its value take the colour of their sign, and that it sits
between the paragraph on the split's years and the one on the running-sum
chart.

The five-year sketches print :class:`FiveYearFigures`, which
``TestTheFiveYearSketches`` in ``tests/test_equity_seasonals.py`` derives.
Lesson 3's three sketches and the January fill are schematic, so what is
pinned for them is what a reader takes from them: who is in the file and who
is not, which stocks a tenth holds, and where each mark stands. The January
ranges sketch draws :data:`PINNED_RANGES`, which
``test_the_whiteboard_draws_these_runs_ranges`` holds the registered run
gives. Six sketches build slowly, and their pace is pinned too.

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
import pandas as pd
import pytest
from PIL import Image

from chan import equity_seasonals as seasonals
from chan import equity_seasonals_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.archive import ArchiveUnavailable
from chan.equity_seasonals_whiteboard import (
    ANNUAL_RANGE,
    AXIS_Y,
    BOOK_YEAR,
    JANUARY_END,
    JANUARY_RANGE,
    RANKED,
    TENTH,
    TIMELINE_X,
    YEAR,
    FiveYearFigures,
    JanuaryRanges,
    RuleFigures,
    Spans,
    SplitFigures,
    Verdicts,
    _at,
    _year,
    five_year_scenes,
    gif_name,
    january_scenes,
    main,
    make_equity_seasonals_whiteboards,
    opening_scenes,
    rule_scenes,
    scenes,
    sketch_timeline,
    split_scenes,
    survivor_scenes,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import GOOD, LOST
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
from tests.test_usdcad_tests_whiteboard import GIFS as USDCAD_GIFS

POST = REPO_ROOT / "blog" / "equity-seasonals-lessons.md"

TITLES = ["The January trade", "The same-month trade"]
STRATEGY_GIFS = ["equity_seasonals_january_trade.gif", "equity_seasonals_same_month_trade.gif"]
OPENING_GIFS = ["equity_seasonals_which_years.gif", "equity_seasonals_two_verdicts.gif"]
RULE_GIFS = [
    "equity_seasonals_rule_short_side.gif",
    "equity_seasonals_rule_filled_close.gif",
    "equity_seasonals_rule_sum_or_mean.gif",
    "equity_seasonals_rule_wrong_close.gif",
    "equity_seasonals_rule_empty_months.gif",
    "equity_seasonals_rule_own_month_end.gif",
    "equity_seasonals_rule_month_end_lookup.gif",
]
SPLIT_GIFS = ["equity_seasonals_split_swing.gif"]
FIVE_YEAR_GIFS = [
    "equity_seasonals_five_year_months.gif",
    "equity_seasonals_five_year_noise.gif",
    "equity_seasonals_five_year_januaries.gif",
]
#: Every GIF in the order :func:`make_equity_seasonals_whiteboards` writes them.
SURVIVOR_GIFS = [
    "equity_seasonals_survivors_file.gif",
    "equity_seasonals_survivors_ranking.gif",
    "equity_seasonals_survivors_panels.gif",
]
JANUARY_GIFS = [
    "equity_seasonals_january_registered.gif",
    "equity_seasonals_january_fill.gif",
    "equity_seasonals_january_ranges.gif",
]
GIFS = (
    OPENING_GIFS
    + STRATEGY_GIFS
    + RULE_GIFS
    + SPLIT_GIFS
    + FIVE_YEAR_GIFS
    + SURVIVOR_GIFS
    + JANUARY_GIFS
)
#: The GIFs a redraw cannot write without the owner's archive.
ARCHIVE_GIFS = {"equity_seasonals_two_verdicts.gif", "equity_seasonals_january_ranges.gif"}

#: The registered runs' figures, as ``tests/test_equity_seasonals.py`` pins
#: them in ``TestThePointInTimePins`` and ``TestTheMonthlyPins``. The vintage
#: is Alpha Vantage's ``adjusted_close`` for the IJR and IVV members files'
#: series, downloaded 2026-10-05, in the owner's archive. The specification is
#: ``MATLAB_JANUARY`` on the S&P 600 at each year-end, January 2009 to January
#: 2026, and ``REVISED_MATLAB`` on the S&P 500 each month, January 2009 to
#: September 2026, both before costs. A re-pin there moves these figures.
PINNED = Verdicts(
    january_low=-0.1047304659686345,
    january_high=0.08787549947820747,
    monthly_mean=-0.0001391960725288475,
    detectable=0.0422031836138127,
    january_low_rejects=False,
    january_high_rejects=True,
    monthly_rejects=False,
)

#: The registered January run's eighteen Januaries, each with its low and high
#: return before costs, as ``test_the_whiteboard_draws_these_runs_ranges`` in
#: ``tests/test_equity_seasonals.py`` holds the run gives them. Same vintage
#: and specification as :data:`PINNED`'s January figures.
PINNED_RANGES = JanuaryRanges(
    (
        (2009, -0.3102916684682715, 0.31512341488232387),
        (2010, -0.19839476507411702, 0.24494937260065897),
        (2011, -0.192227314302099, 0.1889766558224868),
        (2012, -0.10870572849484236, 0.14492043392989745),
        (2013, -0.15467069691120883, 0.1457086223041022),
        (2014, -0.1653363299933961, 0.1597979963136514),
        (2015, -0.13112900962243856, 0.0686157912693974),
        (2016, -0.09597216550984841, 0.06014433261299512),
        (2017, -0.08469806698164244, 0.044717957152853684),
        (2018, -0.08838588652403147, 0.06835439802701994),
        (2019, -0.009638637680710993, 0.1306503085694603),
        (2020, -0.12694805604135495, -0.004070341602840345),
        (2021, -0.18706825793047532, -0.09002848776268077),
        (2022, -0.007092727187004211, 0.03353559694544943),
        (2023, 0.051120529038608704, 0.08356653439121693),
        (2024, -0.049378548477207414, -0.019616922654241906),
        (2025, -0.024022313935317015, 0.0037277705788413724),
        (2026, -0.0023087433400641386, 0.0026855572271426084),
    )
)

STROKES = [
    ["year", "close", "january", "to-rank", "ranked", "buy", "short", "losers-up", "winners-down"],
    [
        "last-year",
        "this-year",
        "march-then",
        "repeat",
        "march-now",
        "april-then",
        "april-now",
        "ranked",
        "buy",
        "short",
        "winners-up",
        "losers-down",
    ],
]

LABELS = [
    [
        "a year of returns",
        "hold January",
        "rank at the year’s last close",
        "buy the worst tenth",
        "short the best tenth",
        "losers up",
        "winners down",
        "mean reversion",
    ],
    [
        "last year",
        "this year",
        "March",
        "rank on",
        "hold",
        "then April, May, …",
        "buy the best tenth",
        "short the worst tenth",
        "winners up",
        "losers down",
        "seasonal momentum",
    ],
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def drawn():
    return scenes()


@pytest.fixture(scope="module")
def spans():
    return Spans.read()


@pytest.fixture(scope="module")
def opening(spans):
    return opening_scenes(PINNED, spans)


@pytest.fixture(scope="module")
def rules():
    return rule_scenes()


@pytest.fixture(scope="module")
def split():
    return split_scenes()


@pytest.fixture(scope="module")
def five():
    return five_year_scenes()


@pytest.fixture(scope="module")
def survivors():
    return survivor_scenes()


@pytest.fixture(scope="module")
def january():
    return january_scenes(PINNED_RANGES)


@pytest.fixture(scope="module")
def every(opening, drawn, rules, split, five, survivors, january):
    """All twenty-one scenes in the order their GIFs are written."""
    return (*opening, *drawn, *rules, *split, *five, *survivors, *january)


@pytest.fixture(scope="module")
def frames(every):
    return [sketch_timeline(scene) for scene in every]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, spans):
    return make_equity_seasonals_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"),
        verdicts=PINNED,
        spans=spans,
        ranges=PINNED_RANGES,
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _inside(ring, x: float, y: float) -> bool:
    """Whether (x, y) lies inside the ellipse ``ring`` traces."""
    cx, cy = ring.x.mean(), ring.y.mean()
    rx, ry = (ring.x.max() - ring.x.min()) / 2, (ring.y.max() - ring.y.min()) / 2
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1


def _ringed(scene, gid) -> list[int]:
    """The ranks, lowest return first, of the stocks the ring ``gid`` encloses."""
    ranked, ring = _stroke(scene, "ranked"), _stroke(scene, gid)
    return [k for k in range(ranked.points) if _inside(ring, ranked.x[k], ranked.y[k])]


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


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, drawn) -> None:
        assert [scene.title for scene in drawn] == TITLES

    def test_each_has_its_own_gif_named_for_it(self, drawn) -> None:
        assert [gif_name(scene) for scene in drawn] == STRATEGY_GIFS

    def test_each_draws_its_strokes_in_order(self, drawn) -> None:
        assert [[s.gid for s in scene.strokes] for scene in drawn] == STROKES

    def test_each_says_what_it_should(self, drawn) -> None:
        assert [scene.labels for scene in drawn] == LABELS

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


class TestTheBets:
    def test_a_tenth_of_the_ranked_row(self) -> None:
        assert TENTH * 10 == RANKED

    def test_the_row_is_sorted_lowest_return_first(self, drawn) -> None:
        for scene in drawn:
            ranked = _stroke(scene, "ranked")
            assert ranked.points == RANKED
            assert np.all(np.diff(ranked.y) > 0), scene.title

    def test_the_january_trade_buys_the_lowest_tenth_and_shorts_the_highest(self, drawn) -> None:
        january = drawn[0]
        assert _ringed(january, "buy") == list(range(TENTH))
        assert _ringed(january, "short") == list(range(RANKED - TENTH, RANKED))

    def test_the_same_month_trade_buys_the_highest_tenth_and_shorts_the_lowest(self, drawn) -> None:
        same = drawn[1]
        assert _ringed(same, "buy") == list(range(RANKED - TENTH, RANKED))
        assert _ringed(same, "short") == list(range(TENTH))

    def test_bought_is_green_and_shorted_red_in_rings_arrows_and_labels(self, drawn) -> None:
        for scene in drawn:
            assert _stroke(scene, "buy").color == GOOD
            assert _stroke(scene, "short").color == LOST
            for step in scene.steps:
                if isinstance(step, Label) and step.names in {"buy", "short"}:
                    assert step.color == _stroke(scene, step.names).color, step.text

    def test_the_january_trade_points_its_extremes_back(self, drawn) -> None:
        """Losers, which it buys, go up, and winners, which it shorts, go down."""
        january = drawn[0]
        up, down = _stroke(january, "losers-up"), _stroke(january, "winners-down")
        assert (up.y[1] > up.y[0], up.color) == (True, GOOD)
        assert (down.y[1] < down.y[0], down.color) == (True, LOST)
        assert up.y.max() < down.y.min()

    def test_the_same_month_trade_points_its_extremes_on(self, drawn) -> None:
        """Winners, which it buys, go further up, and losers, which it shorts,
        further down."""
        same = drawn[1]
        up, down = _stroke(same, "winners-up"), _stroke(same, "losers-down")
        assert (up.y[1] > up.y[0], up.color) == (True, GOOD)
        assert (down.y[1] < down.y[0], down.color) == (True, LOST)
        assert down.y.max() < up.y.min()

    def test_each_names_its_bet_in_the_posts_words(self, drawn) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene, bet in zip(drawn, ("mean reversion", "seasonal momentum"), strict=True):
            assert bet in scene.labels
            assert f"a {bet} trade" in text, bet


class TestTheTiming:
    def test_january_is_a_twelfth_of_the_year_past_the_close(self, drawn) -> None:
        x0, x1, y = YEAR
        january = _stroke(drawn[0], "january")
        close = _stroke(drawn[0], "close")
        assert (january.x[0], january.y[0]) == (close.x[0], close.y[0]) == (x1, y)
        assert january.x[-1] == pytest.approx(JANUARY_END)
        assert JANUARY_END - x1 == pytest.approx((x1 - x0) / 12)

    def test_the_same_month_is_ranked_last_year_and_held_this_year(self, drawn) -> None:
        same = drawn[1]
        then, now = _stroke(same, "march-then"), _stroke(same, "march-now")
        assert (then.x.min(), then.x.max()) == (now.x.min(), now.x.max())
        assert then.y.min() > now.y.max()
        repeat = _stroke(same, "repeat")
        assert repeat.x[0] == repeat.x[1] == pytest.approx((then.x.min() + then.x.max()) / 2)
        assert repeat.y[0] > repeat.y[1]

    def test_then_it_moves_on_a_month(self, drawn) -> None:
        same = drawn[1]
        march, april = _stroke(same, "march-now"), _stroke(same, "april-now")
        width = march.x.max() - march.x.min()
        assert april.x.min() == pytest.approx(march.x.max())
        assert april.x.max() - april.x.min() == pytest.approx(width)
        assert (_stroke(same, "april-then").x == april.x).all()


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

    def test_each_is_680_by_320_and_loops_forever(self, gifs, frames) -> None:
        for path, steps in zip(gifs, frames, strict=True):
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(path) == [f.ms for f in steps], path.name

    def test_each_opens_on_its_title_and_holds_its_drawing(self, every, frames) -> None:
        for scene, steps in zip(every, frames, strict=True):
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            hold = sketches.PACED_HOLD_MS if scene.slug in sketches.PACED else HOLD_MS
            assert steps[-1].ms == hold, scene.slug

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, spans) -> None:
        again = make_equity_seasonals_whiteboards(
            out_dir=tmp_path, verdicts=PINNED, spans=spans, ranges=PINNED_RANGES
        )
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


def _durations(path) -> list[int]:
    with Image.open(path) as image:
        found = []
        for index in range(image.n_frames):
            image.seek(index)
            found.append(image.info["duration"])
        return found


class TestTheCommittedGifs:
    def test_every_gif_in_the_figures_folder_is_drawn_by_one_of_the_two_modules(self) -> None:
        """A GIF no module draws is a figure nothing regenerates."""
        assert {path.name for path in FIGURES_DIR.glob("*.gif")} == set(GIFS) | set(USDCAD_GIFS)

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
            ), f"{path.name}: redraw with: uv run python -m chan.equity_seasonals_whiteboard"


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        """The timeline right after the paragraph that introduces the later
        runs, the last source it draws, then the list of the two verdicts and
        the verdicts sketch right after it, the
        January trade right after Example 7.6's paragraph, and the same-month
        trade right after Example 7.7's."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "Two later runs asked whether either effect still works.",
                "1. **The January effect** averages",
                "**Example 7.6, the January effect.**",
                "**Example 7.7, Heston and Sadka.**",
            ),
            OPENING_GIFS + STRATEGY_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_rule_sketch_closes_the_rule_it_draws(self) -> None:
        """Example 7.6's rules 2 and 3, then Example 7.7's rules 1, 2, 3, 5 and
        8, each with its sketch as the last block before the next heading."""
        text = POST.read_text(encoding="utf-8")
        for (example, rule), name in zip(
            (
                ("### Example 7.6", "#### Rule 2:"),
                ("### Example 7.6", "#### Rule 3:"),
                ("### Example 7.7", "#### Rule 1:"),
                ("### Example 7.7", "#### Rule 2:"),
                ("### Example 7.7", "#### Rule 3:"),
                ("### Example 7.7", "#### Rule 5:"),
                ("### Example 7.7", "#### Rule 8:"),
            ),
            RULE_GIFS,
            strict=True,
        ):
            start = text.index("\n" + rule, text.index("\n" + example))
            end = re.compile(r"\n#{2,4} ").search(text, start + 1).start()
            blocks = [b.strip() for b in text[start:end].split("\n\n") if b.strip()]
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", blocks[-1]
            ), name
            assert sum(name in b for b in blocks) == 1, name

    def test_the_split_sketch_follows_the_paragraph_on_the_years(self) -> None:
        """Before the paragraph that explains the running-sum chart, so that
        paragraph's "the figure below" still names the chart."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith("The 70 months from 2002")]
        name = re.escape(SPLIT_GIFS[0])
        assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{name}\)", paragraphs[index + 1])
        assert paragraphs[index + 2].startswith("The figure below adds up the 83 months")
        assert "equity_seasonals_split.png" in paragraphs[index + 3]

    def test_each_five_year_sketch_follows_its_paragraph(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "That sits beside the split without contradicting it.",
                "That verdict is narrow.",
                "Example 7.6 meets the same limit from another side.",
            ),
            FIVE_YEAR_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_lesson_3s_sketches_follow_their_paragraphs(self) -> None:
        """The saved file and the ranking after the paragraph that defines
        survivorship bias, the two panels after the one that ends on a panel
        keeping the companies that left."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (define,) = [
            k for k, p in enumerate(paragraphs) if p.startswith("Survivorship bias is what")
        ]
        (panel,) = [
            k for k, p in enumerate(paragraphs) if p.startswith("[The post on survivorship and")
        ]
        for offset, name in (
            (define + 1, SURVIVOR_GIFS[0]),
            (define + 2, SURVIVOR_GIFS[1]),
            (panel + 1, SURVIVOR_GIFS[2]),
        ):
            embed = paragraphs[offset]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name
        assert define + 3 == panel

    def test_each_january_sketch_follows_its_paragraph(self) -> None:
        """Each after its own paragraph, all three under the January question."""
        text = POST.read_text(encoding="utf-8")
        start = text.index("### Whether the January effect survived the book")
        end = text.index("\n### ", start + 1)
        paragraphs = [p for p in text[start:end].split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "A second run tested Example 7.6",
                "Free daily prices cover most",
                "The low series averages",
            ),
            JANUARY_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed.strip()
            ), name

    def test_every_sketch_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name


class TestTheCommand:
    def test_it_writes_every_committed_path(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            sketches,
            "make_equity_seasonals_whiteboards",
            lambda: [FIGURES_DIR / name for name in GIFS],
        )
        main()
        assert capsys.readouterr().out.splitlines() == [
            f"wrote {FIGURES_DIR / name}" for name in GIFS
        ]

    @pytest.mark.parametrize(
        "refusal",
        [
            ArchiveUnavailable("no archive here"),
            seasonals.PointInTimeRefused("a member is missing"),
            seasonals.MonthlyRunRefused("a schedule is missing"),
        ],
        ids=["no archive", "January run refused", "monthly run refused"],
    )
    def test_without_the_archive_it_names_the_two_gifs_it_left(
        self, monkeypatch, refusal, tmp_path
    ) -> None:
        """It draws into a scratch folder, because a draw into the figures
        folder would overwrite the committed GIFs that the byte test compares."""

        def refuse():
            raise refusal

        before = {path.name: path.read_bytes() for path in FIGURES_DIR.glob("*.gif")}
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(seasonals, "run_point_in_time", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == (
            "equity_seasonals_two_verdicts.gif and equity_seasonals_january_ranges.gif "
            f"were not redrawn: {refusal}"
        )
        assert len(list(tmp_path.glob("*.gif"))) == len(GIFS) - len(ARCHIVE_GIFS)
        assert {path.name: path.read_bytes() for path in FIGURES_DIR.glob("*.gif")} == before

    def test_without_the_archive_it_still_writes_the_other_nineteen(
        self, monkeypatch, tmp_path, spans
    ) -> None:
        def absent():
            raise ArchiveUnavailable("no archive here")

        monkeypatch.setattr(seasonals, "run_point_in_time", absent)
        with pytest.raises(ArchiveUnavailable):
            make_equity_seasonals_whiteboards(out_dir=tmp_path, spans=spans)
        written = sorted(path.name for path in tmp_path.glob("*.gif"))
        assert written == sorted(set(GIFS) - ARCHIVE_GIFS)


class TestTheVerdicts:
    """The verdicts sketch draws the registered runs' figures to scale."""

    def test_its_labels_print_the_pinned_figures(self, opening) -> None:
        assert opening[1].title == "Two verdicts"
        assert opening[1].labels == [
            "January effect",
            "per January",
            "0",
            "−0.1047",
            "0.0879",
            "free data cannot decide",
            "Heston and Sadka",
            "per year",
            "0",
            "about 4.2% a year",
            "measured",
            "could pass unseen",
        ]

    def test_the_bracket_spans_the_two_means_to_scale(self, opening) -> None:
        bracket = _stroke(opening[1], "bracket")
        assert bracket.x.min() == pytest.approx(_at(PINNED.january_low, *JANUARY_RANGE))
        assert bracket.x.max() == pytest.approx(_at(PINNED.january_high, *JANUARY_RANGE))
        zero = _stroke(opening[1], "january-zero")
        assert bracket.x.min() < zero.x[0] < bracket.x.max()

    def test_the_tint_runs_from_zero_to_x_and_the_dot_sits_at_the_mean(self, opening) -> None:
        scene = opening[1]
        (tint,) = scene.fills
        zero = _stroke(scene, "monthly-zero").x[0]
        detect = _stroke(scene, "detectable").x[0]
        assert (tint.x0, tint.x1) == pytest.approx((zero, detect))
        assert detect == pytest.approx(_at(PINNED.detectable, *ANNUAL_RANGE))
        mean = _stroke(scene, "mean")
        assert mean.x[0] == pytest.approx(_at(12 * PINNED.monthly_mean, *ANNUAL_RANGE))
        assert abs(mean.x[0] - zero) < detect - zero

    def test_other_figures_move_the_labels_and_the_marks(self, spans) -> None:
        moved = dataclasses.replace(
            PINNED, january_low=-0.05, january_high=0.12, monthly_mean=0.001, detectable=0.03
        )
        scene = opening_scenes(moved, spans)[1]
        assert {"−0.0500", "0.1200", "about 3.0% a year"} <= set(scene.labels)
        assert _stroke(scene, "bracket").x.max() == pytest.approx(_at(0.12, *JANUARY_RANGE))

    @pytest.mark.parametrize(
        "changes",
        [
            {"january_low": 0.01},
            {"january_high": -0.01},
            {"monthly_mean": 0.004},
            {"monthly_mean": -0.0015, "detectable": 0.01},
            {"january_low": -0.2},
            {"january_low_rejects": True},
            {"january_high_rejects": False},
            {"monthly_rejects": True},
        ],
        ids=[
            "bracket above zero",
            "bracket below zero",
            "mean past X",
            "mean past minus X",
            "off the line",
            "both January series reject",
            "neither January series rejects",
            "the monthly run rejects",
        ],
    )
    def test_figures_the_words_would_misdescribe_are_refused(self, spans, changes) -> None:
        with pytest.raises(ValueError):
            opening_scenes(dataclasses.replace(PINNED, **changes), spans)

    def test_the_january_line_is_to_scale(self, opening) -> None:
        """Absolute positions, not the scale function checked against itself:
        zero halfway along a line from −0.15 to 0.15, and each end of the
        bracket as far from zero as its value."""
        scene = opening[1]
        line = _stroke(scene, "january-line")
        zero = _stroke(scene, "january-zero").x[0]
        bracket = _stroke(scene, "bracket")
        assert zero == pytest.approx((line.x[0] + line.x[-1]) / 2)
        unit = (line.x[-1] - line.x[0]) / 0.30
        assert zero - bracket.x.min() == pytest.approx(-PINNED.january_low * unit)
        assert bracket.x.max() - zero == pytest.approx(PINNED.january_high * unit)

    def test_the_annual_line_is_to_scale(self, opening) -> None:
        """Zero a fifth of the way along a line from −0.02 to 0.08, and the
        tint as wide as X on that scale."""
        scene = opening[1]
        line = _stroke(scene, "monthly-line")
        width = line.x[-1] - line.x[0]
        (tint,) = scene.fills
        assert tint.x0 == pytest.approx(line.x[0] + 0.2 * width)
        assert tint.x1 - tint.x0 == pytest.approx(PINNED.detectable / 0.10 * width)


class TestTheTimeline:
    """The timeline places each source's years to scale."""

    def test_the_spans_are_the_files_and_the_runs(self, spans) -> None:
        """Chan's files as ``data/README.md`` records them, and the months
        both registered runs hold, January 2009 to September 2026."""
        day = pd.Timestamp
        assert spans.large_caps == (day("1999-11-24"), day("2007-11-23"))
        assert spans.small_caps == (day("2004-01-15"), day("2008-02-01"))
        assert spans.later == (day("2009-01-01"), day("2026-09-30"))
        assert spans.split == seasonals.SPLIT == day("2002-01-01")

    def test_its_labels(self, opening) -> None:
        assert opening[0].title == "Which years each source reads"
        assert opening[0].labels == [
            "1970",
            "1980",
            "1990",
            "2000",
            "2010",
            "2020",
            "Heston and Sadka’s 13%, before 2002",
            "“disappeared since then”",
            "Chan’s files, survivors only",
            "the book",
            "two later runs, index as it stood",
        ]

    def test_every_bar_sits_at_its_dates(self, opening, spans) -> None:
        scene = opening[0]
        assert _stroke(scene, "sample").x[-1] == pytest.approx(_year(spans.split))
        assert _stroke(scene, "split").x[0] == pytest.approx(_year(spans.split))
        for gid, (start, end) in (
            ("large-caps", spans.large_caps),
            ("small-caps", spans.small_caps),
        ):
            bar = _stroke(scene, gid)
            assert (bar.x[0], bar.x[-1]) == pytest.approx((_year(start), _year(end))), gid
        later = _stroke(scene, "later")
        assert (later.x[0], later.x[-1]) == pytest.approx(
            (_year(spans.later[0]), _year(spans.later[1]))
        )
        assert _stroke(scene, "book").x[0] == pytest.approx(_year(float(BOOK_YEAR)))

    def test_the_book_is_the_first_edition_the_post_cites_and_the_runs_start_that_year(
        self, spans
    ) -> None:
        assert "Chan, E. P. (2009)" in POST.read_text(encoding="utf-8")
        assert BOOK_YEAR == spans.later[0].year == seasonals.FIRST_HELD.year

    def test_the_monthly_months_hold_the_januaries_too(self, spans) -> None:
        first = pd.Timestamp(f"{BOOK_YEAR}-01-01")
        last = first + pd.DateOffset(years=seasonals.SURVIVOR_JANUARIES - 1)
        assert spans.later[0] <= first and last <= spans.later[1]

    def test_the_axis_runs_1960_to_2030_with_even_decades(self, opening) -> None:
        """Absolute positions: the axis spans the board's timeline, and
        1999-11-24 sits at its share of the seventy years."""
        axis = _stroke(opening[0], "axis")
        lo, hi = TIMELINE_X
        assert (axis.x.min(), axis.x.max()) == pytest.approx((lo, hi))
        ticks = sorted(
            {round(float(x), 9) for x, y in zip(axis.x, axis.y, strict=True) if y < AXIS_Y - 0.1}
        )
        assert len(ticks) == 6
        assert np.diff(ticks) == pytest.approx([(hi - lo) / 7] * 5)
        start = _stroke(opening[0], "large-caps").x[0]
        share = (pd.Timestamp("1999-11-24") - pd.Timestamp("1960-01-01")).days / (
            pd.Timestamp("2030-01-01") - pd.Timestamp("1960-01-01")
        ).days
        assert start == pytest.approx(lo + share * (hi - lo), abs=0.002)

    def test_the_sample_ends_where_chan_says_the_effect_disappeared(self, opening) -> None:
        """Its start is drawn dashed, since nothing here checked it."""
        scene = opening[0]
        lead, sample = _stroke(scene, "sample-lead"), _stroke(scene, "sample")
        assert lead.dashed and not sample.dashed
        assert lead.x[-1] == pytest.approx(sample.x[0])

    def test_chans_files_end_before_the_book_and_the_runs_begin_at_it(self, spans) -> None:
        assert max(spans.large_caps[1], spans.small_caps[1]) < spans.later[0]

    def test_other_spans_move_the_bars(self, spans) -> None:
        moved = dataclasses.replace(
            spans, large_caps=(pd.Timestamp("1995-01-02"), spans.large_caps[1])
        )
        bar = _stroke(opening_scenes(PINNED, moved)[0], "large-caps")
        assert bar.x[0] == pytest.approx(_year(pd.Timestamp("1995-01-02")))


def _labels(scene) -> list[str]:
    return scene.labels


def _xs(scene, gid) -> np.ndarray:
    return _stroke(scene, gid).x


def _middle(scene, gid) -> float:
    """The middle of the stroke's horizontal extent, the centre of a ring or a cross."""
    x = _stroke(scene, gid).x
    return float(x.min() + x.max()) / 2


#: Figures unlike the defaults in every field, so a mark that ignores its
#: figure and draws the default lands in the wrong place.
MOVED = RuleFigures(
    ranked_2006=600,
    longs_2006=60,
    shorts_2006=57,
    pmc_last_close=5.5,
    pmc_gap_days=800,
    pmc_2007_close=12.0,
    pmc_gain=1.1818,
    pmc_rank=3,
    ranked_2007=590,
    empty_months=11,
    held_months=85,
    month_end_rows=97,
    first_pass_row=240,
    repaired_row=11,
)


@pytest.fixture(params=[RuleFigures(), MOVED], ids=["the files' figures", "other figures"])
def figures(request) -> RuleFigures:
    return request.param


def _bar_heights(scene) -> list[float]:
    """Each bar's drawn return in the add-up scene, read from its stroke."""
    bars = _stroke(scene, "bars")
    heights = []
    for k in range(len(sketches.POSITION_RETURNS)):
        x = 0.8 + k * 0.33
        at = np.isclose(bars.x, x)
        offsets = bars.y[at] - sketches.SUM_BASE
        heights.append(float(offsets[np.argmax(np.abs(offsets))]))
    return heights


class TestTheRuleSketches:
    """What each rule sketch says and where it puts its marks."""

    def test_they_are_seven_in_the_order_the_post_reads_them(self, rules) -> None:
        assert [gif_name(scene) for scene in rules] == RULE_GIFS

    def test_each_prints_its_figures(self, rules) -> None:
        short, filled, _, _, empty, _, lookup = rules
        assert _labels(short) == [
            "buy the 58 worst",
            "short 56 of the 58 best",
            "a tenth: 58",
            "2 left out: the best and the 58th",
            "the winners are sliced as topN − 2",
            "January 2006, 579 stocks ranked",
        ]
        assert [s for s in _labels(filled) if not s.isdigit()] == [
            "PMC",
            "last close 6.02, then 851 trading days with no price",
            "end of 2006",
            "13.88",
            "+130.56% read as 2007’s gain",
            "4th best of 595: shorted",
        ]
        assert _labels(empty) == [
            "month 1: no return",
            "12 months with no position, each a 0",
            "83 months that hold positions",
            "first edition: sum ÷ 95",
            "revised: sum ÷ 83",
        ]
        assert _labels(lookup) == [
            "96 month-end rows",
            "row 1",
            "row 96",
            "row 258",
            "the first pass asks for it and stops",
            "the repair reads row m − 1, here 13",
        ]

    def test_the_schematic_ones_say_what_they_should(self, rules) -> None:
        _, _, bars, wrong, _, own, _ = rules
        assert _labels(bars) == [
            "one month’s N positions",
            "first edition: add them up",
            "summed positions",
            "revised: ÷ N",
            "capital",
            "each month is N times too big",
        ]
        assert _labels(wrong) == [
            "sorted by return",
            *sketches.SORTED,
            "column order",
            *sketches.COLUMNS,
            "no close",
            "E dropped: C has no close",
            "C ranked anyway",
            "each check reads the column, not the stock",
        ]
        assert _labels(own) == [
            "shared month-end row",
            "stock A",
            "stock B",
            "missing",
            "B’s own last priced day, which the revised Python reads",
            "the month’s last five trading days",
        ]

    def test_other_figures_move_the_labels(self) -> None:
        short, filled, _, _, empty, _, lookup = rule_scenes(MOVED)
        assert "3 left out: the best and the 60th" in _labels(short)
        assert "January 2006, 600 stocks ranked" in _labels(short)
        assert "3rd best of 590: shorted" in _labels(filled)
        assert "+118.18% read as 2007’s gain" in _labels(filled)
        assert "last close 5.50, then 800 trading days with no price" in _labels(filled)
        assert "first edition: sum ÷ 96" in _labels(empty)
        assert "revised: sum ÷ 85" in _labels(empty)
        assert "the repair reads row m − 1, here 11" in _labels(lookup)
        assert "row 240" in _labels(lookup) and "97 month-end rows" in _labels(lookup)

    def test_the_two_sides_are_to_scale_and_the_long_side_reaches_a_tenth(self, figures) -> None:
        short = rule_scenes(figures)[0]
        long_bar, short_bar = _stroke(short, "long"), _stroke(short, "short")
        assert np.ptp(long_bar.x) == pytest.approx(figures.longs_2006 * sketches.STOCK_WIDTH)
        assert np.ptp(short_bar.x) == pytest.approx(figures.shorts_2006 * sketches.STOCK_WIDTH)
        assert _xs(short, "tenth").min() == pytest.approx(long_bar.x.max())
        gap = _stroke(short, "missing")
        assert (gap.x.min(), gap.x.max()) == pytest.approx((short_bar.x.max(), long_bar.x.max()))
        assert (long_bar.color, short_bar.color) == (GOOD, LOST)

    def test_pmcs_close_is_carried_flat_to_the_end_of_2006_and_rises_to_2007s(
        self, figures
    ) -> None:
        filled = rule_scenes(figures)[1]
        carried = _stroke(filled, "carried")
        assert np.ptp(carried.y) == pytest.approx(0.0)
        assert carried.y[0] == pytest.approx(sketches._pmc_y(figures.pmc_last_close))
        start, end = _stroke(filled, "end-2006"), _stroke(filled, "end-2007")
        assert start.x[0] == pytest.approx(sketches._pmc_x(2007.0))
        assert carried.x.max() == pytest.approx(start.x[0])
        assert start.y[0] == pytest.approx(sketches._pmc_y(figures.pmc_last_close))
        assert end.y[0] == pytest.approx(sketches._pmc_y(figures.pmc_2007_close))
        assert sketches._pmc_x(2007.5) < end.x[0] < sketches._pmc_x(2008.0)
        after = _stroke(filled, "after")
        assert end.y[0] in after.y and end.x[0] in after.x
        gain = _stroke(filled, "gain")
        assert gain.color == LOST and gain.y.max() > gain.y[0]

    def test_the_sum_is_the_bars_added_up_and_n_times_the_average(self, rules) -> None:
        bars = rules[2]
        heights = _bar_heights(bars)
        assert heights == pytest.approx(list(sketches.POSITION_RETURNS))
        total = _stroke(bars, "sum").y.min() - sketches.SUM_BASE
        mean = _stroke(bars, "mean").y.min() - sketches.SUM_BASE
        assert total == pytest.approx(sum(heights))
        assert total == pytest.approx(len(heights) * mean)
        assert total < mean < 0

    def test_the_check_pairs_columns_and_rings_the_wrong_stock(self, rules) -> None:
        wrong = rules[3]
        hole = sketches.COLUMNS.index(sketches.NO_CLOSE)
        for k in range(len(sketches.COLUMNS)):
            arrow = _stroke(wrong, f"pair-{k}")
            assert arrow.x[0] == pytest.approx(sketches._card(k))
            assert arrow.color == (LOST if k == hole else whiteboard.MUTED)
        rising = _stroke(wrong, f"pair-{hole}")
        assert rising.y[0] < rising.y.max() == pytest.approx(sketches.SORTED_Y - 0.42)
        assert _middle(wrong, "dropped") == pytest.approx(sketches._card(hole), abs=0.01)
        assert sketches.SORTED[hole] != sketches.NO_CLOSE
        kept_at = sketches.SORTED.index(sketches.NO_CLOSE)
        assert _middle(wrong, "kept") == pytest.approx(sketches._card(kept_at), abs=0.01)
        assert _middle(wrong, "no-close") == pytest.approx(sketches._card(hole), abs=0.01)
        assert (_stroke(wrong, "dropped").color, _stroke(wrong, "kept").color) == (
            LOST,
            whiteboard.ACCENT,
        )

    def test_the_months_are_counted_and_each_bracket_spans_its_mean(self, figures) -> None:
        empty = rule_scenes(figures)[4]
        months = 1 + figures.empty_months + figures.held_months
        assert _stroke(empty, "empty").points == figures.empty_months
        assert _stroke(empty, "held").points == figures.held_months
        assert _middle(empty, "missing") == pytest.approx(sketches._month(1, months), abs=0.01)
        first, revised = _stroke(empty, "first"), _stroke(empty, "revised")
        assert (first.x.min(), first.x.max()) == pytest.approx(
            (sketches._month(2, months), sketches._month(months, months))
        )
        assert (revised.x.min(), revised.x.max()) == pytest.approx(
            (sketches._month(2 + figures.empty_months, months), sketches._month(months, months))
        )
        assert revised.x.min() == pytest.approx(_stroke(empty, "held").x.min())

    def test_b_is_read_on_its_own_last_day_and_missing_on_the_shared_row(self, rules) -> None:
        own = rules[5]
        shared = next(step for step in own.fills if step.gid == "shared")
        last = sketches.DAYS_X[-1]
        assert shared.x0 < last < shared.x1
        assert _stroke(own, "a").points == len(sketches.DAYS_X)
        b = _stroke(own, "b")
        assert b.x.max() < shared.x0
        assert _middle(own, "b-own") == pytest.approx(b.x.max(), abs=0.01)
        assert _middle(own, "b-missing") == pytest.approx(last, abs=0.01)
        assert (_stroke(own, "b-own").color, _stroke(own, "b-missing").color) == (GOOD, LOST)

    def test_the_lookup_runs_past_the_rows_and_the_repair_reads_a_row(self, figures) -> None:
        lookup = rule_scenes(figures)[6]
        x0, x1, _ = sketches.ROWS
        assert _stroke(lookup, "past").x.min() == pytest.approx(x1)
        assert _middle(lookup, "asks") > x1
        width = (x1 - x0) / figures.month_end_rows
        repair = _stroke(lookup, "repair")
        assert repair.x[0] == pytest.approx(x0 + (figures.repaired_row - 0.5) * width)


#: Figures unlike the file's, with the halves further apart than the years,
#: so a mark drawn from the defaults lands in the wrong place.
SWUNG = SplitFigures(before_2002=-0.05, from_2002=0.12, year_2002=-0.08, year_2006=0.04)


#: Figures with the halves the other way round, so a gap that is not a
#: distance would print with a minus sign.
FLIPPED = SplitFigures(before_2002=0.09, from_2002=-0.02, year_2002=0.15, year_2006=-0.1)


@pytest.fixture(
    params=[SplitFigures(), SWUNG, FLIPPED],
    ids=["the file's figures", "other figures", "the halves the other way round"],
)
def split_figures(request) -> SplitFigures:
    return request.param


class TestTheSplitSketch:
    """The two halves' annual returns beside two single years, to one scale."""

    def test_it_says_what_it_should(self, split) -> None:
        (swing,) = split
        assert gif_name(swing) == SPLIT_GIFS[0]
        assert swing.labels == [
            "the two halves, an average year",
            "before 2002",
            "−0.145387",
            "from 2002",
            "+0.011967",
            "0.1574 apart",
            "two single years, 12 months each",
            "2002",
            "+0.2227",
            "2006",
            "−0.1319",
            "0.3546 apart",
            "before costs",
        ]

    def test_other_figures_move_the_labels(self) -> None:
        (swing,) = split_scenes(SWUNG)
        for text in (
            "−0.050000",
            "+0.120000",
            "0.1700 apart",
            "−0.0800",
            "+0.0400",
            "0.1200 apart",
        ):
            assert text in swing.labels, text

    def test_each_bar_runs_from_zero_to_its_figure_in_its_signs_colour(self, split_figures) -> None:
        (swing,) = split_scenes(split_figures)
        f = split_figures
        for gid, value in (
            ("before", f.before_2002),
            ("after", f.from_2002),
            ("y2002", f.year_2002),
            ("y2006", f.year_2006),
        ):
            bar = _stroke(swing, gid)
            assert np.ptp(bar.x) == pytest.approx(0.0)
            assert bar.y[0] == pytest.approx(sketches.SWING_ZERO)
            assert bar.y[-1] - bar.y[0] == pytest.approx(value * sketches.SWING_PER)
            assert bar.color == (GOOD if value > 0 else LOST), gid

    def test_each_bracket_spans_its_pairs_gap(self, split_figures) -> None:
        (swing,) = split_scenes(split_figures)
        f = split_figures
        for gid, ends in (
            ("halves-gap", (f.before_2002, f.from_2002)),
            ("years-gap", (f.year_2002, f.year_2006)),
        ):
            bracket = _stroke(swing, gid)
            assert (bracket.y.min(), bracket.y.max()) == pytest.approx(
                tuple(sketches._swing_y(v) for v in sorted(ends))
            ), gid

    def test_the_years_bracket_is_longer_on_the_files_figures(self, split) -> None:
        (swing,) = split
        halves = np.ptp(_stroke(swing, "halves-gap").y)
        years = np.ptp(_stroke(swing, "years-gap").y)
        assert years / halves == pytest.approx(0.35464347755594144 / 0.15735417776401822)
        assert years > 2 * halves

    def test_each_pair_stands_in_its_own_group(self, split) -> None:
        (swing,) = split
        halves = [_stroke(swing, gid).x[0] for gid in ("before", "after")]
        years = [_stroke(swing, gid).x[0] for gid in ("y2002", "y2006")]
        assert max(halves) < _stroke(swing, "halves-gap").x.max() < min(years)
        assert max(years) < _stroke(swing, "years-gap").x.max()

    def test_each_gap_prints_as_a_distance(self, split_figures) -> None:
        (swing,) = split_scenes(split_figures)
        f = split_figures
        gaps = [text for text in swing.labels if text.endswith(" apart")]
        assert gaps == [
            f"{abs(f.from_2002 - f.before_2002):.4f} apart",
            f"{abs(f.year_2002 - f.year_2006):.4f} apart",
        ]

    def test_each_value_sits_by_its_bar_in_its_signs_colour(self, split_figures) -> None:
        (swing,) = split_scenes(split_figures)
        f = split_figures
        values = {
            "before": f.before_2002,
            "after": f.from_2002,
            "y2002": f.year_2002,
            "y2006": f.year_2006,
        }
        for gid, value in values.items():
            places = 6 if gid in ("before", "after") else 4
            text = f"{value:+.{places}f}".replace("-", "−")
            (label,) = [s for s in swing.steps if isinstance(s, Label) and s.text == text]
            assert label.names == gid
            assert abs(label.x - _stroke(swing, gid).x[0]) <= 0.25, gid
            assert label.color == (GOOD if value > 0 else LOST), gid

    def test_both_brackets_and_their_gaps_are_brown(self, split) -> None:
        (swing,) = split
        for gid in ("halves-gap", "years-gap"):
            assert _stroke(swing, gid).color == whiteboard.ACCENT
        gaps = [s for s in swing.steps if isinstance(s, Label) and s.text.endswith(" apart")]
        assert [s.color for s in gaps] == [whiteboard.ACCENT, whiteboard.ACCENT]


#: Five-year figures unlike the file's in every field, so a mark drawn from
#: the defaults lands in the wrong place.
SHIFTED = FiveYearFigures(
    whole_months=80,
    before_months=10,
    after_months=70,
    rerun_months=44,
    between_months=26,
    whole_python=-0.02,
    before_2002=0.1,
    from_2002=-0.02,
    rerun_python=-0.03,
    between=-0.05,
    whole_matlab=-0.01,
    rerun_matlab=-0.02,
    rerun_error=0.015,
    januaries=((2006, 0.03), (2007, -0.02), (2008, 0.05)),
)


@pytest.fixture(params=[FiveYearFigures(), SHIFTED], ids=["the files' figures", "other figures"])
def five_figures(request) -> FiveYearFigures:
    return request.param


def _labelled(scene, text: str) -> Label:
    (label,) = [s for s in scene.steps if isinstance(s, Label) and s.text == text]
    return label


class TestTheFiveYearSketches:
    """The months each figure covers, the gap against the noise, and three Januaries."""

    def test_they_are_three_in_the_order_the_post_reads_them(self, five) -> None:
        assert [gif_name(scene) for scene in five] == FIVE_YEAR_GIFS

    def test_each_says_what_it_should(self, five) -> None:
        months, noise, januaries = five
        assert months.labels == [
            *[str(year) for year in range(2001, 2008)],
            "whole period: 83 months, −0.012679",
            "before 2002: 13 months, −0.145387",
            "from 2002: 70 months, +0.011967",
            "first year only ranks",
            "five-year rerun: 47 months, −0.016431",
            "23 months the rerun leaves out: +0.069997",
            "revised Python’s rules, a year, before costs",
        ]
        assert noise.labels == [
            "one standard error each way, 0.0281",
            "−0.04",
            "−0.02",
            "0",
            "five-year rerun −0.0165",
            "whole period −0.0129",
            "0.0036 apart",
            "revised MATLAB’s rules, a year, before costs",
        ]
        assert januaries.labels == [
            "January 2006",
            "−0.0244",
            "January 2007",
            "−0.0068",
            "January 2008",
            "+0.0881",
            "three trades",
            "Example 7.6 in MATLAB, after costs",
        ]

    def test_other_figures_move_the_labels(self) -> None:
        months, noise, januaries = five_year_scenes(SHIFTED)
        for text in (
            "whole period: 80 months, −0.020000",
            "before 2002: 10 months, +0.100000",
            "five-year rerun: 44 months, −0.030000",
            "26 months the rerun leaves out: −0.050000",
        ):
            assert text in months.labels, text
        for text in (
            "one standard error each way, 0.0150",
            "0.0100 apart",
            "five-year rerun −0.0200",
        ):
            assert text in noise.labels, text
        assert "+0.0300" in januaries.labels and "−0.0200" in januaries.labels

    def test_each_bar_on_the_timeline_covers_its_months(self, five) -> None:
        """Each bar's length is its month count, a twelfth of a year each."""
        (months, _, _) = five
        figures = FiveYearFigures()
        month = sketches._when(sketches.MONTHS_FROM + 1 / 12) - sketches._when(sketches.MONTHS_FROM)
        whole = _stroke(months, "whole")
        assert np.ptp(whole.x) == pytest.approx(figures.whole_months * month)
        halves = np.ptp(_stroke(months, "before").x) + np.ptp(_stroke(months, "after").x)
        assert halves == pytest.approx(
            (figures.before_months + figures.after_months) * month, abs=0.09
        )
        assert np.ptp(_stroke(months, "rerun").x) == pytest.approx(figures.rerun_months * month)
        assert np.ptp(_stroke(months, "warm-up").x) == pytest.approx(12 * month)
        between = _stroke(months, "between")
        assert np.ptp(between.x) == pytest.approx(figures.between_months * month)
        assert between.x.max() == pytest.approx(_stroke(months, "rerun").x.min())
        assert between.x.min() == pytest.approx(sketches._when(sketches.SPLIT_YEAR))

    def test_the_timeline_takes_its_colours_from_the_signs(self, five_figures) -> None:
        months = five_year_scenes(five_figures)[0]
        f = five_figures
        assert _stroke(months, "before").color == (GOOD if f.before_2002 > 0 else LOST)
        assert _stroke(months, "after").color == (GOOD if f.from_2002 > 0 else LOST)
        assert _stroke(months, "between").color == (GOOD if f.between > 0 else LOST)
        assert _stroke(months, "warm-up").dashed
        for gid, prefix in (
            ("before", "before 2002:"),
            ("after", "from 2002:"),
            ("between", f"{f.between_months} months the rerun"),
        ):
            (label,) = [
                s for s in months.steps if isinstance(s, Label) and s.text.startswith(prefix)
            ]
            assert label.color == _stroke(months, gid).color, gid

    def test_each_year_label_sits_on_its_tick(self, five) -> None:
        months = five[0]
        axis = _stroke(months, "axis")
        for year in range(2001, 2008):
            label = _labelled(months, str(year))
            assert label.x == pytest.approx(sketches._when(year))
            assert np.isclose(axis.x, label.x).sum() >= 2, year
            assert axis.y[np.isclose(axis.x, label.x)].min() < sketches.MONTHS_AXIS_Y

    def test_each_value_on_the_noise_line_sits_on_its_tick(self, five) -> None:
        noise = five[1]
        line = _stroke(noise, "line")
        for value, text in ((-0.04, "−0.04"), (-0.02, "−0.02"), (0.0, "0")):
            label = _labelled(noise, text)
            assert label.x == pytest.approx(sketches._on_noise(value))
            assert line.y[np.isclose(line.x, label.x)].min() < sketches.NOISE_Y, text

    def test_each_alt_text_quotes_its_sketchs_words(self, five) -> None:
        """Every label but the axis numbers appears in the alt text word for word."""
        text = POST.read_text(encoding="utf-8")
        ticks = {str(year) for year in range(2001, 2008)} | {"−0.04", "−0.02", "0"}
        for scene in five:
            match = re.search(
                rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text
            )
            assert match, scene.slug
            alt = match.group(1)
            assert f"“{scene.title}”" in alt, scene.slug
            for label in scene.labels:
                if label not in ticks and not label.startswith("January "):
                    assert label in alt, (scene.slug, label)

    def test_the_band_and_dots_stand_at_their_figures(self, five_figures) -> None:
        noise = five_year_scenes(five_figures)[1]
        f = five_figures
        band = next(step for step in noise.fills if step.gid == "band")
        assert band.x0 == pytest.approx(sketches._on_noise(f.rerun_matlab - f.rerun_error))
        assert band.x1 == pytest.approx(sketches._on_noise(f.rerun_matlab + f.rerun_error))
        rerun, whole = _stroke(noise, "rerun"), _stroke(noise, "whole")
        assert rerun.x[0] == pytest.approx(sketches._on_noise(f.rerun_matlab))
        assert whole.x[0] == pytest.approx(sketches._on_noise(f.whole_matlab))
        gap = _stroke(noise, "gap")
        assert (gap.x.min(), gap.x.max()) == pytest.approx(tuple(sorted((rerun.x[0], whole.x[0]))))

    def test_the_gap_is_far_inside_the_band_on_the_files_figures(self, five) -> None:
        noise = five[1]
        band = next(step for step in noise.fills if step.gid == "band")
        gap = _stroke(noise, "gap")
        assert (band.x1 - band.x0) / np.ptp(gap.x) > 15

    def test_each_january_bar_runs_to_its_trade(self, five_figures) -> None:
        januaries = five_year_scenes(five_figures)[2]
        for year, r in five_figures.januaries:
            bar = _stroke(januaries, f"jan-{year}")
            assert bar.y[0] == pytest.approx(sketches.JANUARY_ZERO)
            assert bar.y[-1] - bar.y[0] == pytest.approx(r * sketches.JANUARY_PER)
            assert bar.color == (GOOD if r > 0 else LOST)
            value = _labelled(januaries, f"{r:+.4f}".replace("-", "−"))
            assert value.names == f"jan-{year}" and value.color == bar.color
            assert abs(value.x - bar.x[0]) < 1e-9

    def test_the_paced_sketches_build_slowly_and_hold_twelve_seconds(self, every) -> None:
        """The pace the owner accepted: each label alone for 0.9 s, the drawing for 12 s."""
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        for scene in every:
            frames = sketch_timeline(scene)
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            paced = scene.slug in sketches.PACED
            assert paced == (
                scene.slug
                in (
                    "five_year_months",
                    "five_year_noise",
                    "survivors_ranking",
                    "survivors_panels",
                    "january_fill",
                    "january_ranges",
                )
            )
            assert {f.ms for f in labels} <= {
                sketches.PACED_LABEL_MS if paced else whiteboard.LABEL_MS
            }
            assert frames[-1].ms == (sketches.PACED_HOLD_MS if paced else HOLD_MS)
            assert [(f.done, f.partial) for f in frames] == [
                (f.done, f.partial) for f in timeline(scene)
            ]


class TestTheSurvivorSketches:
    """Lesson 3's three schematic sketches of survivorship bias."""

    def test_they_are_three_in_the_order_the_post_reads_them(self, survivors) -> None:
        assert [gif_name(scene) for scene in survivors] == SURVIVOR_GIFS

    def test_each_says_what_it_should(self, survivors) -> None:
        saved, ranking, panels = survivors
        assert saved.labels == [
            "1999",
            "2003",
            "2007",
            "companies still in the index in 2007",
            "acquired",
            "shrank out of the index",
            "failed",
            "Chan saves the file",
            "in the file",
            "missing from it",
        ]
        assert ranking.labels == [
            "as it stood",
            "lowest return",
            "highest",
            "worst tenth",
            "in the file",
            "the file’s worst tenth: a different set",
            "red rings: companies that left the index before the file was saved",
        ]
        assert panels.labels == [
            "a file saved in 2007",
            "joined later, carried back",
            "2007’s members, carried back",
            "the index as it stood",
            "joined",
            "left",
            "left",
            "members at each ranking date",
            "the later runs, from 2009, used the panel on the right",
        ]

    def test_the_survivors_reach_the_save_and_the_leavers_stop_short(self, survivors) -> None:
        saved = survivors[0]
        save = _stroke(saved, "save")
        for k in range(len(sketches.SURVIVOR_ROWS)):
            line = _stroke(saved, f"survivor-{k}")
            assert (line.x.min(), line.x.max()) == pytest.approx(
                (sketches.SAVED_FROM_X, sketches.SAVED_TO_X)
            )
            assert line.color == whiteboard.INK
        for k, (_, share, why) in enumerate(sketches.LEAVERS):
            line = _stroke(saved, f"leaver-{k}")
            assert line.x.max() < sketches.SAVED_TO_X and line.color == LOST, why
            assert line.x.max() == pytest.approx(
                sketches.SAVED_FROM_X + (sketches.SAVED_TO_X - sketches.SAVED_FROM_X) * share
            )
        assert save.dashed and save.x[0] > sketches.SAVED_TO_X

    def test_each_bracket_spans_its_rows_past_the_save(self, survivors) -> None:
        saved = survivors[0]
        save_x = _stroke(saved, "save").x[0]
        rows = sketches.SURVIVOR_ROWS
        leavers = [y for y, _, _ in sketches.LEAVERS]
        for gid, ys, colour in (("in-file", rows, whiteboard.INK), ("not-in-file", leavers, LOST)):
            bracket = _stroke(saved, gid)
            assert bracket.x.min() > save_x
            assert bracket.y.min() < min(ys) and bracket.y.max() > max(ys)
            assert bracket.color == colour

    def test_the_file_drops_the_leavers_so_its_tenth_is_a_different_set(self, survivors) -> None:
        ranking = survivors[1]
        xs = np.linspace(*sketches.SURVIVOR_XS, sketches.SURVIVOR_RANKED)
        kept = [k for k in range(sketches.SURVIVOR_RANKED) if k not in sketches.GONE]
        stood, in_file = _stroke(ranking, "stood"), _stroke(ranking, "file")
        assert stood.x == pytest.approx(xs[kept]) and in_file.x == pytest.approx(xs[kept])
        for k in sketches.GONE:
            assert _middle(ranking, f"gone-{k}") == pytest.approx(xs[k], abs=0.01)
            assert _stroke(ranking, f"gone-{k}").color == LOST
        tenth = sketches.SURVIVOR_TENTH
        assert _middle(ranking, "stood-tenth") == pytest.approx(xs[:tenth].mean(), abs=0.01)
        assert _middle(ranking, "file-tenth") == pytest.approx(xs[kept[:tenth]].mean(), abs=0.01)
        assert set(range(tenth)) & set(sketches.GONE), "the worst tenth as it stood holds a leaver"
        assert not set(kept[:tenth]) & set(sketches.GONE)
        assert _stroke(ranking, "stood-tenth").dashed
        assert _stroke(ranking, "file-tenth").color == whiteboard.ACCENT
        assert sketches.SURVIVOR_TENTH * 10 == sketches.SURVIVOR_RANKED

    def test_the_saved_panel_keeps_no_leaver_and_carries_the_joiner_back(self, survivors) -> None:
        panels = survivors[2]
        left, right = sketches.SAVED_PANEL, sketches.STOOD_PANEL
        saved = [s for s in panels.strokes if s.gid.startswith("saved-")]
        assert len(saved) == 7
        for line in saved:
            assert (line.x.min(), line.x.max()) == pytest.approx(left)
        assert _stroke(panels, "saved-joiner").color == GOOD
        for k in range(6):
            assert _stroke(panels, f"saved-{k}").color == whiteboard.INK
        stood = [s for s in panels.strokes if s.gid.startswith("stood-")]
        assert len(stood) == 9
        for line, (a, b), colour in zip(
            stood, sketches.STOOD_SPANS, sketches.STOOD_COLOURS, strict=True
        ):
            assert (line.x.min(), line.x.max()) == pytest.approx(
                (sketches._panel_x(right, a), sketches._panel_x(right, b))
            )
            assert line.color == colour
        assert sketches.STOOD_COLOURS.count(LOST) == 2
        assert sketches.STOOD_SPANS[6][0] > 0 and sketches.STOOD_COLOURS[6] == GOOD
        for (a, b), colour in zip(sketches.STOOD_SPANS, sketches.STOOD_COLOURS, strict=True):
            if colour == whiteboard.INK:
                assert (a, b) == (0, 1)
            elif colour == LOST:
                assert a == 0 and b < 1
            else:
                assert a > 0 and b == 1

    def test_each_alt_text_quotes_its_sketchs_words(self, survivors) -> None:
        """Every label but the axis years appears in the alt text word for word,
        and the alt text's counts are the sketch's."""
        text = POST.read_text(encoding="utf-8")
        for scene in survivors:
            alt = _alt(text, scene)
            for label in scene.labels:
                if label not in ("1999", "2003", "2007"):
                    assert label in alt, (scene.slug, label)
        saved = _alt(text, survivors[0]).lower()
        assert f"{_count_word(len(sketches.SURVIVOR_ROWS))} black lines" in saved
        assert f"{_count_word(len(sketches.LEAVERS))} red lines" in saved
        ranking = _alt(text, survivors[1]).lower()
        assert f"ranks {_count_word(sketches.SURVIVOR_RANKED)} stocks" in ranking
        assert f"{_count_word(len(sketches.GONE))} of them drawn as red rings" in ranking


def _alt(text: str, scene) -> str:
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


def _count_word(n: int) -> str:
    return {3: "three", 6: "six", 18: "eighteen", 20: "twenty"}.get(n, str(n))


class TestTheJanuarySketches:
    """The January section's three sketches: registered, the two fills, the ranges."""

    def test_they_are_three_in_the_order_the_post_reads_them(self, january) -> None:
        assert [gif_name(scene) for scene in january] == JANUARY_GIFS

    def test_each_says_what_it_should(self, january) -> None:
        registered, fill, ranges = january
        assert registered.labels == [
            "claim",
            "test",
            "verdict’s words",
            "all written down",
            "then returns computed",
            "registered",
            "returns computed",
            "no claim written down first",
            "exploratory",
            "exploratory can kill an idea, only registered can confirm one",
        ]
        assert fill.labels == [
            "buy the worst tenth",
            "short the best tenth",
            "?",
            "a member with no checked price",
            "could land in a traded tenth",
            "low version",
            "if bought: near the worst January return",
            "if shorted: near the best",
            "high version",
            "if bought: near the best January return",
            "if shorted: near the worst",
            "so each January gets a low and a high result",
        ]
        assert ranges.title == "Eighteen Januaries, each a range"
        assert ranges.labels == [
            "0",
            "2009",
            "2014",
            "2019",
            "2026",
            "each bar runs from a January’s low version to its high",
            "black: straddles zero, so free data cannot tell which side",
            "before costs",
        ]

    def test_the_written_steps_come_before_the_line_and_the_returns_after(self, january) -> None:
        registered = january[0]
        line = _stroke(registered, "written").x[0]
        for k in range(len(sketches.WRITTEN_STEPS)):
            assert _stroke(registered, f"box-{k}").x.max() < line
        assert _stroke(registered, "box-3").x.min() > line
        assert _stroke(registered, "box-3").color == GOOD
        assert _stroke(registered, "box-4").color == LOST
        assert _stroke(registered, "box-4").x.max() < _stroke(registered, "box-5").x.min()

    def test_the_gap_can_land_in_a_traded_tenth(self, january) -> None:
        fill = january[1]
        xs = np.linspace(*sketches.FILL_XS, sketches.FILL_RANKED)
        tenth = sketches.FILL_TENTH
        assert tenth * 10 == sketches.FILL_RANKED
        assert _middle(fill, "buy") == pytest.approx(xs[:tenth].mean(), abs=0.01)
        assert _middle(fill, "short") == pytest.approx(xs[-tenth:].mean(), abs=0.01)
        assert (_stroke(fill, "buy").color, _stroke(fill, "short").color) == (GOOD, LOST)
        colours = {s.text: s.color for s in fill.steps if isinstance(s, Label)}
        for text in (
            "low version",
            "if bought: near the worst January return",
            "if shorted: near the best",
        ):
            assert colours[text] == LOST, text
        for text in (
            "high version",
            "if bought: near the best January return",
            "if shorted: near the worst",
        ):
            assert colours[text] == GOOD, text
        to_buy, to_short = _stroke(fill, "to-buy"), _stroke(fill, "to-short")
        assert to_buy.x[0] < sketches.UNPRICED[0] < to_short.x[0]
        assert to_buy.x.min() < xs[tenth] and to_short.x.max() > xs[-tenth - 1]

    @pytest.mark.parametrize(
        "ranges",
        [
            PINNED_RANGES,
            JanuaryRanges(((2009, -0.2, 0.1), (2010, 0.02, 0.05), (2011, -0.04, -0.01))),
        ],
        ids=["the run's Januaries", "other Januaries"],
    )
    def test_each_bar_runs_from_low_to_high_in_its_colour(self, ranges) -> None:
        scene = january_scenes(ranges)[2]
        xs = np.linspace(*sketches.RANGES_X, len(ranges.januaries))
        for x, (year, low, high) in zip(xs, ranges.januaries, strict=True):
            bar = _stroke(scene, f"jan-{year}")
            assert bar.x == pytest.approx(np.full(bar.points, x))
            assert bar.y[0] == pytest.approx(sketches.RANGES_ZERO + low * sketches.RANGES_PER)
            assert bar.y[-1] == pytest.approx(sketches.RANGES_ZERO + high * sketches.RANGES_PER)
            expected = whiteboard.INK if low < 0 < high else (GOOD if low > 0 else LOST)
            assert bar.color == expected, year
        count = len(ranges.januaries)
        word = {18: "Eighteen", 3: "Three"}[count]
        assert scene.title == f"{word} Januaries, each a range"

    def test_the_runs_januaries_straddle_but_four(self) -> None:
        """What the alt text says: 2020, 2021 and 2024 below zero, 2023 above."""
        below = [y for y, low, high in PINNED_RANGES.januaries if high < 0]
        above = [y for y, low, high in PINNED_RANGES.januaries if low > 0]
        assert (below, above) == ([2020, 2021, 2024], [2023])

    def test_each_alt_text_quotes_its_sketchs_words(self, january) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in january:
            alt = _alt(text, scene)
            for label in scene.labels:
                if label not in ("0", "2014", "2019", "?"):
                    assert label in alt, (scene.slug, label)
        ranges = _alt(text, january[2])
        assert "Eighteen vertical bars" in ranges and "2020, 2021 and 2024" in ranges
        assert "the bar for 2023 is green" in ranges

    def test_the_ranges_average_to_the_verdicts_pinned_means(self) -> None:
        """The two pins come from one run, so the Januaries average to its means."""
        lows = [low for _, low, _ in PINNED_RANGES.januaries]
        highs = [high for _, _, high in PINNED_RANGES.januaries]
        assert float(np.mean(lows)) == pytest.approx(PINNED.january_low, abs=1e-12)
        assert float(np.mean(highs)) == pytest.approx(PINNED.january_high, abs=1e-12)

    def test_a_redraw_with_the_archive_draws_the_ranges_from_the_run(
        self, monkeypatch, tmp_path, spans
    ) -> None:
        """Without this, a redraw could draw the ranges without reading the run."""
        run, seen = object(), []

        def from_run(january):
            seen.append(january)
            return PINNED_RANGES

        monkeypatch.setattr(seasonals, "run_point_in_time", lambda: run)
        monkeypatch.setattr(seasonals, "run_monthly_point_in_time", lambda: object())
        monkeypatch.setattr(sketches.Verdicts, "from_runs", classmethod(lambda cls, a, b: PINNED))
        monkeypatch.setattr(
            sketches.JanuaryRanges, "from_run", classmethod(lambda cls, january: from_run(january))
        )
        written = make_equity_seasonals_whiteboards(out_dir=tmp_path, spans=spans)
        assert sorted(path.name for path in written) == sorted(GIFS)
        assert seen == [run]
        seen.clear()
        make_equity_seasonals_whiteboards(out_dir=tmp_path, spans=spans, verdicts=PINNED)
        assert seen == [run], "the ranges are read from the run even when the verdicts are given"
