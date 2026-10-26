"""The pins for the fourteen whiteboard GIFs in the post on mean reversion on USD.CAD.

One GIF sketches the post's opening section, six the scenes of its section
"The tests and the file", two its Lesson 1, one its Lesson 2, two its Lesson 3
and two its Lesson 5. Each sits right after the text it draws. The first seven
are schematic, so what is pinned for every GIF is what a reader takes from
it: which scenes there are and in which order the post reads them, what each
one says and draws, that a label never appears before the stroke it names,
that no label touches a line or sits on a tint, how long each GIF
shows before it loops, and each file's size, frame count and loop.

Labels in ten scenes quote the run. The opening scene prints the count of
closes. The half-life scene and the linear rule's
warning print the lookback, the half-life rounded, and the count of closes.
Chan's reading prints the three critical values and the ADF statistic, and
places each on a line drawn to scale. The fingerprint prints the count of
closes, the ADF statistic, the AR(1) estimate, the variance ratio's p-value
and the half-life. One row apart prints the count of closes and each toolbox's
row count and ADF statistic, and starts each bar at the cell of the first day
its regression fits. Lesson 3's scene prints the run's H and draws a
histogram of ``genhurst`` on the random walks and a dot for each start day, all
from :mod:`chan.usdcad_hurst_noise`, to scale. Lesson 3's gauges print the
ADF statistic and its 10 percent critical value, H, and the variance ratio's
statistic and the critical value its test rejects at, and band H by the same
measurement's mean and SD, each gauge to its own scale. Lesson 5's look-ahead prints
the first close, the first position and the last close and places its bars by
date, and its count of half-lives prints the closes over the half-life and
ticks the line every lookback. All of them are read from the run or the
measurement rather than written in, and the tests below hand the scenes a run
and a measurement with other figures to prove it. Where other figures would
make a scene's words false, as a statistic past its critical value would in
Chan's reading or the gauges, or a value the script did not print would in the
fingerprint, the tests hold that the scene refuses the run instead. The
numbers come from the vintage and the specification
``tests/test_usdcad_mean_reversion.py`` names as its ``SPEC``, which failure
messages here carry:
``pythoncodesanddata/inputData_USDCAD.csv``, vendor ``chan-py``, basis
``raw``, saved 2018-10-13, its 16:59 bar of each day, 1,216 closes, a
lookback of 115 days, an ADF statistic of −1.840744 against critical values of
−3.458, −2.871 and −2.594, an AR(1) estimate of 0.994120, a variance ratio
p-value of 0.367281 from a statistic of −0.901577, an H of 0.473233, and a
half-life of 115.209794 days. ``adfuller`` at the
same lag fits 1,214 rows from day 3, counting the first close as day 1, and
gives −1.843018, where jplv7's ``adf`` fits 1,213 from day 4. The walks and
start days are the ones ``NOISE_SPEC`` there names.

Two draws on one machine give the same bytes, and a test holds that. Whether a
committed GIF equals a fresh draw depends on the font, because the hand font
is whichever one is installed and font rasterising varies by platform. So that
comparison runs only on macOS arm64 with Comic Sans MS installed, where the
committed files were drawn, and skips elsewhere with the reason. The frame
count, the size, the loop, the timing and the palette of each committed file
are pinned everywhere.

The post's scenes draw in :mod:`chan.palette`'s colours, while the renderer's
own defaults stay the shared ones every other post draws in. So a colour here
is pinned as ``own.ACCENT`` and its kin, ``own`` being :mod:`chan.palette`
imported the way the module imports it, and a frame is rendered with
``own.INKS`` the way the module renders its GIFs.
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
import pytest
from PIL import Image
from scipy.stats import norm

from chan import palette as own
from chan import usdcad_mean_reversion
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR
from chan.series import WindowCrossesScaleBreak
from chan.stationarity_tests import VRATIO_ALPHA
from chan.usdcad_mean_reversion import read_sources, stationarity_tests
from chan.usdcad_tests_whiteboard import (
    FRAME_MS,
    HEIGHT,
    HOLD_MS,
    LABEL_MS,
    TITLE_MS,
    WIDTH,
    Fill,
    Label,
    Stroke,
    clearances,
    hand_font,
    main,
    make_usdcad_tests_whiteboards,
    palette,
    render,
    scenes,
    spread,
    timeline,
)
from chan.vintage import VintageUnavailable
from tests.test_usdcad_mean_reversion import NOISE_SPEC, SPEC

TITLES = [
    "Every day or a few round trips",
    "The question",
    "ADF",
    "Hurst",
    "Variance ratio",
    "Half-life",
    "The linear rule",
    "Chan’s reading",
    "The fingerprint",
    "One row apart",
    "Chance and the start day",
    "Leaning, not crossing",
    "The look-ahead",
    "Ten half-lives",
]

GIFS = [
    "usdcad_tests_every_day.gif",
    "usdcad_tests_question.gif",
    "usdcad_tests_adf.gif",
    "usdcad_tests_hurst.gif",
    "usdcad_tests_variance_ratio.gif",
    "usdcad_tests_half_life.gif",
    "usdcad_tests_linear_rule.gif",
    "usdcad_tests_no_rejection.gif",
    "usdcad_tests_fingerprint.gif",
    "usdcad_tests_one_row.gif",
    "usdcad_tests_noise_band.gif",
    "usdcad_tests_lean_not_cross.gif",
    "usdcad_tests_look_ahead.gif",
    "usdcad_tests_half_lives.gif",
]

#: Each scene's strokes, by their ids, in the order they are drawn.
STROKES = [
    ["top-path", "closes", "bottom-path", "trip-1", "trip-2", "trip-3"],
    ["mean", "price", "pull"],
    ["mean", "rise", "high", "fall"],
    ["start", "wide-up", "wide-down", "narrow-up", "narrow-down"],
    ["floor", "two-day", "one-day", "gap"],
    ["axes", "decay", "half"],
    ["mean", "price", "above", "below", "warning", "bang", "bang-dot"],
    ["line", "tick-1", "tick-5", "tick-10", "zone", "statistic", "needs"],
    [
        "matlab",
        "csv",
        "link",
        "cross-a",
        "cross-b",
        "to-adf",
        "adf",
        "adf-out",
        "check-adf-0",
        "check-adf-1",
        "to-vratio",
        "vratio",
        "vratio-out",
        "check-vratio-0",
        "to-half-life",
        "half-life",
        "half-life-out",
        "check-half-life-0",
    ],
    ["days", "last", "grey", "adfuller", "jplv7", "one-row"],
    ["axis", "walks", "half", "run", "book", *[f"start-{k}" for k in range(11)]],
    [
        "adf-line",
        "adf-zero",
        "adf-critical",
        "adf-dot",
        "h-line",
        "h-half",
        "h-dot",
        "vr-line",
        "vr-zero",
        "vr-critical",
        "vr-dot",
    ],
    ["timeline", "measure", "trade", "earlier", "after"],
    ["sample", *[f"tick-{k}" for k in range(1, 11)]],
]

LABELS = [
    [
        "a test reads all 1,216 closes",
        "round trip",
        "round trip",
        "round trip",
        "a backtest sees only its round trips",
    ],
    ["Random walk?", "Pulled back?"],
    ["high close…", "…then a fall", "λ < 0"],
    ["random walk, H = 0.5", "reverting, H < 0.5", r"variance $\sim \tau^{2H}$"],
    ["2-day variance", "2 × 1-day variance", "ratio < 1 → pulled back"],
    ["distance from the mean", "half", "≈ 115 days", "−ln 2 / λ"],
    ["z = +2 → short 2", "z = −1.5 → long 1.5", "115 days measured on all 1,216 closes"],
    [
        "−3.458",
        "1%",
        "−2.871",
        "5%",
        "−2.594",
        "10%",
        "reject a random walk",
        "−1.84",
        "ADF statistic",
        "must sit left of 10% to reject",
    ],
    [
        "Chan’s MATLAB file",
        "not public",
        "the CSV here",
        "1,216 closes",
        "can’t compare",
        "ADF regression",
        "−1.840744",
        "0.994120",
        "variance ratio",
        "0.367281",
        "half-life",
        "115.209794",
        "closes × a constant would match too",
    ],
    [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "…",
        "1,216",
        "no earlier\nchange\nto lag",
        "adfuller, 1,214 rows",
        "−1.843018",
        "jplv7 adf, 1,213 rows",
        "−1.840744",
        "the script’s figure",
        "the one row",
    ],
    [
        "40,000 random walks",
        "±1 SD",
        "0.5",
        "0.4732",
        "this run",
        "0.49",
        "the book",
        "eleven start days",
        "six print as 0.49",
    ],
    [
        "← more reverting",
        "random walk →",
        "ADF statistic",
        "0",
        "reject",
        "−2.594 at 10%",
        "−1.84",
        "H",
        "no test:\nH is an estimate",
        "0.5",
        "±1 SD of a random walk",
        "0.4732",
        "variance ratio\nstatistic",
        "0",
        "reject",
        "−1.96 at 5%, two-sided",
        "−0.90",
    ],
    [
        "2007-07-23",
        "2012-03-28",
        "measure the half-life: all 1,216 closes",
        "2008-01-02",
        "trade with a 115-day lookback",
        "every day traded sits inside the days measured",
        "measure on earlier days",
        "trade only after",
        "a sketch of the fix, not a run",
    ],
    [
        "2007-07-23",
        "2012-03-28",
        "115 days",
        "10.6 half-lives",
        "only a few stretches for a distance from the mean to halve",
    ],
]

#: The frames each GIF takes, and how long one pass shows, in milliseconds.
FRAMES = [55, 29, 31, 29, 30, 29, 32, 44, 77, 58, 53, 52, 44, 34]
MS = [
    10700,
    7350,
    7800,
    7600,
    7700,
    7850,
    7900,
    10850,
    14900,
    13500,
    11750,
    14150,
    10600,
    8600,
]

#: How far, in pixels, every label and title must sit from the nearest stroke.
#: The sketch's wobble moves a line a pixel or two off its points, so this
#: leaves room for it with a visible gap to spare.
CLEAR_PX = 10
#: Labels that state something about the whole scene rather than name a
#: stroke. Each stands apart from every stroke, by at least
#: :data:`APART_PX`, so it cannot be read as one curve's label. The Hurst
#: formula once sat beside the end of the lower reverting curve, 12 pixels from
#: it, and read as that curve's label. The fingerprint's margin note is about
#: the four values together, so it stands apart from the last check mark.
STATEMENTS = {"λ < 0", r"variance $\sim \tau^{2H}$", "closes × a constant would match too"}
APART_PX = 25
#: How far, in pixels, every label and title must sit inside the frame's edge.
INSIDE_PX = 5
#: How far apart, in pixels, any two labels or a label and the title must sit.
#: In DejaVu Sans two critical values of Chan's reading once sat 1.5 pixels
#: apart and read as one number.
APART_LABELS_PX = 4


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def run(sources):
    return stationarity_tests(*sources)


@pytest.fixture(scope="module")
def measured(sources):
    """The random walks and start days Lesson 3's scene draws, a few seconds."""
    return spread(sources[1])


