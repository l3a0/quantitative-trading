"""The pins for the colours a post moves to, in :mod:`chan.palette`.

A colour that fails a reader fails silently: the figure still draws, and only
the reader who cannot tell two lines apart notices. So this file measures the
three colours rather than trusting the hex codes.

1. Each clears WCAG's 4.5 to 1 contrast against the sketches' white board and
   a chart's figure ground, the bar for text.
2. Each pair stays apart in normal vision and under the three kinds of colour
   blindness, and so does each colour against the shared ink and grey.
3. The shared brass and red they replace do not, which is the reason for the
   change.
4. The sketches' two tints are colours the renderer's palette already holds
   for the new inks, so a tint adds no colour to a GIF.

Two measurements fall short, and the tests pin them at their values rather
than leave them unrecorded: the blue and the vermilion on the axes' darker
ground, and the vermilion against the grey under protanopia.

The measurements were first written for the commodity-seasonals post's figure
tests, on the pull request that drew in these colours first.
"""

from __future__ import annotations

import itertools
import math

import pytest
from matplotlib.colors import to_rgb, to_rgba

from chan import regime_figure
from chan import usdcad_tests_whiteboard as whiteboard
from chan.palette import ACCENT, GOOD, INKS, LOST, REJECT_TINT, TINT

# Contrast is WCAG's. The colour-blind separation simulates protanopia,
# deuteranopia and tritanopia with Machado, Oliveira and Fernandes (2009) at
# full severity, then measures the distance in OKLab times 100. 8 is the
# separation a reader can rely on, and 15 the floor for normal vision, the
# thresholds the dataviz guidance this repo's charts follow sets.

_MACHADO = {
    "protan": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deutan": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritan": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


def _linear(colour: str) -> tuple[float, float, float]:
    r, g, b, _ = to_rgba(colour)
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b))


def _contrast(one: str, two: str) -> float:
    lum = [
        sum(w * c for w, c in zip((0.2126, 0.7152, 0.0722), _linear(x), strict=True))
        for x in (one, two)
    ]
    return (max(lum) + 0.05) / (min(lum) + 0.05)


def _oklab(rgb) -> tuple[float, float, float]:
    r, g, b = rgb
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)  # noqa: E741
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def _apart(one: str, two: str, kind: str | None = None) -> float:
    def seen(colour):
        rgb = _linear(colour)
        if kind is None:
            return _oklab(rgb)
        return _oklab(
            [
                min(1.0, max(0.0, sum(k * c for k, c in zip(row, rgb, strict=True))))
                for row in _MACHADO[kind]
            ]
        )

    return 100 * math.dist(seen(one), seen(two))


class TestTheColours:
    INKS = {"accent": ACCENT, "good": GOOD, "lost": LOST}

    @pytest.mark.parametrize("name", ["accent", "good", "lost"])
    def test_each_reads_as_text_on_the_board_and_the_ground(self, name) -> None:
        for ground in (whiteboard.BOARD, regime_figure.SURFACE):
            assert _contrast(self.INKS[name], ground) >= 4.5, (name, ground)

    def test_every_pair_stays_apart_with_and_without_colour_blindness(self) -> None:
        pairs = itertools.combinations(self.INKS.values(), 2)
        for one, two in pairs:
            assert _apart(one, two) >= 15, (one, two)
            for kind in _MACHADO:
                assert _apart(one, two, kind) >= 8, (one, two, kind)

    def test_the_shared_colours_they_replace_do_not(self) -> None:
        """The brass and red the other posts draw in sit 3.0 apart under deuteranopia."""
        shared = _apart(regime_figure.ACCENT, regime_figure.LOST, "deutan")
        assert shared == pytest.approx(3.0, abs=0.05)

    def test_each_stays_apart_from_the_ink_and_the_grey_but_one(self) -> None:
        """The vermilion sits 7.5 from the grey under protanopia, short of 8."""
        for one in (regime_figure.INK, regime_figure.MUTED):
            for two in self.INKS.values():
                assert _apart(one, two) >= 15, (one, two)
                for kind in _MACHADO:
                    if (one, two, kind) == (regime_figure.MUTED, LOST, "protan"):
                        assert _apart(one, two, kind) == pytest.approx(7.5, abs=0.05)
                    else:
                        assert _apart(one, two, kind) >= 8, (one, two, kind)

    def test_only_the_accent_reads_as_text_on_the_axes_ground(self) -> None:
        """Inside a chart's axes the blue reaches 4.37 to 1 and the vermilion 4.30."""
        ground = regime_figure.GROUND
        assert _contrast(ACCENT, ground) >= 4.5
        assert _contrast(GOOD, ground) == pytest.approx(4.37, abs=0.005)
        assert _contrast(LOST, ground) == pytest.approx(4.30, abs=0.005)

    def test_the_sketch_inks_keep_the_shared_ink_and_grey(self) -> None:
        assert INKS == (regime_figure.INK, regime_figure.MUTED, ACCENT, GOOD, LOST)


class TestTheTints:
    @staticmethod
    def _colours(inks) -> set[tuple[int, ...]]:
        flat = whiteboard.palette(inks).getpalette()
        return {tuple(flat[i : i + 3]) for i in range(0, len(flat), 3)}

    @pytest.mark.parametrize(("tint", "ink"), [(TINT, GOOD), (REJECT_TINT, LOST)])
    def test_each_is_its_ink_at_the_renderers_lightest_blend(self, tint, ink) -> None:
        blended = whiteboard._blend(ink, whiteboard.BLENDS[-1])
        assert to_rgb(tint) == pytest.approx(tuple(blended), abs=0.5 / 255)

    @pytest.mark.parametrize("tint", [TINT, REJECT_TINT])
    def test_each_adds_no_colour_to_the_palette_of_the_new_inks(self, tint) -> None:
        rgb = tuple(round(255 * c) for c in to_rgb(tint))
        assert rgb in self._colours(INKS)
        assert rgb not in self._colours(whiteboard.INKS)

    def test_the_renderer_still_defaults_to_the_shared_inks(self) -> None:
        """The default palette is the shared one. ``test_each_is_a_fresh_draw_byte_for_byte``
        in ``tests/test_usdcad_tests_whiteboard.py`` holds the GIFs themselves."""
        shared = (
            regime_figure.INK,
            regime_figure.MUTED,
            regime_figure.ACCENT,
            regime_figure.GOOD,
            regime_figure.LOST,
        )
        assert whiteboard.INKS == shared
        assert whiteboard.palette().getpalette() == whiteboard.palette(shared).getpalette()

    def test_render_draws_onto_the_palette_of_the_inks_it_is_given(self) -> None:
        """A post that moves passes these inks to ``render``, and its frames use them."""
        scene = whiteboard.Scene("t", "t", ())
        images = whiteboard.render(scene, whiteboard.timeline(scene)[-1:], INKS)
        assert images
        for image in images:
            assert image.getpalette() == whiteboard.palette(INKS).getpalette()
