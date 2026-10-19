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

from chan import usdcad_tests_whiteboard as whiteboard
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.usdcad_tests_whiteboard import Label, Scene, Stroke, _line, _stroke

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

    def test_a_label_off_the_board(self, tmp_path) -> None:
        scene = _scene(_line_across(), Label("off the board", 9.8, 4.6, names="line"))
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

    def test_a_dot_drawn_in_one_frame_is_ok(self, tmp_path) -> None:
        assert _found(_scene(whiteboard._dot("dot", 5.0, 2.0)), tmp_path) == []


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

    def test_the_command_stops_before_drawing(self, tmp_path) -> None:
        with pytest.raises(SystemExit, match="not docs/figures"):
            draft.main(["chan.usdcad_tests_whiteboard:_adf", "--out", str(FIGURES_DIR)])


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
