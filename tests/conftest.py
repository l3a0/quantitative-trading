"""Fixtures more than one test file reads.

One run of Example 7.1 on the owner's archive takes minutes, and two files pin
what it computes: ``tests/test_cpo.py`` its figures, and
``tests/test_cpo_figures.py`` the cells its figure labels. A session-scoped
fixture here makes them share that run rather than pay for it twice.

It is named ``cpo_result`` rather than ``result`` because other test files
define a ``result`` fixture of their own, ``tests/test_cpo_figures.py`` with a
synthetic run among them. A shared one under that name would be shadowed in
those files and reachable in the rest, so which run a test read would depend on
which file it sat in.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

import pytest

from chan import cpo
from chan.archive import ArchiveUnavailable, archive_dir

#: Set to 1 to run the archive pins. The full run takes minutes, and every
#: session here runs the suite, so they do not run by default.
RUN_ENV = "QT_ARCHIVE_RUN"


def archive_skip_reason(
    environ: Mapping[str, str] | None = None, config: Path | None = None
) -> str | None:
    """Why the archive pins should skip here, or None when they should run.

    A function rather than inline in the fixture, so ``tests/test_cpo.py`` can
    show the pins run when both conditions hold. An inverted condition would
    otherwise skip every archive pin silently, on the one machine meant to run
    them.
    """
    environ = os.environ if environ is None else environ
    try:
        archive_dir(environ, config)
    except ArchiveUnavailable as absent:
        return str(absent)
    if environ.get(RUN_ENV) != "1":
        return f"the archive pins take minutes, so they run only with {RUN_ENV}=1"
    return None


@pytest.fixture(scope="session")
def cpo_result() -> cpo.Result:
    """One full run of Example 7.1, or a skip naming what is missing."""
    reason = archive_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    return cpo.run()
