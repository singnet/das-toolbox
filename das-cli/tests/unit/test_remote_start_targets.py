import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[2] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from common.factory.atomdb.remote_start_targets import remote_local_persistences  # noqa: E402


def _config():
    return {
        "atomdb": {
            "type": "remotedb",
            "remote_peers": [
                {
                    "uid": "peer1",
                    "type": "redismongodb",
                    "local_persistence": {
                        "type": "morkdb",
                        "context": "remotedb_peer1_local_",
                        "morkdb": {"endpoint": "10.0.0.8:40022"},
                        "mongodb": {"endpoint": "10.0.0.8:40023", "username": "admin", "password": "admin"},
                    },
                },
                {
                    "uid": "peer2",
                    "type": "morkdb",
                    "local_persistence": {
                        "type": "inmemorydb",
                        "context": "remotedb_peer2_local_",
                    },
                },
                {
                    "uid": "peer3",
                    "type": "inmemorydb",
                    "local_persistence": {
                        "type": "redismongodb",
                        "context": "remotedb_peer3_local_",
                        "redis": {"endpoint": "localhost:40020"},
                        "mongodb": {"endpoint": "localhost:40021", "username": "admin", "password": "admin"},
                    },
                },
            ],
        },
        "db_start_targets": [
            {
                "codename": "remotedb_peer1_local_",
                "type": "morkdb",
                "nodes": [{"context": "ctx-peer1", "ip": "10.0.0.8", "username": "levi"}],
            },
            {
                "codename": "remotedb_peer2_local_",
                "type": "inmemorydb",
                "nodes": [{"context": "default", "ip": "localhost", "username": "levi"}],
            },
            {
                "codename": "remotedb_peer3_local_",
                "type": "redismongodb",
                "nodes": [{"context": "default", "ip": "localhost", "username": "levi"}],
            },
        ],
    }


def test_remote_local_persistences_skip_inmemory():
    persistences = remote_local_persistences(_config())

    assert [persistence["codename"] for persistence in persistences] == [
        "remotedb_peer1_local_",
        "remotedb_peer3_local_",
    ]
    assert persistences[0]["type"] == "morkdb"
    assert persistences[0]["morkdb"]["nodes"] == [
        {"context": "ctx-peer1", "ip": "10.0.0.8", "username": "levi"}
    ]
    assert persistences[0]["morkdb"]["endpoint"] == "10.0.0.8:40022"
    assert persistences[1]["type"] == "redismongodb"
    assert persistences[1]["redis"]["endpoint"] == "localhost:40020"
    assert "morkdb" not in persistences[1]


def test_non_remote_config_has_no_local_persistences():
    assert remote_local_persistences({"atomdb": {"type": "redismongodb"}}) == []


def test_remote_without_start_targets_returns_nothing():
    config = _config()
    config.pop("db_start_targets")
    assert remote_local_persistences(config) == []
