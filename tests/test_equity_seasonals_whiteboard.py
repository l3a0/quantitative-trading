"""The pins for the four whiteboard GIFs in the equity-seasonals post.

Two sketch the post's opening section and two its section "The two
strategies". The opening's timeline places each source's years to scale, from
Chan's committed files and the registered runs' constants, and its verdicts
sketch draws the two registered runs' figures to scale. Those figures are
pinned here as :data:`PINNED`, the values ``tests/test_equity_seasonals.py``
pins, so every test but one runs without the owner's archive. The one,
:class:`TestTheRunsGiveThePinnedVerdicts`, holds that the runs give them.

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
    JANUARY_END,
    JANUARY_RANGE,
    RANKED,
    TENTH,
    YEAR,
    Spans,
    Verdicts,
    _at,
    _year,
    gif_name,
    main,
    make_equity_seasonals_whiteboards,
    opening_scenes,
    scenes,
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
#: Every GIF in the order :func:`make_equity_seasonals_whiteboards` writes them.
GIFS = OPENING_GIFS + STRATEGY_GIFS

#: The registered runs' figures, as ``tests/test_equity_seasonals.py`` pins
#: them in ``TestThePointInTimePins`` and ``TestTheMonthlyPins``.
PINNED = Verdicts(
    january_low=-0.1047304659686345,
    january_high=0.08787549947820747,
    monthly_mean=-0.0001391960725288475,
    detectable=0.0422031836138127,
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
def every(opening, drawn):
    """All four scenes in the order their GIFs are written."""
    return (*opening, *drawn)


@pytest.fixture(scope="module")
def frames(every):
    return [timeline(scene) for scene in every]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, spans):
    return make_equity_seasonals_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), verdicts=PINNED, spans=spans
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
    def test_there_are_four_named_for_their_scenes(self, gifs) -> None:
        assert [path.name for path in gifs] == GIFS

    def test_each_is_680_by_320_and_loops_forever(self, gifs, frames) -> None:
        for path, steps in zip(gifs, frames, strict=True):
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )

    def test_each_opens_on_its_title_and_holds_its_drawing(self, frames) -> None:
        for steps in frames:
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            assert steps[-1].ms == HOLD_MS

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, spans) -> None:
        again = make_equity_seasonals_whiteboards(out_dir=tmp_path, verdicts=PINNED, spans=spans)
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
        """The timeline right after the paragraph on what Chan's files can
        show, the verdicts right after the list of the two verdicts, the
        January trade right after Example 7.6's paragraph, and the same-month
        trade right after Example 7.7's."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "Running Chan’s code on his own data files",
                "1. **The January effect** averages",
                "**Example 7.6, the January effect.**",
                "**Example 7.7, Heston and Sadka.**",
            ),
            GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name


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

    def test_without_the_archive_it_stops_on_one_line(self, monkeypatch) -> None:
        def absent():
            raise ArchiveUnavailable("no archive here")

        monkeypatch.setattr(seasonals, "run_point_in_time", absent)
        with pytest.raises(SystemExit, match="no archive here"):
            main()


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
            "4.2% a year",
            "measured",
            "too small to detect",
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
        moved = Verdicts(january_low=-0.05, january_high=0.12, monthly_mean=0.001, detectable=0.03)
        scene = opening_scenes(moved, spans)[1]
        assert {"−0.0500", "0.1200", "3.0% a year"} <= set(scene.labels)
        assert _stroke(scene, "bracket").x.max() == pytest.approx(_at(0.12, *JANUARY_RANGE))

    @pytest.mark.parametrize(
        "moved",
        [
            Verdicts(january_low=0.01, january_high=0.08, monthly_mean=0.0, detectable=0.04),
            Verdicts(january_low=-0.1, january_high=-0.01, monthly_mean=0.0, detectable=0.04),
            Verdicts(january_low=-0.1, january_high=0.08, monthly_mean=0.004, detectable=0.04),
            Verdicts(january_low=-0.2, january_high=0.08, monthly_mean=0.0, detectable=0.04),
        ],
        ids=["bracket above zero", "bracket below zero", "mean past X", "off the line"],
    )
    def test_figures_the_words_would_misdescribe_are_refused(self, spans, moved) -> None:
        with pytest.raises(ValueError):
            opening_scenes(moved, spans)


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
            "Heston and Sadka’s sample",
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
        assert _stroke(scene, "book").x[0] == pytest.approx(later.x[0])

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


class TestTheRunsGiveThePinnedVerdicts:
    def test_from_the_runs(self) -> None:
        """The two registered runs on the owner's archive, about twenty
        seconds, or a skip naming what is missing."""
        try:
            runs = seasonals.run_point_in_time(), seasonals.run_monthly_point_in_time()
        except ArchiveUnavailable as absent:
            pytest.skip(str(absent))
        assert Verdicts.from_runs(*runs) == PINNED
