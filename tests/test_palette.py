"""The pins that this repository's two sets of colours are ithildincore's.

The colours live in :mod:`ithildincore.palette`, where ithildin-core's
``tests/test_palette.py`` measures their contrast against the board and the
chart grounds and their separation under each kind of colour blindness, and
pins every hex code. This file holds what stays here: that
:mod:`chan.palette` names the colour-blind safe set, that
:mod:`chan.regime_figure` names the brass set under the roles its charts draw
them in, and that the renderer's defaults are the brass set every post that
has not moved draws in.

The contrast and colour-blind separation helpers stay here, because this
repository's figure tests measure their own charts' colours with them. They
are the same measurements ithildin-core's palette tests make.
"""

from __future__ import annotations

import math

import pytest
from ithildincore import palette as shared
from ithildincore import whiteboard
from matplotlib.colors import to_rgba

from chan import palette, regime_figure

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


@pytest.mark.parametrize(
    "name", ["ACCENT", "GOOD", "LOST", "INK", "MUTED", "INKS", "TINT", "REJECT_TINT"]
)
def test_chan_palette_is_the_colour_blind_safe_set(name) -> None:
    assert getattr(palette, name) is getattr(shared, name)


@pytest.mark.parametrize(
    ("role", "colour"),
    [
        ("ACCENT", "BRASS"),
        ("GOOD", "GREEN"),
        ("LOST", "RED"),
        ("INK", "INK"),
        ("MUTED", "MUTED"),
        ("SURFACE", "SURFACE"),
        ("GROUND", "GROUND"),
        ("RULE", "RULE"),
    ],
)
def test_regime_figure_names_the_brass_set_by_role(role, colour) -> None:
    assert getattr(regime_figure, role) is getattr(shared, colour)


def test_the_brass_hex_codes_are_the_essays() -> None:
    """The GLD/GDX essay's page sets these, so the charts read as part of it."""
    assert (regime_figure.ACCENT, regime_figure.GOOD, regime_figure.LOST) == (
        "#8B651A",
        "#4A7C59",
        "#A24C3C",
    )


def test_the_renderer_still_defaults_to_the_brass_inks() -> None:
    """``test_each_is_a_fresh_draw_byte_for_byte`` in each post's whiteboard
    tests holds the GIFs themselves."""
    brass = (
        regime_figure.INK,
        regime_figure.MUTED,
        regime_figure.ACCENT,
        regime_figure.GOOD,
        regime_figure.LOST,
    )
    assert shared.BRASS_INKS == brass
    assert whiteboard.palette().getpalette() == whiteboard.palette(brass).getpalette()
