"""The sketch-notes skill's draft script draws through the shared checks and guards its folder.

``.claude/skills/sketch-notes/draft.py`` draws a whiteboard sketch into a
scratch folder and says whether it is ready to show. Its checks are
:func:`ithildincore.whiteboard.draft`'s, and ithildin-core's
``tests/test_whiteboard.py`` gives each rule a sketch that breaks it. What this
file holds is what stays here: that the script calls those checks and reports
what they find, that it never writes into ``docs/figures``, and that it reads
whether a post has moved to :mod:`chan.palette` from the module it loads. The
script is loaded by path, as ``tests/test_substack_converter.py`` loads its
skill's converter.
"""

from __future__ import annotations

import importlib.util
import os
import textwrap
from pathlib import Path

import pytest
from ithildincore import whiteboard
from ithildincore.palette import BRASS
from PIL import Image

from chan import usdcad_tests_whiteboard as usdcad
from chan.paths import FIGURES_DIR, REPO_ROOT

SCRIPT = REPO_ROOT / ".claude" / "skills" / "sketch-notes" / "draft.py"


def _load():
    spec = importlib.util.spec_from_file_location("sketch_draft", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


draft = _load()


def _found(scene, tmp_path) -> list[str]:
    return draft.draft(scene, tmp_path, paced=False)


class TestAClearSketch:
    def test_one_of_the_usdcad_scenes_is_ok(self, tmp_path) -> None:
        assert _found(usdcad._adf(), tmp_path) == []

    def test_it_writes_the_gif_and_its_last_frame(self, tmp_path) -> None:
        _found(usdcad._adf(), tmp_path)
        assert {path.name for path in tmp_path.iterdir()} == {"adf.gif", "adf_last.png"}


class TestTheChecksAreTheLibrarys:
    def test_the_script_drafts_with_the_shared_function(self) -> None:
        assert draft.draft is whiteboard.draft

    def test_a_broken_rule_reaches_the_report(self, tmp_path) -> None:
        line = whiteboard.stroke("line", whiteboard.line([(1.0, 2.0), (9.0, 2.0)]))
        scene = whiteboard.Scene(
            "Broken", "broken", (line, whiteboard.Label("on it", 3, 2.05, "line"))
        )
        assert any("px from a stroke" in found for found in _found(scene, tmp_path))


class TestAPostThatHasMoved:
    """A moved post's scene can hold no colour of :mod:`chan.palette` at all, such
    as ink strokes and a ``_dot`` left on its default brass. The script learns
    the post has moved from the module it loads, or from ``--palette``."""

    LONE_DOT = """
        {imports}
        from ithildincore.whiteboard import Scene, dot, line, stroke

        def scene():
            across = stroke("line", line([(1, 2), (9, 2)]))
            return Scene("A lone dot", "lone_dot", (across, dot("dot", 5, 3)))
        """

    def _module(self, tmp_path, monkeypatch, name: str, imports: str = "") -> str:
        (tmp_path / f"{name}.py").write_text(textwrap.dedent(self.LONE_DOT.format(imports=imports)))
        monkeypatch.syspath_prepend(str(tmp_path))
        return f"{name}:scene"

    @pytest.mark.parametrize(
        "imports",
        [
            "from chan.palette import INKS",
            "from chan import palette as own",
            "from ithildincore.palette import INKS",
            "from ithildincore import palette",
        ],
    )
    def test_a_module_that_imports_the_new_palette_has_moved(
        self, tmp_path, monkeypatch, capsys, imports
    ) -> None:
        name = "moved_" + "".join(c if c.isalnum() else "_" for c in imports)
        target = self._module(tmp_path, monkeypatch, name, imports)
        assert draft.main([target, "--out", str(tmp_path / "out")]) == 1
        printed = capsys.readouterr().out
        assert "keeps the brass set's" in printed and BRASS.lower() in printed

    def test_a_module_that_does_not_has_not(self, tmp_path, monkeypatch) -> None:
        target = self._module(tmp_path, monkeypatch, "unmoved_sketch")
        assert draft.main([target, "--out", str(tmp_path / "out")]) == 0

    def test_the_flag_moves_a_scratch_module(self, tmp_path, monkeypatch, capsys) -> None:
        target = self._module(tmp_path, monkeypatch, "scratch_sketch")
        assert draft.main([target, "--out", str(tmp_path / "out"), "--palette"]) == 1
        assert "keeps the brass set's" in capsys.readouterr().out


class TestThePacing:
    def test_the_paced_flag_draws_on_the_paced_timeline(self, tmp_path) -> None:
        assert (
            draft.main(["chan.usdcad_tests_whiteboard:_adf", "--out", str(tmp_path), "--paced"])
            == 0
        )
        with Image.open(tmp_path / "adf.gif") as image:
            durations = []
            for index in range(image.n_frames):
                image.seek(index)
                durations.append(image.info["duration"])
        assert durations == [f.ms for f in whiteboard.paced_timeline(usdcad._adf())]


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
                from ithildincore.whiteboard import Label, Scene
                from ithildincore.whiteboard import line as _line
                from ithildincore.whiteboard import stroke as _stroke

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
                from ithildincore.whiteboard import Label, Scene
                from ithildincore.whiteboard import line as _line
                from ithildincore.whiteboard import stroke as _stroke

                from chan.usdcad_tests_whiteboard import _adf

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
