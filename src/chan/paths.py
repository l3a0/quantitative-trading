"""Where the committed vintages live.

A run reads a series from disk, never from a vendor. That is the premise in
[docs/design.md](../../docs/design.md): a number computed from a series nobody
kept is a number nobody can check. So the data tree is named once, relative to
the repository root, and the same files are found whether the caller is
``python -m chan.pair_cointegration`` from the root or a pytest run from
anywhere else.

``DATA_DIR`` is the single switch that says where the vintages sit. Moving the
data tree is a one-line change in this file, and :mod:`chan.vintage` reads the
name through this module rather than binding it at import, so the switch stays
one switch. Which file inside that tree a run reads is not decided here at all:
:mod:`chan.series` asks ``data/vintages.jsonl`` for the path.

``FIGURES_DIR`` does the same for the one committed image, which
:mod:`chan.regime_figure` draws from those same vintages.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
FIGURES_DIR = REPO_ROOT / "docs" / "figures"
