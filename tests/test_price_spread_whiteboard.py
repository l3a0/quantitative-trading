"""The pins for the whiteboard GIF in the price spread post.

``blog/price-spread-ratio-lessons.md`` carries one sketch, in Lesson 4, right
after the list that ends on the leftover earning close to nothing. It draws why
the spread is mostly the 20-day fit's intercept ``c``: two real windows a
trading week apart, whose fitted lines turn about clouds that sit about 91.5
dollars from GLD = 0, so ``c`` moves a long way while the leftover ``e`` stays
small.

Every figure it prints and every point it places comes from
:class:`chan.price_spread_whiteboard.Lever`, which reads the committed vintage
itself, so the tests here read the run rather than a frozen copy of it. The
vintage and specification are those ``tests/test_price_spread.py`` names as its
``SPEC``: ``inputdata_etf/gld.csv`` and ``inputdata_etf/uso.csv`` from Chan's
``inputData_ETF.mat``, saved 2012-04-10, 1,500 days, and the 20-row regression
``ols(USO, [GLD ones])`` of ``PriceSpread.m`` over the 1,480 kept rows. The
whole run's figures it closes on, a correlation of 0.9987 and standard
deviations of 45.37 and 2.27 dollars, are the ones
``test_the_spread_is_almost_all_the_fits_intercept`` there pins, so a re-pin
there moves them here. A second, made-up :class:`Lever` holds that the words,
the dates, the verbs and the figures follow the data rather than being typed in,
and made-up scales hold that the frame's "12× taller" follows the two panels'
scales.

What else is pinned is what a reader takes from it: the labels in order, the
ink of each mark, that each panel places every point by an affine map of its
dollars, that each ``c`` sits where its line meets GLD = 0, that the whole
run's figures sit below the magnified panel rather than beside one window's
points, that "GLD = 0" sits at the upright axis's foot as its second name,
the shared layout rules, the GIF's size, frames, loop and pace, and where the
post places it, what its alt text says and that its caption's figures are the
run's.

Two draws on one machine give the same bytes. Whether the committed GIF equals
a fresh draw depends on the font, as ``tests/test_usdcad_tests_whiteboard.py``
explains, so that comparison runs only on macOS arm64 with Comic Sans MS.

Exploratory, like every Example 3.1 pin.
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
from ithildincore.timeseries import ols
from PIL import Image

from chan import price_spread_whiteboard as sketch
from chan import usdcad_tests_whiteboard as whiteboard
from chan.palette import ACCENT, INKS
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.price_spread import LOOKBACK, X_SYMBOL, Y_SYMBOL, price_spread, read_sources
from chan.price_spread_whiteboard import (
    GLD_TOP,
    MAIN_X,
    MAIN_Y,
    PACED_HOLD_MS,
    PACED_LABEL_MS,
    RULE_Y,
    TALLER_Y,
    USO_SPAN,
    WEEK,
    ZOOM_GLD,
    ZOOM_USO,
    ZOOM_X,
    ZOOM_Y,
    Lever,
    Window,
    gif_name,
    main,
    make_price_spread_whiteboards,
    scenes,
    sketch_timeline,
    taller,
)
from chan.regime_figure import INK, MUTED
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    TITLE_MS,
    WIDTH,
    Frame,
    Label,
    clearances,
    hand_font,
    timeline,
)
from chan.vintage import VintageUnavailable

POST = REPO_ROOT / "blog" / "price-spread-ratio-lessons.md"
GIFS = ["price_spread_intercept_lever.gif"]
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4

#: What the sketch prints on the committed vintage, in drawing order.
LABELS = [
    "USO",
    "GLD = 0",
    "GLD",
    "12× taller",
    "7 July, h 0.97",
    "c −51.65",
    "14 July, h 2.17",
    "c −161.60",
    "c fell 109.95",
    "91.5 dollars",
    "≈ 1.20 × 91.5",
    "h rose 1.20",
    "e −3.21, a week before −2.71",
    "over all 1,480 traded days",
    "correlation of c and the spread 0.9987",
    "SD of the spread 45.37 dollars, of e 2.27",
]
STROKES = [
    "uso-axis",
    "gld-axis",
    "zoom",
    "to-top",
    "to-bottom",
    "panel",
    "cloud-before",
    "fit-before",
    "reach-before",
    "c-before",
    "cloud-after",
    "fit-after",
    "reach-after",
    "c-after",
    "drop",
    "distance",
    "last-day",
    "leftover",
    "rule",
]


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def lever(sources) -> Lever:
    return Lever.from_run(sources[1])


@pytest.fixture(scope="module")
def scene(lever):
    (only,) = scenes(lever)
    return only


@pytest.fixture(scope="module")
def frames(scene):
    return sketch_timeline(scene)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, lever):
    return make_price_spread_whiteboards(out_dir=tmp_path_factory.mktemp("sketch"), lever=lever)


def _made_up_window(end: str, hedge: float, intercept: float, leftover: float) -> Window:
    """A window of 20 made-up points along ``c + h·GLD``, with the last one ``leftover`` off it."""
    gld = np.linspace(90.0, 94.0, LOOKBACK)
    uso = intercept + hedge * gld + 0.4 * np.sin(np.arange(LOOKBACK))
    uso[-1] = intercept + hedge * gld[-1] + leftover
    return Window(pd.Timestamp(end), gld, uso, hedge, intercept, leftover)


#: Figures no run gives: ``c`` rises as ``h`` falls, on other days and with
#: other whole-run figures, so every word and number that should follow the
#: data has to move.
MADE_UP = Lever(
    before=_made_up_window("2010-03-01", 1.5, -100.0, -1.25),
    after=_made_up_window("2010-03-08", 0.4, 0.0, 2.5),
    correlation=0.5,
    spread_sd=10.0,
    leftover_sd=3.0,
    days=300,
)


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, start):
    (found,) = [s for s in scene.steps if isinstance(s, Label) and s.text.startswith(start)]
    return found


def _main_x(gld):
    return MAIN_X[0] + np.asarray(gld) / GLD_TOP * (MAIN_X[1] - MAIN_X[0])


def _main_y(uso):
    return MAIN_Y[0] + (np.asarray(uso) - USO_SPAN[0]) / (USO_SPAN[1] - USO_SPAN[0]) * (
        MAIN_Y[1] - MAIN_Y[0]
    )


def _zoom_gld(x):
    """The GLD dollars at board x in the magnified panel, the inverse of its map."""
    return ZOOM_GLD[0] + (np.asarray(x) - ZOOM_X[0]) / (ZOOM_X[1] - ZOOM_X[0]) * (
        ZOOM_GLD[1] - ZOOM_GLD[0]
    )


def _zoom_uso(y):
    return ZOOM_USO[0] + (np.asarray(y) - ZOOM_Y[0]) / (ZOOM_Y[1] - ZOOM_Y[0]) * (
        ZOOM_USO[1] - ZOOM_USO[0]
    )


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


def _alt(scene) -> str:
    text = POST.read_text(encoding="utf-8")
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    return match.group(1)


class TestTheRun:
    """What :meth:`Lever.from_run` reads from the committed vintage."""

    def test_it_draws_the_week_that_ends_on_the_spreads_lowest_day(self, lever, sources) -> None:
        """The spread is lowest on 14 July 2009, the hedge ratio highest the same day,
        and the first window ends a trading week before."""
        closes = sources[1]
        signal = price_spread(
            closes.index, closes[X_SYMBOL].to_numpy(), closes[Y_SYMBOL].to_numpy()
        )
        assert lever.after.end == signal.days[np.argmin(signal.value)]
        assert lever.after.end == signal.days[np.argmax(signal.hedge)]
        assert (lever.before.end, lever.after.end) == (
            pd.Timestamp("2009-07-07"),
            pd.Timestamp("2009-07-14"),
        )
        assert WEEK == 5
        assert closes.index.get_loc(lever.after.end) - closes.index.get_loc(lever.before.end) == 5
        for window, first in ((lever.before, "2009-06-09"), (lever.after, "2009-06-16")):
            end = closes.index.get_loc(window.end)
            assert closes.index[end - LOOKBACK + 1] == pd.Timestamp(first)
            np.testing.assert_array_equal(
                window.gld, closes[X_SYMBOL].to_numpy()[end - LOOKBACK + 1 : end + 1]
            )
            np.testing.assert_array_equal(
                window.uso, closes[Y_SYMBOL].to_numpy()[end - LOOKBACK + 1 : end + 1]
            )
        assert round(lever.after.hedge, 3) == 2.168
        assert round(lever.after.spread, 1) == -164.8

    def test_each_window_is_the_regression_it_names(self, lever) -> None:
        """``h`` and ``c`` are that window's own fit, and ``e`` its last day's residual."""
        for window in (lever.before, lever.after):
            fit = ols(window.uso, np.column_stack([window.gld, np.ones(LOOKBACK)]))
            assert window.hedge == pytest.approx(fit.beta[0], abs=1e-9)
            assert window.intercept == pytest.approx(fit.beta[1], abs=1e-9)
            assert window.leftover == pytest.approx(fit.resid[-1], abs=1e-9)
            assert window.spread == pytest.approx(window.intercept + window.leftover, abs=1e-9)

    def test_the_two_windows_share_all_but_a_weeks_points(self, lever) -> None:
        np.testing.assert_array_equal(lever.before.gld[WEEK:], lever.after.gld[: LOOKBACK - WEEK])

    def test_c_fell_by_about_the_turn_times_the_distance(self, lever) -> None:
        """``c`` fell 109.95 while ``h`` rose 1.1965, and 1.1965 times the clouds' mean GLD
        of 91.532 is 109.52. ``e`` moved half a dollar."""
        before, after = lever.before, lever.after
        assert round(before.intercept - after.intercept, 2) == 109.95
        assert round(after.hedge - before.hedge, 4) == 1.1965
        assert round(lever.mean_gld, 3) == 91.532
        assert round((after.hedge - before.hedge) * lever.mean_gld, 2) == 109.52
        assert round(before.leftover - after.leftover, 2) == 0.51

    def test_the_whole_runs_figures_are_the_ones_the_run_pins(self, lever) -> None:
        """``test_the_spread_is_almost_all_the_fits_intercept`` pins these."""
        assert round(lever.correlation, 4) == 0.9987
        assert (round(lever.spread_sd, 2), round(lever.leftover_sd, 2)) == (45.37, 2.27)
        assert round(lever.leftover_sd, 4) == 2.2707, "the n - 1 deviation, not the n one"
        assert lever.days == 1480


class TestTheScene:
    def test_it_is_the_one_sketch_and_names_its_gif(self, scene) -> None:
        assert (scene.title, gif_name(scene)) == ("Why c carries the spread", GIFS[0])

    def test_it_draws_its_strokes_in_order(self, scene) -> None:
        assert [s.gid for s in scene.strokes] == STROKES

    def test_it_says_what_it_should(self, scene) -> None:
        assert scene.labels == LABELS

    def test_every_label_names_a_stroke_drawn_before_it(self, scene) -> None:
        for index, step in enumerate(scene.steps):
            if isinstance(step, Label):
                earlier = [s.gid for s in scene.steps[:index] if not isinstance(s, Label)]
                assert step.names in earlier, step.text

    def test_no_label_is_parsed_as_math(self, scene) -> None:
        assert not [s.text for s in scene.steps if getattr(s, "math", 0)]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, scene) -> None:
        for stroke in scene.strokes:
            assert stroke.points >= stroke.frames, stroke.gid

    def test_it_draws_no_tint(self, scene) -> None:
        """A pale tint would need a blue edge, and this sketch shades nothing."""
        assert scene.fills == []


class TestTheInks:
    def test_c_is_berry_and_the_windows_grey_then_black(self, scene) -> None:
        """``c`` is the idea the sketch points at. The first window is context for the
        second, so it is grey, and the second, with its ``e``, is the main drawing."""
        colours = {s.gid: s.color for s in scene.strokes}
        assert {g for g, c in colours.items() if c == ACCENT} == {"c-before", "c-after", "drop"}
        assert {g for g, c in colours.items() if c == INK} == {
            "cloud-after",
            "fit-after",
            "reach-after",
            "last-day",
            "leftover",
        }
        assert all(colours[g] == MUTED for g in STROKES if colours[g] not in (ACCENT, INK))
        assert _stroke(scene, "reach-before").dashed and _stroke(scene, "reach-after").dashed
        assert not (_stroke(scene, "fit-before").dashed or _stroke(scene, "fit-after").dashed)

    def test_each_label_takes_the_ink_of_what_it_names(self, scene) -> None:
        """The arithmetic label and the change in ``h`` under it are berry like the
        bracket beside them, though they name the grey span whose distance the first
        multiplies, and the whole run's two figures are black under a grey heading."""
        colours = {s.gid: s.color for s in scene.strokes}
        for step in scene.steps:
            if not isinstance(step, Label) or step.names in ("distance", "rule"):
                continue
            assert step.color == colours[step.names], step.text
        assert _label(scene, "≈").color == ACCENT
        assert _label(scene, "h rose").color == ACCENT
        assert _label(scene, "12×").color == MUTED
        assert _label(scene, "91.5").color == MUTED
        assert [_label(scene, t).color for t in ("over", "correlation", "SD")] == [MUTED, INK, INK]