@pytest.fixture(scope="module")
def drawn(run, measured):
    return scenes(run, measured)


@pytest.fixture(scope="module")
def frames(drawn):
    return [timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, sources, measured):
    return make_usdcad_tests_whiteboards(
        out_dir=tmp_path_factory.mktemp("whiteboards"), sources=sources, measured=measured
    )


@pytest.fixture(scope="module")
def question(drawn):
    """The question's scene drawn in the post's inks, as its GIF is, which is
    enough to watch strokes and labels."""
    steps = timeline(drawn[1])
    return steps, render(drawn[1], steps, own.INKS)


def _durations(path) -> list[int]:
    with Image.open(path) as image:
        durations = []
        for index in range(image.n_frames):
            image.seek(index)
            durations.append(image.info["duration"])
        return durations


def _inked(image: Image.Image) -> int:
    """How many pixels are not the white board, which is palette entry 0."""
    return int((np.asarray(image) != 0).sum())


class TestTheScenes:
    def test_there_are_fourteen_in_the_order_the_post_reads_them(self, drawn) -> None:
        assert [scene.title for scene in drawn] == TITLES

    def test_no_title_carries_a_scene_number(self, drawn) -> None:
        """Each GIF stands alone beside its own text, so a number such as
        "3" in front of "Hurst" would count scenes the reader never sees
        together."""
        for scene in drawn:
            assert not re.search(r"\d", scene.title), scene.title

    def test_each_scene_has_its_own_gif_named_for_it(self, drawn) -> None:
        assert [scene.gif for scene in drawn] == GIFS
        assert not [name for name in GIFS if re.search(r"\d", name)]

    def test_each_scene_draws_its_strokes_in_order(self, drawn) -> None:
        assert [[s.gid for s in scene.strokes] for scene in drawn] == STROKES

    def test_each_scene_says_what_it_should(self, drawn) -> None:
        assert [scene.labels for scene in drawn] == LABELS, SPEC

    def test_every_label_names_a_stroke_or_tint_drawn_before_it(self, drawn) -> None:
        for scene in drawn:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if not isinstance(s, Label)]
                    assert step.names in earlier, (scene.title, step.text)

    def test_only_the_hurst_formula_is_parsed_as_math(self, drawn) -> None:
        maths = [step.text for scene in drawn for step in scene.steps if getattr(step, "math", 0)]
        assert maths == [r"variance $\sim \tau^{2H}$"]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, drawn) -> None:
        """A stroke with fewer points than frames would repeat a frame, and the
        GIF writer merges repeated frames, which would change the count."""
        for scene in drawn:
            for stroke in scene.strokes:
                assert stroke.points >= stroke.frames, (scene.title, stroke.gid)
                assert stroke.points == len(stroke.y)


