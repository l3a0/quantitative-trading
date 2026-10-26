"""The pins for the three whiteboard GIFs in the crude oil reversal and momentum post.

One sketches the rule, the join's first long and first short each between its
two lags, one Lesson 2's grid of half positions, and one what the swings take
from each rule's average day.

1. The rule sketch is schematic: each panel keeps the order of its day's
   three closes and not their spacing, and its spacing across does not
   follow the days between them. Its days come from
   :class:`chan.cl_reversal_momentum_whiteboard.JoinFigures`, which reads the
   2012-05-04 save, and the caption under it in the post gives each day's
   three closes, which the tests read from the run. What is pinned is each
   day and close, that every dot sits at the height its order calls for, that
   each dashed level runs from its lag across today's close, and that each
   arrow points the way the join trades.
2. The grid sketch is not schematic. Its counts come from the same run, and
   what is pinned is each count it prints, that each cell's arrows point the
   way its column and row say, that each sum names what the two halves add
   to, and that a made-up set of counts moves the words with them.
3. The swing sketch is not schematic either. What is pinned is each kept and
   lost figure it prints, read from the run at six decimals, that the two add
   to the average day at that precision, that 252 days of the kept return
   give each rule's APR, that every bar is drawn to one scale, and the
   comparisons its caption draws: lost close to half the square of the
   standard deviation but not equal to it, the rules alone swinging nearly
   three times as much as the join and losing about eight times as much.

The run reads committed vintages, so the tests read it directly rather than a
frozen copy of its figures. ``tests/test_cl_reversal_momentum.py`` pins the
98 longs, the 59 shorts, the 803 rows of disagreement and the first position
on 2008-07-18 on its own derivation, and each rule's average day and standard
deviation. The first long on 2008-07-30, the split of the 803 into 422 and
381, which the sketch does not draw, the closes in the caption, and each
rule's kept and lost returns are pinned only here.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, every
sketch's slower pace, the blue edge on every pale tint, that two draws give
the same bytes, and that each committed GIF is a fresh draw, a comparison
that runs only on macOS arm64 with Comic Sans MS, as
``tests/test_usdcad_tests_whiteboard.py`` explains.
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
from decimal import Decimal

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import cl_reversal_momentum as crude
from chan import cl_reversal_momentum_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.cl_reversal_momentum_whiteboard import (
    ARROW_X,
    BETWEEN,
    COLUMNS,
    HIGH,
    LONG_PANEL,
    LOW,
    MOMENTUM_X,
    REVERSAL_X,
    ROWS,
    SHORT_PANEL,
    SWING_FOOT,
    SWING_NAMES_Y,
    SWING_PAST,
    SWING_TOP,
    SWING_WIDTH,
    SWING_XS,
    TODAY_X,
    Agreement,
    JoinFigures,
    Swing,
    gif_name,
    main,
    make_cl_reversal_momentum_whiteboards,
    price,
    scenes,
    six,
    sketch_timeline,
    swing_scale,
)
from chan.palette import GOOD, INKS, LOST, TINT
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import INK, MUTED
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

POST = REPO_ROOT / "blog" / "crude-oil-reversal-momentum-lessons.md"

#: Every GIF in the order :func:`make_cl_reversal_momentum_whiteboards` writes them.
GIFS = [
    "cl_reversal_momentum_sketch_dip_and_bounce.gif",
    "cl_reversal_momentum_sketch_half_of_each.gif",
    "cl_reversal_momentum_sketch_swing_cost.gif",
]

#: What each GIF follows: the paragraph on the join's rule, keyed on its last
#: sentence, Lesson 2's paragraph on how often the rules disagree, and its
#: paragraph on why compounding charges for swings.
RULE_PARAGRAPH_END = "It shorts on a bounce inside a fall, and holds nothing on any other day."
GRID_PARAGRAPH = "The two rules mostly disagree."
SWING_PARAGRAPH = "Smaller swings give the join the highest APR of the three"

RULE_LABELS = [
    "40 days ago",
    "30 days ago",
    "today",
    "the join’s first long, 2008-07-30",
    "below the 30-day lag: reversal buys",
    "above the 40-day lag: momentum buys",
    "both buy: long",
    "40 days ago",
    "30 days ago",
    "today",
    "the join’s first short, 2008-07-18",
    "above the 30-day lag: reversal shorts",
    "below the 40-day lag: momentum shorts",
    "both short: short",
    "any other day: flat",
]

GRID_LABELS = [
    "reversal: long",
    "reversal: short",
    "momentum:\nlong",
    "momentum:\nshort",
    "½",
    "½",
    "½ + ½ = long",
    "98 days",
    "½",
    "½",
    "−½ + ½ = flat",
    "½",
    "½",
    "½ − ½ = flat",
    "½",
    "½",
    "−½ − ½ = short",
    "59 days",
    "803 days:\nflat",
    "on these 960 days, the join holds the average of the two rules’ positions",
]

SWING_LABELS = [
    "the join",
    "kept 0.000441",
    "lost to swings\n0.000022",
    "momentum alone",
    "kept 0.000343",
    "lost to swings\n0.000176",
    "reversal alone",
    "kept 0.000262",
    "lost to swings\n0.000178",
    "the join keeps the most of its average day",
]

#: Each cell by its reversal and momentum positions, as the module names it.
CELLS = {
    "long-long": (1, 1),
    "short-long": (-1, 1),
    "long-short": (1, -1),
    "short-short": (-1, -1),
}

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def figures() -> JoinFigures:
    return JoinFigures.from_run()


@pytest.fixture(scope="module")
def every(figures):
    return scenes(figures)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory):
    return make_cl_reversal_momentum_whiteboards(out_dir=tmp_path_factory.mktemp("sketches"))


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


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


def _caption(index: int) -> str:
    paragraphs = _paragraphs()
    (at,) = [k for k, p in enumerate(paragraphs) if f"(../docs/figures/{GIFS[index]})" in p]
    return paragraphs[at + 1]


def _end(arrow) -> int:
    """The index where an arrow's shaft ends, the tip its head is drawn around.

    :func:`chan.usdcad_tests_whiteboard._arrow` draws the shaft, then turns
    back along one arm of the head, so the tip is the first point where the
    pen reverses.
    """
    xs, ys = arrow.x, arrow.y
    for k in range(1, len(xs) - 1):
        ahead = (xs[k + 1] - xs[k]) * (xs[k] - xs[k - 1]) + (ys[k + 1] - ys[k]) * (
            ys[k] - ys[k - 1]
        )
        if ahead < 0:
            return k
    raise AssertionError("no arrowhead")


def _shaft(arrow) -> tuple[float, float, float, float]:
    """An arrow's tail and tip, as x and y each."""
    tip = _end(arrow)
    return float(arrow.x[0]), float(arrow.y[0]), float(arrow.x[tip]), float(arrow.y[tip])


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_three_in_the_order_the_post_reads_them(self, every) -> None:
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

    def test_every_pale_tint_has_a_blue_edge(self, every) -> None:
        """The tint alone stands 1.31 to 1 against the white board, under WCAG
        2.1's 3 to 1 for a graphical object, so every tinted region gets a
        blue edge, GOOD at 4.77 to 1, that spans it, as the equity seasonals
        module's ``_tinted`` draws it. The swing sketch's kept parts are the
        only tints."""
        assert sketches.TINT_EDGE >= 1.0
        tints = [fill for scene in every for fill in scene.fills if fill.color == TINT]
        assert len(tints) == 3
        for scene in every:
            for fill in scene.fills:
                if fill.color != TINT:
                    continue
                edges = [
                    s
                    for s in scene.strokes
                    if s.color == GOOD
                    and s.width == sketches.TINT_EDGE
                    and s.x.min() <= fill.x0 + 1e-9
                    and s.x.max() >= fill.x1 - 1e-9
                    and s.y.min() == pytest.approx(fill.y0)
                    and s.y.max() == pytest.approx(fill.y1)
                ]
                assert edges, (scene.slug, fill.gid)


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
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("dip_and_bounce", "half_of_each", "swing_cost")
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

    def test_each_draws_in_the_colour_blind_safe_inks(self, gifs) -> None:
        """Every frame maps onto the palette of :data:`chan.palette.INKS`, so
        a GIF drawn in the shared inks fails here on any machine, not only
        where the byte comparison below runs."""
        for path in gifs:
            with Image.open(path) as image:
                assert image.getpalette() == whiteboard.palette(INKS).getpalette(), path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path) -> None:
        again = make_cl_reversal_momentum_whiteboards(out_dir=tmp_path)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        """No chart starts like these, so the prefix check above reads only
        this module's GIFs."""
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert "cl_reversal_momentum.png" in names

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
            ), f"{path.name}: redraw with: uv run python -m chan.cl_reversal_momentum_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


