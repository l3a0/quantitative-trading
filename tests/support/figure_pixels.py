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

The comparison is exact, and it holds only on the platform the committed
figures are drawn on, macOS arm64. The first CI run of issue 581, on Linux
x86_64 with the same locked packages, drew 15 of 57 figures differently, by up
to 13 levels out of 255 on ``etf_cointegration.png``. A tolerance that wide
would also pass ``risk_parity_cash_rate.png``'s stale copy, which was 2 levels
off. So :func:`platform_skip_reason` skips the comparison anywhere else, and
only a run on macOS arm64 catches a stale figure.

Decoding goes through Pillow, which the lock carries only because matplotlib
depends on it. ``png_size`` in ``tests/test_regime_figure.py`` reads its header
by hand to stay off an image library. Comparing pixels needs one, and Pillow is
the one already installed.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

import numpy as np
from PIL import Image

#: Where the committed figures are drawn, as ``sys.platform`` and
#: ``platform.machine()`` report it.
DRAWING_PLATFORM = ("darwin", "arm64")


def platform_skip_reason(system: str | None = None, machine: str | None = None) -> str | None:
    """Why a comparison with a committed figure should skip here, or None.

    The arguments default to this machine, and a test passes them to show the
    gate opens on macOS arm64 and closes elsewhere.
    """
    here = (
        sys.platform if system is None else system,
        platform.machine() if machine is None else machine,
    )
    if here == DRAWING_PLATFORM:
        return None
    return (
        f"the committed figures are drawn on {' '.join(DRAWING_PLATFORM)} and this is "
        f"{' '.join(here)}, where matplotlib draws some edges differently"
    )


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
