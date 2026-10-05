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

The suite runs across pytest-xdist workers, and each worker holds a session of
its own, so the run is built once in every worker that draws a test reading
it. ``--dist loadfile`` keeps each file on one worker, so an archive run builds
it at most twice, once for each of the two files, at the same time. ``-n 0``
runs the suite in one process and builds it once. The design doc's
considered-and-rejected register says why one worker for both files was cut.

The hook below caps each worker's numerical thread pools at one thread. A
pool sizes itself to every core, so four workers on four cores ran up to four
threads each. Two paired runs on CI's 4-core runner, measured on 2026-10-05,
took 334 and 338 seconds with the cap and 465 and 557 without it, against 719
and 769 serially.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

import pytest

from chan import cpo
from chan.archive import ArchiveUnavailable, archive_dir

#: The thread-count variables of OpenMP, OpenBLAS, MKL and Apple's Accelerate,
#: which between them size every numerical thread pool this suite reaches.
THREAD_ENVS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


def pytest_configure(config: pytest.Config) -> None:
    """Give each xdist worker one numerical thread, before any worker starts.

    It runs in the process that starts the workers, which inherit its
    environment, and only when there will be workers, so ``-n 0`` keeps every
    thread. ``setdefault`` leaves a value already in the environment alone.
    """
    if getattr(config.option, "numprocesses", 0) and not hasattr(config, "workerinput"):
        for name in THREAD_ENVS:
            os.environ.setdefault(name, "1")


#: Set to 1 to run the archive pins. The full run takes minutes, so they do not
#: run by default. ``.claude/settings.json`` sets it for every Claude Code
#: session here, and the design doc's Configuration table says why.
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