class TestTheGeometry:
    def test_the_left_panel_draws_gld_0_as_usos_axis(self, scene) -> None:
        axis, gld = _stroke(scene, "uso-axis"), _stroke(scene, "gld-axis")
        assert np.allclose(axis.x, MAIN_X[0])
        assert np.allclose(gld.y, _main_y(0.0))
        assert gld.x.min() == pytest.approx(MAIN_X[0])

    def test_gld_0_sits_at_the_upright_axis_foot_as_its_second_name(self, scene) -> None:
        """It sits just right of the upright axis's foot, below the lower ``c`` dot, so
        it reads as naming the axis rather than as a height beside the ``c`` labels or
        as the name of the span, which runs level with where it sat before."""
        uso, zero = _label(scene, "USO"), _label(scene, "GLD = 0")
        assert (zero.x, zero.ha, zero.names, zero.size) == (
            MAIN_X[0] + 0.25,
            "left",
            "uso-axis",
            uso.size,
        )
        assert zero.y == sketch.GLD_ZERO_Y == 0.22
        assert zero.y < MAIN_Y[0]
        assert all(zero.y < _label(scene, t).y for t in ("c −51.65", "c −161.60", "c fell"))
        assert abs(zero.y - (float(_main_y(0.0)) + 0.3)) > 2.0

    def test_each_c_sits_where_its_line_meets_gld_0(self, scene, lever) -> None:
        for window, dot, reach in (
            (lever.before, "c-before", "reach-before"),
            (lever.after, "c-after", "reach-after"),
        ):
            mark = _stroke(scene, dot)
            assert (mark.x[0], mark.y[0]) == pytest.approx(
                (MAIN_X[0], float(_main_y(window.intercept)))
            )
            line = _stroke(scene, reach)
            assert (line.x[-1], line.y[-1]) == pytest.approx((mark.x[0], mark.y[0]))

    def test_each_dashed_line_is_its_fit_to_scale(self, scene, lever) -> None:
        """Every point of the dashed line, read back to dollars, sits on ``c + h·GLD``,
        from the window's lowest GLD down to 0."""
        for window, gid in ((lever.before, "reach-before"), (lever.after, "reach-after")):
            line = _stroke(scene, gid)
            gld = (line.x - MAIN_X[0]) / (MAIN_X[1] - MAIN_X[0]) * GLD_TOP
            uso = USO_SPAN[0] + (line.y - MAIN_Y[0]) / (MAIN_Y[1] - MAIN_Y[0]) * (
                USO_SPAN[1] - USO_SPAN[0]
            )
            np.testing.assert_allclose(uso, window.intercept + window.hedge * gld, atol=1e-9)
            assert (gld[0], gld[-1]) == pytest.approx((window.gld.min(), 0.0))

    def test_the_drop_brackets_one_c_to_the_other(self, scene, lever) -> None:
        drop = _stroke(scene, "drop")
        assert (drop.y.max(), drop.y.min()) == pytest.approx(
            (float(_main_y(lever.before.intercept)), float(_main_y(lever.after.intercept)))
        )
        assert drop.x.max() < MAIN_X[0]

    def test_the_distance_runs_from_gld_0_to_the_clouds_mean(self, scene, lever) -> None:
        span = _stroke(scene, "distance")
        assert (span.x.min(), span.x.max()) == pytest.approx(
            (MAIN_X[0], float(_main_x(lever.mean_gld)))
        )

    def test_the_box_on_the_left_frames_what_the_right_magnifies(self, scene) -> None:
        box, panel = _stroke(scene, "zoom"), _stroke(scene, "panel")
        assert (box.x.min(), box.x.max()) == pytest.approx(tuple(_main_x(np.array(ZOOM_GLD))))
        assert (box.y.min(), box.y.max()) == pytest.approx(tuple(_main_y(np.array(ZOOM_USO))))
        assert (panel.x.min(), panel.x.max(), panel.y.min(), panel.y.max()) == pytest.approx(
            (*ZOOM_X, *ZOOM_Y)
        )
        top, bottom = _stroke(scene, "to-top"), _stroke(scene, "to-bottom")
        assert (top.x[0], top.y[0], top.x[-1], top.y[-1]) == pytest.approx(
            (box.x.max(), box.y.max(), ZOOM_X[0], ZOOM_Y[1])
        )
        assert (bottom.x[0], bottom.y[0], bottom.x[-1], bottom.y[-1]) == pytest.approx(
            (box.x.max(), box.y.min(), ZOOM_X[0], ZOOM_Y[0])
        )

    def test_each_cloud_is_its_windows_closes_magnified(self, scene, lever) -> None:
        for window, gid in ((lever.before, "cloud-before"), (lever.after, "cloud-after")):
            cloud = _stroke(scene, gid)
            assert cloud.dots > 0
            np.testing.assert_allclose(_zoom_gld(cloud.x), window.gld, atol=1e-9)
            np.testing.assert_allclose(_zoom_uso(cloud.y), window.uso, atol=1e-9)

    def test_each_magnified_line_is_its_fit_over_its_own_closes(self, scene, lever) -> None:
        for window, gid in ((lever.before, "fit-before"), (lever.after, "fit-after")):
            line = _stroke(scene, gid)
            gld, uso = _zoom_gld(line.x), _zoom_uso(line.y)
            np.testing.assert_allclose(uso, window.intercept + window.hedge * gld, atol=1e-9)
            assert (gld.min(), gld.max()) == pytest.approx((window.gld.min(), window.gld.max()))

    def test_e_runs_from_the_line_to_the_last_point(self, scene, lever) -> None:
        """Its length in dollars is ``e``, on the second window's last day."""
        after = lever.after
        tick = _stroke(scene, "leftover")
        assert np.allclose(_zoom_gld(tick.x), after.gld[-1])
        top, bottom = float(_zoom_uso(tick.y[0])), float(_zoom_uso(tick.y[-1]))
        assert top == pytest.approx(after.intercept + after.hedge * after.gld[-1])
        assert bottom == pytest.approx(after.uso[-1])
        assert bottom - top == pytest.approx(after.leftover)

    def test_a_ring_marks_the_last_point_among_its_neighbours(self, scene, lever) -> None:
        """Two other points sit within a tenth of a dollar of GLD from the last one, so
        the ring, centred on it, says which point the tick ends at."""
        after = lever.after
        assert np.sum(np.abs(after.gld - after.gld[-1]) <= 0.1 + 1e-9) == 3
        ring, tick = _stroke(scene, "last-day"), _stroke(scene, "leftover")
        centre = ((ring.x.max() + ring.x.min()) / 2, (ring.y.max() + ring.y.min()) / 2)
        assert centre == pytest.approx((tick.x[-1], tick.y[-1]), abs=1e-3)
        assert np.hypot(ring.x - tick.x[-1], ring.y - tick.y[-1]) == pytest.approx(
            sketch.RING, abs=1e-9
        )

    def test_the_frame_says_how_much_taller_it_draws_inside_its_top_right(self, scene) -> None:
        """Right after the frame is drawn, inside its top right corner and above every
        magnified point."""
        steps = list(scene.steps)
        label = _label(scene, "12×")
        assert steps.index(label) == steps.index(_stroke(scene, "panel")) + 1
        assert (label.x, label.y, label.ha, label.size, label.names) == (
            pytest.approx(ZOOM_X[1] - 0.2),
            TALLER_Y,
            "right",
            10,
            "panel",
        )
        assert TALLER_Y == 4.1 and ZOOM_Y[0] < TALLER_Y < ZOOM_Y[1]
        for gid in ("cloud-before", "cloud-after"):
            assert _stroke(scene, gid).y.max() < TALLER_Y, gid

    def test_the_change_in_h_sits_under_the_arithmetic_it_multiplies(self, scene) -> None:
        """Right after "≈ 1.20 × 91.5" in the steps, at its x and below it, naming the
        same span."""
        steps = list(scene.steps)
        approx, turned = _label(scene, "≈"), _label(scene, "h rose")
        assert steps.index(turned) == steps.index(approx) + 1
        assert (turned.x, turned.ha, turned.names, turned.size) == (
            approx.x,
            "right",
            approx.names,
            10,
        )
        assert turned.y == pytest.approx(approx.y - 0.3)
        assert turned.y > float(_main_y(-161.60)) + 0.1

    def test_the_whole_runs_figures_sit_below_the_magnified_points(self, scene) -> None:
        """They describe every traded day, so none sits inside the panel beside one
        window's points."""
        rule = _stroke(scene, "rule")
        assert np.allclose(rule.y, RULE_Y) and RULE_Y < ZOOM_Y[0]
        for start in ("over", "correlation", "SD"):
            assert _label(scene, start).y < RULE_Y, start


