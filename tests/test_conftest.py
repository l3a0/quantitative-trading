"""The pins for how ``tests/conftest.py`` hands files to xdist's workers.

``pca_factor_momentum_run`` saves its 100 seconds of CI time only while every
file reading it runs on one worker, and nothing else in the suite would
notice if they stopped. The pins run xdist's own ``schedule`` through
:class:`tests.conftest.JoinedFileScheduling`, with two stub workers that
record which tests each is sent, so they fail when xdist stops calling the
method the class overrides as well as when the mapping is wrong. One more pin
holds the fixture at session scope, since a fixture rebuilt for each file
would build the run twice on that one worker.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from xdist.scheduler import LoadFileScheduling

from tests.conftest import JOINED_FILES, JoinedFileScheduling, pytest_xdist_make_scheduler

TESTS = Path(__file__).parent


def _config(dist: str = "loadfile") -> SimpleNamespace:
    """The two options a scheduler reads, for two workers."""
    values = {"dist": dist, "tx": ["2*popen"]}
    return SimpleNamespace(
        getvalue=values.__getitem__, option=SimpleNamespace(loadscopereorder=False)
    )


class _Worker:
    """A worker that records the node ids it is sent rather than running them."""

    def __init__(self, name: str, collection: list[str]) -> None:
        self.gateway = SimpleNamespace(id=name)
        self.shutting_down = False
        self.collection = collection
        self.sent: list[str] = []

    def send_runtest_some(self, indices: list[int]) -> None:
        self.sent += [self.collection[i] for i in indices]

    def shutdown(self) -> None:
        self.shutting_down = True


def _schedule(scheduler: LoadFileScheduling, collection: list[str]) -> list[list[str]]:
    workers = [_Worker(f"gw{i}", collection) for i in range(2)]
    for worker in workers:
        scheduler.add_node(worker)
        scheduler.add_node_collection(worker, collection)
    scheduler.schedule()
    return [worker.sent for worker in workers]


#: Three tests of the pair between two other files, in the order pytest
#: collects them. Plain ``loadfile`` splits this onto both workers.
COLLECTION = [
    "tests/test_pca_factor.py::test_a",
    "tests/test_pca_factor_momentum.py::test_a",
    "tests/test_pca_factor_momentum.py::test_b",
    "tests/test_pca_factor_momentum_figures.py::test_a",
    "tests/test_series.py::test_a",
]


def _files(sent: list[str]) -> set[str]:
    return {nodeid.split("::")[0] for nodeid in sent}


def test_plain_loadfile_splits_the_pair() -> None:
    """The control, which shows this collection can separate the pair at all."""
    sent = _schedule(LoadFileScheduling(_config()), COLLECTION)
    momentum, figures = "tests/test_pca_factor_momentum.py", next(iter(JOINED_FILES))
    assert not any({momentum, figures} <= _files(s) for s in sent)


def test_the_pair_runs_on_one_worker_and_every_other_file_keeps_its_own_unit() -> None:
    scheduler = JoinedFileScheduling(_config())
    sent = _schedule(scheduler, COLLECTION)
    pair = {*JOINED_FILES, *JOINED_FILES.values()}
    assert sorted(_files(s) & pair for s in sent) == [set(), pair]
    units = {unit for work in scheduler.assigned_work.values() for unit in work}
    assert units == {
        "tests/test_pca_factor.py",
        "tests/test_pca_factor_momentum.py",
        "tests/test_series.py",
    }


def test_every_file_reading_the_shared_run_is_in_one_work_unit() -> None:
    """A new reader of ``pca_factor_momentum_run`` fails here until it joins the pair."""
    scheduler = JoinedFileScheduling(_config())
    readers = {
        f"tests/{path.name}"
        for path in TESTS.glob("test_*.py")
        if path.name != Path(__file__).name and "pca_factor_momentum_run" in path.read_text()
    }
    assert readers == {*JOINED_FILES, *JOINED_FILES.values()}
    assert len({scheduler._split_scope(f"{reader}::test") for reader in readers}) == 1


def test_only_loadfile_is_scheduled_here() -> None:
    assert isinstance(pytest_xdist_make_scheduler(_config(), None), JoinedFileScheduling)
    for dist in ("load", "loadscope", "loadgroup", "worksteal", "no"):
        assert pytest_xdist_make_scheduler(_config(dist), None) is None


def test_the_shared_run_is_built_once_per_session(request) -> None:
    """One work unit saves nothing if the fixture is rebuilt for each file in it.

    ``_fixturemanager`` is private to pytest, the same price the scheduling
    pins pay for ``_split_scope``.
    """
    (definition,) = request._fixturemanager.getfixturedefs("pca_factor_momentum_run", request.node)
    assert definition.scope == "session"
