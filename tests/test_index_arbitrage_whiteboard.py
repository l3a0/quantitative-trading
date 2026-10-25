"""The pins for the whiteboard GIF in the SPY index arbitrage post.

It sketches what one unit of the combination holds: 98 stocks long the same
dollars each, gathered into one green column, beside a red column for SPY's
short at the same scale.

The sketch is not schematic. Its figures come from
:class:`chan.index_arbitrage_whiteboard.OneUnit`, which reads
:func:`chan.index_arbitrage.index_arbitrage` on the committed files, and the
run reads committed vintages, so the tests read the run directly rather than a
frozen copy of its figures. What is pinned is each figure it prints, that it
draws one dot for each stock, that both columns' heights are one affine
function of their dollars, that a made-up set of figures moves the words and
the heights with them, and that a run whose figures would make the words false
is refused. ``tests/test_index_arbitrage.py`` holds the same three totals on
its own derivation, in
``test_the_98_stocks_together_carry_107_198_against_spys_105_560``.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, the GIF's size, frames, loop and timing, that two
draws give the same bytes, and that the committed GIF is a fresh draw, a
comparison that runs only on macOS arm64 with Comic Sans MS, as
``tests/test_usdcad_tests_whiteboard.py`` explains. The check that
``docs/figures`` holds exactly the GIFs the modules draw lives in
``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS` from
here.
"""

from __future__ import annotations