class TestOtherFigures:
    """A made-up :class:`Lever` moves every word and number that follows the data."""

    def test_the_labels_follow_the_figures(self) -> None:
        (scene,) = scenes(MADE_UP)
        assert scene.labels == [
            "USO",
            "GLD = 0",
            "GLD",
            "12× taller",
            "1 March, h 1.50",
            "c −100.00",
            "8 March, h 0.40",
            "c 0.00",
            "c rose 100.00",
            "92.0 dollars",
            "≈ 1.10 × 92.0",
            "h fell 1.10",
            "e 2.50, a week before −1.25",
            "over all 300 traded days",
            "correlation of c and the spread 0.5000",
            "SD of the spread 10.00 dollars, of e 3.00",
        ]

    def test_the_marks_follow_the_figures(self) -> None:
        (scene,) = scenes(MADE_UP)
        assert _stroke(scene, "c-after").y[0] == pytest.approx(float(_main_y(0.0)))
        assert _stroke(scene, "c-before").y[0] == pytest.approx(float(_main_y(-100.0)))
        tick = _stroke(scene, "leftover")
        assert float(_zoom_uso(tick.y[-1]) - _zoom_uso(tick.y[0])) == pytest.approx(2.5)

    def test_taller_is_the_ratio_of_the_two_panels_heights_per_dollar(self) -> None:
        """The frame draws a dollar of USO 11.81 times as tall as the left panel does,
        and a dollar of GLD 16.71 times as wide, so the label names heights only."""
        zoom = (ZOOM_Y[1] - ZOOM_Y[0]) / (ZOOM_USO[1] - ZOOM_USO[0])
        main = (MAIN_Y[1] - MAIN_Y[0]) / (USO_SPAN[1] - USO_SPAN[0])
        assert taller() == pytest.approx(zoom / main)
        assert round(taller(), 2) == 11.81 and round(taller()) == 12
        wider = ((ZOOM_X[1] - ZOOM_X[0]) / (ZOOM_GLD[1] - ZOOM_GLD[0])) / (
            (MAIN_X[1] - MAIN_X[0]) / GLD_TOP
        )
        assert round(wider, 2) == 16.71 and round(wider) != round(taller())

    def test_the_taller_label_follows_the_scales(self, monkeypatch) -> None:
        """Halving the left panel's height doubles the magnification the frame names, and
        a ratio of 11.08 prints 11, so the label rounds rather than rounding up."""
        monkeypatch.setattr(sketch, "MAIN_Y", (MAIN_Y[0], MAIN_Y[0] + (MAIN_Y[1] - MAIN_Y[0]) / 2))
        assert round(taller(), 2) == 23.63
        (scene,) = scenes(MADE_UP)
        assert "24× taller" in scene.labels
        monkeypatch.setattr(sketch, "MAIN_Y", MAIN_Y)
        monkeypatch.setattr(sketch, "ZOOM_USO", (ZOOM_USO[0] - 15.0, ZOOM_USO[1]))
        assert round(taller(), 2) == 5.91
        (scene,) = scenes(MADE_UP)
        assert "6× taller" in scene.labels
        monkeypatch.setattr(sketch, "ZOOM_USO", (ZOOM_USO[0], ZOOM_USO[0] + 16.0))
        assert round(taller(), 2) == 11.08
        (scene,) = scenes(MADE_UP)
        assert "11× taller" in scene.labels

    def test_the_change_in_h_takes_its_verb_from_its_own_sign(self) -> None:
        """``h`` fell where ``c`` rose, so each verb follows its own figure."""
        (scene,) = scenes(MADE_UP)
        assert ("c rose 100.00", "h fell 1.10") == (
            _label(scene, "c rose").text,
            _label(scene, "h fell").text,
        )
        both = dataclasses.replace(MADE_UP, before=_made_up_window("2010-03-01", 0.39, -3.0, -1.25))
        (scene,) = scenes(both)
        assert _label(scene, "c rose").text == "c rose 3.00"
        assert _label(scene, "h rose").text == "h rose 0.01"

    def test_a_window_that_would_fall_off_the_board_is_refused(self) -> None:
        """A ``c`` below the left panel, or points outside the magnified one, would be
        drawn clipped, so the sketch refuses them."""
        low = dataclasses.replace(MADE_UP, after=_made_up_window("2010-03-08", 3.0, -240.0, 0.0))
        with pytest.raises(ValueError, match="falls outside the sketch's panels"):
            scenes(low)
        moved = dataclasses.replace(
            MADE_UP, before=dataclasses.replace(MADE_UP.before, gld=MADE_UP.before.gld + 5.0)
        )
        with pytest.raises(ValueError, match="window to 2010-03-01"):
            scenes(moved)
        left = dataclasses.replace(
            MADE_UP, before=dataclasses.replace(MADE_UP.before, gld=MADE_UP.before.gld - 2.0)
        )
        with pytest.raises(ValueError, match="window to 2010-03-01"):
            scenes(left)
        for shift in (-10.0, 10.0):
            off = dataclasses.replace(
                MADE_UP, after=dataclasses.replace(MADE_UP.after, uso=MADE_UP.after.uso + shift)
            )
            with pytest.raises(ValueError, match="window to 2010-03-08"):
                scenes(off)
        for shift in (-10.0, 10.0):
            line = dataclasses.replace(
                MADE_UP,
                after=dataclasses.replace(MADE_UP.after, intercept=MADE_UP.after.intercept + shift),
            )
            with pytest.raises(ValueError, match="window to 2010-03-08"):
                scenes(line)


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, scene, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        found = clearances(scene)
        assert set(found) == {*scene.labels, scene.title}
        for text, pixels in found.items():
            assert pixels >= CLEAR_PX, (text, round(pixels, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_sits_inside_the_board(
        self, scene, monkeypatch, fallback
    ) -> None:
        _font(monkeypatch, fallback)
        for text, box in _boxes(scene):
            inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
            assert inside >= INSIDE_PX, (text, round(inside, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_no_two_labels_touch(self, scene, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        boxes = _boxes(scene)
        for k, (one, a) in enumerate(boxes):
            for other, b in boxes[k + 1 :]:
                gap = math.hypot(
                    max(a.x0 - b.x1, b.x0 - a.x1, 0.0), max(a.y0 - b.y1, b.y0 - a.y1, 0.0)
                )
                assert gap >= APART_LABELS_PX, (one, other, round(gap, 1))


class TestTheGifs:
    def test_there_is_one_named_for_the_scene(self, gifs) -> None:
        assert [path.name for path in gifs] == GIFS

    def test_it_is_680_by_320_and_loops_forever(self, gifs, frames) -> None:
        (path,) = gifs
        with Image.open(path) as image:
            assert (image.size, image.n_frames, image.info["loop"]) == (
                (WIDTH, HEIGHT),
                len(frames),
                0,
            )
        assert _durations(path) == [f.ms for f in frames]

    def test_it_opens_on_its_title_and_builds_slowly(self, scene, frames) -> None:
        """It carries sixteen labels, so each shows on its own for 900 ms and the
        finished drawing holds twelve seconds."""
        assert scene.slug in sketch.PACED
        assert (frames[0].done, frames[0].ms) == (0, TITLE_MS)
        assert frames[-1].ms == PACED_HOLD_MS == 12000
        shown = {
            f.ms
            for f in frames[1:-1]
            if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
        }
        assert shown == {PACED_LABEL_MS} and PACED_LABEL_MS == 900
        assert [(f.done, f.partial) for f in frames] == [
            (f.done, f.partial) for f in timeline(scene)
        ]

    def test_it_is_under_1_mb(self, gifs) -> None:
        assert gifs[0].stat().st_size < 1_000_000

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, lever) -> None:
        (again,) = make_price_spread_whiteboards(out_dir=tmp_path, lever=lever)
        assert gifs[0].read_bytes() == again.read_bytes()

    def test_it_draws_on_the_palette_of_the_colour_blind_safe_inks(self, gifs) -> None:
        """Without :data:`chan.palette.INKS`, ``render`` maps every frame onto the shared
        inks, and the berry of each ``c`` lands on the nearest of them."""
        with Image.open(gifs[0]) as image:
            assert image.getpalette() == whiteboard.palette(INKS).getpalette()


class TestTheCommittedGif:
    def test_it_draws_on_the_palette_of_the_colour_blind_safe_inks(self) -> None:
        """Unlike the byte-for-byte comparison, this holds on every machine, so a GIF
        left in the shared inks fails wherever the suite runs."""
        with Image.open(FIGURES_DIR / GIFS[0]) as image:
            assert image.getpalette() == whiteboard.palette(INKS).getpalette()

    def test_the_figures_folder_holds_this_gif_under_its_prefix(self) -> None:
        """``tests/test_equity_seasonals_whiteboard.py`` holds that every GIF in the
        folder is one a sketch module draws."""
        assert {p.name for p in FIGURES_DIR.glob(f"{sketch.GIF_PREFIX}*.gif")} == set(GIFS)

    def test_it_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, frames) -> None:
        committed = FIGURES_DIR / GIFS[0]
        with Image.open(committed) as image:
            assert (image.size, image.n_frames, image.info["loop"]) == (
                (WIDTH, HEIGHT),
                len(frames),
                0,
            )
        assert _durations(committed) == [f.ms for f in frames]

    def test_it_is_a_fresh_draw_byte_for_byte(self, gifs) -> None:
        system, machine, font = platform.system(), platform.machine(), hand_font()
        if (system, machine, font) != ("Darwin", "arm64", "Comic Sans MS"):
            pytest.skip(
                f"the committed GIF was drawn on Darwin arm64 in Comic Sans MS, and this is "
                f"{system} {machine} drawing in {font}"
            )
        committed = (FIGURES_DIR / GIFS[0]).read_bytes()
        assert (
            hashlib.sha256(gifs[0].read_bytes()).hexdigest()
            == hashlib.sha256(committed).hexdigest()
        ), f"{GIFS[0]}: redraw with: uv run python -m chan.price_spread_whiteboard"


class TestThePost:
    def test_it_follows_the_list_that_ends_on_the_leftover_earning_close_to_nothing(self) -> None:
        """Then its caption, then the paragraph that says what the spread mostly is."""
        paragraphs = _paragraphs()
        (index,) = [
            k
            for k, p in enumerate(paragraphs)
            if p.startswith("1. **The intercept tracks the spread.**")
        ]
        assert "3. **The leftover alone earns close to nothing.**" in paragraphs[index]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(GIFS[0])}\)", paragraphs[index + 1]
        )
        assert paragraphs[index + 2].startswith("*Two real 20-day windows")
        assert paragraphs[index + 3].startswith(
            "So the spread in the second panel of Lesson 1’s figure"
        )
        assert sum(GIFS[0] in p for p in paragraphs) == 1

    def test_its_alt_text_quotes_the_title_and_every_label_in_order(self, scene) -> None:
        alt = _alt(scene)
        places = [alt.index(f"“{text}”") for text in [scene.title, *scene.labels]]
        assert places == sorted(places)

    def test_its_alt_text_gives_the_pace_and_the_scales(self, scene) -> None:
        alt = _alt(scene)
        assert "drawn slowly" in alt and "twelve seconds" in alt
        assert "Each axis on the left is drawn to its own linear scale" in alt
        assert "neither is broken" in alt and "a scale of its own" in alt

    def test_its_alt_text_names_the_inks_the_sketch_draws(self, scene) -> None:
        """Berry for each ``c``, grey for the first window and black for the second."""
        alt = _alt(scene)
        assert [_stroke(scene, g).color for g in ("c-before", "c-after")] == [ACCENT, ACCENT]
        assert alt.count("berry dot") == 2
        assert "a grey cloud" in alt and "A black cloud" in alt
        assert "a black ring circles the last black point" in alt

    def test_its_alt_text_directions_follow_the_scene(self, scene, lever) -> None:
        """Each word of direction, place or ink the alt text uses holds in the run or the scene."""
        alt = _alt(scene)
        before, after = lever.before, lever.after
        assert "black line down to it" in alt and after.leftover < 0
        assert "line is steeper" in alt and after.hedge > before.hedge
        assert "lands much lower" in alt and after.intercept < before.intercept
        assert "A berry bracket joins" in alt and _stroke(scene, "drop").color == ACCENT
        assert "Below a grey rule under the frame" in alt and RULE_Y < ZOOM_Y[0]
        assert "its five newest sit below the rest" in alt
        assert after.uso[-WEEK:].max() < after.uso[:-WEEK].min()
        assert "mostly at the top and right" in alt
        oldest_gld, oldest_uso = before.gld[:WEEK], before.uso[:WEEK]
        assert (oldest_gld > before.gld.mean()).sum() >= 3
        assert (oldest_uso > before.uso.mean()).sum() >= 3

    def test_its_alt_text_says_where_the_new_labels_sit(self, scene) -> None:
        """ "GLD = 0" names the upright axis, "12× taller" sits in the frame and the change
        in ``h`` under the arithmetic."""
        alt = _alt(scene)
        assert "a second label, “GLD = 0”, says the axis stands where GLD is zero" in alt
        assert (
            f"Inside the frame’s top right, a grey label reads “{round(taller())}× taller”" in alt
        )
        assert _label(scene, "12×").color == MUTED
        assert "“≈ 1.20 × 91.5”, and under that another reads “h rose 1.20”" in alt
        assert f"around GLD of {sum(ZOOM_GLD) / 2:.1f} dollars" in alt

    def test_its_alt_text_counts_the_points_each_window_shares(self, scene) -> None:
        alt = _alt(scene)
        assert "the second window, which shares fifteen days with the first" in alt
        assert f"cloud of {LOOKBACK} points" in alt
        assert "Fifteen of its points" in alt and LOOKBACK - WEEK == 15
        assert "its five newest" in alt and "five oldest" in alt and WEEK == 5

    def test_its_caption_names_the_days_and_the_count_the_run_gives(self, lever) -> None:
        paragraphs = _paragraphs()
        (caption,) = [p for p in paragraphs if p.startswith("*Two real 20-day windows")]
        before, after = lever.before.end, lever.after.end
        assert f"ending {before.day} and {after.day} {after:%B} {after.year}" in caption
        assert f"all {lever.days:,} traded days" in caption
        assert "the second on the day the spread is lowest in the whole run" in caption

    def test_its_caption_takes_the_turn_and_the_distance_from_the_run(self, lever) -> None:
        """The rise in ``h``, both slopes, the clouds' mean GLD and the product they make
        are the run's, at the precision the sketch prints them."""
        (caption,) = [p for p in _paragraphs() if p.startswith("*Two real 20-day windows")]
        before, after = lever.before, lever.after
        rise, mean = after.hedge - before.hedge, lever.mean_gld
        assert rise > 0 and after.intercept < before.intercept
        assert (
            f"the slope h rose by {rise:.2f}, from {before.hedge:.2f} to {after.hedge:.2f}"
            in caption
        )
        assert f"about {mean:.1f} dollars to the right of GLD = 0" in caption
        assert f"moved c down by about {rise:.2f} × {mean:.1f} dollars" in caption
        assert (f"{rise:.2f}", f"{mean:.1f}") == ("1.20", "91.5")
        assert caption.endswith("*") and "\n" not in caption

    def test_its_caption_is_the_run_in_words(self, lever) -> None:
        """The whole caption, with every figure and date read from the run."""
        (caption,) = [p for p in _paragraphs() if p.startswith("*Two real 20-day windows")]
        before, after = lever.before, lever.after
        rise, mean = after.hedge - before.hedge, lever.mean_gld
        assert caption == (
            f"*Two real 20-day windows from Chan’s file, ending {before.end.day} and "
            f"{after.end.day} {after.end:%B} {after.end.year}, the second on the day the "
            f"spread is lowest in the whole run. Between them the slope h rose by {rise:.2f}, "
            f"from {before.hedge:.2f} to {after.hedge:.2f}. Both clouds sit about {mean:.1f} "
            f"dollars to the right of GLD = 0, where c is read. Steepening the line by "
            f"{rise:.2f} while it still runs through the clouds moved c down by about "
            f"{rise:.2f} × {mean:.1f} dollars. Over the same week the leftover e on each "
            f"window’s last day moved only from {sketch._signed(before.leftover, 2)} to "
            f"{sketch._signed(after.leftover, 2)}, so c makes up nearly all of the spread’s fall. "
            f"Every figure comes from the run, and the three lines under the frame are figures "
            f"over all {lever.days:,} traded days, not over these two windows. The frame on the "
            f"right draws each dollar of USO about {round(taller())} times taller than the left "
            f"side does.*"
        )


class TestTheCommand:
    def test_it_prints_each_path_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            sketch, "make_price_spread_whiteboards", lambda: [FIGURES_DIR / name for name in GIFS]
        )
        main()
        assert capsys.readouterr().out.splitlines() == [f"wrote {FIGURES_DIR / GIFS[0]}"]

    def test_a_missing_vintage_stops_it_with_one_line(self, monkeypatch) -> None:
        def refuse():
            raise VintageUnavailable("no file here")

        monkeypatch.setattr(sketch, "make_price_spread_whiteboards", refuse)
        with pytest.raises(SystemExit, match="no file here"):
            main()

    def test_it_reads_the_committed_vintage_when_handed_nothing(self, lever) -> None:
        again = Lever.from_run()
        assert (again.before.end, again.after.end, again.days) == (
            lever.before.end,
            lever.after.end,
            lever.days,
        )
