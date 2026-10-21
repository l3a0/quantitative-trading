"""The pins for how ``tests/conftest.py`` hands files to xdist's workers.

``pca_factor_momentum_run`` and ``cpo_result`` are each built once per run
only while every file reading them runs on one worker, and nothing else in the
suite would notice if they stopped. The pins run xdist's own ``schedule``
through :class:`tests.conftest.JoinedFileScheduling`, with two stub workers
that record which tests each is sent, so they fail when xdist stops calling
the method the class overrides as well as when the mapping is wrong. One more
pin holds each fixture at session scope, since a fixture rebuilt for each file
would build its run twice on that one worker.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from xdist.scheduler import LoadFileScheduling

from tests.conftest import JOINED_FILES, JoinedFileScheduling, pytest_xdist_make_scheduler

TESTS = Path(__file__).parent

#: Each session fixture whose run two files share, and those two files, the
#: second of which joins the first's work unit. Written out here rather than
#: read from :data:`tests.conftest.JOINED_FILES`, so a wrong entry there fails.
SHARED_RUNS = {
    "pca_factor_momentum_run": (
        "tests/test_pca_factor_momentum.py",
        "tests/test_pca_factor_momentum_figures.py",
    ),
    "cpo_result": ("tests/test_cpo.py", "tests/test_cpo_figures.py"),
}

shared_runs = pytest.mark.parametrize(
    ("fixture", "pair"), SHARED_RUNS.items(), ids=list(SHARED_RUNS)
)


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


#: A file outside every pair, which :func:`_collection` puts after the pair.
AFTER = "tests/test_after.py"


def _near_miss(pair: tuple[str, str]) -> str:
    """A file outside the pair whose name is a prefix of the joined file's name.

    It sits before the pair, as ``tests/test_pca_factor.py`` sits before the
    factor momentum pair, so a scheduler matching names by prefix rather than
    whole fails.
    """
    return pair[1].removesuffix(".py")[:-1] + ".py"


def _collection(pair: tuple[str, str]) -> list[str]:
    """Three tests of the pair between two other files, in the order pytest collects them.

    Plain ``loadfile`` splits this onto both workers.
    """
    first, second = pair
    return [
        f"{_near_miss(pair)}::test_a",
        f"{first}::test_a",
        f"{first}::test_b",
        f"{second}::test_a",
        f"{AFTER}::test_a",
    ]


def _files(sent: list[str]) -> set[str]:
    return {nodeid.split("::")[0] for nodeid in sent}


@shared_runs
def test_plain_loadfile_splits_the_pair(fixture, pair) -> None:
    """The control, which shows this collection can separate the pair at all."""
    sent = _schedule(LoadFileScheduling(_config()), _collection(pair))
    assert not any(set(pair) <= _files(s) for s in sent)


@shared_runs
def test_the_pair_runs_on_one_worker_and_every_other_file_keeps_its_own_unit(fixture, pair) -> None:
    scheduler = JoinedFileScheduling(_config())
    sent = _schedule(scheduler, _collection(pair))
    assert sorted(_files(s) & set(pair) for s in sent) == [set(), set(pair)]
    units = {unit for work in scheduler.assigned_work.values() for unit in work}
    assert units == {_near_miss(pair), pair[0], AFTER}


@shared_runs
def test_every_file_reading_the_shared_run_is_in_one_work_unit(fixture, pair) -> None:
    """A new reader of a shared run fails here until it joins the pair."""
    scheduler = JoinedFileScheduling(_config())
    readers = {
        f"tests/{path.name}"
        for path in TESTS.glob("test_*.py")
        if path.name != Path(__file__).name and fixture in path.read_text()
    }
    assert readers == set(pair)
    assert len({scheduler._split_scope(f"{reader}::test") for reader in readers}) == 1


def test_only_the_shared_runs_join_files() -> None:
    """A join beyond the pairs above would take a file out of its own work unit."""
    assert JOINED_FILES == {second: first for first, second in SHARED_RUNS.values()}


def test_only_loadfile_is_scheduled_here() -> None:
    assert isinstance(pytest_xdist_make_scheduler(_config(), None), JoinedFileScheduling)
    for dist in ("load", "loadscope", "loadgroup", "worksteal", "no"):
        assert pytest_xdist_make_scheduler(_config(dist), None) is None


@pytest.mark.parametrize("fixture", SHARED_RUNS)
def test_the_shared_run_is_built_once_per_session(request, fixture) -> None:
    """One work unit saves nothing if the fixture is rebuilt for each file in it.

    ``_fixturemanager`` is private to pytest, the same price the scheduling
    pins pay for ``_split_scope``.
    """
    (definition,) = request._fixturemanager.getfixturedefs(fixture, request.node)
    assert definition.scope == "session"
