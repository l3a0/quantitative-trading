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

One run of Example 1.1's three hypothesis tests takes about half a minute, a
time no test holds, and two files pin what it computes:
``tests/test_tu_hypothesis_tests.py`` its figures, and
``tests/test_tu_hypothesis_tests_figures.py`` what its figure draws. So
``tu_hypothesis_run`` shares that run as ``cpo_result`` does, under the same
rules, and ``--dist loadfile`` computes it at most twice.

Example 7.4's factor momentum run on Chan's S&P 600 file takes about 100
seconds on CI, and two files pin what it computes:
``tests/test_pca_factor_momentum.py`` its figures, and
``tests/test_pca_factor_momentum_figures.py`` what its figure draws.
``pca_factor_momentum_run`` shares it, and the scheduler hook below puts both
files in one ``loadfile`` work unit, so one worker builds it once per run.
Every other file keeps its own unit. That is the difference from
``--dist loadgroup``, which the register cut because it hands every test
outside a group out one at a time. ``tests/test_pca_factor.py`` reads the same
file and stays out, because ``chan.pca_factor.compute`` is a different
computation and the two share only the panel read.

The ``pytest_configure`` hook below caps each worker's numerical thread
pools at one thread. A pool sizes itself to every core, so four workers on
four cores ran up to four threads each. Two paired runs on CI's 4-core
runner, measured on 2026-10-05, took 334 and 338 seconds with the cap and 465
and 557 without it, against 719 and 769 serially.
"""

from __future__ import annotations

import io
import os
from collections.abc import Mapping
from contextlib import redirect_stdout
from pathlib import Path

import pytest
from xdist.scheduler import LoadFileScheduling

from chan import cpo, tu_hypothesis_tests
from chan.archive import ArchiveUnavailable, archive_dir
from chan.pca_factor import SMALL_CAPS
from chan.pca_factor_momentum import (
    Decomposition,
    Results,
    WeightStatistics,
    compute_both,
    daily_components,
    file_returns,
    weight_statistics,
)
from chan.series import load_panel

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


#: Test files that join another file's ``loadfile`` work unit, keyed by their
#: own path and mapped to the path whose unit they join, because both read one
#: session fixture.
JOINED_FILES = {
    "tests/test_pca_factor_momentum_figures.py": "tests/test_pca_factor_momentum.py",
}


class JoinedFileScheduling(LoadFileScheduling):
    """``--dist loadfile``, with each file in :data:`JOINED_FILES` run beside its partner.

    ``_split_scope`` is where xdist turns a test's node id into its work unit.
    The method is private, so ``tests/test_conftest.py`` runs xdist's own
    ``schedule`` through this class, and a release that stops calling it fails
    there rather than quietly building the shared run twice.
    """

    def _split_scope(self, nodeid: str) -> str:
        scope = super()._split_scope(nodeid)
        return JOINED_FILES.get(scope, scope)


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_make_scheduler(config: pytest.Config, log) -> LoadFileScheduling | None:
    """Schedule ``--dist loadfile`` with :class:`JoinedFileScheduling`, and leave the rest."""
    if config.getvalue("dist") == "loadfile":
        return JoinedFileScheduling(config, log)
    return None


#: Set to 1 to run the archive pins. Example 7.1's full run takes minutes, so
#: they do not run by default. ``.claude/settings.json`` sets it for every
#: Claude Code session here, and the design doc's Configuration table says why.
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
        return f"the archive pins run only with {RUN_ENV}=1"
    return None


@pytest.fixture(scope="session")
def cpo_result() -> cpo.Result:
    """One full run of Example 7.1, or a skip naming what is missing."""
    reason = archive_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    return cpo.run()


@pytest.fixture(scope="session")
def tu_hypothesis_run() -> tuple[tu_hypothesis_tests.HypothesisTests, str]:
    """``chan.tu_hypothesis_tests.run`` on the declared seeds, with what it prints.

    Every test reading it treats it as read-only, since a session fixture
    hands the same object to each.
    """
    out = io.StringIO()
    with redirect_stdout(out):
        result = tu_hypothesis_tests.run()
    return result, out.getvalue()


@pytest.fixture(scope="session")
def pca_factor_momentum_run() -> tuple[Results, list[Decomposition], WeightStatistics]:
    """``compute_both``, every fitting day's decomposition, and the weight statistics.

    All three read the Close column of :data:`chan.pca_factor.SMALL_CAPS`.
    The 753 decompositions and the 1,504 more inside ``weight_statistics``
    are most of the time. Every test reading it treats it as read-only.
    """
    _, closes = load_panel(SMALL_CAPS, field="Close")
    returns = file_returns(closes)
    components = daily_components(returns)
    return compute_both(closes), components, weight_statistics(returns, components)
