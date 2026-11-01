"""The pins for the two whiteboard GIFs in the XLE against USO post.

One sketches Lesson 1's claim that the script's front moves to the next
contract 10 rows before the old one's last price, so on those rows the front
is the second-nearest contract the file prices. The other sketches Lesson 5's
split: on the contango days the roll return the ratio implies comes close to
USO's log move, and on the backwardation days USO's log move far exceeds it.
What is pinned is what a reader takes from each.

1. The handover sketch reads its dates, row counts and day counts from
   :class:`chan.xle_uso_roll_return_whiteboard.Handover`. The test derives
   them again from :func:`chan.xle_uso_roll_return.front_windows` and, for the
   734 and 641, by comparing each day's ratio with the two nearest priced
   contracts' as ``tests/test_xle_uso_roll_return.py`` does, rather than
   trusting the sketch's own count. Every bar sits on the axis at its own
   trading days.
2. The split sketch reads its values from
   :class:`chan.xle_uso_roll_return_whiteboard.Split`, which the test derives
   again from :func:`chan.xle_uso_roll_return.by_view`, at the post's
   precision. Every bar ends at an affine function of its value on one
   scale.

A made-up set of figures for each shows the words and the bars follow the run.
The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, both
sketches' slower pace, that two draws give the same bytes, and that each
committed GIF is a fresh draw, a comparison that runs only on macOS arm64
with Comic Sans MS, as ``tests/test_usdcad_tests_whiteboard.py`` explains.
The check that ``docs/figures`` holds exactly the GIFs the modules draw lives
in ``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS`
from here.
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

from chan import usdcad_tests_whiteboard as whiteboard
from chan import xle_uso_roll_return as trade
from chan import xle_uso_roll_return_whiteboard as sketches
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, INK, MUTED
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
from chan.xle_uso_roll_return_whiteboard import (
    PER_LOG,
    ZERO_Y,
    Handover,
    Split,
    bar_y,
    day_x,
    gif_name,
    main,
    make_xle_uso_roll_return_whiteboards,
    scenes,
    sketch_timeline,
)

POST = REPO_ROOT / "blog" / "xle-uso-roll-return-lessons.md"

#: Every GIF in the order :func:`make_xle_uso_roll_return_whiteboards` writes them.
GIFS = [
    "xle_uso_roll_return_sketch_front_handover.gif",
    "xle_uso_roll_return_sketch_roll_vs_uso.gif",
]

#: The list each GIF follows, by its opening words.
FOLLOWS = (
    "1. **XLE stands in for crude’s spot price.**",
    "1. **On the contango days, the implied roll return comes close to USO’s fall.**",
)

SPEC = (
    "USO and XLE from inputData_ETF.mat, chan-mat, adjusted, saved 2012-04-10, and the CL "
    "strip from inputDataDaily_CL_20120502.mat, chan-mat, raw, saved 2012-05-03; the "
    "script's front from 40 to 10 rows before each contract's last priced row"
)

HANDOVER_LABELS = [
    "Oct 2006",
    "Jan 2007",
    "last price 12-19",
    "CL-2007F front, 10-20 to 12-05: 31 rows",
    "CL-2007G front, 12-06 to 01-05: 20 rows",
    "the February 2007 contract",
    "CL-2007F still priced: 10 rows",
    "so the front is the second-nearest",
    "of the 1,375 days with a ratio, the front is the nearest priced contract",
    "on 734 days and the second-nearest on 641",
]

SPLIT_LABELS = [
    "1,128 days earning on contango",
    "USO",
    "−0.838762",
    "roll return",
    "−0.766081",
    "close to",
    "USO’s fall",
    "244 days earning on backwardation",
    "USO",
    "0.532304",
    "roll return",
    "0.072380",
    "USO’s move beyond",
    "the roll return",
    "roll return: 12 · ln(front / back) / 252, each group’s days summed,",
    "on the ratio that set the view",
]

#: The two lines beside the contango roll bar, which read as one phrase.
CLOSE_TO = ("close to", "USO’s fall")

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def sources():
    return trade.read_sources()


@pytest.fixture(scope="module")
def handover() -> Handover:
    return Handover.from_run()


@pytest.fixture(scope="module")
def split() -> Split:
    return Split.from_run()


@pytest.fixture(scope="module")
def every(handover, split):
    return scenes(handover, split)


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, handover, split):
    return make_xle_uso_roll_return_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"), handover=handover, split=split
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text, nth: int = 0):
    return [s for s in scene.steps if isinstance(s, Label) and s.text == text][nth]


def _labels_of(scene, gid):
    return [s.text for s in scene.steps if isinstance(s, Label) and s.names == gid]


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
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, every) -> None:
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

    def test_neither_draws_a_tint(self, every) -> None:
        """No pale tint, so none needs the green edge the shared rules ask of one."""
        assert not [fill for scene in every for fill in scene.fills]


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
            frames = sketch_timeline(scene)
            assert (frames[0].done, frames[0].ms) == (0, TITLE_MS)
            assert frames[-1].ms == sketches.PACED_HOLD_MS
        assert sketches.PACED_HOLD_MS > HOLD_MS

    def test_both_sketches_build_slowly_and_hold_twelve_seconds(self, every) -> None:
        """Each label alone for 0.9 s and the drawing for 12 s, the equity
        post's slow pace, in both sketches."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == ("front_handover", "roll_vs_uso")
        for scene in every:
            frames = sketch_timeline(scene)
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            assert labels, scene.slug
            assert {f.ms for f in labels} == {sketches.PACED_LABEL_MS}, scene.slug
            assert [(f.done, f.partial) for f in frames] == [
                (f.done, f.partial) for f in timeline(scene)
            ], scene.slug
            assert frames != timeline(scene), scene.slug

    def test_an_unpaced_scene_keeps_the_usual_pace(self, every, monkeypatch) -> None:
        monkeypatch.setattr(sketches, "PACED", ())
        for scene in every:
            assert sketch_timeline(scene) == timeline(scene)

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, handover, split) -> None:
        again = make_xle_uso_roll_return_whiteboards(
            out_dir=tmp_path, handover=handover, split=split
        )
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_the_figures_folder_holds_exactly_this_modules_gifs_under_its_prefix(self) -> None:
        found = {path.name for path in FIGURES_DIR.glob(f"{sketches.GIF_PREFIX}*.gif")}
        assert found == set(GIFS)

    def test_the_prefix_is_clear_of_the_posts_chart(self) -> None:
        names = {path.name for path in FIGURES_DIR.iterdir()} - set(GIFS)
        assert not [name for name in names if name.startswith(sketches.GIF_PREFIX)]
        assert (FIGURES_DIR / "xle_uso_roll_return.png").exists()

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
            ), f"{path.name}: redraw with: uv run python -m chan.xle_uso_roll_return_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_each_gif_follows_the_list_it_draws(self) -> None:
        paragraphs = _paragraphs()
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_sits_in_its_lesson(self) -> None:
        text = POST.read_text(encoding="utf-8")
        handover, split = (text.index(f"(../docs/figures/{name})") for name in GIFS)
        lessons = [text.index(f"## Lesson {n}:") for n in (1, 2, 5)]
        cannot = text.index("## What this replication cannot say")
        assert lessons[0] < handover < lessons[1]
        assert lessons[2] < split < cannot

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        for scene in every:
            alt, at = _alt(scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2

    def test_each_alt_text_names_its_pace(self, every) -> None:
        for scene in every:
            alt = _alt(scene)
            assert "drawn slowly" in alt and "twelve seconds" in alt, scene.slug

    def test_the_footer_links_the_sketch_code_and_its_tests(self) -> None:
        footer = POST.read_text(encoding="utf-8").rstrip().splitlines()[-1]
        base = "https://github.com/l3a0/quantitative-trading/blob/main/"
        code = f"[the whiteboard sketches]({base}src/chan/xle_uso_roll_return_whiteboard.py)"
        tests = f"[what the sketches draw]({base}tests/test_xle_uso_roll_return_whiteboard.py)"
        assert code in footer and tests in footer

    def test_the_module_says_neither_sketch_is_schematic(self) -> None:
        doc = " ".join((sketches.__doc__ or "").split())
        assert "Neither sketch is schematic." in doc


# --- Lesson 1: the front moves on before the last price -----------------------


class TestTheHandover:
    def test_it_is_the_runs_first_two_front_windows(self, sources, handover) -> None:
        """Read again from :func:`chan.xle_uso_roll_return.front_windows`."""
        contracts = sources[2].contracts
        old, new = trade.front_windows(contracts)[:2]
        day = lambda row: str(contracts.index[row].date())  # noqa: E731
        assert (handover.old, handover.new) == ("CL-2007F", "CL-2007G"), SPEC
        assert (contracts.columns[old.column], contracts.columns[new.column]) == (
            handover.old,
            handover.new,
        )
        assert (handover.old_first, handover.old_last, handover.old_expiry) == (
            day(old.first),
            day(old.last),
            day(old.expiry),
        )
        assert (handover.new_first, handover.new_last) == (day(new.first), day(new.last))
        assert (handover.old_first, handover.old_last, handover.old_expiry) == (
            "2006-10-20",
            "2006-12-05",
            "2006-12-19",
        ), SPEC
        assert (handover.new_first, handover.new_last) == ("2006-12-06", "2007-01-05"), SPEC
        assert (handover.old_rows, handover.new_rows) == (len(old.rows), len(new.rows)) == (31, 20)

    def test_the_new_front_starts_on_the_row_after_the_old_ends(self, sources, handover) -> None:
        """The 40-row start binds only for CL-2007F: CL-2007G's falls on
        2006-11-17, inside CL-2007F's window, so it starts the row after."""
        contracts = sources[2].contracts
        old, new = trade.front_windows(contracts)[:2]
        assert old.first == old.expiry - trade.FRONT_START
        assert new.first == old.last + 1 > new.expiry - trade.FRONT_START
        assert str(contracts.index[new.expiry - trade.FRONT_START].date()) == "2006-11-17"

    def test_the_old_contract_is_priced_on_10_of_the_new_fronts_rows(
        self, sources, handover
    ) -> None:
        contracts = sources[2].contracts
        new = trade.front_windows(contracts)[1]
        column = contracts[handover.old].iloc[new.rows]
        assert handover.overlap == int(column.notna().sum()) == trade.FRONT_END == 10
        assert column.notna().to_numpy().tolist() == [True] * 10 + [False] * 10
        assert handover.overlap_last == handover.old_expiry

    def test_the_front_is_the_nearest_on_734_days_and_the_second_on_641(
        self, sources, handover
    ) -> None:
        """Derived as ``tests/test_xle_uso_roll_return.py`` does, from which of
        each day's two nearest priced contracts gives the day's ratio."""
        _, closes, strip = sources
        contracts = strip.contracts
        result = trade.arbitrage(closes, trade.front_ratio(contracts))
        places = []
        for d, value in zip(result.days, result.ratio, strict=True):
            if not np.isfinite(value):
                continue
            row = contracts.loc[d].to_numpy()
            priced = np.flatnonzero(np.isfinite(row))
            nearest = [row[priced[k] + 1] / row[priced[k]] for k in (0, 1)]
            assert (nearest[0] == value) != (nearest[1] == value)
            places.append(1 if nearest[0] == value else 2)
        assert (handover.with_ratio, handover.nearest, handover.second) == (
            len(places),
            places.count(1),
            places.count(2),
        )
        assert (handover.with_ratio, handover.nearest, handover.second) == (1375, 734, 641), SPEC

    def test_the_axis_is_the_strips_trading_days(self, sources, handover) -> None:
        index = sources[2].contracts.index
        axis = index[(index >= sketches.AXIS_FROM) & (index <= sketches.AXIS_TO)]
        assert handover.days == tuple(str(d.date()) for d in axis)
        assert handover.days[0] < handover.old_first and handover.new_last < handover.days[-1]

    def test_a_front_past_the_second_nearest_is_refused(self, sources) -> None:
        """The closing note names two places, so a third would make it false."""
        _, closes, strip = sources
        contracts = strip.contracts.copy()
        old, new = trade.front_windows(contracts)[:2]
        # Price CL-2007F until 15 rows past CL-2007G's last price, so on
        # CL-2007H's first front rows both are still priced.
        first = int(np.flatnonzero(contracts.iloc[:, old.column].notna())[0])
        contracts.iloc[first : new.expiry + 15, old.column] = 1.0
        with pytest.raises(ValueError, match="second-nearest"):
            Handover.from_contracts(closes, contracts)


#: A made-up handover, so the words that should follow the run do.
OTHER_HANDOVER = Handover(
    days=("2001-01-02", "2001-01-03", "2001-01-04", "2001-01-05", "2001-01-08", "2001-01-09"),
    old="CL-2001H",
    new="CL-2001J",
    old_first="2001-01-03",
    old_last="2001-01-04",
    old_rows=2,
    old_expiry="2001-01-08",
    new_first="2001-01-05",
    new_last="2001-01-08",
    new_rows=3,
    overlap=2,
    with_ratio=2345,
    nearest=1234,
    second=1111,
)


class TestTheHandoverSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "The front moves on before the last price"
        assert every[0].labels == HANDOVER_LABELS

    def test_its_words_follow_the_run(self) -> None:
        assert scenes(OTHER_HANDOVER, Split(1, -0.1, -0.1, 1, 0.1, 0.1))[0].labels == [
            "Jan 2001",
            "Jan 2001",
            "last price 01-08",
            "CL-2001H front, 01-03 to 01-04: 2 rows",
            "CL-2001J front, 01-05 to 01-08: 3 rows",
            "the April 2001 contract",
            "CL-2001H still priced: 2 rows",
            "so the front is the second-nearest",
            "of the 2,345 days with a ratio, the front is the nearest priced contract",
            "on 1,234 days and the second-nearest on 1,111",
        ]

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert {s.gid: s.color for s in scene.strokes} == {
            "axis": MUTED,
            "old-priced": MUTED,
            "old-front": INK,
            "new-front": INK,
            "overlap": ACCENT,
        }
        assert [_label(scene, text).color for text in HANDOVER_LABELS] == [
            MUTED,
            MUTED,
            MUTED,
            INK,
            INK,
            MUTED,
            ACCENT,
            ACCENT,
            INK,
            INK,
        ]

    def test_each_label_names_the_stroke_it_sits_beside(self, every) -> None:
        scene = every[0]
        assert _labels_of(scene, "axis") == HANDOVER_LABELS[:2]
        assert _labels_of(scene, "old-priced") == [HANDOVER_LABELS[2]]
        assert _labels_of(scene, "old-front") == [HANDOVER_LABELS[3]]
        assert _labels_of(scene, "new-front") == HANDOVER_LABELS[4:6]
        assert _labels_of(scene, "overlap") == HANDOVER_LABELS[6:]

    def test_each_label_sits_beside_what_it_names(self, every) -> None:
        """Which words sit by which bar is the sketch's meaning, so each
        label's side of its stroke is held, not only the stroke it names."""
        scene = every[0]
        old, priced = _stroke(scene, "old-front"), _stroke(scene, "old-priced")
        new, brace = _stroke(scene, "new-front"), _stroke(scene, "overlap")
        old_label, new_label, month = (_label(scene, t) for t in HANDOVER_LABELS[3:6])
        assert old_label.ha == "left" and old.x.min() <= old_label.x < old.x.max()
        assert old_label.y > sketches.OLD_Y
        assert new_label.ha == month.ha == "right"
        assert new_label.x == month.x < new.x.min()
        assert new_label.y == sketches.NEW_Y > month.y > sketches.AXIS_Y
        last = _label(scene, HANDOVER_LABELS[2])
        assert last.x > priced.x.max() and last.y == sketches.OLD_Y
        for text in HANDOVER_LABELS[6:8]:
            label = _label(scene, text)
            assert label.ha == "right" and label.x < brace.x.min(), text
            assert sketches.NEW_Y < label.y < sketches.OLD_Y, text
        start, end = (_label(scene, t) for t in HANDOVER_LABELS[:2])
        assert (start.x, end.x) == (sketches.AXIS_X0, sketches.AXIS_X1)
        assert start.y == end.y < sketches.AXIS_Y
        assert _label(scene, HANDOVER_LABELS[-1]).y < start.y

    def test_every_bar_sits_at_its_own_trading_days(self, every, handover) -> None:
        scene = every[0]
        x = lambda date: day_x(handover, date)  # noqa: E731
        for gid, first, last in (
            ("old-front", handover.old_first, handover.old_last),
            ("new-front", handover.new_first, handover.new_last),
            ("overlap", handover.new_first, handover.old_expiry),
        ):
            stroke = _stroke(scene, gid)
            assert (stroke.x.min(), stroke.x.max()) == pytest.approx((x(first), x(last))), gid
        priced = _stroke(scene, "old-priced")
        assert (priced.x.min(), priced.x.max()) == pytest.approx(
            (sketches.AXIS_X0, x(handover.old_expiry))
        )

    def test_day_x_is_affine_in_the_count_of_trading_days(self, handover) -> None:
        xs = np.array([day_x(handover, d) for d in handover.days])
        assert (xs[0], xs[-1]) == pytest.approx((sketches.AXIS_X0, sketches.AXIS_X1))
        assert np.diff(xs) == pytest.approx(np.full(len(xs) - 1, xs[1] - xs[0]))

    def test_the_old_contract_sits_on_one_row_and_the_new_on_a_lower_one(self, every) -> None:
        scene = every[0]
        old, priced, new = (_stroke(scene, g) for g in ("old-front", "old-priced", "new-front"))
        assert set(old.y) == set(priced.y) == {sketches.OLD_Y}
        assert set(new.y) == {sketches.NEW_Y} and sketches.NEW_Y < sketches.OLD_Y
        assert old.width > priced.width and new.width == old.width
        brace = _stroke(scene, "overlap")
        assert sketches.NEW_Y < brace.y.min() < brace.y.max() < sketches.OLD_Y

    def test_the_old_front_ends_where_its_price_still_runs(self, every, handover) -> None:
        """The thick bar stops short of the grey one's end, and the brace spans
        exactly the grey stretch past it, where the new bar runs below."""
        scene = every[0]
        old, priced = _stroke(scene, "old-front"), _stroke(scene, "old-priced")
        brace, new = _stroke(scene, "overlap"), _stroke(scene, "new-front")
        assert old.x.max() < brace.x.min() < brace.x.max() == pytest.approx(priced.x.max())
        assert brace.x.min() == pytest.approx(new.x.min())
        assert new.x.max() > priced.x.max()

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[0])
        for phrase in (
            "a thin grey bar runs in from the left",
            "A grey axis of the CL file’s trading days",
            "ends at “last price 12-19”. It marks the days the file prices CL-2007F.",
            "A thick black bar over its left part",
            "a second thick black bar starts on the next trading day",
            "On the upper row",
            "On the lower row",
            "Between the rows",
            "a brown brace spans the days from 12-06 to 12-19",
            "with grey words under it",
            "where the grey bar still runs above the second black bar",
            "with brown words",
            "Black words at the bottom read",
            "Every bar sits at its own trading days on the axis.",
            "The finished drawing holds for twelve seconds.",
        ):
            assert phrase in alt, phrase


