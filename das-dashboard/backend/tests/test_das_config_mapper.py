from shared.builders.atom_db_builder import AtomDbBuilder
from shared.internal.configuration_constants import CONSTANTS
from shared.mappers.das_config_mapper import ConfigMapper
from shared.mappers.nested_config_mapper import NestedConfigMapper
from shared.utils.flat_config_utils import merge_flat_config


def test_dashboard_config_matches_das_1_2_1_schema_and_vault_contract():
    flat_config = merge_flat_config({})
    flat_config["agents.link_creation"].update(
        {
            "repeat_count": 1,
            "query_interval": 0,
            "query_timeout": 0,
            "max_answers": 10,
        }
    )

    config = ConfigMapper.build_config(flat_config)

    assert config["atomdb"]["uid"] == "local"
    assert config["atomdb"]["composite_type_enabled"] is True
    assert config["agents"]["schema_version"] == "1.2.1"
    assert config["agents"]["base_proxy"] == {"params": {"orchestration_schema": 0}}
    assert config["vault"] == CONSTANTS["vault"]
    assert set(config["agents"]["base_query"]["params"]) == {
        "unique_assignment_flag",
        "attention_update",
        "attention_correlation",
        "attention_focus_strictness",
        "max_bundle_size",
        "max_answers",
        "populate_metta_mapping",
        "use_metta_as_query_tokens",
        "allow_incomplete_chain_path",
        "public_key_tokens",
    }
    assert set(config["agents"]["link_creation"]["params"]) == {
        "max_successful_creation_per_round",
        "max_unproductive_visits_per_round",
        "max_visit_attempts_per_round",
        "max_rounds",
        "link_creation_strength_threshold",
    }
    assert set(config["agents"]["query"]["params"]) == {
        "positive_importance_flag",
        "disregard_importance_flag",
        "unique_value_flag",
        "count_flag",
    }
    assert set(config["agents"]["evolution"]["params"]) == {
        "population_size",
        "max_generations",
        "elitism_rate",
        "selection_rate",
    }
    assert set(config["agents"]["context"]["params"]) == {
        "context",
        "use_cache",
        "enforce_cache_recreation",
        "initial_rent_rate",
        "initial_spreading_rate_lowerbound",
        "initial_spreading_rate_upperbound",
    }
    flat_round_trip = NestedConfigMapper.to_flat(config)
    assert flat_round_trip["atomdb"]["atomdb_uid"] == "local"
    assert flat_round_trip["atomdb"]["composite_type_enabled"] is True
    assert flat_round_trip["agents.base_proxy"] == {"orchestration_schema": 0}
    assert flat_round_trip["vault"] == CONSTANTS["vault"]


def test_atomdb_composite_type_setting_survives_round_trip():
    for enabled in (True, False):
        nested = {
            "atomdb": {
                "type": "inmemorydb",
                "uid": "local",
                "composite_type_enabled": enabled,
            }
        }

        flat = NestedConfigMapper.to_flat(nested)

        assert flat["atomdb"]["composite_type_enabled"] is enabled
        assert AtomDbBuilder().build(flat["atomdb"]) == nested["atomdb"]


def test_remote_peer_persistence_uids_are_unique_and_survive_round_trip():
    peers = [
        {
            "uid": uid,
            "type": "redismongodb",
            "context": "default",
            "redis_endpoint": "127.0.0.1",
            "redis_port": 40020,
            "mongo_endpoint": "127.0.0.1",
            "mongo_port": 40021,
            "mongo_username": "admin",
            "mongo_password": "example",
            "local_persistence": {"type": "inmemorydb"},
        }
        for uid in ("peer-one", "peer-two")
    ]
    peers[1]["local_persistence"]["uid"] = "custom-store"
    builder = AtomDbBuilder()

    atomdb = builder.build({"atomdb_type": "remotedb", "remote_peers": peers})

    assert atomdb["remote_peers"][0]["local_persistence"]["uid"] == "peer-one-local"
    assert atomdb["remote_peers"][1]["local_persistence"]["uid"] == "custom-store"
    flat = NestedConfigMapper.to_flat({"atomdb": atomdb})
    assert builder.build(flat["atomdb"]) == atomdb


def test_remote_peer_provisioning_generates_independent_server_configurations():
    config = {
        "atomdb": {
            "type": "remotedb",
            "uid": "local",
            "composite_type_enabled": True,
            "remote_peers": [
                {
                    "uid": uid,
                    "type": "redismongodb",
                    "redis": {"endpoint": f"{host}:40020"},
                    "mongodb": {
                        "endpoint": f"{host}:40021",
                        "username": "admin",
                        "password": "example",
                    },
                }
                for uid, host in (("peer1", "192.0.2.1"), ("peer2", "192.0.2.2"))
            ],
        },
        "agents": {"schema_version": "1.2.1"},
    }

    configurations = AtomDbBuilder(profile_username="levi").build_remote_peer_configs(config)

    assert set(configurations) == {"192.0.2.1", "192.0.2.2"}
    for index, host in enumerate(configurations, start=1):
        remote = configurations[host]
        assert remote["atomdb"]["type"] == "redismongodb"
        assert remote["atomdb"]["uid"] == f"peer{index}"
        assert remote["atomdb"]["redis"]["endpoint"] == "127.0.0.1:40020"
        assert remote["atomdb"]["mongodb"]["endpoint"] == "127.0.0.1:40021"
        assert remote["atomdb"]["mongodb"]["password"] == "example"
        assert remote["agents"] == config["agents"]
        assert "remote_peers" not in remote["atomdb"]
    assert config["atomdb"]["type"] == "remotedb"
    assert config["atomdb"]["remote_peers"][0]["redis"]["endpoint"] == "192.0.2.1:40020"