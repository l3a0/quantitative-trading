"""The sketch-notes skill's draft script flags every rule a broken sketch breaks.

``.claude/skills/sketch-notes/draft.py`` draws a whiteboard sketch into a
scratch folder and says whether it is ready to show. A check in it that stops
working prints ``ok`` on a sketch the repo's own tests would reject, which is
the one way the script can mislead, so each rule gets a sketch that breaks it.
The script is loaded by path, as ``tests/test_substack_converter.py`` loads its
skill's converter.
"""

from __future__ import annotations

import importlib.util
import os
import textwrap
from pathlib import Path

import numpy as np
import pytest
from matplotlib.colors import to_rgb
from PIL import Image

from chan import palette
from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.usdcad_tests_whiteboard import Fill, Label, Scene, Stroke, _line, _stroke

SCRIPT = REPO_ROOT / ".claude" / "skills" / "sketch-notes" / "draft.py"


def _load():
    spec = importlib.util.spec_from_file_location("sketch_draft", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


draft = _load()


def _scene(*steps) -> Scene:
    return Scene("A test sketch", "test_sketch", steps)


def _line_across(frames: int = 8) -> Stroke:
    return _stroke("line", _line([(1.0, 2.0), (9.0, 2.0)]), frames=frames)


def _found(scene: Scene, tmp_path) -> list[str]:
    return draft.draft(scene, tmp_path, paced=False)


class TestAClearSketch:
    def test_one_of_the_usdcad_scenes_is_ok(self, tmp_path) -> None:
        assert _found(whiteboard._adf(), tmp_path) == []

    def test_it_writes_the_gif_and_its_last_frame(self, tmp_path) -> None:
        _found(whiteboard._adf(), tmp_path)
        assert {path.name for path in tmp_path.iterdir()} == {"adf.gif", "adf_last.png"}


class TestEachBrokenRuleIsFlagged:
    def test_a_label_on_its_line(self, tmp_path) -> None:
        scene = _scene(_line_across(), Label("on the line", 3.0, 2.05, names="line"))
        assert any("px from a stroke" in line for line in _found(scene, tmp_path))

    @pytest.mark.parametrize(
        ("x", "y", "ha"),
        [(9.8, 4.6, "left"), (9.9, 3.0, "left"), (5.0, 4.68, "left"), (0.02, 3.0, "right")],
        ids=["corner", "right edge", "top edge", "left edge"],
    )
    def test_a_label_off_the_board(self, tmp_path, x, y, ha) -> None:
        scene = _scene(_line_across(), Label("off the board", x, y, names="line", ha=ha))
        assert any("px inside the board" in line for line in _found(scene, tmp_path))

    def test_two_labels_touching(self, tmp_path) -> None:
        scene = _scene(
            _line_across(),
            Label("one", 5.0, 3.5, names="line"),
            Label("two", 5.3, 3.5, names="line"),
        )
        assert any("px apart" in line for line in _found(scene, tmp_path))

    def test_a_label_naming_a_stroke_drawn_after_it(self, tmp_path) -> None:
        scene = _scene(Label("too early", 3.0, 3.5, names="line"), _line_across())
        assert any("not drawn before it" in line for line in _found(scene, tmp_path))

    @pytest.mark.parametrize(
        ("points", "frames"), [(5, 8), (6, 6)], ids=["more frames", "as many frames"]
    )
    def test_a_stroke_with_too_few_points_for_its_frames(self, tmp_path, points, frames) -> None:
        stroke = Stroke("short", np.linspace(1.0, 9.0, points), np.full(points, 2.0), frames=frames)
        found = _found(_scene(stroke), tmp_path)
        assert any(f"{frames} frames for {points} points" in line for line in found)
        assert any("the GIF holds" in line for line in found)

    def test_a_one_point_dot_drawn_over_many_frames(self, tmp_path) -> None:
        dot = Stroke("dot", np.array([5.0]), np.array([2.0]))
        found = _found(_scene(dot), tmp_path)
        assert any("8 frames for 1 points" in line for line in found)
        assert any("the GIF holds" in line for line in found)

    def test_a_label_naming_a_tint_drawn_before_it_is_ok(self, tmp_path) -> None:
        scene = _scene(
            Fill("band", 1.0, 1.0, 4.0, 1.5, whiteboard.MUTED),
            Label("a band", 5.0, 3.5, names="band"),
        )
        assert not any("not drawn before it" in line for line in _found(scene, tmp_path))

    def test_a_dot_drawn_in_one_frame_is_ok(self, tmp_path) -> None:
        assert _found(_scene(whiteboard._dot("dot", 5.0, 2.0)), tmp_path) == []


class TestThePalette:
    """A post that has moved to :mod:`chan.palette` drafts in its own colours, and
    a scene that keeps a mark of the shared palette is flagged."""

    @staticmethod
    def _wide(color: str) -> Stroke:
        return _stroke("band", _line([(1.0, 2.0), (9.0, 2.0)]), color=color, width=12.0)

    @staticmethod
    def _rgbs(png: Path) -> set[tuple[int, ...]]:
        with Image.open(png) as image:
            return {rgb for _, rgb in image.convert("RGB").getcolors(1 << 16)}

    def test_a_scene_in_the_new_colours_draws_in_them(self, tmp_path) -> None:
        assert _found(_scene(self._wide(palette.ACCENT)), tmp_path) == []
        berry = tuple(round(255 * c) for c in to_rgb(palette.ACCENT))
        assert berry in self._rgbs(tmp_path / "test_sketch_last.png")

    @pytest.mark.parametrize("color", [whiteboard.ACCENT, whiteboard.INK])
    def test_a_scene_in_the_shared_colours_keeps_the_shared_inks(self, color) -> None:
        assert draft.inks_for(_scene(self._wide(color))) == (whiteboard.INKS, [])

    @pytest.mark.parametrize("tint", [palette.TINT, palette.REJECT_TINT])
    def test_a_new_tint_alone_moves_the_scene(self, tint) -> None:
        scene = _scene(Fill("band", 1.0, 1.0, 4.0, 1.5, tint))
        assert draft.inks_for(scene) == (palette.INKS, [])

    @pytest.mark.parametrize(
        ("mark", "colour"),
        [
            (whiteboard._dot("dot", 5.0, 3.0), whiteboard.ACCENT),
            (Fill("zone", 1.0, 3.0, 4.0, 3.5, whiteboard.TINT), whiteboard.TINT),
        ],
        ids=["a dot in the shared brass", "the shared tint"],
    )
    def test_a_mark_left_in_the_shared_palette_is_flagged(self, tmp_path, mark, colour) -> None:
        found = _found(_scene(self._wide(palette.GOOD), mark), tmp_path)
        assert len(found) == 1
        assert "shared" in found[0] and colour.lower() in found[0]


class TestAPostThatHasMoved:
    """A moved post's scene can hold no colour of :mod:`chan.palette` at all, such
    as ink strokes and a ``_dot`` left on its default brass. The script learns
    the post has moved from the module it loads, or from ``--palette``."""

    LONE_DOT = """
        {imports}
        from chan.usdcad_tests_whiteboard import Scene, _dot, _line, _stroke

        def scene():
            line = _stroke("line", _line([(1, 2), (9, 2)]))
            return Scene("A lone dot", "lone_dot", (line, _dot("dot", 5, 3)))
        """

    def _module(self, tmp_path, monkeypatch, name: str, imports: str = "") -> str:
        (tmp_path / f"{name}.py").write_text(textwrap.dedent(self.LONE_DOT.format(imports=imports)))
        monkeypatch.syspath_prepend(str(tmp_path))
        return f"{name}:scene"

    def test_a_lone_dot_is_flagged_once_the_post_has_moved(self) -> None:
        scene = _scene(_line_across(), whiteboard._dot("dot", 5.0, 3.0))
        assert draft.inks_for(scene) == (whiteboard.INKS, [])
        inks, found = draft.inks_for(scene, moved=True)
        assert inks == palette.INKS
        assert len(found) == 1 and whiteboard.ACCENT.lower() in found[0]

    @pytest.mark.parametrize(
        "imports", ["from chan.palette import INKS", "from chan import palette as own"]
    )
    def test_a_module_that_imports_the_new_palette_has_moved(
        self, tmp_path, monkeypatch, capsys, imports
    ) -> None:
        name = "moved_by_alias" if "own" in imports else "moved_by_inks"
        target = self._module(tmp_path, monkeypatch, name, imports)
        assert draft.main([target, "--out", str(tmp_path / "out")]) == 1
        assert "keeps the shared" in capsys.readouterr().out

    def test_a_module_that_does_not_has_not(self, tmp_path, monkeypatch) -> None:
        target = self._module(tmp_path, monkeypatch, "unmoved_sketch")
        assert draft.main([target, "--out", str(tmp_path / "out")]) == 0

    def test_the_flag_moves_a_scratch_module(self, tmp_path, monkeypatch, capsys) -> None:
        target = self._module(tmp_path, monkeypatch, "scratch_sketch")
        assert draft.main([target, "--out", str(tmp_path / "out"), "--palette"]) == 1
        assert "keeps the shared" in capsys.readouterr().out


class TestThePacing:
    def test_paced_labels_show_900_ms_and_the_drawing_holds_12_seconds(self) -> None:
        scene = whiteboard._adf()
        plain, paced = draft.frames_for(scene, False), draft.frames_for(scene, True)
        assert [(f.done, f.partial) for f in paced] == [(f.done, f.partial) for f in plain]
        for before, after in zip(plain[1:-1], paced[1:-1], strict=True):
            labelled = (
                after.partial == 0
                and after.done
                and not isinstance(scene.steps[after.done - 1], Stroke)
            )
            assert after.ms == (900 if labelled else before.ms)
        assert (paced[0].ms, paced[-1].ms) == (plain[0].ms, 12000)


class TestBothFontsAreChecked:
    def test_the_layout_runs_in_the_hand_font_and_the_fallback(self, monkeypatch) -> None:
        monkeypatch.setattr(whiteboard, "hand_font", lambda: "Comic Sans MS")
        drawn = []
        monkeypatch.setattr(
            draft, "clearances", lambda scene: drawn.append(whiteboard.hand_font()) or {}
        )
        monkeypatch.setattr(draft, "boxes", lambda scene: [])
        draft.layout_problems(_scene(_line_across()))
        assert drawn == ["Comic Sans MS", whiteboard.FALLBACK_FONT]
        assert whiteboard.hand_font() == "Comic Sans MS"

    def test_the_fallback_is_checked_once_when_it_is_the_hand_font(self, monkeypatch) -> None:
        monkeypatch.setattr(whiteboard, "hand_font", lambda: whiteboard.FALLBACK_FONT)
        drawn = []
        monkeypatch.setattr(
            draft, "clearances", lambda scene: drawn.append(whiteboard.hand_font()) or {}
        )
        monkeypatch.setattr(draft, "boxes", lambda scene: [])
        draft.layout_problems(_scene(_line_across()))
        assert drawn == [whiteboard.FALLBACK_FONT]


class TestItNeverWritesIntoTheFigures:
    def test_the_folder_and_any_folder_in_it_are_refused(self) -> None:
        assert draft.inside_figures(FIGURES_DIR)
        assert draft.inside_figures(FIGURES_DIR / "scratch")

    def test_a_relative_spelling_from_another_folder_is_refused(self, monkeypatch) -> None:
        monkeypatch.chdir(REPO_ROOT / "src")
        assert draft.inside_figures(Path("../docs/figures"))

    def test_another_case_is_refused_where_the_disk_ignores_case(self) -> None:
        upper = REPO_ROOT / "DOCS" / "Figures"
        if not upper.exists():
            pytest.skip("this disk tells cases apart, so DOCS/Figures is another folder")
        assert draft.inside_figures(upper)

    def test_a_folder_beside_it_is_allowed(self, tmp_path) -> None:
        assert not draft.inside_figures(tmp_path)
        assert not draft.inside_figures(FIGURES_DIR.parent / "figures-draft")

    def test_a_symlink_followed_by_dotdot_is_refused(self, tmp_path) -> None:
        inside = tmp_path / "figures" / "sub"
        inside.mkdir(parents=True)
        (tmp_path / "link").symlink_to(inside)
        guarded = tmp_path / "figures"
        assert os.path.samefile(os.path.realpath(tmp_path / "link" / ".."), guarded)
        original = draft.FIGURES_DIR
        try:
            draft.FIGURES_DIR = guarded
            assert draft.inside_figures(tmp_path / "link" / "..")
        finally:
            draft.FIGURES_DIR = original

    def test_the_command_stops_before_drawing(self, tmp_path, monkeypatch) -> None:
        """The figures folder is a scratch one here, so a broken guard writes nothing real."""
        monkeypatch.setattr(draft, "FIGURES_DIR", tmp_path)
        with pytest.raises(SystemExit, match="not docs/figures"):
            draft.main(["chan.usdcad_tests_whiteboard:_adf", "--out", str(tmp_path)])
        assert list(tmp_path.iterdir()) == []


class TestTheCommand:
    def test_it_exits_0_when_every_scene_is_ok(self, tmp_path, capsys) -> None:
        code = draft.main(["chan.usdcad_tests_whiteboard:_adf", "--out", str(tmp_path)])
        assert code == 0
        assert capsys.readouterr().out.strip().endswith(": ok")

    def test_it_exits_1_and_names_each_problem_when_one_breaks_a_rule(
        self, tmp_path, monkeypatch, capsys
    ) -> None:
        (tmp_path / "broken_sketch.py").write_text(
            textwrap.dedent(
                """
                from chan.usdcad_tests_whiteboard import Label, Scene, _line, _stroke

                def scene():
                    line = _stroke("line", _line([(1, 2), (9, 2)]))
                    return Scene("Broken", "broken", (line, Label("on it", 3, 2.05, names="line")))
                """
            )
        )
        monkeypatch.syspath_prepend(str(tmp_path))
        out = tmp_path / "out"
        assert draft.main(["broken_sketch:scene", "--out", str(out)]) == 1
        printed = capsys.readouterr().out
        assert "see below" in printed and "px from a stroke" in printed
        assert os.path.exists(out / "broken.gif")

    def test_one_broken_scene_among_several_exits_1(self, tmp_path, monkeypatch) -> None:
        (tmp_path / "two_sketches.py").write_text(
            textwrap.dedent(
                """
                from chan.usdcad_tests_whiteboard import Label, Scene, _adf, _line, _stroke

                def scenes():
                    line = _stroke("line", _line([(1, 2), (9, 2)]))
                    on_it = Label("on it", 3, 2.05, names="line")
                    broken = Scene("Broken", "broken", (line, on_it))
                    return (broken, _adf())
                """
            )
        )
        monkeypatch.syspath_prepend(str(tmp_path))
        assert draft.main(["two_sketches:scenes", "--out", str(tmp_path / "out")]) == 1