# --- Lesson 5: USO's log move against the roll return the ratio implies -------


class TestTheSplit:
    def test_it_is_the_runs(self, sources, split) -> None:
        """Read again from :func:`chan.xle_uso_roll_return.by_view`, at the post's precision."""
        _, closes, strip = sources
        result = trade.arbitrage(closes, trade.front_ratio(strip.contracts))
        views = trade.by_view(closes, result)
        contango, backwardation = views["contango"], views["backwardation"]
        assert (split.contango_days, split.backwardation_days) == (
            contango.days,
            backwardation.days,
        )
        assert split.contango_uso == math.log1p(contango.uso)
        assert split.backwardation_uso == math.log1p(backwardation.uso)
        assert (split.contango_roll, split.backwardation_roll) == (
            contango.roll,
            backwardation.roll,
        )
        assert (split.contango_days, split.backwardation_days) == (1128, 244), SPEC
        assert f"{split.contango_uso:.6f}" == "-0.838762", SPEC
        assert f"{split.backwardation_uso:.6f}" == "0.532304", SPEC
        assert f"{split.contango_roll:.6f}" == "-0.766081", SPEC
        assert f"{split.backwardation_roll:.6f}" == "0.072380", SPEC

    def test_the_words_close_and_beyond_hold_on_the_run(self, split) -> None:
        """The words "close to" and the brace on the gap describe the run, and these
        bounds are guards that keep the words true if a figure is re-pinned:
        the roll return is over nine tenths of USO's move on the contango days
        and under a fifth of it on the backwardation days."""
        assert split.contango_roll / split.contango_uso > 0.9, SPEC
        assert split.backwardation_roll / split.backwardation_uso < 0.2, SPEC


