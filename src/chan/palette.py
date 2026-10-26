"""The three colours a post's charts and sketches draw in once it moves off the
shared brass, green and red.

Every post's figures used to take their colours from :mod:`chan.regime_figure`,
whose brass, green and red were chosen to match the GLD/GDX essay's page. Two of
those pairs fall apart for a reader with red-green colour blindness. Under
deuteranopia the brass of a post's subject and the red of a loss sit 3.0 apart,
on a scale where 8 is the least a reader can rely on, so a figure that says
which line is the subject and which is the loss says it only to readers who see
every colour. This module holds the replacement.

1. ``ACCENT``, a berry, marks the thing a picture is about.
2. ``GOOD``, a blue, marks a profit or the side that wins.
3. ``LOST``, a vermilion, marks a loss or a warning.

Each clears 4.5 to 1 against the sketches' white board and a chart's figure
ground, :data:`chan.regime_figure.SURFACE`, so a label drawn in it reads as
text. Each pair stays at least 8 apart under protanopia, deuteranopia and
tritanopia, and at least 15 apart in normal vision. ``tests/test_palette.py``
measures all of it, and ``docs/design.md`` says why posts move to these colours
one at a time rather than all at once.

The ink and the grey come from :mod:`chan.regime_figure` unchanged. Its brass,
green and red stay there too, because every post that has not moved still draws
in them. The measurements leave two gaps, and the tests pin both so a post that
moves meets them as numbers rather than by surprise.

1. Inside a chart's axes, whose ground is the darker
   :data:`chan.regime_figure.GROUND`, ``GOOD`` reaches only 4.37 to 1 and
   ``LOST`` 4.30. A label in either colour that sits on the axes falls short of
   the bar for text, so it goes on a white box or in ``INK``.
2. Under protanopia ``LOST`` sits 7.5 from the grey, just short of 8. The
   shared red sat 3.8 from it, so the move narrows the gap without closing it.
   Where a loss and a note in grey sit side by side, a label or a sign tells
   them apart as well as the colour.

The sketches need two more colours, the pale tints a band or a reject zone is
filled with. :mod:`chan.usdcad_tests_whiteboard` makes its own by laying its
green and its red on the white board at the lightest blend its palette holds,
so a tint adds no colour to a GIF. ``TINT`` and ``REJECT_TINT`` here do the same
with ``GOOD`` and ``LOST``. The blend is written out rather than imported,
because that module draws the USD.CAD post's sketches and would have to import
this one when the post moves. ``tests/test_palette.py`` holds that both tints
are colours the renderer's palette already carries for :data:`INKS`.

A post moves by importing these names in place of :mod:`chan.regime_figure`'s,
and its sketch module passes :data:`INKS` to
:func:`chan.usdcad_tests_whiteboard.render`.
"""

from __future__ import annotations

from matplotlib.colors import to_hex, to_rgb

from chan.regime_figure import INK, MUTED

ACCENT = "#981E87"  # berry -- the subject
GOOD = "#276EE1"  # blue -- a profit, or the side that wins
LOST = "#D24011"  # vermilion -- a loss, or a warning

#: The inks a sketch's frames are mapped onto, in the order
#: :data:`chan.usdcad_tests_whiteboard.INKS` gives the shared ones.
INKS = (INK, MUTED, ACCENT, GOOD, LOST)


def _lightest(ink: str) -> str:
    """``ink`` laid on the white board at a fifth of its strength, the lightest
    blend :data:`chan.usdcad_tests_whiteboard.BLENDS` holds."""
    return to_hex([0.2 * channel + 0.8 for channel in to_rgb(ink)])


#: A band's tint: ``GOOD`` at the palette's lightest blend with the board.
TINT = _lightest(GOOD)
#: A reject zone's tint: ``LOST`` at the same blend.
REJECT_TINT = _lightest(LOST)