# --- The figures, read from the run ----------------------------------------------


class TestTheFigures:
    def test_the_first_long_and_the_first_short(self, figures: JoinFigures) -> None:
        """The days and closes the rule sketch and its caption give, read from
        the 2012-05-04 save."""
        long, short = figures.first_long, figures.first_short
        assert (long.day, short.day) == ("2008-07-30", "2008-07-18")
        assert [price(v) for v in (long.close, long.reversal_lag, long.momentum_lag)] == [
            "174.35",
            "182.73",
            "173.07",
        ]
        assert [price(v) for v in (short.close, short.reversal_lag, short.momentum_lag)] == [
            "177.05",
            "176.55",
            "181.93",
        ]
        assert (long.position, short.position) == (1, -1)

    def test_the_first_short_is_the_joins_first_position(self) -> None:
        _, cl = crude.read_cl()
        positions = crude.combination_positions(cl)
        first = int(np.argmax(positions != 0))
        assert (str(cl.index[first].date()), positions[first]) == ("2008-07-18", -1.0)

    def test_the_counts(self, figures: JoinFigures) -> None:
        """98 both long, 59 both short, and 803 split 422 and 381, which the
        sketch draws only as their sum because the post gives only that."""
        agree = figures.agreement
        assert (agree.long_long, agree.long_short, agree.short_long, agree.short_short) == (
            98,
            422,
            381,
            59,
        )
        assert (agree.rows, agree.disagree) == (960, 803)
        assert agree.long_long + agree.short_short == 157

    def test_the_counts_match_the_replications_positions(self, figures: JoinFigures) -> None:
        """The join's longs and shorts over the whole window are the two
        agreeing cells, since the join trades nowhere else."""
        _, cl = crude.read_cl()
        positions = crude.combination_positions(cl)
        agree = figures.agreement
        assert int((positions > 0).sum()) == agree.long_long
        assert int((positions < 0).sum()) == agree.short_short
        assert len(positions) - agree.long_long - agree.short_short == 843

    def test_it_reads_the_save_through_the_scale_break_guard(self, monkeypatch) -> None:
        """Not a second read path that skips the guard ``read_cl`` runs."""

        def refuse(*args, **kwargs):
            raise RuntimeError("guard ran")

        monkeypatch.setattr(crude, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(RuntimeError, match="guard ran"):
            JoinFigures.from_run()

    def test_it_refuses_a_rule_flat_where_both_lags_exist(self, monkeypatch) -> None:
        """The grid has no row or column for a flat rule."""
        real = crude.momentum_positions

        def one_flat(closes, **kwargs):
            held = real(closes, **kwargs)
            held[crude.MOMENTUM_LOOKBACK + 5] = 0.0
            return held

        monkeypatch.setattr(crude, "momentum_positions", one_flat)
        with pytest.raises(ValueError, match="a rule is flat on a row where both lags exist"):
            JoinFigures.from_run()

    def test_it_refuses_a_reversal_rule_flat_where_both_lags_exist(self, monkeypatch) -> None:
        real = crude.reversal_positions

        def one_flat(closes, **kwargs):
            held = real(closes, **kwargs)
            held[crude.MOMENTUM_LOOKBACK + 5] = 0.0
            return held

        monkeypatch.setattr(crude, "reversal_positions", one_flat)
        with pytest.raises(ValueError, match="a rule is flat on a row where both lags exist"):
            JoinFigures.from_run()

    def test_it_refuses_a_join_that_is_not_half_of_each_rule(self, monkeypatch) -> None:
        real = crude.combination_positions

        def one_off(closes, **kwargs):
            held = real(closes, **kwargs)
            held[crude.MOMENTUM_LOOKBACK + 5] = 1.0 - held[crude.MOMENTUM_LOOKBACK + 5]
            return held

        monkeypatch.setattr(crude, "combination_positions", one_off)
        with pytest.raises(ValueError, match="not half of each rule"):
            JoinFigures.from_run()

    def test_each_rules_average_kept_and_lost_day(self, figures: JoinFigures) -> None:
        """The swing sketch's figures at the six decimals it prints, in the
        post's table order, with kept and lost adding to the average day at
        that precision."""
        assert [swing.rule for swing in figures.swings] == [
            "the join",
            "momentum alone",
            "reversal alone",
        ]
        assert [(six(s.average), six(s.kept), six(s.lost)) for s in figures.swings] == [
            ("0.000463", "0.000441", "0.000022"),
            ("0.000519", "0.000343", "0.000176"),
            ("0.000440", "0.000262", "0.000178"),
        ]
        for swing in figures.swings:
            assert Decimal(six(swing.kept)) + Decimal(six(swing.lost)) == Decimal(
                six(swing.average)
            ), swing.rule

    def test_the_swings_are_read_from_each_rules_daily_returns(self, figures) -> None:
        """The average day is the mean over all 1,000 rows, flat ones
        included, and kept is the one return that compounds to the same
        final capital."""
        _, cl = crude.read_cl()
        rules = crude.four_rules(cl)
        for swing, traded in zip(
            figures.swings, (rules.combination, rules.momentum, rules.reversal), strict=True
        ):
            assert len(traded.daily) == 1000
            assert swing.average == pytest.approx(traded.daily.mean(), rel=1e-12)
            final = np.prod(1 + traded.daily)
            assert (1 + swing.kept) ** len(traded.daily) == pytest.approx(final, rel=1e-12)

    def test_252_days_of_the_kept_return_give_each_rules_apr(self, figures) -> None:
        _, cl = crude.read_cl()
        rules = crude.four_rules(cl)
        for swing, traded, printed in zip(
            figures.swings,
            (rules.combination, rules.momentum, rules.reversal),
            ("0.117600", "0.090228", "0.068326"),
            strict=True,
        ):
            assert (1 + swing.kept) ** 252 - 1 == pytest.approx(traded.apr, rel=1e-12)
            assert f"{(1 + swing.kept) ** 252 - 1:.6f}" == printed, swing.rule

    def test_lost_comes_close_to_half_the_variance_without_equalling_it(self, figures) -> None:
        """Within 1e-6 of σ²/2 on each rule, with n − 1 in the variance as
        MATLAB's ``std`` takes it, and more than 1e-8 away, so the caption
        says "comes close to" rather than "equals"."""
        _, cl = crude.read_cl()
        rules = crude.four_rules(cl)
        for swing, traded in zip(
            figures.swings, (rules.combination, rules.momentum, rules.reversal), strict=True
        ):
            half = traded.daily.std(ddof=1) ** 2 / 2
            assert 1e-8 < abs(swing.lost - half) < 1e-6, swing.rule

    def test_the_rules_alone_swing_nearly_three_times_and_lose_about_eight(self, figures) -> None:
        """Two of the caption's three comparisons: each rule alone's standard
        deviation over the join's, about 2.80 and 2.82, and each one's lost
        return over the join's, about 7.92 and 8.01."""
        _, cl = crude.read_cl()
        rules = crude.four_rules(cl)
        join = rules.combination.daily.std(ddof=1)
        for traded in (rules.momentum, rules.reversal):
            assert 2.5 < traded.daily.std(ddof=1) / join < 3
        first, *alone = figures.swings
        for swing in alone:
            assert 7.5 < swing.lost / first.lost < 8.5, swing.rule

    def test_a_day_the_join_holds_nothing_is_refused(self, figures: JoinFigures) -> None:
        flat = replace(figures.first_long, close=figures.first_long.reversal_lag + 1)
        assert flat.position == 0
        with pytest.raises(ValueError, match="the join holds nothing"):
            scenes(replace(figures, first_long=flat))


# --- The rule and the file: a dip inside a rise, a bounce inside a fall -----------


class TestTheRuleSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "A dip inside a rise, a bounce inside a fall"
        assert every[0].labels == RULE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        for side, ink in (("long", GOOD), ("short", LOST)):
            for gid, colour in (
                (f"{side}-path", INK),
                (f"{side}-momentum-lag", INK),
                (f"{side}-reversal-lag", INK),
                (f"{side}-today", INK),
                (f"{side}-reversal-level", MUTED),
                (f"{side}-momentum-level", MUTED),
                (f"{side}-position", ink),
            ):
                assert _stroke(scene, gid).color == colour, gid
            for gid in (f"{side}-reversal-level", f"{side}-momentum-level", f"{side}-today"):
                for label in _labels_of(scene, gid):
                    assert label.color == INK, label.text
            (verdict,) = _labels_of(scene, f"{side}-position")
            assert verdict.color == ink
        assert _stroke(scene, "flat").color == MUTED
        assert [label.color for label in _labels_of(scene, "flat")] == [MUTED]

    @pytest.mark.parametrize("side", ["long", "short"])
    def test_the_closes_sit_in_time_order_and_today_between_its_lags(
        self, every, figures, side
    ) -> None:
        """40 days ago, then 30, then today across the panel, and each dot at
        the height the order of its close calls for: today between, the
        higher lag high and the lower low."""
        scene = every[0]
        day = figures.first_long if side == "long" else figures.first_short
        x0 = LONG_PANEL if side == "long" else SHORT_PANEL
        mom, rev, today = (
            _stroke(scene, f"{side}-{gid}") for gid in ("momentum-lag", "reversal-lag", "today")
        )
        assert (mom.x[0], rev.x[0], today.x[0]) == (
            x0 + MOMENTUM_X,
            x0 + REVERSAL_X,
            x0 + TODAY_X,
        )
        assert mom.x[0] < rev.x[0] < today.x[0]
        heights = {day.momentum_lag: mom.y[0], day.reversal_lag: rev.y[0], day.close: today.y[0]}
        ordered = [heights[v] for v in sorted(heights)]
        assert ordered == [LOW, BETWEEN, HIGH]
        assert today.y[0] == BETWEEN
        path = _stroke(scene, f"{side}-path")
        assert (path.x[0], path.y[0]) == (mom.x[0], mom.y[0])
        assert (path.x[-1], path.y[-1]) == (today.x[0], today.y[0])
        assert (rev.x[0], rev.y[0]) in set(zip(path.x, path.y, strict=True))

    def test_the_long_dips_inside_a_rise_and_the_short_bounces_inside_a_fall(self, every) -> None:
        scene = every[0]
        assert _stroke(scene, "long-momentum-lag").y[0] == LOW
        assert _stroke(scene, "long-reversal-lag").y[0] == HIGH
        assert _stroke(scene, "short-momentum-lag").y[0] == HIGH
        assert _stroke(scene, "short-reversal-lag").y[0] == LOW

    @pytest.mark.parametrize("side", ["long", "short"])
    def test_each_dashed_level_runs_from_its_lag_across_today(self, every, side) -> None:
        scene = every[0]
        today = _stroke(scene, f"{side}-today")
        for lag in ("reversal", "momentum"):
            level, dot = _stroke(scene, f"{side}-{lag}-level"), _stroke(scene, f"{side}-{lag}-lag")
            assert level.dashed, lag
            assert set(level.y) == {dot.y[0]}, lag
            assert level.x.min() == dot.x[0] and level.x.max() > today.x[0], lag

    @pytest.mark.parametrize(("side", "up"), [("long", True), ("short", False)])
    def test_each_arrow_stands_beside_today_and_points_the_way_the_join_trades(
        self, every, side, up
    ) -> None:
        """Colour is never the only cue: the long's arrow points up and the
        short's down, and the verdicts say "long" and "short"."""
        scene = every[0]
        arrow = _stroke(scene, f"{side}-position")
        x0 = LONG_PANEL if side == "long" else SHORT_PANEL
        tail_x, tail_y, tip_x, tip_y = _shaft(arrow)
        assert tail_x == tip_x == x0 + ARROW_X
        assert (tip_y > tail_y) == up
        assert min(tail_y, tip_y) < BETWEEN < max(tail_y, tip_y)
        assert _stroke(scene, f"{side}-today").x[0] < tip_x
        (verdict,) = _labels_of(scene, f"{side}-position")
        assert verdict.text.endswith(f": {side}")

    @pytest.mark.parametrize("side", ["long", "short"])
    def test_each_panels_words_sit_under_their_own_panel(self, every, side) -> None:
        """Every label that names one of a panel's strokes sits across that
        panel's half of the board, the names of the closes on one baseline
        under the drawing, and the rule lines in order beneath them, the
        verdict last."""
        scene = every[0]
        x0 = LONG_PANEL if side == "long" else SHORT_PANEL
        mine = [
            label
            for label in scene.steps
            if isinstance(label, Label) and label.names.startswith(f"{side}-")
        ]
        assert len(mine) == 7
        for label in mine:
            assert x0 <= label.x <= x0 + 5, label.text
        rules = [
            _labels_of(scene, f"{side}-{gid}")[0]
            for gid in ("reversal-level", "momentum-level", "position")
        ]
        assert [label.y for label in rules] == sorted((label.y for label in rules), reverse=True)
        dots = [_stroke(scene, f"{side}-{g}") for g in ("momentum-lag", "reversal-lag", "today")]
        names = [label for label in mine if label.text.endswith(("days ago", "today"))]
        assert [label.x for label in names] == [dot.x[0] for dot in dots]
        assert {label.y for label in names} == {sketches.NAMES_Y}
        assert rules[0].y < sketches.NAMES_Y < min(dot.y[0] for dot in dots)

    def test_the_flat_mark_is_level(self, every) -> None:
        """A flat line beside "any other day: flat", the sign for no position."""
        flat = _stroke(every[0], "flat")
        assert len(set(flat.y)) == 1 and flat.x.max() > flat.x.min()
        (label,) = _labels_of(every[0], "flat")
        assert label.y == flat.y[0] and label.x > flat.x.max()

    def test_the_heading_follows_the_day(self, figures) -> None:
        """A made-up first long on another day prints that day."""
        moved = replace(figures, first_long=replace(figures.first_long, day="2011-01-03"))
        assert "the join’s first long, 2011-01-03" in scenes(moved)[0].labels

    def test_its_caption_names_the_days_the_save_and_each_close(self, figures) -> None:
        caption = " ".join(_caption(0).split())
        assert caption.startswith("*") and caption.endswith("*")
        long, short = figures.first_long, figures.first_short
        assert (
            f"The left panel is the join’s first long, on {long.day}, and the right its "
            f"first short, on {short.day}, which is also its first position." in caption
        )
        assert "Both days come from the 2012-05-04 save." in caption
        assert (
            "The sketch is schematic. Its heights keep only the order of each day’s three "
            "closes, and its spacing across does not follow the days between them." in caption
        )
        assert (
            f"On {long.day} the close of {price(long.close)} sat below its 30-day lag of "
            f"{price(long.reversal_lag)} and above its 40-day lag of {price(long.momentum_lag)}."
            in caption
        )
        assert (
            f"On {short.day} the close of {price(short.close)} sat above its 30-day lag of "
            f"{price(short.reversal_lag)} and below its 40-day lag of {price(short.momentum_lag)}."
            in caption
        )

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "It is schematic: each panel keeps the order" in alt
        assert "A black line rises from a low black dot to a high one and falls back" in alt
        assert "Its black line falls from a high dot to a low one and rises a little" in alt
        assert "A blue arrow beside today’s dot points up" in alt
        assert "A vermilion arrow beside today’s dot points down" in alt
        assert "a short grey flat line at the bottom" in alt
        assert "The left panel comes first." in alt
        assert "A grey dashed line runs from the high dot across past today’s dot" in alt
        assert "A grey dashed line runs from the low dot across past today’s dot" in alt
        assert "rises a little to a dot between them" in alt
        assert "A grey dashed line from the low dot comes with “above the 30-day lag" in alt
        assert "and one from the high dot with “below the 40-day lag" in alt


# --- Lesson 2: half of each rule is the join -------------------------------------


class TestTheGridSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Half of each rule is the join"
        assert every[1].labels == GRID_LABELS

    def test_it_never_splits_the_803(self, every, figures) -> None:
        """The post gives only the sum of the two disagreeing cells."""
        agree = figures.agreement
        words = " ".join(every[1].labels)
        assert str(agree.long_short) not in words and str(agree.short_long) not in words

    @pytest.mark.parametrize("cell", list(CELLS))
    def test_each_cells_arrows_point_the_way_its_column_and_row_say(self, every, cell) -> None:
        """Reversal's arrow on the left and momentum's on the right, each up
        and blue for a long and down and vermilion for a short, each with a "½"
        beside it in its own colour."""
        scene = every[1]
        rev, mom = CELLS[cell]
        column = COLUMNS[0] if rev > 0 else COLUMNS[1]
        row = ROWS[0] if mom > 0 else ROWS[1]
        xs = []
        for rule, sign in (("reversal", rev), ("momentum", mom)):
            arrow = _stroke(scene, f"{cell}-{rule}")
            tail_x, tail_y, tip_x, tip_y = _shaft(arrow)
            assert tail_x == tip_x, rule
            assert (tip_y > tail_y) == (sign > 0), rule
            assert arrow.color == (GOOD if sign > 0 else LOST), rule
            assert column[0] < tip_x < column[1] and row[0] < min(tail_y, tip_y), rule
            assert max(tail_y, tip_y) < row[1], rule
            (half, *_rest) = _labels_of(scene, f"{cell}-{rule}")
            assert (half.text, half.color) == ("½", arrow.color), rule
            assert half.x == pytest.approx(tip_x + sketches.HALF_PAST), rule
            xs.append(tip_x)
        assert xs[0] < xs[1]

    @pytest.mark.parametrize(
        ("cell", "text", "ink"),
        [
            ("long-long", "½ + ½ = long", GOOD),
            ("short-long", "−½ + ½ = flat", MUTED),
            ("long-short", "½ − ½ = flat", MUTED),
            ("short-short", "−½ − ½ = short", LOST),
        ],
    )
    def test_each_sum_adds_its_halves_and_names_the_joins_position(
        self, every, cell, text, ink
    ) -> None:
        """The terms carry the arrows' signs in the arrows' order, and the
        word is the join's position, so the sum reads without colour."""
        scene = every[1]
        rev, mom = CELLS[cell]
        found = [label for label in _labels_of(scene, f"{cell}-momentum") if "=" in label.text]
        assert [(label.text, label.color) for label in found] == [(text, ink)]
        terms = text.split(" = ")[0].replace("+ ", "+").replace("− ", "−").split()
        assert [-1 if term.startswith("−") else 1 for term in terms] == [rev, mom]
        total = (rev + mom) / 2
        assert text.endswith("long" if total > 0 else "short" if total < 0 else "flat")

    def test_the_counts_sit_in_the_cells_where_the_rules_agree(self, every, figures) -> None:
        scene = every[1]
        agree = figures.agreement
        for cell, count, ink in (
            ("long-long", agree.long_long, GOOD),
            ("short-short", agree.short_short, LOST),
        ):
            found = [
                label for label in _labels_of(scene, f"{cell}-momentum") if "days" in label.text
            ]
            assert [(label.text, label.color) for label in found] == [(f"{count} days", ink)]
        for cell in ("short-long", "long-short"):
            assert not [
                label for label in _labels_of(scene, f"{cell}-momentum") if "days" in label.text
            ]

    def test_one_grey_note_points_at_both_flat_cells(self, every, figures) -> None:
        """From the gap between the columns, one arrow ends at the top right
        cell and one at the bottom left, the two where the rules disagree."""
        scene = every[1]
        (note,) = _labels_of(scene, "to-long-short")
        assert (note.text, note.color) == (f"{figures.agreement.disagree} days:\nflat", MUTED)
        assert COLUMNS[0][1] < note.x < COLUMNS[1][0]
        for gid, column, row in (
            ("to-short-long", COLUMNS[1], ROWS[0]),
            ("to-long-short", COLUMNS[0], ROWS[1]),
        ):
            arrow = _stroke(scene, gid)
            assert arrow.color == MUTED, gid
            _, _, end_x, end_y = _shaft(arrow)
            assert row[0] < end_y < row[1], gid
            assert min(abs(end_x - column[0]), abs(end_x - column[1])) < 0.15, gid
            assert COLUMNS[0][1] <= arrow.x[0] <= COLUMNS[1][0], gid

    def test_each_header_sits_over_its_column_or_beside_its_row(self, every) -> None:
        scene = every[1]
        labels = {label.text: label for label in scene.steps if isinstance(label, Label)}
        for word, (x0, x1) in zip(("long", "short"), COLUMNS, strict=True):
            header = labels[f"reversal: {word}"]
            assert x0 < header.x < x1 and header.y > ROWS[0][1], word
        for word, (y0, y1) in zip(("long", "short"), ROWS, strict=True):
            header = labels[f"momentum:\n{word}"]
            assert y0 < header.y < y1 and header.x < COLUMNS[0][0], word

    def test_each_count_sits_inside_its_own_cell_right_of_its_arrows(self, every) -> None:
        scene = every[1]
        for cell, column, row in (
            ("long-long", COLUMNS[0], ROWS[0]),
            ("short-short", COLUMNS[1], ROWS[1]),
        ):
            (count,) = [
                label for label in _labels_of(scene, f"{cell}-momentum") if "days" in label.text
            ]
            assert column[0] < count.x < column[1] and row[0] < count.y < row[1], cell
            for rule in ("reversal", "momentum"):
                assert count.x > _shaft(_stroke(scene, f"{cell}-{rule}"))[2], (cell, rule)

    def test_each_sum_sits_inside_its_own_cell_under_its_arrows(self, every) -> None:
        scene = every[1]
        for cell, (rev, mom) in CELLS.items():
            column = COLUMNS[0] if rev > 0 else COLUMNS[1]
            row = ROWS[0] if mom > 0 else ROWS[1]
            (total,) = [
                label for label in _labels_of(scene, f"{cell}-momentum") if "=" in label.text
            ]
            assert column[0] < total.x < column[1] and row[0] < total.y < row[1], cell
            assert total.y < _stroke(scene, f"{cell}-reversal").y.min(), cell

    def test_the_closing_line_counts_every_row_with_both_lags(self, every, figures) -> None:
        last = every[1].steps[-1]
        assert isinstance(last, Label)
        assert last.text == (
            f"on these {figures.agreement.rows} days, the join holds the average of the two "
            "rules’ positions"
        )

    def test_its_words_follow_made_up_counts(self, figures) -> None:
        made_up = replace(
            figures, agreement=Agreement(long_long=10, long_short=20, short_long=30, short_short=7)
        )
        labels = scenes(made_up)[1].labels
        assert "10 days" in labels and "7 days" in labels
        assert "50 days:\nflat" in labels
        assert labels[-1].startswith("on these 67 days,")
        assert "98 days" not in labels

    def test_its_caption(self) -> None:
        caption = " ".join(_caption(1).split())
        assert caption == (
            "*Counted over the 960 rows of the 2012-05-04 save where both lags exist. In each "
            "box the left arrow is half of reversal’s position and the right arrow half of "
            "momentum’s.*"
        )

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        assert "Its counts come from the run." in alt
        assert "reversal’s on the left and momentum’s on the right" in alt
        assert "blue and pointing up for a long, vermilion and pointing down for a short" in alt
        assert (
            "one grey arrow points up to the top right box and one down to the bottom left box"
            in alt
        )
        for sentence in (
            "Top left, two blue up arrows, labelled “½” and “½”, sum to “½ + ½ = long”, in blue",
            "Top right, a vermilion down arrow labelled “½” and a blue up arrow labelled “½” "
            "sum to “−½ + ½ = flat”, in grey",
            "Bottom left, a blue up arrow labelled “½” and a vermilion down arrow labelled “½” "
            "sum to “½ − ½ = flat”, in grey",
            "Bottom right, two vermilion down arrows, labelled “½” and “½”, sum to "
            "“−½ − ½ = short”, in vermilion",
        ):
            assert sentence in alt, sentence


# --- Lesson 2: what the swings take from an average day ---------------------------


def _swing_parts(scene, swing):
    """A bar's kept tint, its lost fill, and the id both start with."""
    gid = swing.rule.replace(" ", "-")
    fills = {fill.gid: fill for fill in scene.fills}
    return fills[f"{gid}-kept"], fills[f"{gid}-lost"], gid


def _part_words(scene, gid):
    """The labels naming a bar's part, leaving out the closing line, which
    names the last part drawn."""
    return [label for label in _labels_of(scene, gid) if label is not scene.steps[-1]]


#: Made-up figures where momentum alone keeps the largest share of its
#: average day, while reversal alone has the tallest average day and keeps the
#: most in absolute terms, and the join loses the least. So the closing line is
#: seen to follow the share, not the size of what is kept or lost, and the
#: scale is seen to follow the tallest average day.
OTHER_SWINGS = (
    Swing("the join", 0.0001, 0.00002),
    Swing("momentum alone", 0.0005, 0.00035),
    Swing("reversal alone", 0.0008, 0.0004),
)


class TestTheSwingSketch:
    def test_its_words(self, every) -> None:
        assert every[2].title == "What the swings take from an average day"
        assert every[2].labels == SWING_LABELS

    def test_its_colours(self, every, figures) -> None:
        """Kept is a pale tint with a blue edge and blue words, lost is
        solid vermilion with vermilion words, and the words "kept" and "lost" say which
        is which without the colour."""
        scene = every[2]
        for swing in figures.swings:
            kept, lost, gid = _swing_parts(scene, swing)
            assert (kept.color, lost.color) == (TINT, LOST), gid
            assert _stroke(scene, f"{gid}-kept-edge").color == GOOD
            name, kept_words = _labels_of(scene, kept.gid)
            (lost_words,) = _part_words(scene, lost.gid)
            assert (name.text, name.color) == (swing.rule, INK)
            assert (kept_words.text.split()[0], kept_words.color) == ("kept", GOOD)
            assert (lost_words.text.split("\n")[0], lost_words.color) == ("lost to swings", LOST)
        assert scene.steps[-1].color == INK

    def test_every_bar_is_drawn_to_one_scale(self, every, figures) -> None:
        """Each part's top sits at an affine function of its value, the same
        one for every bar, with the foot at zero and the tallest average day
        at the top."""
        scene = every[2]
        scale = swing_scale(figures.swings)
        tallest = max(swing.average for swing in figures.swings)
        assert SWING_FOOT + tallest * scale == pytest.approx(SWING_TOP)
        for swing in figures.swings:
            kept, lost, gid = _swing_parts(scene, swing)
            assert kept.y0 == SWING_FOOT, gid
            assert kept.y1 == pytest.approx(SWING_FOOT + swing.kept * scale), gid
            assert lost.y0 == kept.y1, gid
            assert lost.y1 == pytest.approx(SWING_FOOT + swing.average * scale), gid
            assert (lost.y1 - lost.y0) / (kept.y1 - kept.y0) == pytest.approx(
                swing.lost / swing.kept
            ), gid

    def test_the_joins_lost_part_is_thin_but_shows(self, every, figures) -> None:
        """About 8 pixels tall, which is why it is solid rather than hatched."""
        _, lost, _ = _swing_parts(every[2], figures.swings[0])
        pixels = (lost.y1 - lost.y0) * HEIGHT / 4.7
        assert 5 < pixels < 12

    def test_the_bars_stand_in_the_tables_order(self, every, figures) -> None:
        scene = every[2]
        for swing, x0 in zip(figures.swings, SWING_XS, strict=True):
            kept, lost, gid = _swing_parts(scene, swing)
            assert (kept.x0, kept.x1) == (x0, x0 + SWING_WIDTH), gid
            assert (lost.x0, lost.x1) == (kept.x0, kept.x1), gid
        assert list(SWING_XS) == sorted(SWING_XS)

    def test_each_part_has_its_words_beside_it(self, every, figures) -> None:
        """Each part's words start just right of its bar at the height of
        that part's middle, and each rule's name sits centred under its bar."""
        scene = every[2]
        for swing in figures.swings:
            kept, lost, _ = _swing_parts(scene, swing)
            name, kept_words = _labels_of(scene, kept.gid)
            (lost_words,) = _part_words(scene, lost.gid)
            assert (name.x, name.y) == ((kept.x0 + kept.x1) / 2, SWING_NAMES_Y)
            assert name.ha == "center" and name.y < SWING_FOOT
            for words, part in ((kept_words, kept), (lost_words, lost)):
                assert words.x == pytest.approx(part.x1 + SWING_PAST), words.text
                assert words.y == pytest.approx((part.y0 + part.y1) / 2), words.text

    def test_the_closing_line_names_the_rule_that_keeps_the_largest_share(
        self, every, figures
    ) -> None:
        keeper = max(figures.swings, key=lambda swing: swing.kept / swing.average)
        assert keeper.rule == "the join"
        assert keeper is max(figures.swings, key=lambda swing: swing.kept)
        last = every[2].steps[-1]
        assert isinstance(last, Label)
        assert last.text == f"{keeper.rule} keeps the most of its average day"

    def test_its_words_and_scale_follow_made_up_figures(self, figures) -> None:
        scene = scenes(replace(figures, swings=OTHER_SWINGS))[2]
        assert scene.labels[-1] == "momentum alone keeps the most of its average day"
        assert "kept 0.000400" in scene.labels
        assert "lost to swings\n0.000150" in scene.labels
        assert "kept 0.000441" not in scene.labels
        tallest = next(f for f in scene.fills if f.gid == "reversal-alone-lost")
        assert tallest.y1 == pytest.approx(SWING_TOP)

    def test_a_rule_that_keeps_nothing_is_refused(self, figures) -> None:
        """Kept at zero or below has no lower part to draw, on any of the three bars."""
        for kept in (0.0, -0.0002):
            for at, swing in enumerate(figures.swings):
                losing = list(figures.swings)
                losing[at] = Swing(swing.rule, 0.0001, kept)
                with pytest.raises(ValueError, match=f"{swing.rule} keeps nothing"):
                    scenes(replace(figures, swings=tuple(losing)))

    def test_its_caption(self) -> None:
        """The rows, the save and the 252 days it names, read where they
        come from. The caption's three comparisons are held on the run in
        :class:`TestTheFigures`."""
        _, cl = crude.read_cl()
        assert (len(cl), str(cl.index[-1].date()), crude.TRADING_DAYS) == (1000, "2012-05-04", 252)
        caption = " ".join(_caption(2).split())
        assert caption == (
            "*Over the 1,000 rows of the 2012-05-04 save. Kept is the daily return that would "
            "reach the same final capital as the rule if it were earned every day. Compounded "
            "over 252 days, it gives the rule’s APR in the table. Lost to swings is the average "
            "day minus kept. On each rule, the amount lost to swings comes close to half the "
            "square of the standard deviation, so "
            "momentum alone and reversal alone, which swing nearly three times as much as the "
            "join, lose about eight times as much.*"
        )

    def test_its_alt_text_says_what_the_picture_shows(self, every, figures) -> None:
        """The proportions it names are checked on the run: the join's vermilion
        part a thin strip, momentum alone the tallest bar, and the vermilion parts
        of the rules alone about a half and about two thirds of their
        lower parts."""
        alt = _alt(POST.read_text(encoding="utf-8"), every[2])
        assert "Its figures come from the run." in alt
        assert "drawn to one scale, each as tall as its rule’s average day" in alt
        assert (
            "lower part is a pale tint with a blue edge, and its upper part is solid vermilion"
            in alt
        )
        assert "Its vermilion part is only a thin strip at the top" in alt
        assert "The middle bar, the tallest, is named “momentum alone”" in alt
        assert "beside a vermilion part about half as tall as the lower part" in alt
        assert "beside a vermilion part about two thirds as tall as the lower part" in alt
        join, momentum, reversal = figures.swings
        assert max(figures.swings, key=lambda swing: swing.average) is momentum
        assert join.lost / join.kept < 0.1
        assert 0.45 < momentum.lost / momentum.kept < 0.55
        assert 0.6 < reversal.lost / reversal.kept < 0.73


# --- The post ------------------------------------------------------------------


class TestThePost:
    def test_the_rule_sketch_follows_the_rules_paragraph(self) -> None:
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.endswith(RULE_PARAGRAPH_END)]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", paragraphs[index + 1]
        )
        assert paragraphs[index + 2].startswith("*The left panel is the join’s first long")
        assert paragraphs[index + 3].startswith("The script’s fourth rule")

    def test_the_grid_sketch_follows_its_paragraph(self) -> None:
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(GRID_PARAGRAPH)]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[1])}\)", paragraphs[index + 1]
        )
        assert paragraphs[index + 2].startswith("*Counted over the 960 rows")
        assert paragraphs[index + 3].startswith("The join’s average day")

    def test_the_swing_sketch_follows_its_paragraph(self) -> None:
        """The paragraph hands over to the sketch, then to the chart."""
        paragraphs = _paragraphs()
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(SWING_PARAGRAPH)]
        assert paragraphs[index].endswith(
            "The sketch below measures what the swings took from each rule’s average day, "
            "and the chart after it shows where those swings carried each rule’s capital."
        )
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[2])}\)", paragraphs[index + 1]
        )
        assert paragraphs[index + 2].startswith("*Over the 1,000 rows")
        assert paragraphs[index + 3].startswith("![Two line charts")

    def test_the_rule_sketch_sits_in_the_rule_and_the_others_in_lesson_2(self) -> None:
        text = POST.read_text(encoding="utf-8")
        rule, grid, swing = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        section = text.index("## The rule and the file")
        lesson_1 = text.index("## Lesson 1:")
        lesson_2 = text.index("## Lesson 2:")
        cost = text.index("### What the swings cost")
        chart = text.index("(../docs/figures/cl_reversal_momentum.png)")
        lesson_3 = text.index("## Lesson 3:")
        assert section < rule < lesson_1 < lesson_2 < grid < cost < swing < chart < lesson_3

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
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

    def test_each_alt_text_says_it_is_slow_and_whether_it_is_schematic(self, every) -> None:
        text = POST.read_text(encoding="utf-8")
        rule, grid, swing = every
        assert "It is schematic: each panel keeps the order" in _alt(text, rule)
        assert "schematic" not in _alt(text, grid)
        assert "schematic" not in _alt(text, swing)
        for scene in every:
            alt = _alt(text, scene)
            assert "drawn slowly" in alt, scene.slug
            assert "holds for twelve seconds" in alt, scene.slug

    def test_the_footer_links_the_module_and_its_tests(self) -> None:
        text = POST.read_text(encoding="utf-8")
        base = "https://github.com/l3a0/quantitative-trading/blob/main"
        assert (
            f"[the whiteboard sketches]({base}/src/chan/cl_reversal_momentum_whiteboard.py)" in text
        )
        assert (
            f"[what the sketches draw]({base}/tests/test_cl_reversal_momentum_whiteboard.py)"
            in text
        )

    def test_the_module_says_which_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert doc.count("This sketch is schematic.") == 1
        assert doc.count("This sketch is not schematic") == 2
