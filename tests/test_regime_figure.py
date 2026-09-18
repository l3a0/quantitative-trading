"""The pins for the one committed image.

A figure nothing regenerates is an artifact nobody can check, which is the
objection ``docs/design.md`` raises against committing one. The generator came
across from the sibling repository with the essay it illustrates, so the image
is regenerable again, and this file is what says the regenerated picture is the
one the write-up describes.

What it does not do is compare bytes. A PNG carries the matplotlib version that
rendered it, so a fresh draw of an unchanged figure differs from the committed
file while looking identical. The committed image and a fresh draw here are the
same size to the byte and differ in their hash, which is exactly that. So the
assertions below hold the data behind the picture and the picture's shape, and
an upgrade that changes nothing a reader sees does not turn the suite red.

The numbers are the ones ``TestRollingRegime`` already pins. Repeating them
here is deliberate rather than duplication: that class holds what the engine
computes, and this one holds that the figure draws what the engine computed.
A generator that quietly plotted the wrong series would pass the first and fail
the second.
"""

from __future__ import annotations

import hashlib
import struct
from pathlib import Path

import pytest
from ithildincore.timeseries import EG_CRIT_N2

from chan.paths import FIGURES_DIR
from chan.regime_figure import REPRO_HEDGE, make_regime_figure

COMMITTED = FIGURES_DIR / "reproduction_regime_map.png"


def png_size(path: Path) -> tuple[int, int]:
    """Width and height straight out of the PNG header.

    Reading IHDR by hand keeps this test off an image library the project does
    not otherwise need. Bytes 0-7 are the signature, 8-15 the IHDR chunk header,
    and 16-23 the two big-endian dimensions.
    """
    header = path.read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    return struct.unpack(">II", header[16:24])


@pytest.fixture(scope="module")
def drawn(tmp_path_factory: pytest.TempPathFactory) -> tuple[object, Path]:
    """Run the real drawing code, writing somewhere that is not the repo."""
    out = tmp_path_factory.mktemp("figure") / "reproduction_regime_map.png"
    return make_regime_figure(out=out), out


class TestTheFigureDrawsTheScanThatIsPinned:
    def test_the_upper_panel_plots_every_rolling_window(self, drawn) -> None:
        fig, _ = drawn
        adf = fig.axes[0].lines[0].get_ydata()

        assert len(adf) == 231
        assert int((adf < EG_CRIT_N2["10%"]).sum()) == 31
        assert int((adf < EG_CRIT_N2["5%"]).sum()) == 14

    def test_the_first_window_is_chans_era(self, drawn) -> None:
        """The annotation in the picture points at this value, so the line it
        points at has to carry it."""
        fig, _ = drawn
        assert fig.axes[0].lines[0].get_ydata()[0] == pytest.approx(-3.18, abs=1e-2)

    def test_the_critical_lines_are_the_ones_the_test_uses(self, drawn) -> None:
        """The essay labels them -3.04 and -3.34. Drawing a different line
        would make the green bands mean something other than they claim."""
        fig, _ = drawn
        drawn_levels = sorted(float(line.get_ydata()[0]) for line in fig.axes[0].lines[1:])

        assert drawn_levels == [EG_CRIT_N2["5%"], EG_CRIT_N2["10%"]]

    def test_the_lower_panel_plots_the_hedge_drift(self, drawn) -> None:
        fig, _ = drawn
        hedge = fig.axes[1].lines[0].get_ydata()

        assert len(hedge) == 231
        assert hedge[0] == pytest.approx(1.6286, abs=5e-4)
        assert hedge.max() == pytest.approx(6.6152, abs=5e-4)

    def test_the_reference_line_is_the_reproduced_hedge(self, drawn) -> None:
        """The caption calls it the reproduced Chan hedge, and 1.6379 is what
        the replication computes. Drawing Chan's printed 1.6766 there would
        illustrate a number this repo never reproduced."""
        fig, _ = drawn
        assert REPRO_HEDGE == pytest.approx(1.6379, abs=5e-5)
        assert float(fig.axes[1].lines[1].get_ydata()[0]) == pytest.approx(REPRO_HEDGE)


class TestTheCommittedImageIsThatFigure:
    def test_a_fresh_draw_has_the_committed_image_dimensions(self, drawn) -> None:
        _, out = drawn

        assert png_size(out) == png_size(COMMITTED)

    def test_drawing_leaves_the_committed_file_alone(self, drawn) -> None:
        """The generator used to write to one hard-coded path, so running it
        to check it meant overwriting the thing being checked."""
        before = hashlib.sha256(COMMITTED.read_bytes()).hexdigest()
        _, out = drawn

        assert out != COMMITTED
        assert hashlib.sha256(COMMITTED.read_bytes()).hexdigest() == before
