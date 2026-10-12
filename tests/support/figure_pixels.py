"""Whether two PNGs show the same picture, and how far apart they are when not.

``tests/test_figures_match_code.py`` and ``tests/test_cpo_figures.py`` both
compare a fresh draw with a committed figure, so the comparison is written once
here.

It compares decoded pixels rather than file bytes. A PNG matplotlib writes
carries one text chunk, ``Software``, naming the matplotlib version that drew
it, and decoding drops it. So a draw under another matplotlib release that
paints the same pixels compares equal, while a byte comparison would fail on
the tag alone. ``docs/design.md``'s register row on the regime map says why the
byte comparison was declined.

Decoding goes through Pillow, which the lock carries only because matplotlib
depends on it. ``png_size`` in ``tests/test_regime_figure.py`` reads its header
by hand to stay off an image library. Comparing pixels needs one, and Pillow is
the one already installed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def rgba(path: Path) -> np.ndarray:
    """The PNG's pixels as an array of height by width by four 8-bit channels."""
    with Image.open(path) as image:
        return np.asarray(image.convert("RGBA"))


def pixel_difference(drawn: Path, committed: Path) -> str | None:
    """None when the two PNGs decode to the same pixels, else what differs.

    The message gives how many pixels differ and the largest difference in any
    one channel, so a failure says how far off the committed file is rather
    than only that it is off.
    """
    new, old = rgba(drawn), rgba(committed)
    if new.shape != old.shape:
        return (
            f"{committed.name}: a fresh draw is {new.shape[1]} by {new.shape[0]} pixels "
            f"and the committed file is {old.shape[1]} by {old.shape[0]}"
        )
    gap = np.abs(new.astype(np.int16) - old.astype(np.int16))
    differing = int(np.count_nonzero(gap.max(axis=2)))
    if differing == 0:
        return None
    return (
        f"{committed.name}: {differing:,} of {new.shape[0] * new.shape[1]:,} pixels differ "
        f"from a fresh draw, by at most {int(gap.max())} of 255"
    )


def assert_same_pixels(drawn: Path, committed: Path) -> None:
    """Fail with :func:`pixel_difference`'s message when the pixels differ."""
    difference = pixel_difference(drawn, committed)
    assert difference is None, difference
