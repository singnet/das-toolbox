from shared.builders.atom_db_builder import AtomDbBuilder
from shared.builders.db_start_targets import build_db_start_targets


def test_remote_inmemory_peer_keeps_type_and_atomdb_identity():
    built = AtomDbBuilder("das").build(
        {
            "atomdb_type": "remotedb",
            "atomdb_uid": "dataset-1",
            "composite_type_enabled": False,
            "remote_peers": [
                {
                    "uid": "peer2",
                    "type": "inmemorydb",
                    "context": "remotedb_test_peer2_",
                    "local_persistence": {"type": "inmemorydb", "context": "remotedb_test_peer2_local_"},
                }
            ],
        }
    )

    assert built["uid"] == "dataset-1"
    assert built["composite_type_enabled"] is False
    peer = built["remote_peers"][0]
    assert peer["type"] == "inmemorydb"
    assert peer["context"] == "remotedb_test_peer2_"
    assert "redis" not in peer
    assert "mongodb" not in peer
    assert peer["local_persistence"]["type"] == "inmemorydb"


def test_remote_peer_databases_do_not_carry_docker_nodes():
    built = AtomDbBuilder("das").build(
        {
            "atomdb_type": "remotedb",
            "remote_peers": [
                {
                    "uid": "peer1",
                    "type": "redismongodb",
                    "context": "remotedb_peer1_",
                    "redis_endpoint": "10.0.0.8",
                    "redis_port": 40020,
                    "mongo_endpoint": "10.0.0.8",
                    "mongo_port": 40021,
                    "mongo_username": "admin",
                    "mongo_password": "admin",
                    "local_persistence": {
                        "type": "morkdb",
                        "context": "remotedb_peer1_local_",
                        "mork_endpoint": "10.0.0.8",
                        "mork_port": 40022,
                        "mongo_endpoint": "10.0.0.8",
                        "mongo_port": 40023,
                        "mongo_username": "admin",
                        "mongo_password": "admin",
                    },
                },
                {
                    "uid": "peer2",
                    "type": "morkdb",
                    "context": "remotedb_peer2_",
                    "mork_endpoint": "10.0.0.9",
                    "mork_port": 40022,
                    "mongo_endpoint": "10.0.0.9",
                    "mongo_port": 40021,
                    "mongo_username": "admin",
                    "mongo_password": "admin",
                    "local_persistence": {"type": "inmemorydb", "context": "remotedb_peer2_local_"},
                },
            ],
        }
    )

    assert "nodes" not in built["remote_peers"][0]["redis"]
    assert "nodes" not in built["remote_peers"][0]["mongodb"]
    assert build_db_start_targets(built, "levi") == [
        {
            "codename": "remotedb_peer1_local_",
            "type": "morkdb",
            "nodes": [{
                "context": "",
                "ip": "10.0.0.8",
                "username": "levi",
            }],
        }
    ]
