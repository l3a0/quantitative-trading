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

**Where this came from.** ``common/paths.py`` in the sibling
``trading-strategies`` repo, at commit ``b27222b``, landed here in ``ce3f757``.
The commit is the anchor rather than the path, because that repo retired its
Chan material in ``cc1ec3a`` and ``b27222b`` is the ancestor where every file
copied here still resolves. The copy changed three things.

1. ``parents[1]`` became ``parents[2]``, for the deeper ``src/chan/`` layout.
2. ``FIGURES_DIR`` was dropped, because nothing here drew a figure yet.
3. The comment above ``DATA_DIR`` was dropped and the docstring rewritten.

Those three describe the file at ``ce3f757`` rather than today's file.
``data_path`` came across intact and went later, in ``71061d6``, and
``FIGURES_DIR`` came back in ``fbb29ea``, so a diff against today's file shows
the sibling and this one agreeing on a constant the port had dropped. Diff
``b27222b`` against ``ce3f757`` to read the port and against ``HEAD`` to read
everything since, with docstrings stripped from both sides, because they are
most of it.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
FIGURES_DIR = REPO_ROOT / "docs" / "figures"
