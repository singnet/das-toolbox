from shared.builders.atom_db_builder import AtomDbBuilder


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
