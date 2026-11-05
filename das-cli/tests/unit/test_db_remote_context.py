import sys
from pathlib import Path

import pytest

SRC_PATH = Path(__file__).resolve().parents[2] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from commands.db.db_services import DbOperations  # noqa: E402


class _ExecutionContext:
    source = {"ip": "203.0.113.5"}


class _Command:
    def log(self, *args, **kwargs):
        return None

    def stdout(self, *args, **kwargs):
        return None

    def get_execution_context(self):
        return _ExecutionContext()


class _Manager:
    def __init__(self, nodes, *, cluster=False):
        self._options = {
            "redis_port": 6379,
            "redis_nodes": nodes,
            "redis_cluster": cluster,
            "mongodb_port": 27017,
            "mongodb_nodes": nodes,
            "mongodb_cluster": cluster,
            "mongodb_username": "admin",
            "mongodb_password": "admin",
            "mongodb_cluster_secret_key": None,
        }
        self.started = 0
        self.stopped = 0
        self.cluster_started = False

    def set_exec_context(self, context):
        return None

    def unset_exec_context(self):
        return None

    def start_container(self, *args, **kwargs):
        self.started += 1

    def start_cluster(self, *args, **kwargs):
        self.cluster_started = True

    def stop(self, **kwargs):
        self.stopped += 1


def _operations():
    return DbOperations(_Command())


@pytest.mark.parametrize("ip", ["", "localhost", "127.0.0.1", "0.0.0.0"])
def test_local_peers_are_not_rejected_for_missing_context(ip):
    operations = _operations()
    node = {"ip": ip, "context": "", "username": "das"}

    assert operations._missing_remote_context("Redis", node) is False
    assert operations.errors == []


def test_remote_peer_without_context_fails_start_and_skips_cluster():
    operations = _operations()
    manager = _Manager(
        [
            {"ip": "10.1.0.8", "context": "", "username": "das"},
            {"ip": "10.1.0.9", "context": "remote-context", "username": "das"},
        ],
        cluster=True,
    )

    operations._start_redis_nodes(manager)

    assert manager.started == 1
    assert manager.cluster_started is False
    assert any(
        "10.1.0.8" in error and "has no Docker context" in error for error in operations.errors
    )

    operations.reset()
    operations._start_mongo_nodes(manager)
    assert manager.cluster_started is False
    assert any("has no Docker context" in error for error in operations.errors)


def test_remote_peer_without_context_fails_stop():
    operations = _operations()
    manager = _Manager([{"ip": "10.2.0.8", "context": "", "username": "das"}])

    operations._stop_redis_nodes(manager, prune=False)
    operations._stop_mongo_nodes(manager, prune=False)

    assert manager.stopped == 0
    assert len(operations.errors) == 2
    assert all("has no Docker context" in error for error in operations.errors)
