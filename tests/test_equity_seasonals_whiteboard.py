"""The pins for the two whiteboard GIFs in the equity-seasonals post.

The post's section "The two strategies" describes Example 7.6 and Example 7.7,
and each paragraph is followed by a sketch of its strategy. Both sketches are
schematic and read no data, so what is pinned is what a reader takes from
them.

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

import hashlib
import math
import platform
import re

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import equity_seasonals_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.equity_seasonals_whiteboard import (
    JANUARY_END,
    RANKED,
    TENTH,
    YEAR,
    gif_name,
    main,
    make_equity_seasonals_whiteboards,
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
GIFS = ["equity_seasonals_january_trade.gif", "equity_seasonals_same_month_trade.gif"]

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
def frames(drawn):
    return [timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_equity_seasonals_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


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
        assert [gif_name(scene) for scene in drawn] == GIFS

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
    def test_there_are_two_named_for_their_scenes(self, gifs) -> None:
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_equity_seasonals_whiteboards(out_dir=tmp_path)
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
        """The January trade right after Example 7.6's paragraph, and the
        same-month trade right after Example 7.7's."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            ("**Example 7.6, the January effect.**", "**Example 7.7, Heston and Sadka.**"),
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
