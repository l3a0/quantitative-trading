"""The three colours a post's charts and sketches draw in once it moves off the
brass, green and red of :mod:`chan.regime_figure`.

Every post's figures used to take their colours from :mod:`chan.regime_figure`,
whose brass, green and red were chosen to match the GLD/GDX essay's page. Two of
those pairs fall apart for a reader with red-green colour blindness. Under
deuteranopia the brass of a post's subject and the red of a loss sit 3.0 apart,
on a scale where 8 is the least a reader can rely on.

1. ``ACCENT``, a berry, marks the thing a picture is about.
2. ``GOOD``, a blue, marks a profit or the side that wins.
3. ``LOST``, a vermilion, marks a loss or a warning.

The colours, and the pale tints ``TINT`` and ``REJECT_TINT`` a band or a reject
zone is filled with, live in :mod:`ithildincore.palette`, so the account's other
repositories draw in the same ones. ithildin-core's ``tests/test_palette.py``
measures their contrast and their separation under each kind of colour
blindness, and :mod:`ithildincore.palette`'s docstring names the two gaps the
measurements leave. ``docs/design.md`` says why posts move to them one at a
time rather than all at once.

A post moves by importing these names in place of :mod:`chan.regime_figure`'s,
and its sketch module passes :data:`INKS` to
:func:`ithildincore.whiteboard.render` or :func:`ithildincore.whiteboard.write_gif`.
"""

from __future__ import annotations

from ithildincore.palette import ACCENT, GOOD, INK, INKS, LOST, MUTED, REJECT_TINT, TINT

__all__ = ["ACCENT", "GOOD", "INK", "INKS", "LOST", "MUTED", "REJECT_TINT", "TINT"]
