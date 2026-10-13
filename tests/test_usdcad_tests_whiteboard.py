"""The pins for the nine whiteboard GIFs in the post on mean reversion on USD.CAD.

Six GIFs sketch the scenes of the post's section "The tests and the file", two
sketch its Lesson 1 and one its Lesson 2. Each sits right after the text it
draws. The first
six are schematic, so what is pinned for every GIF is what a reader takes from
it: which scenes there are and in which order the post reads them, what each
one says and draws, that a label never appears before the stroke it names,
that no label touches a line, how long each GIF shows before it loops, and
each file's size, frame count and loop.

Labels in five scenes quote the run. The half-life scene and the linear rule's
warning print the lookback, the half-life rounded, and the count of closes.
Chan's reading prints the three critical values and the ADF statistic, and
places each on a line drawn to scale. The fingerprint prints the count of
closes, the ADF statistic, the AR(1) estimate, the variance ratio's p-value
and the half-life. One row apart prints the count of closes and each toolbox's
row count and ADF statistic, and starts each bar at the cell of the first day
its regression fits. All of them are read from the run rather than written in,
and the tests below hand the scenes a run with other figures to prove it. The
numbers come from the vintage and the specification
``tests/test_usdcad_mean_reversion.py`` names as its ``SPEC``, which failure
messages here carry:
``pythoncodesanddata/inputData_USDCAD.csv``, vendor ``chan-py``, basis
``raw``, saved 2018-10-13, its 16:59 bar of each day, 1,216 closes, a
lookback of 115 days, an ADF statistic of −1.840744 against critical values of
−3.458, −2.871 and −2.594, an AR(1) estimate of 0.994120, a variance ratio
p-value of 0.367281 and a half-life of 115.209794 days. ``adfuller`` at the
same lag fits 1,214 rows from day 3, counting the first close as day 1, and
gives −1.843018, where jplv7's ``adf`` fits 1,213 from day 4.

Two draws on one machine give the same bytes, and a test holds that. Whether a
committed GIF equals a fresh draw depends on the font, because the hand font
is whichever one is installed and font rasterising varies by platform. So that
comparison runs only on macOS arm64 with Comic Sans MS installed, where the
committed files were drawn, and skips elsewhere with the reason. The frame
count, the size, the loop and the timing of each committed file are pinned
everywhere.
"""

from __future__ import annotations

import dataclasses
import hashlib
import logging
import platform
import re
import warnings

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import usdcad_mean_reversion
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR
from chan.series import WindowCrossesScaleBreak
from chan.usdcad_mean_reversion import read_sources, stationarity_tests
from chan.usdcad_tests_whiteboard import (
    FRAME_MS,
    HEIGHT,
    HOLD_MS,
    LABEL_MS,
    TITLE_MS,
    WIDTH,
    Label,
    Stroke,
    clearances,
    hand_font,
    main,
    make_usdcad_tests_whiteboards,
    palette,
    render,
    scenes,
    timeline,
)
from chan.vintage import VintageUnavailable
from tests.test_usdcad_mean_reversion import SPEC

TITLES = [
    "The question",
    "ADF",
    "Hurst",
    "Variance ratio",
    "Half-life",
    "The linear rule",
    "Chan’s reading",
    "The fingerprint",
    "One row apart",
]

GIFS = [
    "usdcad_tests_question.gif",
    "usdcad_tests_adf.gif",
    "usdcad_tests_hurst.gif",
    "usdcad_tests_variance_ratio.gif",
    "usdcad_tests_half_life.gif",
    "usdcad_tests_linear_rule.gif",
    "usdcad_tests_no_rejection.gif",
    "usdcad_tests_fingerprint.gif",
    "usdcad_tests_one_row.gif",
]

#: Each scene's strokes, by their ids, in the order they are drawn.
STROKES = [
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
]

LABELS = [
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
]

#: The frames each GIF takes, and how long one pass shows, in milliseconds.
FRAMES = [29, 31, 29, 30, 29, 32, 44, 77, 58]
MS = [7350, 7800, 7600, 7700, 7850, 7900, 10850, 14900, 13500]