#: A made-up split, so the words and bars that should follow the run do.
OTHER_SPLIT = Split(
    contango_days=2000,
    contango_uso=-0.4,
    contango_roll=-0.1234567,
    backwardation_days=99,
    backwardation_uso=0.3,
    backwardation_roll=0.25,
)


class TestTheSplitSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "USO’s log move against the implied roll return"
        assert every[1].labels == SPLIT_LABELS

    def test_its_words_follow_the_run(self, handover) -> None:
        labels = scenes(handover, OTHER_SPLIT)[1].labels
        assert [labels[k] for k in (0, 2, 4, 7, 9, 11)] == [
            "2,000 days earning on contango",
            "−0.400000",
            "−0.123457",
            "99 days earning on backwardation",
            "0.300000",
            "0.250000",
        ]

    def test_its_colours(self, every) -> None:
        scene = every[1]
        assert {s.gid: s.color for s in scene.strokes} == {
            "zero": MUTED,
            "contango-uso": INK,
            "contango-roll": ACCENT,
            "backwardation-uso": INK,
            "backwardation-roll": ACCENT,
            "level": MUTED,
            "gap": INK,
        }
        colours = [s.color for s in scene.steps if isinstance(s, Label)]
        assert colours == [
            INK,
            INK,
            INK,
            ACCENT,
            ACCENT,
            INK,
            INK,
            INK,
            INK,
            INK,
            ACCENT,
            ACCENT,
            INK,
            INK,
            MUTED,
            MUTED,
        ]

    def test_each_bar_is_named_and_valued_beside_itself(self, every) -> None:
        scene = every[1]
        for gid in ("contango-uso", "contango-roll", "backwardation-uso", "backwardation-roll"):
            names = [
                s
                for s in scene.steps
                if isinstance(s, Label) and s.names == gid and s.text not in CLOSE_TO
            ]
            bar = _stroke(scene, gid)
            assert len(names) == 2, gid
            middle = (bar.x.min() + bar.x.max()) / 2
            for label in names:
                assert label.ha == "center" and label.x == pytest.approx(middle), gid
        assert _labels_of(scene, "contango-roll") == ["roll return", "−0.766081", *CLOSE_TO]
        assert _labels_of(scene, "gap") == SPLIT_LABELS[12:]

    def test_every_bar_ends_at_an_affine_function_of_its_value(self, every, split) -> None:
        """One scale for every bar, from the zero line, so the two in a group
        compare by length."""
        scene = every[1]
        for gid, value in (
            ("contango-uso", split.contango_uso),
            ("contango-roll", split.contango_roll),
            ("backwardation-uso", split.backwardation_uso),
            ("backwardation-roll", split.backwardation_roll),
        ):
            bar = _stroke(scene, gid)
            far = bar.y.min() if value < 0 else bar.y.max()
            near = bar.y.max() if value < 0 else bar.y.min()
            assert near == pytest.approx(ZERO_Y), gid
            assert far == pytest.approx(ZERO_Y + PER_LOG * value), gid
            assert bar_y(value) == pytest.approx(far), gid

    def test_the_bars_follow_a_made_up_split(self, handover) -> None:
        scene = scenes(handover, OTHER_SPLIT)[1]
        assert _stroke(scene, "contango-roll").y.min() == pytest.approx(
            ZERO_Y + PER_LOG * OTHER_SPLIT.contango_roll
        )
        assert _stroke(scene, "backwardation-roll").y.max() == pytest.approx(
            ZERO_Y + PER_LOG * OTHER_SPLIT.backwardation_roll
        )

    def test_contango_hangs_left_and_backwardation_stands_right(self, every) -> None:
        scene = every[1]
        bars = {g: _stroke(scene, g) for g in ("contango-uso", "contango-roll")}
        up = {g: _stroke(scene, g) for g in ("backwardation-uso", "backwardation-roll")}
        assert max(b.x.max() for b in bars.values()) < min(b.x.min() for b in up.values())
        assert all(b.y.max() == pytest.approx(ZERO_Y) for b in bars.values())
        assert all(b.y.min() == pytest.approx(ZERO_Y) for b in up.values())
        contango = _label(scene, SPLIT_LABELS[0])
        backwardation = _label(scene, SPLIT_LABELS[7])
        assert contango.y > ZERO_Y > backwardation.y
        left_edge = min(b.x.min() for b in bars.values())
        right_edge = max(b.x.max() for b in bars.values())
        assert contango.x <= left_edge and backwardation.x > right_edge

    def test_the_gap_words_sit_right_of_the_braces_point(self, every) -> None:
        scene = every[1]
        brace = _stroke(scene, "gap")
        for text in SPLIT_LABELS[12:14]:
            label = _label(scene, text)
            assert label.ha == "left" and label.x > brace.x.max(), text
            assert brace.y.min() < label.y < brace.y.max(), text

    def test_each_value_sits_past_its_bars_end_and_each_name_across_the_line(self, every) -> None:
        scene = every[1]
        steps = list(scene.steps)
        for gid in ("contango-uso", "contango-roll", "backwardation-uso", "backwardation-roll"):
            bar = _stroke(scene, gid)
            name, value = [
                s
                for s in steps
                if isinstance(s, Label) and s.names == gid and s.text not in CLOSE_TO
            ]
            if gid.startswith("contango"):
                assert value.y < bar.y.min() and name.y > ZERO_Y, gid
            else:
                assert value.y > bar.y.max() and name.y < ZERO_Y, gid

    def test_the_brace_spans_the_gap_between_the_backwardation_bars_tops(
        self, every, split
    ) -> None:
        scene = every[1]
        brace, level = _stroke(scene, "gap"), _stroke(scene, "level")
        assert (brace.y.min(), brace.y.max()) == pytest.approx(
            (bar_y(split.backwardation_roll), bar_y(split.backwardation_uso))
        )
        assert brace.x.min() > _stroke(scene, "backwardation-roll").x.max()
        assert level.y == pytest.approx(np.full(level.points, bar_y(split.backwardation_uso)))
        assert level.x.min() > _stroke(scene, "backwardation-uso").x.max()
        # It runs above the brown bar, starting left of it.
        assert level.x.min() < _stroke(scene, "backwardation-roll").x.min()
        assert level.x.max() == pytest.approx(brace.x.min())
        assert level.dashed

    def test_close_to_sits_beside_the_contango_roll_bar_in_plain_ink(self, every) -> None:
        """The words describe one exploratory sample, so they carry no green
        check, the mark that grades a value as checked out. They read as two
        lines, "close to" over "USO’s fall", at one place left of the
        backwardation words, so "close" never stands alone to read as a price."""
        scene = every[1]
        top, bottom = (_label(scene, text) for text in CLOSE_TO)
        roll = _stroke(scene, "contango-roll")
        backwardation = _label(scene, SPLIT_LABELS[7])
        for close in (top, bottom):
            assert close.names == "contango-roll" and close.color == INK, close.text
            assert roll.x.max() < close.x < _stroke(scene, "backwardation-uso").x.min()
            assert close.x < backwardation.x and close.ha == "left", close.text
            assert roll.y.min() < close.y < ZERO_Y, close.text
        assert top.x == bottom.x and top.y > bottom.y
        assert not [s for s in scene.strokes if s.color == GOOD]

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(every[1])
        for phrase in (
            "A black bar hangs down from the line",
            "A grey zero line runs across the board.",
            "Above it on the left, black words read",
            "named “USO” above the line",
            "Below the line on the right, black words read",
            "named “USO” below the line",
            "Grey words at the bottom read",
            "a brown bar nearly as long",
            "A black bar stands up from the line",
            "a short brown bar",
            "A dashed grey line runs from the top of the black bar, above the brown bar, to a "
            "black brace.",
            "The brace stands to the right of the brown bar and spans from the brown bar’s top "
            "up to the dashed line, with black words beside it",
            "Both values in each group are log quantities",
            "Black words beside the brown bar read “close to” and “USO’s fall”.",
            "every bar is drawn to one scale",
            "The finished drawing holds for twelve seconds.",
        ):
            assert phrase in alt, phrase