import hashlib
import math
import platform
import re
from dataclasses import replace
from types import SimpleNamespace

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import index_arbitrage as run
from chan import index_arbitrage_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.index_arbitrage_whiteboard import (
    BASE,
    GRID_COLUMNS,
    LONG_X,
    SHORT_X,
    OneUnit,
    gif_name,
    height,
    main,
    make_index_arbitrage_whiteboards,
    scenes,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import GOOD, INK, LOST, MUTED
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
from chan.vintage import VintageUnavailable

POST = REPO_ROOT / "blog" / "index-arbitrage-lessons.md"

#: Every GIF in the order :func:`make_index_arbitrage_whiteboards` writes them.
GIFS = ["index_arbitrage_sketch_one_unit.gif"]

#: What the GIF follows, in "What one unit holds".
UNIT_PARAGRAPH = "So one unit of the combination is long $1.09386 of each stock"

UNIT_LABELS = [
    "98 stocks",
    "$1.09386 each",
    "long\n$107.198",
    "short SPY\n$105.560",
    "$1.638 apart",
    "the rule scales the whole unit\nby minus the z-score",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def unit() -> OneUnit:
    return OneUnit.from_run()


@pytest.fixture(scope="module")
def every(unit):
    return scenes(unit)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, unit):
    return make_index_arbitrage_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"), unit=unit)


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


def _paragraphs() -> list[str]:
    return [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]


def _top(stroke) -> float:
    return float(stroke.y.max())


def _faked_run(monkeypatch, weights) -> None:
    """Hand :meth:`OneUnit.from_run` these weights without reading the files."""
    monkeypatch.setattr(run, "read_sources", lambda data_dir=None: (None, None, None, None))
    monkeypatch.setattr(
        run, "index_arbitrage", lambda stocks, index: SimpleNamespace(weights=np.array(weights))
    )


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_is_one(self, every) -> None:
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
        """The sketch draws no tint today. One that did would need the green
        edge the equity seasonals module's ``_tinted`` draws, since the tint
        alone stands 1.29 to 1 against the board."""
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, unit) -> None:
        again = make_index_arbitrage_whiteboards(out_dir=tmp_path, unit=unit)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        """No chart starts like this GIF, so the prefix check above reads only
        this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert "index_arbitrage.png" in names

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
            ), f"{path.name}: redraw with: uv run python -m chan.index_arbitrage_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys, unit
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(OneUnit, "from_run", classmethod(lambda cls, data_dir=None: unit))
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]

    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        refusal = VintageUnavailable("the committed file's hash does not match its manifest")

        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(run, "read_sources", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)


class TestThePost:
    def test_the_sketch_follows_its_paragraph_with_a_caption(self) -> None:
        """Right after the paragraph on one unit, and before the one on the
        first return."""
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(UNIT_PARAGRAPH)]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", paragraphs[index + 1]
        )
        caption = paragraphs[index + 2]
        assert caption.startswith("*Drawn to scale from the run.") and caption.endswith("*")
        assert "The short SPY column’s top sits $1.638 below the long column’s" in caption
        assert paragraphs[index + 3].startswith("The 5-day standard deviation first exists")

    def test_the_sketch_sits_in_what_one_unit_holds(self) -> None:
        text = POST.read_text(encoding="utf-8")
        at = text.index(f"(../docs/figures/{GIFS[0]})")
        assert text.index("### What one unit holds") < at < text.index("## Lesson 1:")

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_the_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Each label is quoted after the one drawn before it, with a line
        break in a label read as a space."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                quoted = f"“{label.replace(chr(10), ' ')}”"
                found = alt.find(quoted, at)
                assert found >= 0, (scene.slug, label)
                at = found + len(quoted)

    def test_the_alt_text_says_it_is_drawn_to_scale_and_not_slowly(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "drawn to one scale from the run" in alt
        assert "schematic" not in alt
        assert "drawn slowly" not in alt

    def test_the_module_says_it_is_not_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "The sketch is not schematic." in doc


# --- What one unit holds ---------------------------------------------------------


class TestTheUnitSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "What one unit holds"
        assert every[0].labels == UNIT_LABELS

    def test_the_run_gives_the_figures_it_prints(self, unit: OneUnit) -> None:
        """The eigenvector's two weights, and the totals
        ``tests/test_index_arbitrage.py`` pins on its own derivation."""
        assert unit.stocks == 98
        assert unit.each == pytest.approx(1.0938617147080432, abs=1e-12)
        assert unit.long == pytest.approx(107.198448, abs=1e-6)
        assert unit.short == pytest.approx(105.559992, abs=1e-6)
        assert unit.apart == pytest.approx(1.638456, abs=1e-6)
        assert [f"{v:.3f}" for v in (unit.long, unit.short, unit.apart)] == [
            "107.198",
            "105.560",
            "1.638",
        ]

    def test_its_colours(self, every) -> None:
        """Green for the stocks held long, red for SPY held short, black for
        the callout and grey for the baseline and the closing words."""
        scene = every[0]
        for gid, ink in (
            ("stocks", GOOD),
            ("gather", GOOD),
            ("long", GOOD),
            ("short", LOST),
            ("base", MUTED),
            ("callout-long", INK),
            ("callout-short", INK),
        ):
            assert _stroke(scene, gid).color == ink, gid
        for text, ink in zip(UNIT_LABELS, (GOOD, GOOD, GOOD, LOST, INK, MUTED), strict=True):
            assert _label(scene, text).color == ink, text

    def test_it_draws_one_dot_for_each_stock(self, every, unit) -> None:
        dots = _stroke(every[0], "stocks")
        assert dots.dots > 0
        assert dots.points == unit.stocks == 98
        assert len(set(zip(dots.x.tolist(), dots.y.tolist(), strict=True))) == 98
        assert len(set(dots.x.tolist())) == GRID_COLUMNS
        assert len(set(dots.y.tolist())) == math.ceil(98 / GRID_COLUMNS)

    def test_the_column_heights_are_one_affine_function_of_their_dollars(self, every, unit) -> None:
        """Both columns stand on one baseline, and each top is where one
        scale puts its dollars, so nothing in the drawing is magnified."""
        scene = every[0]
        long, short = _stroke(scene, "long"), _stroke(scene, "short")
        assert long.y.min() == pytest.approx(BASE) and short.y.min() == pytest.approx(BASE)
        dollars = np.array([0.0, unit.long, unit.short])
        heights = np.array([BASE, _top(long), _top(short)])
        slope, intercept = np.polyfit(dollars, heights, 1)
        assert heights == pytest.approx(intercept + slope * dollars, abs=1e-9)
        assert slope > 0
        assert (_top(long) - _top(short)) / (_top(long) - BASE) == pytest.approx(
            unit.apart / unit.long
        )
        assert _top(long) == height(unit, unit.long)

    def test_the_columns_stand_side_by_side_at_one_width(self, every) -> None:
        scene = every[0]
        long, short = _stroke(scene, "long"), _stroke(scene, "short")
        assert (long.x.min(), long.x.max()) == LONG_X
        assert (short.x.min(), short.x.max()) == SHORT_X
        assert LONG_X[1] < SHORT_X[0]
        assert LONG_X[1] - LONG_X[0] == pytest.approx(SHORT_X[1] - SHORT_X[0])
        base = _stroke(scene, "base")
        assert set(base.y) == {BASE}
        assert base.x.min() < LONG_X[0] and base.x.max() > SHORT_X[1]

    def test_the_gap_is_too_small_to_draw_so_a_callout_names_it(self, every, unit) -> None:
        """At 1.5 percent of the column's height the gap is about 3 pixels, so
        each callout arrow ends just above one top and the words carry the
        figure."""
        scene = every[0]
        long, short = _stroke(scene, "long"), _stroke(scene, "short")
        pixels = (_top(long) - _top(short)) * HEIGHT / whiteboard.YLIM[1]
        assert 2 < pixels < 4
        assert f"{100 * unit.apart / unit.long:.1f}" == "1.5"
        for gid, column, x in (("callout-long", long, LONG_X), ("callout-short", short, SHORT_X)):
            arrow = _stroke(scene, gid)
            tip = int(np.argmin(arrow.y))
            tip_x, tip_y = arrow.x[tip], arrow.y[tip]
            assert x[0] < tip_x < x[1], gid
            assert 0 < tip_y - _top(column) < 0.2, gid
        label = _label(scene, "$1.638 apart")
        assert label.y > max(_top(long), _top(short))
        assert LONG_X[1] < label.x < SHORT_X[0]

    def test_the_words_long_and_short_sit_inside_their_columns(self, every) -> None:
        """Colour is never the only cue, so each column carries its word."""
        scene = every[0]
        for gid, text in (("long", "long\n$107.198"), ("short", "short SPY\n$105.560")):
            column, label = _stroke(scene, gid), _label(scene, text)
            assert label.names == gid
            assert column.x.min() < label.x < column.x.max(), gid
            assert column.y.min() < label.y < column.y.max(), gid

    def test_the_arrow_gathers_the_dots_into_the_green_column(self, every) -> None:
        scene = every[0]
        dots, arrow = _stroke(scene, "stocks"), _stroke(scene, "gather")
        assert dots.x.max() < arrow.x[0] < arrow.x.max() < LONG_X[0]
        assert dots.y.min() < arrow.y[0] < dots.y.max()

    def test_its_words_and_heights_follow_made_up_figures(self, unit) -> None:
        """Another run's count, weight and SPY dollars print their own figures,
        draw their own dots, and put the taller column at the top."""
        made_up = replace(unit, stocks=50, each=2.0, long=100.0, short=120.0)
        scene = scenes(made_up)[0]
        assert scene.labels == [
            "50 stocks",
            "$2.00000 each",
            "long\n$100.000",
            "short SPY\n$120.000",
            "$-20.000 apart",
            "the rule scales the whole unit\nby minus the z-score",
        ]
        assert _stroke(scene, "stocks").points == 50
        long, short = _top(_stroke(scene, "long")), _top(_stroke(scene, "short"))
        assert short == sketches.TOP
        assert (long - BASE) / (short - BASE) == pytest.approx(100 / 120)

    def test_it_reads_the_files_through_the_runs_own_path(self, monkeypatch) -> None:
        """Through :func:`chan.index_arbitrage.read_sources`, whose scale-break
        guard runs on SPY, rather than a second read path that skips it."""

        def refuse(*args, **kwargs):
            raise RuntimeError("read_sources ran")

        monkeypatch.setattr(run, "read_sources", refuse)
        with pytest.raises(RuntimeError, match="read_sources ran"):
            OneUnit.from_run()

    @pytest.mark.parametrize(
        ("weights", "words"),
        [
            ([1.0, 1.1, -2.0], "one weight on every stock"),
            ([-1.0, -1.0, 2.0], "the stocks long"),
            ([1.0, 1.0, 2.0], "SPY short"),
        ],
        ids=["unequal", "stocks short", "spy long"],
    )
    def test_it_refuses_a_run_that_would_make_its_words_false(
        self, monkeypatch, weights, words
    ) -> None:
        _faked_run(monkeypatch, weights)
        with pytest.raises(ValueError, match=words):
            OneUnit.from_run()

    def test_it_sums_the_stocks_weights(self, monkeypatch) -> None:
        _faked_run(monkeypatch, [0.5, 0.5, 0.5, -1.25])
        assert OneUnit.from_run() == OneUnit(stocks=3, each=0.5, long=1.5, short=1.25)

    def test_its_alt_text_says_what_the_picture_shows(self, every, unit) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert f"a grid of {unit.stocks} green dots appears, one for each stock" in alt
        assert "A green arrow points right from the grid. A grey baseline appears" in alt
        assert "A red column of the same width stands beside it on the same baseline" in alt
        assert "lower than the green column’s by 1.5 percent of the height" in alt
        assert "of the height, about 3 pixels, too little to measure by eye" in alt
        assert "Two black arrows point down at the two tops, then “$1.638 apart” appears" in alt
        assert "grey words at the lower left" in alt
