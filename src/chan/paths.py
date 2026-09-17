"""Where the committed vintages live.

A run reads a series from disk, never from a vendor. That is the premise in
[docs/design.md](../../docs/design.md): a number computed from a series nobody
kept is a number nobody can check. So every reader resolves its path through
here, relative to the repository root, and the same file is found whether the
caller is ``python -m chan.pair_cointegration`` from the root or a pytest run
from anywhere else.

``DATA_DIR`` is the single switch that says where the vintages sit. Moving the
data tree is a one-line change in this file. ``FIGURES_DIR`` does the same for
the one committed image, which :mod:`chan.regime_figure` draws from those same
vintages.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
FIGURES_DIR = REPO_ROOT / "docs" / "figures"


def data_path(name: str) -> str:
    """Absolute path, as ``str`` for the CSV readers, to ``name`` under ``DATA_DIR``."""
    return str(DATA_DIR / name)