def _font(monkeypatch, fallback: bool) -> None:
    """Draw in DejaVu Sans, the font CI falls back to and wider than the hand
    fonts, when ``fallback`` is set, and in the installed hand font otherwise."""
    if fallback:
        monkeypatch.setattr(whiteboard, "hand_font", lambda: whiteboard.FALLBACK_FONT)


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, drawn, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in drawn:
            found = clearances(scene)
            assert set(found) == {*scene.labels, scene.title}
            for text, pixels in found.items():
                assert pixels >= CLEAR_PX, (scene.title, text, round(pixels, 1))

    def test_a_statement_about_the_scene_stands_apart_from_every_curve(self, drawn) -> None:
        found = {text: px for scene in drawn for text, px in clearances(scene).items()}
        assert STATEMENTS <= set(found)
        for text in STATEMENTS:
            assert found[text] >= APART_PX, (text, round(found[text], 1))

    def test_the_hurst_formula_sits_under_the_starting_point(self, drawn) -> None:
        """Left of where the curves end and below where they start, so it
        reads as a statement about both pairs."""
        hurst = drawn[3]
        start = next(s for s in hurst.strokes if s.gid == "start")
        formula = next(s for s in hurst.steps if isinstance(s, Label) and s.math)
        assert formula.x <= start.x[0]
        assert formula.y < min(float(s.y.min()) for s in hurst.strokes)

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_sits_inside_the_board(
        self, drawn, monkeypatch, fallback
    ) -> None:
        """Clearance from the strokes says nothing about the frame's edge, and a
        wider font can push a label at the right end off the GIF."""
        _font(monkeypatch, fallback)
        for scene in drawn:
            with matplotlib.rc_context(whiteboard._style()):
                canvas, artists = whiteboard._board(scene)
                whiteboard._show(scene, artists, whiteboard.Frame(len(scene.steps), 0, 0))
                canvas.draw()
                renderer = canvas.get_renderer()
                for artist in artists:
                    if not hasattr(artist, "get_text") or not artist.get_visible():
                        continue
                    box = artist.get_window_extent(renderer)
                    inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                    assert inside >= INSIDE_PX, (scene.title, artist.get_text(), round(inside, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_no_two_labels_touch(self, drawn, monkeypatch, fallback) -> None:
        """Clearance from the strokes says nothing about two labels side by
        side, which a wider font pushes together."""
        _font(monkeypatch, fallback)
        for scene in drawn:
            with matplotlib.rc_context(whiteboard._style()):
                canvas, artists = whiteboard._board(scene)
                whiteboard._show(scene, artists, whiteboard.Frame(len(scene.steps), 0, 0))
                canvas.draw()
                renderer = canvas.get_renderer()
                boxes = [
                    (artist.get_text(), artist.get_window_extent(renderer))
                    for artist in artists
                    if hasattr(artist, "get_text") and artist.get_visible()
                ]
            for k, (one, a) in enumerate(boxes):
                for other, b in boxes[k + 1 :]:
                    dx = max(a.x0 - b.x1, b.x0 - a.x1, 0.0)
                    dy = max(a.y0 - b.y1, b.y0 - a.y1, 0.0)
                    gap = math.hypot(dx, dy)
                    assert gap >= APART_LABELS_PX, (scene.title, one, other, round(gap, 1))

    def test_the_measure_sees_a_label_on_a_line(self, drawn) -> None:
        """A label moved onto its own stroke reads as touching, so the two
        tests above can fail."""
        hurst = drawn[3]
        steps = tuple(
            dataclasses.replace(s, x=0.6, y=2.0) if isinstance(s, Label) and s.math else s
            for s in hurst.steps
        )
        moved = dataclasses.replace(hurst, steps=steps)
        assert clearances(moved)[r"variance $\sim \tau^{2H}$"] < 0

    def test_the_measure_sees_a_label_on_the_tint(self, drawn) -> None:
        """Labels stay off Lesson 3's tint rather than sit on it, so a label
        moved into the band reads zero, and one beside it reads its gap."""
        (band,) = drawn[10].fills
        label = next(s for s in drawn[10].steps if isinstance(s, Label) and s.text == "±1 SD")
        middle = ((band.x0 + band.x1) / 2, (band.y0 + band.y1) / 2)
        on = dataclasses.replace(label, x=middle[0], y=middle[1], ha="center")
        assert clearances(whiteboard.Scene("", "", (band, on)))["±1 SD"] == 0
        beside = dataclasses.replace(label, x=band.x1 + 1, y=middle[1])
        gap = clearances(whiteboard.Scene("", "", (band, beside)))["±1 SD"]
        # One board unit is a tenth of the frame's width, 68 pixels.
        assert gap == pytest.approx(WIDTH / 10, abs=3)


class TestTheNumbersComeFromTheRun:
    def test_spread_draws_the_walks_it_is_asked_for(self, run) -> None:
        """``paths`` sets how many walks, and ``seed`` which ones, so a test
        that asks for a few walks gets a few, and another seed other walks."""
        few = spread(run.closes, paths=40)
        assert len(few.walks) == 40
        other = spread(run.closes, paths=40, seed=7)
        assert not np.array_equal(other.walks, few.walks)

    def test_the_run_has_1216_closes_and_a_115_day_lookback(self, run) -> None:
        assert (len(run.closes), run.lookback) == (1216, 115), SPEC
        assert round(run.half_life) == 115, SPEC

    def test_the_half_life_scene_prints_the_runs_lookback(self, run) -> None:
        other = dataclasses.replace(run, lookback=100)
        assert "≈ 100 days" in _scenes(other)[5].labels
        assert "≈ 115 days" not in _scenes(other)[5].labels

    def test_the_warning_prints_the_runs_lookback_and_closes(self, run) -> None:
        other = dataclasses.replace(_shortened(run, 1000), lookback=100)
        assert _scenes(other)[6].labels[-1] == "100 days measured on all 1,000 closes"

    def test_the_gifs_are_drawn_from_the_sources_handed_in(
        self, monkeypatch, tmp_path, sources
    ) -> None:
        """The first 800 closes have a half-life that rounds to 100 days, as
        ``tests/test_usdcad_mean_reversion_figures.py`` pins, so a GIF that
        read the file or wrote 115 in would fail here. The random walks are
        measured on those closes too, so they are 800 long."""
        seen = []

        def record(run, measured):
            seen.append((run.lookback, len(run.closes), measured.length))
            return (whiteboard._half_life(run.lookback),)

        monkeypatch.setattr(whiteboard, "scenes", record)
        entry, closes = sources
        make_usdcad_tests_whiteboards(out_dir=tmp_path, sources=(entry, closes[:800]))
        assert seen == [(100, 800, 800)]


#: Random walks drawn for a measurement a test makes on a run it altered. Few
#: are needed, since such a test reads what the scene does with the walks
#: rather than how they spread.
FEW_PATHS = 400


def _scenes(run, measured=None):
    """Every scene of ``run``, with Lesson 3's walks and start days measured on
    ``run``'s own closes from :data:`FEW_PATHS` walks unless handed in."""
    return scenes(run, measured if measured is not None else spread(run.closes, paths=FEW_PATHS))


def _shortened(run, closes: int, drops: tuple[int, int] = (2, 3)):
    """``run`` cut to its first ``closes`` closes, with ``adfuller`` and jplv7
    dropping ``drops`` rows, so each regression's first day stays a day the
    closes hold."""
    return dataclasses.replace(
        run,
        closes=run.closes.iloc[:closes],
        adfuller_nobs=closes - drops[0],
        adf=dataclasses.replace(run.adf, nobs=closes - drops[1]),
    )


def _altered(run, statistic: float = -2.2):
    """``run`` with every figure Lesson 1's and Lesson 2's scenes print moved
    to another value. The fingerprint refuses such a run, so a test hands it
    to one scene rather than to :func:`scenes`."""
    short = _shortened(run, 1000)
    return dataclasses.replace(
        short,
        adf=dataclasses.replace(
            short.adf, statistic=statistic, ar1=0.98765, critical=(-3.9, -3.1, -2.7)
        ),
        vratio=dataclasses.replace(run.vratio, p_value=0.05),
        half_life=80.123456,
        adfuller_statistic=-2.5,
    )


def _reading(run):
    """Chan's reading of ``run``, drawn on its own."""
    return whiteboard._no_rejection(run.adf.statistic, run.adf.critical)


def _x(scene, gid: str) -> float:
    """Where the stroke ``gid`` stands on the board, for a tick or a dot."""
    stroke = next(s for s in scene.strokes if s.gid == gid)
    assert np.ptp(stroke.x) == 0, gid
    return float(stroke.x[0])


class TestChansReading:
    """The scene is drawn to scale, so its positions are pinned as well as its
    words. Chan reads it as no rejection: the statistic, −1.84 in the post, sits
    right of the 10 percent value of −2.594, and has to sit left of it."""

    def test_the_run_does_not_reject_at_10_percent(self, run) -> None:
        assert round(run.adf.statistic, 6) == -1.840744, SPEC
        assert [round(c, 3) for c in run.adf.critical] == [-3.458, -2.871, -2.594], SPEC
        assert run.adf.statistic > run.adf.critical[2], SPEC

    @pytest.mark.parametrize("altered", [False, True])
    def test_every_position_is_proportional_to_its_value(self, run, altered) -> None:
        """The board distance between any two marks over the gap between their
        values is one number, so the line is a ruler rather than a sketch."""
        run = _altered(run) if altered else run
        scene = _reading(run)
        values = [*run.adf.critical, run.adf.statistic]
        xs = [_x(scene, gid) for gid in ("tick-1", "tick-5", "tick-10", "statistic")]
        slopes = [
            (xs[j] - xs[i]) / (values[j] - values[i])
            for i in range(len(xs))
            for j in range(i + 1, len(xs))
        ]
        assert slopes[0] > 0
        assert slopes == pytest.approx([slopes[0]] * len(slopes), rel=1e-12)
        line = next(s for s in scene.strokes if s.gid == "line")
        assert line.x.min() < min(xs) and max(xs) < line.x.max()

    def test_the_dot_sits_right_of_the_10_percent_tick(self, drawn) -> None:
        reading = drawn[7]
        assert _x(reading, "statistic") > _x(reading, "tick-10")

    @pytest.mark.parametrize("statistic", [-3.0, -2.7], ids=["left of it", "on it"])
    def test_a_statistic_not_right_of_the_10_percent_value_is_refused(self, run, statistic) -> None:
        """The arrow says the statistic must move left to reject, which would
        be false of a statistic already there."""
        with pytest.raises(ValueError, match="right of its 10 percent critical value"):
            _reading(_altered(run, statistic=statistic))

    def test_the_shaded_zone_runs_from_the_line_start_to_the_10_percent_tick(self, drawn) -> None:
        reading = drawn[7]
        zone = next(s for s in reading.strokes if s.gid == "zone")
        line = next(s for s in reading.strokes if s.gid == "line")
        assert zone.x.min() == line.x.min()
        assert zone.x.max() == pytest.approx(_x(reading, "tick-10"))
        assert zone.y.min() > line.y[0], "the zone sits above the line"

    def test_the_arrow_runs_from_the_dot_to_the_10_percent_tick(self, drawn) -> None:
        reading = drawn[7]
        arrow = next(s for s in reading.strokes if s.gid == "needs")
        dot, edge = _x(reading, "statistic"), _x(reading, "tick-10")
        assert dot - 0.5 < arrow.x[0] < dot
        tip = int(np.argmin(arrow.x))
        assert edge < arrow.x[tip] < edge + 0.5

    def test_each_tick_is_labelled_with_its_value_and_level(self, drawn) -> None:
        reading = drawn[7]
        for gid, value, level in zip(
            ("tick-1", "tick-5", "tick-10"),
            ("−3.458", "−2.871", "−2.594"),
            ("1%", "5%", "10%"),
            strict=True,
        ):
            named = [s for s in reading.steps if isinstance(s, Label) and s.names == gid]
            assert [s.text for s in named] == [value, level], SPEC
            assert all(s.x == pytest.approx(_x(reading, gid)) for s in named)

    def test_the_labels_follow_the_runs_figures(self, run) -> None:
        assert _reading(_altered(run)).labels == [
            "−3.900",
            "1%",
            "−3.100",
            "5%",
            "−2.700",
            "10%",
            "reject a random walk",
            "−2.20",
            "ADF statistic",
            "must sit left of 10% to reject",
        ]


class TestTheFingerprint:
    """Lesson 1's argument: Chan's file cannot be compared, so four values from
    three calculations on the CSV here stand in for it, each to six decimals."""

    VALUE = re.compile(r"^−?\d+\.\d{6}$")

    def test_the_run_prints_the_scripts_four_values(self, run) -> None:
        printed = [
            f"{run.adf.statistic:.6f}",
            f"{run.adf.ar1:.6f}",
            f"{run.vratio.p_value:.6f}",
            f"{run.half_life:.6f}",
        ]
        assert printed == ["-1.840744", "0.994120", "0.367281", "115.209794"], SPEC

    def test_four_values_each_with_its_own_check_mark(self, drawn) -> None:
        """Every value is followed at once by a blue check, and nothing else
        is checked."""
        steps = drawn[8].steps
        values = [
            k for k, s in enumerate(steps) if isinstance(s, Label) and self.VALUE.match(s.text)
        ]
        checks = [
            k for k, s in enumerate(steps) if isinstance(s, Stroke) and s.gid.startswith("check-")
        ]
        assert len(values) == 4
        assert checks == [k + 1 for k in values]
        assert {steps[k].color for k in checks} == {own.GOOD}

    def test_each_value_sits_beside_the_calculation_that_gives_it(self, drawn) -> None:
        steps = drawn[8].steps
        given = {
            s.names: [v.text for v in steps if isinstance(v, Label) and v.names == s.names]
            for s in steps
            if isinstance(s, Label) and self.VALUE.match(s.text)
        }
        assert given == {
            "adf-out": ["−1.840744", "0.994120"],
            "vratio-out": ["0.367281"],
            "half-life-out": ["115.209794"],
        }, SPEC

    def test_three_arrows_leave_the_csv(self, drawn) -> None:
        fingerprint = drawn[8]
        csv = next(s for s in fingerprint.strokes if s.gid == "csv")
        arrows = [s for s in fingerprint.strokes if s.gid.startswith("to-")]
        assert len(arrows) == 3
        for arrow in arrows:
            assert arrow.x[0] > csv.x.max()
            assert csv.y.min() < arrow.y[0] < csv.y.max()

    def test_the_runs_four_values_are_the_scripts(self, run) -> None:
        """The check marks are true of the committed run, so it is drawn."""
        assert [t for t in whiteboard._fingerprint(run).labels if self.VALUE.match(t)] == [
            "−1.840744",
            "0.994120",
            "0.367281",
            "115.209794",
        ], SPEC

    def test_the_count_of_closes_follows_the_run(self, run) -> None:
        assert "1,000 closes" in whiteboard._fingerprint(_shortened(run, 1000)).labels

    @pytest.mark.parametrize(
        "moved",
        [
            {"adf": {"statistic": -1.840741}},
            {"adf": {"ar1": 0.98765}},
            {"vratio": {"p_value": 0.05}},
            {"half_life": 115.209791},
        ],
        ids=["ADF statistic", "AR(1) estimate", "p-value", "half-life"],
    )
    def test_a_value_the_script_did_not_print_is_refused(self, run, moved) -> None:
        """A check mark beside a value the script did not print would claim a
        match that is not there. Each value is moved alone. The ADF statistic
        and the half-life move in the sixth decimal only, so a check at five
        decimals would pass them."""
        changes = {
            key: dataclasses.replace(getattr(run, key), **value)
            if isinstance(value, dict)
            else value
            for key, value in moved.items()
        }
        with pytest.raises(ValueError, match="where the script printed"):
            whiteboard._fingerprint(dataclasses.replace(run, **changes))


def _cells(scene) -> list[float]:
    """The edges of the row's cells, read off the vertical sides of the
    ``days`` stroke, so cell ``d`` runs from ``edges[d - 1]`` to ``edges[d]``."""
    days = next(s for s in scene.strokes if s.gid == "days")
    sides = {
        round(float(x0), 9)
        for x0, x1, y0, y1 in zip(days.x, days.x[1:], days.y, days.y[1:], strict=False)
        if x0 == x1 and y0 != y1
    }
    return sorted(sides)


def _stroke(scene, gid: str) -> Stroke:
    return next(s for s in scene.strokes if s.gid == gid)


class TestOneRowApart:
    """Lesson 2's point: jplv7's ``adf`` starts a day later than ``adfuller``,
    so it fits one row fewer and lands the script's statistic. The bars are
    placed from the run's first days, so a run that starts them elsewhere moves
    them, which the altered run below shows."""

    def test_the_run_fits_one_row_fewer_from_one_day_later(self, run) -> None:
        assert (run.adfuller_nobs, run.adf.nobs) == (1214, 1213), SPEC
        assert (run.adfuller_first_day, run.adf_first_day) == (3, 4), SPEC
        assert f"{run.adfuller_statistic:.6f}" == "-1.843018", SPEC
        assert f"{run.adf.statistic:.6f}" == "-1.840744", SPEC

    def test_the_row_shows_six_days_and_the_last(self, drawn) -> None:
        one_row = drawn[9]
        assert len(_cells(one_row)) == 7
        assert one_row.labels[:8] == ["1", "2", "3", "4", "5", "6", "…", "1,216"], SPEC
        last = _stroke(one_row, "last")
        assert last.x.min() > _cells(one_row)[-1]

    @pytest.mark.parametrize("moved", [False, True])
    def test_each_bar_starts_at_the_cell_of_its_first_day(self, run, moved) -> None:
        """The moved run drops three and four rows, so its bars start on days 4
        and 5 and three days are greyed. Its last cell still counts every
        close rather than one more than a row count."""
        run = _shortened(run, 1000, (3, 4)) if moved else run
        one_row = _scenes(run)[9]
        assert one_row.labels[7] == f"{len(run.closes):,}"
        edges = _cells(one_row)
        early, late = run.adfuller_first_day, run.adf_first_day
        assert (early, late) == ((4, 5) if moved else (3, 4))
        adfuller, jplv7 = _stroke(one_row, "adfuller"), _stroke(one_row, "jplv7")
        assert adfuller.x[0] == pytest.approx(edges[early - 1])
        assert jplv7.x[0] == pytest.approx(edges[late - 1])
        width = edges[1] - edges[0]
        assert jplv7.x[0] - adfuller.x[0] == pytest.approx(width), "one cell apart"
        assert adfuller.x[0] == adfuller.x.min() and jplv7.x[0] == jplv7.x.min()
        grey = _stroke(one_row, "grey")
        assert (grey.x.min(), grey.x.max()) == pytest.approx((edges[0], edges[early - 1]))
        assert round((grey.x.max() - grey.x.min()) / width) == early - 1
        assert grey.x.max() <= adfuller.x.min() < jplv7.x.min()

    def test_two_days_are_greyed_on_the_runs_closes(self, drawn) -> None:
        one_row = drawn[9]
        edges = _cells(one_row)
        grey = _stroke(one_row, "grey")
        assert grey.x.max() == pytest.approx(edges[2]), "days 1 and 2"
        assert grey.color == whiteboard.MUTED

    def test_both_bars_end_at_the_last_cell_and_adfuller_runs_above(self, drawn) -> None:
        one_row = drawn[9]
        last = _stroke(one_row, "last")
        adfuller, jplv7 = _stroke(one_row, "adfuller"), _stroke(one_row, "jplv7")
        assert adfuller.x.max() == jplv7.x.max() == last.x.max()
        assert np.median(adfuller.y) > np.median(jplv7.y)
        assert last.y.min() > adfuller.y.max()

    def test_each_value_sits_at_the_end_of_its_bar(self, drawn) -> None:
        one_row = drawn[9]
        for gid, name, value in (
            ("adfuller", "adfuller, 1,214 rows", "−1.843018"),
            ("jplv7", "jplv7 adf, 1,213 rows", "−1.840744"),
        ):
            bar = _stroke(one_row, gid)
            named = {s.text: s for s in one_row.steps if isinstance(s, Label) and s.names == gid}
            assert name in named and value in named, SPEC
            assert named[value].x > bar.x.max()
            assert named[value].y == pytest.approx(np.median(bar.y))
            assert bar.x.min() < named[name].x < bar.x.max()
        script = next(s for s in one_row.steps if isinstance(s, Label) and "script" in s.text)
        assert script.names == "jplv7"

    def test_the_one_row_is_adfullers_first_day_marked_last(self, run, drawn) -> None:
        one_row = drawn[9]
        edges = _cells(one_row)
        mark = one_row.steps[-2]
        assert mark.gid == "one-row" and mark.color == own.ACCENT
        day = run.adfuller_first_day
        assert (mark.x.min(), mark.x.max()) == pytest.approx((edges[day - 1], edges[day]))
        note = one_row.steps[-1]
        assert (note.text, note.names, note.color) == ("the one row", "one-row", mark.color)
        assert note.x == pytest.approx((edges[day - 1] + edges[day]) / 2)

    def test_the_labels_follow_the_runs_figures(self, run) -> None:
        labels = whiteboard._one_row(_altered(run)).labels
        assert labels[7] == "1,000"
        assert labels[9:13] == [
            "adfuller, 998 rows",
            "−2.500000",
            "jplv7 adf, 997 rows",
            "−2.200000",
        ]

    @pytest.mark.parametrize(
        "drops",
        [(2, 4), (3, 3), (4, 3), (0, 1), (5, 6), (6, 7)],
        ids=[
            "two apart",
            "together",
            "swapped",
            "from day 1",
            "jplv7 past the row",
            "past the row",
        ],
    )
    def test_a_run_the_words_would_misdescribe_is_refused(self, run, drops) -> None:
        with pytest.raises(ValueError, match="one day later"):
            _scenes(_shortened(run, 1000, drops))


class TestEveryDayOrAFewRoundTrips:
    """The opening section's point. One schematic path is drawn twice: a dot on
    every point of the upper copy, and a few round trips under the fainter
    lower copy. Only the count of closes comes from the run."""

    def test_the_label_prints_the_runs_closes(self, run) -> None:
        assert _scenes(run)[0].labels[0] == "a test reads all 1,216 closes", SPEC
        assert _scenes(_shortened(run, 1000))[0].labels[0] == "a test reads all 1,000 closes"

    def test_both_copies_are_the_same_path(self, drawn) -> None:
        every_day = drawn[0]
        top, bottom = _stroke(every_day, "top-path"), _stroke(every_day, "bottom-path")
        assert np.array_equal(top.x, bottom.x)
        gap = top.y - bottom.y
        assert gap == pytest.approx(np.full(len(gap), gap[0]), abs=1e-12)
        assert gap[0] > np.ptp(top.y), "the copies do not overlap"
        assert (top.color, bottom.color) == (whiteboard.INK, whiteboard.MUTED)

    def test_a_dot_lands_on_every_point_of_the_upper_copy(self, drawn) -> None:
        every_day = drawn[0]
        top, closes = _stroke(every_day, "top-path"), _stroke(every_day, "closes")
        assert closes.dots > 0 and closes.points > 30
        assert (closes.x.min(), closes.x.max()) == (top.x.min(), top.x.max())
        assert closes.y == pytest.approx(np.interp(closes.x, top.x, top.y), abs=0.01)
        assert np.all(np.diff(closes.x) > 0), "drawn from left to right"

    def test_each_round_trip_is_a_bracket_under_the_lower_copy(self, drawn) -> None:
        every_day = drawn[0]
        bottom = _stroke(every_day, "bottom-path")
        trips = [s for s in every_day.strokes if s.gid.startswith("trip-")]
        assert len(trips) == 3
        for trip in trips:
            entry, exit_ = trip.x[0], trip.x[-1]
            assert bottom.x.min() < entry < exit_ < bottom.x.max()
            for end in (0, -1):
                assert trip.y[end] < np.interp(trip.x[end], bottom.x, bottom.y)
            assert trip.y.min() < bottom.y.min(), "its base runs under the whole copy"
            named = [s for s in every_day.steps if isinstance(s, Label) and s.names == trip.gid]
            assert [s.text for s in named][0] == "round trip"
            assert entry < named[0].x < exit_
        ends = [(t.x[0], t.x[-1]) for t in trips]
        assert all(a[1] < b[0] for a, b in zip(ends, ends[1:], strict=False))

    def test_the_round_trips_carry_no_number(self, drawn) -> None:
        """They stand for a generic rule, not the post's, so nothing on the
        lower copy counts anything."""
        every_day = drawn[0]
        lower = every_day.steps[[s.gid for s in every_day.strokes].index("bottom-path") + 2 :]
        assert not [s.text for s in lower if isinstance(s, Label) and re.search(r"\d", s.text)]


def _axis(scene) -> tuple[float, float]:
    axis = _stroke(scene, "axis")
    return float(axis.x.min()), float(axis.x.max())


def _bins(measured) -> tuple[np.ndarray, np.ndarray]:
    """The bins the histogram should draw: a third of an SD wide, three SDs
    either side of the walks' mean."""
    mean, sd = measured.walks.mean(), measured.walks.std(ddof=1)
    edges = mean + sd * np.arange(-9, 10) / 3
    return edges, np.histogram(measured.walks, bins=edges)[0]


def _palette_rgbs() -> list[list[int]]:
    """The colours of the palette this post's GIFs draw in, as RGB triples, in
    palette order."""
    flat = palette(own.INKS).getpalette()
    return [flat[k : k + 3] for k in range(0, len(flat), 3)]


def _altered_spread(measured) -> whiteboard.Spread:
    """The measurement with every figure Lesson 3's scene prints moved: fewer
    walks with another mean and SD, and every start day printing as 0.49."""
    offsets = tuple(
        dataclasses.replace(row, genhurst=0.486 + 0.0008 * row.offset) for row in measured.offsets
    )
    return dataclasses.replace(
        measured, walks=0.5 * measured.walks[:30_000] + 0.26, offsets=offsets
    )


class TestChanceAndTheStartDay:
    """Lesson 3's scene, drawn to scale: a histogram of ``genhurst`` on the
    random walks, its ±1 SD band, lines at 0.5, the run's H and the book's
    0.49, and a dot for each start day's ``genhurst``. The bins, the mean, the
    SD, the start days and the run's H come from the measurement and the run,
    and only the book's 0.49 and a random walk's 0.5 are constants."""

    def test_the_measurement_is_the_one_the_post_quotes(self, run, measured) -> None:
        assert (len(measured.walks), measured.length) == (40_000, 1216), NOISE_SPEC
        assert round(float(measured.walks.mean()), 3) == 0.496, NOISE_SPEC
        assert round(float(measured.walks.std(ddof=1)), 3) == 0.023, NOISE_SPEC
        assert f"{run.hurst:.4f}" == "0.4732", SPEC
        assert [row.offset for row in measured.offsets if row.prints_as_book] == [1, 3, 4, 6, 8, 9]
        assert measured.offsets[0].genhurst == run.hurst

    def test_the_axis_leaves_out_111_walks_beyond_three_sds(self, measured) -> None:
        """The drawn bins hold every walk but these, which are not piled into
        the end bins."""
        _, counts = _bins(measured)
        assert len(measured.walks) - counts.sum() == 111, NOISE_SPEC

    @pytest.mark.parametrize("altered", [False, True])
    def test_each_bar_is_a_bin_of_the_walks_in_proportion_to_its_count(
        self, run, measured, altered
    ) -> None:
        measured = _altered_spread(measured) if altered else measured
        scene = _scenes(run, measured)[10]
        edges, counts = _bins(measured)
        left, right = _axis(scene)

        def at(value):
            return left + (value - edges[0]) / (edges[-1] - edges[0]) * (right - left)

        walks = _stroke(scene, "walks")
        base = float(_stroke(scene, "axis").y[0])
        heights = []
        for k in range(len(counts)):
            inside = (walks.x > at(edges[k]) + 1e-9) & (walks.x < at(edges[k + 1]) - 1e-9)
            assert inside.any() and np.ptp(walks.y[inside]) == 0, k
            heights.append(float(walks.y[inside][0]) - base)
        assert counts.max() > 0
        per_count = np.array(heights) / counts
        assert per_count == pytest.approx(np.full(len(counts), per_count[0]), rel=1e-12)
        assert (walks.x.min(), walks.x.max()) == pytest.approx((left, right))

    @pytest.mark.parametrize("altered", [False, True])
    def test_every_line_and_dot_sits_at_its_value(self, run, measured, altered) -> None:
        """One affine map from the bins' edges onto the axis places 0.5, the
        run's H, the book's 0.49 and every start day's dot."""
        if altered:
            run, measured = dataclasses.replace(run, hurst=0.4612), _altered_spread(measured)
        scene = _scenes(run, measured)[10]
        edges, _ = _bins(measured)
        left, right = _axis(scene)
        values = {"half": 0.5, "run": run.hurst, "book": 0.49}
        values |= {f"start-{row.offset}": row.genhurst for row in measured.offsets}
        for gid, value in values.items():
            expected = left + (value - edges[0]) / (edges[-1] - edges[0]) * (right - left)
            assert _x(scene, gid) == pytest.approx(expected, abs=1e-12), gid
        xs = [_x(scene, gid) for gid in values]
        slopes = [
            (xs[j] - xs[0]) / (v - values["half"])
            for j, v in enumerate(values.values())
            if j and v != values["half"]
        ]
        assert slopes == pytest.approx([slopes[0]] * len(slopes), rel=1e-9)

    @pytest.mark.parametrize("altered", [False, True])
    def test_the_band_is_a_tint_one_sd_either_side_up_to_the_tallest_bar(
        self, run, measured, altered
    ) -> None:
        """The band is one flat rectangle from the walks' mean less one SD to
        their mean plus one SD, on the same map that places every line and
        dot, and from the axis up to the tallest bar."""
        measured = _altered_spread(measured) if altered else measured
        scene = _scenes(run, measured)[10]
        edges, _ = _bins(measured)
        left, right = _axis(scene)
        mean, sd = measured.walks.mean(), measured.walks.std(ddof=1)
        span = [
            left + (v - edges[0]) / (edges[-1] - edges[0]) * (right - left)
            for v in (mean - sd, mean + sd)
        ]
        (band,) = scene.fills
        assert band.gid == "band"
        assert (band.x0, band.x1) == pytest.approx(tuple(span), abs=1e-12)
        base, walks = float(_stroke(scene, "axis").y[0]), _stroke(scene, "walks")
        assert (band.y0, band.y1) == pytest.approx((base, float(walks.y.max())), abs=1e-12)
        label = next(s for s in scene.steps if isinstance(s, Label) and s.text == "±1 SD")
        assert (label.names, label.color) == ("band", own.GOOD)

    def test_the_tint_is_a_pale_blue_the_palette_already_holds(self) -> None:
        """The band's blue at the lightest blend, so the tint adds no colour
        to the palette the post's GIFs draw in."""
        tint = [round(255 * c) for c in matplotlib.colors.to_rgb(own.TINT)]
        good = np.array(matplotlib.colors.to_rgb(own.GOOD))
        assert tint == [round(255 * (0.2 * c + 0.8)) for c in good]
        assert tint in _palette_rgbs()

    def test_the_tint_lies_beneath_every_stroke(self, drawn) -> None:
        """On the finished drawing, each line through the band, and the walks'
        outline, shows in its own full ink inside the tint, which it would not
        if the tint were laid over it."""
        scene = drawn[10]
        (band,) = scene.fills
        (image,) = render(scene, timeline(scene)[-1:], own.INKS)
        with matplotlib.rc_context(whiteboard._style()):
            _, artists = whiteboard._board(scene)
            (x0, y0), (x1, y1) = artists[0].axes.transData.transform(
                [(band.x0, band.y0), (band.x1, band.y1)]
            )
        # Pixel rows run down from the top, and 3 pixels in from each edge
        # leaves the axis and the tint's own rim out.
        inside = np.asarray(image)[
            round(HEIGHT - y1) + 3 : round(HEIGHT - y0) - 3, round(x0) + 3 : round(x1) - 3
        ]
        rgbs = _palette_rgbs()
        found = {tuple(rgbs[k]) for k in np.unique(inside)}
        tint = tuple(round(255 * c) for c in matplotlib.colors.to_rgb(own.TINT))
        assert tint in found
        for gid in ("walks", "half", "run", "book"):
            ink = tuple(round(255 * c) for c in matplotlib.colors.to_rgb(_stroke(scene, gid).color))
            assert ink in found, gid

    def test_the_tint_appears_after_the_outline_and_before_the_lines(self, drawn, frames) -> None:
        """It arrives whole on one frame, once the outline and its label are
        drawn and before 0.5, the run's H and the book's 0.49."""
        scene, steps = drawn[10], frames[10]
        order = [getattr(step, "gid", None) for step in scene.steps]
        band = order.index("band")
        assert isinstance(scene.steps[band], Fill)
        assert order.index("walks") < band < min(order.index(g) for g in ("half", "run", "book"))
        assert not [f for f in steps if f.done == band and f.partial]
        arrives = [f for f in steps if f.done == band + 1]
        assert [(f.partial, f.ms) for f in arrives] == [(0, LABEL_MS)]

    def test_the_dots_that_print_as_the_book_take_its_colour(self, drawn, measured) -> None:
        scene = drawn[10]
        colours = [_stroke(scene, f"start-{row.offset}").color for row in measured.offsets]
        book = [row.prints_as_book for row in measured.offsets]
        assert colours == [own.LOST if hit else own.ACCENT for hit in book]
        assert _stroke(scene, "book").color == own.LOST
        assert _x(scene, "start-0") == _x(scene, "run")

    def test_the_dots_sit_under_the_axis_and_none_touch(self, drawn) -> None:
        scene = drawn[10]
        base = float(_stroke(scene, "axis").y[0])
        dots = [s for s in scene.strokes if s.gid.startswith("start-")]
        assert all(dot.y[0] < base - 1 for dot in dots)
        for i, a in enumerate(dots):
            for b in dots[i + 1 :]:
                assert math.hypot(a.x[0] - b.x[0], a.y[0] - b.y[0]) >= 0.19, (a.gid, b.gid)

    def test_the_labels_follow_the_run_and_the_measurement(self, run, measured) -> None:
        altered = _altered_spread(measured)
        scene = _scenes(dataclasses.replace(run, hurst=0.4612), altered)[10]
        assert scene.labels == [
            "30,000 random walks",
            "±1 SD",
            "0.5",
            "0.4612",
            "this run",
            "0.49",
            "the book",
            "eleven start days",
            "eleven print as 0.49",
        ]

    @pytest.mark.parametrize("cut", ["length", "start"])
    def test_a_measurement_of_other_closes_is_refused(self, run, measured, cut) -> None:
        other = (
            dataclasses.replace(measured, length=1000)
            if cut == "length"
            else dataclasses.replace(
                measured,
                offsets=(dataclasses.replace(measured.offsets[0], first_day=run.closes.index[1]),),
            )
        )
        with pytest.raises(ValueError, match="walks as long as the run"):
            scenes(run, other)


def _fill(scene, gid: str) -> Fill:
    return next(f for f in scene.fills if f.gid == gid)


def _gauges(scene, run, measured) -> dict[str, dict[str, tuple[float, float]]]:
    """Each gauge's marks as board position and value, keyed by what each
    mark is: its random-walk end, its threshold or band edges, its dot."""
    mean, sd = float(measured.walks.mean()), float(measured.walks.std(ddof=1))
    critical = float(norm.ppf(VRATIO_ALPHA / 2))
    return {
        "adf": {
            "zero": (_x(scene, "adf-zero"), 0.0),
            "critical": (_x(scene, "adf-critical"), run.adf.critical[2]),
            "zone": (_fill(scene, "adf-zone").x1, run.adf.critical[2]),
            "dot": (_x(scene, "adf-dot"), run.adf.statistic),
        },
        "h": {
            "half": (_x(scene, "h-half"), 0.5),
            "low": (_fill(scene, "h-band").x0, mean - sd),
            "high": (_fill(scene, "h-band").x1, mean + sd),
            "dot": (_x(scene, "h-dot"), run.hurst),
        },
        "vr": {
            "zero": (_x(scene, "vr-zero"), 0.0),
            "critical": (_x(scene, "vr-critical"), critical),
            "zone": (_fill(scene, "vr-zone").x1, critical),
            "dot": (_x(scene, "vr-dot"), run.vratio.statistic),
        },
    }


def _leaning(run, measured=None):
    """The gauges of ``run``, drawn on their own, with the walks measured on
    its closes from :data:`FEW_PATHS` walks unless handed in."""
    walks = measured if measured is not None else spread(run.closes, paths=FEW_PATHS)
    return whiteboard._lean_not_cross(run, walks)


def _altered_lean(run):
    """``run`` with every figure the gauges print moved: an ADF statistic and
    critical values, H and a variance ratio statistic of other values."""
    return dataclasses.replace(
        run,
        adf=dataclasses.replace(run.adf, statistic=-2.3, critical=(-3.9, -3.1, -2.7)),
        hurst=0.4612,
        vratio=dataclasses.replace(run.vratio, statistic=-1.5),
    )


class TestLeaningNotCrossing:
    """Lesson 3's close: three gauges, each to its own scale, with the random
    walk toward the right and more reverting values to the left. The ADF
    statistic sits between 0 and its 10 percent critical value, H between the
    left edge of the random walks' ±1 SD band and 0.5, and the variance ratio's
    statistic between 0 and the critical value its own test rejects at."""

    def test_the_run_leans_toward_reversion_without_crossing(self, run, measured) -> None:
        assert f"{run.adf.statistic:.6f}" == "-1.840744", SPEC
        assert run.adf.critical[2] < run.adf.statistic < 0, SPEC
        assert f"{run.vratio.statistic:.6f}" == "-0.901577", SPEC
        assert f"{run.vratio.ratio:.6f}" == "0.964745", SPEC
        assert norm.ppf(VRATIO_ALPHA / 2) < run.vratio.statistic < 0, SPEC
        assert not run.vratio.rejects, SPEC
        mean, sd = measured.walks.mean(), measured.walks.std(ddof=1)
        assert mean - sd < run.hurst < 0.5, (SPEC, NOISE_SPEC)

    def test_the_variance_ratio_threshold_is_its_tests_own(self, run, drawn) -> None:
        """``vratiotest`` rejects when its two-sided p-value is at most its
        fixed level, 5 percent, so its lower critical value is the normal
        quantile of half that level, and a statistic there gives a p-value of
        exactly that level."""
        assert VRATIO_ALPHA == 0.05
        critical = whiteboard._vratio_critical()
        assert critical == norm.ppf(VRATIO_ALPHA / 2)
        assert 2 * norm.cdf(critical) == pytest.approx(VRATIO_ALPHA, rel=1e-12)
        assert f"{critical:.6f}" == "-1.959964"
        assert run.vratio.rejects == (abs(run.vratio.statistic) >= -critical)
        assert "−1.96 at 5%, two-sided" in drawn[11].labels

    def test_the_threshold_follows_the_tests_level(self, run, monkeypatch) -> None:
        monkeypatch.setattr(whiteboard, "VRATIO_ALPHA", 0.10)
        assert "−1.64 at 10%, two-sided" in _leaning(run).labels

    @pytest.mark.parametrize("altered", [False, True])
    def test_every_position_is_proportional_to_its_value_within_its_gauge(
        self, run, measured, altered
    ) -> None:
        """Along one gauge, the board distance between any two marks over the
        gap between their values is one positive number, so each gauge is a
        ruler that runs from reverting on the left to a random walk on the
        right, and the band spans one SD either side of the walks' mean."""
        if altered:
            run, measured = _altered_lean(run), _altered_spread(measured)
        scene = _leaning(run, measured)
        for name, marks in _gauges(scene, run, measured).items():
            points = list(marks.values())
            slopes = [
                (b[0] - a[0]) / (b[1] - a[1])
                for i, a in enumerate(points)
                for b in points[i + 1 :]
                if b[1] != a[1]
            ]
            assert slopes[0] > 0, name
            assert slopes == pytest.approx([slopes[0]] * len(slopes), rel=1e-9), name
            line = _stroke(scene, f"{name}-line")
            xs = [x for x, _ in points]
            assert line.x.min() <= min(xs) and max(xs) <= line.x.max(), name

    def test_each_reject_zone_runs_from_the_line_start_to_its_threshold(self, drawn) -> None:
        scene = drawn[11]
        for name in ("adf", "vr"):
            zone, line = _fill(scene, f"{name}-zone"), _stroke(scene, f"{name}-line")
            assert zone.x0 == line.x.min(), name
            assert zone.x1 == pytest.approx(_x(scene, f"{name}-critical")), name
            assert zone.y0 < line.y[0] < zone.y1, name
        assert {f.color for f in scene.fills} == {own.REJECT_TINT, own.TINT}
        assert _fill(scene, "h-band").color == own.TINT

    def test_each_tint_is_a_colour_the_palette_already_holds(self) -> None:
        for tint in (own.TINT, own.REJECT_TINT):
            assert [round(255 * c) for c in matplotlib.colors.to_rgb(tint)] in _palette_rgbs()

    def test_each_dot_sits_on_the_reverting_side_short_of_its_threshold(self, drawn) -> None:
        scene = drawn[11]
        assert _x(scene, "adf-critical") < _x(scene, "adf-dot") < _x(scene, "adf-zero")
        assert _fill(scene, "h-band").x0 <= _x(scene, "h-dot") < _x(scene, "h-half")
        assert _x(scene, "vr-critical") < _x(scene, "vr-dot") < _x(scene, "vr-zero")

    @pytest.mark.parametrize(
        ("moved", "says"),
        [
            ({"adf": {"statistic": -3.0}}, "ADF statistic"),
            ({"adf": {"statistic": -10.0}}, "ADF statistic"),
            ({"adf": {"statistic": 0.5}}, "ADF statistic"),
            ({"vratio": {"statistic": -2.5}}, "variance ratio's statistic"),
            ({"vratio": {"statistic": -10.0}}, "variance ratio's statistic"),
            ({"vratio": {"statistic": 0.5}}, "variance ratio's statistic"),
            ({"hurst": 0.5}, "H below"),
        ],
        ids=[
            "ADF past its critical value",
            "ADF far past it",
            "ADF right of 0",
            "variance ratio past its critical value",
            "variance ratio far past it",
            "variance ratio right of 0",
            "H at 0.5",
        ],
    )
    def test_a_run_that_crosses_or_does_not_lean_is_refused(
        self, run, measured, moved, says
    ) -> None:
        """The title says each statistic leans toward reversion without
        crossing, which would be false of any of these."""
        changes = {
            key: dataclasses.replace(getattr(run, key), **value)
            if isinstance(value, dict)
            else value
            for key, value in moved.items()
        }
        with pytest.raises(ValueError, match=f"Lesson 3's gauges draw .*{re.escape(says)}"):
            _leaning(dataclasses.replace(run, **changes), measured)

    def test_each_gauge_is_drawn_whole_before_the_next_and_its_dot_comes_last(self, drawn) -> None:
        steps = drawn[11].steps
        names = [s.gid.split("-")[0] if not isinstance(s, Label) else None for s in steps]
        drawn_order = [n for n in names if n]
        assert drawn_order == sorted(drawn_order, key=["adf", "h", "vr"].index)
        for name in ("adf", "h", "vr"):
            own = [k for k, n in enumerate(names) if n == name]
            assert steps[own[-1]].gid == f"{name}-dot", name
            label = steps[own[-1] + 1]
            assert isinstance(label, Label) and label.names == f"{name}-dot", name
            assert label.x == _x(drawn[11], f"{name}-dot"), name

    def test_the_header_runs_from_reverting_on_the_left_to_a_random_walk(self, drawn) -> None:
        header = {s.text: s for s in drawn[11].steps if isinstance(s, Label) and "→" in s.text}
        header |= {s.text: s for s in drawn[11].steps if isinstance(s, Label) and "←" in s.text}
        assert header["← more reverting"].x < header["random walk →"].x

    def test_h_has_no_threshold_and_says_so(self, drawn) -> None:
        scene = drawn[11]
        assert not [s for s in scene.strokes if s.gid.startswith("h-") and "critical" in s.gid]
        assert not [f for f in scene.fills if f.gid.startswith("h-") and "zone" in f.gid]
        assert "no test:\nH is an estimate" in scene.labels

    def test_the_labels_follow_the_run_and_the_measurement(self, run, measured) -> None:
        altered = _altered_spread(measured)
        mean, sd = altered.walks.mean(), altered.walks.std(ddof=1)
        scene = _leaning(_altered_lean(run), altered)
        assert scene.labels == [
            "← more reverting",
            "random walk →",
            "ADF statistic",
            "0",
            "reject",
            "−2.700 at 10%",
            "−2.30",
            "H",
            "no test:\nH is an estimate",
            "0.5",
            "±1 SD of a random walk",
            "0.4612",
            "variance ratio\nstatistic",
            "0",
            "reject",
            "−1.96 at 5%, two-sided",
            "−1.50",
        ]
        band = _fill(scene, "h-band")
        original = _fill(_leaning(run, measured), "h-band")
        assert (band.x0, band.x1) != pytest.approx((original.x0, original.x1))
        assert (mean, sd) != pytest.approx((measured.walks.mean(), measured.walks.std(ddof=1))), (
            "the altered measurement moves both"
        )


class TestTheLookAhead:
    """Lesson 5's look-ahead, the run's three rows drawn to scale by date, and
    a dashed schematic pair that carries no dates or numbers."""

    def test_the_run_starts_trading_on_2008_01_02(self, run) -> None:
        dates = [
            str(d.date()) for d in (run.closes.index[0], run.first_position, run.closes.index[-1])
        ]
        assert dates == ["2007-07-23", "2008-01-02", "2012-03-28"], SPEC

    @pytest.mark.parametrize("closes", [1216, 800])
    def test_the_bars_are_to_scale_by_date(self, sources, closes) -> None:
        """The first 800 closes trade from day 100 rather than day 115, so the
        trading bar starts elsewhere."""
        entry, every = sources
        run = stationarity_tests(entry, every[:closes])
        scene = whiteboard._look_ahead(run)
        timeline, measure, trade = (_stroke(scene, g) for g in ("timeline", "measure", "trade"))
        left, right = timeline.x.min(), timeline.x.max()
        assert (measure.x.min(), measure.x.max()) == (left, right)
        assert trade.x.max() == right
        first, last = run.closes.index[0], run.closes.index[-1]
        share = (run.first_position - first) / (last - first)
        assert (trade.x.min() - left) / (right - left) == pytest.approx(share, rel=1e-12)
        assert trade.x.min() > left, "the trading bar does not start on the first close"
        assert scene.labels[:5] == [
            str(first.date()),
            str(last.date()),
            f"measure the half-life: all {closes:,} closes",
            str(run.first_position.date()),
            f"trade with a {run.lookback}-day lookback",
        ]

    def test_the_schematic_pair_splits_the_sample_and_carries_no_number(self, drawn) -> None:
        scene = drawn[12]
        timeline = _stroke(scene, "timeline")
        earlier, after = _stroke(scene, "earlier"), _stroke(scene, "after")
        assert earlier.dashed and after.dashed
        assert earlier.x.min() == timeline.x.min() and after.x.max() == timeline.x.max()
        assert earlier.x.max() == after.x.min(), "the measuring bar ends where trading begins"
        named = [s for s in scene.steps if isinstance(s, Label) and s.names in ("earlier", "after")]
        assert [s.text for s in named] == [
            "measure on earlier days",
            "trade only after",
            "a sketch of the fix, not a run",
        ]
        assert not [s.text for s in named if re.search(r"\d", s.text)]

    def test_the_note_names_the_trading_bar(self, drawn) -> None:
        note = next(s for s in drawn[12].steps if isinstance(s, Label) and "inside" in s.text)
        assert (note.names, note.color) == ("trade", own.LOST)


class TestTenHalfLives:
    """Lesson 5's other limit: a tick every lookback along the closes, the
    title counting the ticks and the label the closes over the unrounded
    half-life, which the post prints as 10.6."""

    def test_the_label_divides_the_closes_by_the_unrounded_half_life(self, run, drawn) -> None:
        assert "10.6 half-lives" in drawn[13].labels, SPEC
        other = whiteboard._half_lives(dataclasses.replace(run, half_life=100.0))
        assert "12.2 half-lives" in other.labels
        assert other.title == "Ten half-lives", "the ticks follow the lookback"

    @pytest.mark.parametrize("lookback", [115, 100])
    def test_a_tick_falls_every_lookback(self, run, lookback) -> None:
        run = dataclasses.replace(run, lookback=lookback)
        scene = _scenes(run)[13]
        sample = _stroke(scene, "sample")
        left, right = sample.x.min(), sample.x.max()
        ticks = [s for s in scene.strokes if s.gid.startswith("tick-")]
        assert len(ticks) == len(run.closes) // lookback
        xs = [_x(scene, t.gid) for t in ticks]
        step = lookback / len(run.closes) * (right - left)
        assert xs == pytest.approx([left + step * k for k in range(1, len(xs) + 1)], abs=1e-12)
        assert scene.title == {115: "Ten half-lives", 100: "Twelve half-lives"}[lookback]
        assert f"{lookback} days" in scene.labels

    def test_the_line_runs_from_the_first_close_to_the_last(self, run) -> None:
        scene = _scenes(_shortened(run, 1000))[13]
        assert scene.labels[:2] == ["2007-07-23", str(run.closes.index[999].date())]


class TestTheTimeline:
    def test_each_gif_takes_the_frames_and_time_it_should(self, frames) -> None:
        assert [len(f) for f in frames] == FRAMES
        assert [sum(frame.ms for frame in f) for f in frames] == MS

    def test_each_gif_opens_on_its_title_alone(self, frames) -> None:
        for steps in frames:
            assert (steps[0].done, steps[0].partial, steps[0].ms) == (0, 0, TITLE_MS)

    def test_each_gif_holds_its_finished_drawing_for_four_seconds(self, drawn, frames) -> None:
        assert HOLD_MS == 4000
        for scene, steps in zip(drawn, frames, strict=True):
            last = steps[-1]
            assert (last.done, last.partial, last.ms) == (len(scene.steps), 0, HOLD_MS)
            assert all(frame.ms < HOLD_MS for frame in steps[:-1])

    def test_strokes_draw_at_ten_frames_a_second_and_labels_pop_in(self, drawn, frames) -> None:
        """Every frame between a GIF's title and its held last frame is a
        stroke's frame of 100 ms or a label's or a tint's single frame of
        350 ms."""
        for scene, steps in zip(drawn, frames, strict=True):
            for frame in steps[1:-1]:
                if frame.partial:
                    assert frame.ms == FRAME_MS
                    continue
                latest = scene.steps[frame.done - 1]
                assert frame.ms == (FRAME_MS if isinstance(latest, Stroke) else LABEL_MS)
        assert FRAME_MS == 100

    def test_a_label_appears_only_once_its_stroke_is_complete(self, drawn, frames) -> None:
        for scene, steps in zip(drawn, frames, strict=True):
            for frame in steps:
                complete = {s.gid for s in scene.steps[: frame.done] if not isinstance(s, Label)}
                for step in scene.steps[: frame.done]:
                    if isinstance(step, Label):
                        assert step.names in complete, step.text

    def test_each_frame_shows_more_than_the_one_before(self, drawn, frames) -> None:
        """Pillow merges two identical frames in a row into one, which would
        cut the frame count the GIF tests pin. So each frame shows a later
        step, or more points of the stroke being drawn, than the frame before
        it, and a stroke drawn in part shows at least two points, because a
        line of one point inks nothing."""
        for scene, steps in zip(drawn, frames, strict=True):
            for before, after in zip(steps, steps[1:], strict=False):
                assert (after.done, after.partial) > (before.done, before.partial), scene.title
                assert after.partial == 0 or after.partial >= 2, scene.title

    def test_a_stroke_grows_frame_by_frame(self, drawn, frames) -> None:
        """The question's price line shows a longer prefix on each of its 14 frames."""
        price = drawn[1].steps[1]
        assert price.gid == "price"
        shown = [f.partial for f in frames[1] if f.done == 1 and f.partial]
        assert len(shown) == price.frames - 1 == 13
        assert shown == sorted(set(shown))
        assert shown[-1] < price.points


class TestTheDrawing:
    def test_ink_only_grows_within_a_scene(self, question) -> None:
        _, images = question
        inked = [_inked(image) for image in images]
        assert inked == sorted(inked)
        assert inked[0] > 0, "the title shows on the first frame"

    def test_a_partial_stroke_inks_less_than_the_whole(self, question) -> None:
        steps, images = question
        price = [k for k, f in enumerate(steps) if f.done == 1 and f.partial]
        whole = next(k for k, f in enumerate(steps) if f.done == 2)
        assert _inked(images[price[0]]) < _inked(images[price[-1]]) < _inked(images[whole])

    def test_each_label_adds_ink_on_the_frame_it_appears(self, drawn, question) -> None:
        steps, images = question
        labels = [i + 1 for i, s in enumerate(drawn[1].steps) if isinstance(s, Label)]
        for done in labels:
            k = next(k for k, f in enumerate(steps) if f.done == done and f.partial == 0)
            assert _inked(images[k]) > _inked(images[k - 1]), done

    def test_every_frame_uses_the_fixed_palette(self, question) -> None:
        _, images = question
        expected = palette(own.INKS).getpalette()
        for image in images:
            assert image.mode == "P"
            assert image.getpalette() == expected

    @pytest.mark.parametrize("inks", [whiteboard.INKS, own.INKS], ids=["shared", "post"])
    def test_the_palette_is_white_and_five_inks_at_five_blends(self, inks) -> None:
        colours = palette(inks).getpalette()
        assert colours[:3] == [255, 255, 255]
        assert len({tuple(colours[i : i + 3]) for i in range(0, len(colours), 3)}) == 26

    def test_no_glyph_falls_back_to_an_empty_box(self, drawn, caplog) -> None:
        """λ, ∼, ≈, −, → and × must all be drawn by some installed font."""
        with warnings.catch_warnings(record=True) as caught, caplog.at_level(logging.WARNING):
            warnings.simplefilter("always")
            for scene in drawn:
                steps = timeline(scene)
                render(scene, steps[-1:], own.INKS)
        messages = [str(w.message) for w in caught] + [r.getMessage() for r in caplog.records]
        assert not [m for m in messages if "glyph" in m.lower()], messages


class TestTheGifs:
    def test_there_are_fourteen_named_for_their_scenes(self, gifs) -> None:
        assert [path.name for path in gifs] == GIFS

    def test_each_is_680_by_320_with_its_frames(self, gifs) -> None:
        for path, count in zip(gifs, FRAMES, strict=True):
            with Image.open(path) as image:
                assert (image.size, image.n_frames) == ((680, 320), count), path.name

    def test_each_loops_forever(self, gifs) -> None:
        for path in gifs:
            with Image.open(path) as image:
                assert image.info["loop"] == 0, path.name

    def test_each_frame_shows_as_long_as_the_timeline_says(self, gifs, frames) -> None:
        for path, steps, total in zip(gifs, frames, MS, strict=True):
            durations = _durations(path)
            assert durations == [f.ms for f in steps], path.name
            assert (durations[-1], sum(durations)) == (HOLD_MS, total), path.name

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_each_draws_in_the_posts_palette(self, gifs) -> None:
        """Every frame maps onto :mod:`chan.palette`'s inks, not the shared ones
        the renderer defaults to."""
        expected = palette(own.INKS).getpalette()
        for path in gifs:
            with Image.open(path) as image:
                assert image.getpalette()[: len(expected)] == expected, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, sources) -> None:
        again = make_usdcad_tests_whiteboards(out_dir=tmp_path, sources=sources)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_these_gifs_and_no_others(self) -> None:
        """A GIF left behind by a renamed or retired scene fails here.

        It reads this module's prefix, because other posts' sketches share the
        folder. ``tests/test_equity_seasonals_whiteboard.py`` holds that every GIF
        there is one that some whiteboard module draws.
        """
        assert {path.name for path in FIGURES_DIR.glob("usdcad_tests_*.gif")} == set(GIFS)

    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, frames) -> None:
        for name, count, steps in zip(GIFS, FRAMES, frames, strict=True):
            committed = FIGURES_DIR / name
            with Image.open(committed) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == ((680, 320), count, 0)
            assert _durations(committed) == [f.ms for f in steps], name

    def test_each_draws_in_the_posts_palette(self) -> None:
        """Checked on every platform, so a GIF left in the shared colours fails
        even where the byte-for-byte comparison below skips."""
        expected = palette(own.INKS).getpalette()
        for name in GIFS:
            with Image.open(FIGURES_DIR / name) as image:
                assert image.getpalette()[: len(expected)] == expected, name

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
            ), f"{path.name}: redraw with: uv run python -m chan.usdcad_tests_whiteboard"