#: How far, in pixels, every label and title must sit from the nearest stroke.
#: The sketch's wobble moves a line a pixel or two off its points, so this
#: leaves room for it with a visible gap to spare.
CLEAR_PX = 10
#: Labels that state something about the whole scene rather than name a
#: stroke. Each stands apart from every stroke, by at least
#: :data:`APART_PX`, so it cannot be read as one curve's label. The Hurst
#: formula once sat beside the end of the lower green curve, 12 pixels from
#: it, and read as that curve's label. The fingerprint's margin note is about
#: the four values together, so it stands apart from the last check mark.
STATEMENTS = {"λ < 0", r"variance $\sim \tau^{2H}$", "closes × a constant would match too"}
APART_PX = 25
#: How far, in pixels, every label and title must sit inside the frame's edge.
INSIDE_PX = 5


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def run(sources):
    return stationarity_tests(*sources)


@pytest.fixture(scope="module")
def drawn(run):
    return scenes(run)


@pytest.fixture(scope="module")
def frames(drawn):
    return [timeline(scene) for scene in drawn]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, sources):
    return make_usdcad_tests_whiteboards(
        out_dir=tmp_path_factory.mktemp("whiteboards"), sources=sources
    )


@pytest.fixture(scope="module")
def question(drawn):
    """The first scene drawn, which is enough to watch strokes and labels."""
    steps = timeline(drawn[0])
    return steps, render(drawn[0], steps)


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
    def test_there_are_nine_in_the_order_the_post_reads_them(self, drawn) -> None:
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

    def test_every_label_names_a_stroke_drawn_before_it(self, drawn) -> None:
        for scene in drawn:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if isinstance(s, Stroke)]
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


class TestTheLabelsStayClearOfTheLines:
    def test_every_label_and_title_clears_every_stroke(self, drawn) -> None:
        for scene in drawn:
            found = clearances(scene)
            assert sorted(found) == sorted([*scene.labels, scene.title])
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
        hurst = drawn[2]
        start = next(s for s in hurst.strokes if s.gid == "start")
        formula = next(s for s in hurst.steps if isinstance(s, Label) and s.math)
        assert formula.x <= start.x[0]
        assert formula.y < min(float(s.y.min()) for s in hurst.strokes)

    def test_every_label_and_title_sits_inside_the_board(self, drawn) -> None:
        """Clearance from the strokes says nothing about the frame's edge, and a
        wider font can push a label at the right end off the GIF."""
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

    def test_the_measure_sees_a_label_on_a_line(self, drawn) -> None:
        """A label moved onto its own stroke reads as touching, so the two
        tests above can fail."""
        hurst = drawn[2]
        steps = tuple(
            dataclasses.replace(s, x=0.6, y=2.0) if isinstance(s, Label) and s.math else s
            for s in hurst.steps
        )
        moved = dataclasses.replace(hurst, steps=steps)
        assert clearances(moved)[r"variance $\sim \tau^{2H}$"] < 0