class TestTheCommand:
    def test_it_writes_every_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []

        def draw(**kwargs):
            drawn.append(kwargs)
            return [FIGURES_DIR / name for name in GIFS]

        monkeypatch.setattr(whiteboard, "make_usdcad_tests_whiteboards", draw)
        main()
        assert drawn == [{}]
        out = capsys.readouterr().out
        assert out.splitlines() == [f"wrote {FIGURES_DIR / name}" for name in GIFS]

    def test_drawing_with_no_out_dir_writes_the_committed_paths(self, monkeypatch, sources) -> None:
        saved = []
        monkeypatch.setattr(whiteboard, "read_sources", lambda: sources)
        monkeypatch.setattr(whiteboard, "spread", lambda closes: spread(closes, paths=FEW_PATHS))
        monkeypatch.setattr(whiteboard, "render", lambda scene, frames, inks: [Image.new("P", (1, 1))])
        monkeypatch.setattr(Image.Image, "save", lambda self, path, **kw: saved.append(path))
        paths = make_usdcad_tests_whiteboards()
        assert paths == saved == [FIGURES_DIR / name for name in GIFS]

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage of USDCAD saved 2018-10-13"),
            WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2008-01-02"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(whiteboard, "make_usdcad_tests_whiteboards", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_the_guard_refuses_before_any_walk_is_drawn(self, monkeypatch, tmp_path) -> None:
        """The run comes first, so a flagged window stops the draw before the
        walks, which take most of its time, are drawn for nothing."""

        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2009-01-02")

        def no_walks(*_a, **_k):
            raise AssertionError("the walks were drawn before the guard ran")

        monkeypatch.setattr(usdcad_mean_reversion, "refuse_window_crossing_a_break", refuse)
        monkeypatch.setattr(whiteboard, "spread", no_walks)
        with pytest.raises(WindowCrossesScaleBreak):
            make_usdcad_tests_whiteboards(out_dir=tmp_path)

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2009-01-02")

        monkeypatch.setattr(usdcad_mean_reversion, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale on 2009-01-02"):
            make_usdcad_tests_whiteboards(out_dir=tmp_path)