class TestTheNumbersComeFromTheRun:
    def test_the_run_has_1216_closes_and_a_115_day_lookback(self, run) -> None:
        assert (len(run.closes), run.lookback) == (1216, 115), SPEC
        assert round(run.half_life) == 115, SPEC

    def test_the_half_life_scene_prints_the_runs_lookback(self, run) -> None:
        other = dataclasses.replace(run, lookback=100)
        assert "≈ 100 days" in scenes(other)[4].labels
        assert "≈ 115 days" not in scenes(other)[4].labels

    def test_the_warning_prints_the_runs_lookback_and_closes(self, run) -> None:
        other = dataclasses.replace(_shortened(run, 1000), lookback=100)
        assert scenes(other)[5].labels[-1] == "100 days measured on all 1,000 closes"

    def test_the_gifs_are_drawn_from_the_sources_handed_in(
        self, monkeypatch, tmp_path, sources
    ) -> None:
        """The first 800 closes have a half-life that rounds to 100 days, as
        ``tests/test_usdcad_mean_reversion_figures.py`` pins, so a GIF that
        read the file or wrote 115 in would fail here."""
        seen = []
        original = whiteboard.scenes

        def record(run):
            seen.append((run.lookback, len(run.closes)))
            return original(run)[4:5]

        monkeypatch.setattr(whiteboard, "scenes", record)
        entry, closes = sources
        make_usdcad_tests_whiteboards(out_dir=tmp_path, sources=(entry, closes[:800]))
        assert seen == [(100, 800)]


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
    to another value."""
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
        scene = scenes(run)[6]
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
        reading = drawn[6]
        assert _x(reading, "statistic") > _x(reading, "tick-10")

    def test_a_statistic_below_the_10_percent_value_moves_the_dot_left_of_it(self, run) -> None:
        reading = scenes(_altered(run, statistic=-3.0))[6]
        assert _x(reading, "tick-5") < _x(reading, "statistic") < _x(reading, "tick-10")

    def test_the_shaded_zone_runs_from_the_line_start_to_the_10_percent_tick(self, drawn) -> None:
        reading = drawn[6]
        zone = next(s for s in reading.strokes if s.gid == "zone")
        line = next(s for s in reading.strokes if s.gid == "line")
        assert zone.x.min() == line.x.min()
        assert zone.x.max() == pytest.approx(_x(reading, "tick-10"))
        assert zone.y.min() > line.y[0], "the zone sits above the line"

    def test_the_arrow_runs_from_the_dot_to_the_10_percent_tick(self, drawn) -> None:
        reading = drawn[6]
        arrow = next(s for s in reading.strokes if s.gid == "needs")
        dot, edge = _x(reading, "statistic"), _x(reading, "tick-10")
        assert dot - 0.5 < arrow.x[0] < dot
        tip = int(np.argmin(arrow.x))
        assert edge < arrow.x[tip] < edge + 0.5

    def test_each_tick_is_labelled_with_its_value_and_level(self, drawn) -> None:
        reading = drawn[6]
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
        assert scenes(_altered(run))[6].labels == [
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
        """Every value is followed at once by a green check, and nothing else
        is checked."""
        steps = drawn[7].steps
        values = [
            k for k, s in enumerate(steps) if isinstance(s, Label) and self.VALUE.match(s.text)
        ]
        checks = [
            k for k, s in enumerate(steps) if isinstance(s, Stroke) and s.gid.startswith("check-")
        ]
        assert len(values) == 4
        assert checks == [k + 1 for k in values]
        assert {steps[k].color for k in checks} == {whiteboard.GOOD}

    def test_each_value_sits_beside_the_calculation_that_gives_it(self, drawn) -> None:
        steps = drawn[7].steps
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
        fingerprint = drawn[7]
        csv = next(s for s in fingerprint.strokes if s.gid == "csv")
        arrows = [s for s in fingerprint.strokes if s.gid.startswith("to-")]
        assert len(arrows) == 3
        for arrow in arrows:
            assert arrow.x[0] > csv.x.max()
            assert csv.y.min() < arrow.y[0] < csv.y.max()

    def test_the_labels_follow_the_runs_figures(self, run) -> None:
        labels = scenes(_altered(run))[7].labels
        assert [t for t in labels if self.VALUE.match(t) or "closes" in t] == [
            "1,000 closes",
            "−2.200000",
            "0.987650",
            "0.050000",
            "80.123456",
            "closes × a constant would match too",
        ]


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
        one_row = drawn[8]
        assert len(_cells(one_row)) == 7
        assert one_row.labels[:8] == ["1", "2", "3", "4", "5", "6", "…", "1,216"], SPEC
        last = _stroke(one_row, "last")
        assert last.x.min() > _cells(one_row)[-1]

    @pytest.mark.parametrize("moved", [False, True])
    def test_each_bar_starts_at_the_cell_of_its_first_day(self, run, moved) -> None:
        """The moved run drops three and four rows, so its bars start on days 4
        and 5 and three days are greyed."""
        run = _shortened(run, 1000, (3, 4)) if moved else run
        one_row = scenes(run)[8]
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
        one_row = drawn[8]
        edges = _cells(one_row)
        grey = _stroke(one_row, "grey")
        assert grey.x.max() == pytest.approx(edges[2]), "days 1 and 2"
        assert grey.color == whiteboard.MUTED

    def test_both_bars_end_at_the_last_cell_and_adfuller_runs_above(self, drawn) -> None:
        one_row = drawn[8]
        last = _stroke(one_row, "last")
        adfuller, jplv7 = _stroke(one_row, "adfuller"), _stroke(one_row, "jplv7")
        assert adfuller.x.max() == jplv7.x.max() == last.x.max()
        assert np.median(adfuller.y) > np.median(jplv7.y)
        assert last.y.min() > adfuller.y.max()

    def test_each_value_sits_at_the_end_of_its_bar(self, drawn) -> None:
        one_row = drawn[8]
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
        one_row = drawn[8]
        edges = _cells(one_row)
        mark = one_row.steps[-2]
        assert mark.gid == "one-row" and mark.color == whiteboard.ACCENT
        day = run.adfuller_first_day
        assert (mark.x.min(), mark.x.max()) == pytest.approx((edges[day - 1], edges[day]))
        note = one_row.steps[-1]
        assert (note.text, note.names, note.color) == ("the one row", "one-row", mark.color)
        assert note.x == pytest.approx((edges[day - 1] + edges[day]) / 2)

    def test_the_labels_follow_the_runs_figures(self, run) -> None:
        labels = scenes(_altered(run))[8].labels
        assert labels[7] == "1,000"
        assert labels[9:13] == [
            "adfuller, 998 rows",
            "−2.500000",
            "jplv7 adf, 997 rows",
            "−2.200000",
        ]

    @pytest.mark.parametrize(
        "drops",
        [(2, 4), (3, 3), (4, 3), (0, 1), (6, 7)],
        ids=["two apart", "together", "swapped", "from day 1", "past the row"],
    )
    def test_a_run_the_words_would_misdescribe_is_refused(self, run, drops) -> None:
        with pytest.raises(ValueError, match="one day later"):
            scenes(_shortened(run, 1000, drops))


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
        stroke's frame of 100 ms or a label's single frame of 350 ms."""
        for scene, steps in zip(drawn, frames, strict=True):
            for frame in steps[1:-1]:
                if frame.partial:
                    assert frame.ms == FRAME_MS
                    continue
                latest = scene.steps[frame.done - 1]
                assert frame.ms == (LABEL_MS if isinstance(latest, Label) else FRAME_MS)
        assert FRAME_MS == 100

    def test_a_label_appears_only_once_its_stroke_is_complete(self, drawn, frames) -> None:
        for scene, steps in zip(drawn, frames, strict=True):
            for frame in steps:
                complete = {s.gid for s in scene.steps[: frame.done] if isinstance(s, Stroke)}
                for step in scene.steps[: frame.done]:
                    if isinstance(step, Label):
                        assert step.names in complete, step.text

    def test_a_stroke_grows_frame_by_frame(self, drawn, frames) -> None:
        """The question's price line shows a longer prefix on each of its 14 frames."""
        price = drawn[0].steps[1]
        assert price.gid == "price"
        shown = [f.partial for f in frames[0] if f.done == 1 and f.partial]
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
        labels = [i + 1 for i, s in enumerate(drawn[0].steps) if isinstance(s, Label)]
        for done in labels:
            k = next(k for k, f in enumerate(steps) if f.done == done and f.partial == 0)
            assert _inked(images[k]) > _inked(images[k - 1]), done

    def test_every_frame_uses_the_fixed_palette(self, question) -> None:
        _, images = question
        expected = palette().getpalette()
        for image in images:
            assert image.mode == "P"
            assert image.getpalette() == expected

    def test_the_palette_is_white_and_five_inks_at_five_blends(self) -> None:
        colours = palette().getpalette()
        assert colours[:3] == [255, 255, 255]
        assert len({tuple(colours[i : i + 3]) for i in range(0, len(colours), 3)}) == 26

    def test_no_glyph_falls_back_to_an_empty_box(self, drawn, caplog) -> None:
        """λ, ∼, ≈, −, → and × must all be drawn by some installed font."""
        with warnings.catch_warnings(record=True) as caught, caplog.at_level(logging.WARNING):
            warnings.simplefilter("always")
            for scene in drawn:
                steps = timeline(scene)
                render(scene, steps[-1:])
        messages = [str(w.message) for w in caught] + [r.getMessage() for r in caplog.records]
        assert not [m for m in messages if "glyph" in m.lower()], messages


class TestTheGifs:
    def test_there_are_nine_named_for_their_scenes(self, gifs) -> None:
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

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, sources) -> None:
        again = make_usdcad_tests_whiteboards(out_dir=tmp_path, sources=sources)
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_old_combined_gif_is_gone(self) -> None:
        assert not (FIGURES_DIR / "usdcad_tests_whiteboard.gif").exists()

    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, frames) -> None:
        for name, count, steps in zip(GIFS, FRAMES, frames, strict=True):
            committed = FIGURES_DIR / name
            with Image.open(committed) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == ((680, 320), count, 0)
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
        monkeypatch.setattr(whiteboard, "render", lambda scene, frames: [Image.new("P", (1, 1))])
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

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_USDCAD.csv changes scale on 2009-01-02")

        monkeypatch.setattr(usdcad_mean_reversion, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale on 2009-01-02"):
            make_usdcad_tests_whiteboards(out_dir=tmp_path)
