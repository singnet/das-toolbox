from shared.internal.constants import WORKSPACE_METTA_OUTPUT

# Flat export contract — same shape the frontend sends and receives.
FLAT_SECTION_ORDER = (
    "atomdb",
    "agents.attention",
    "agents.base_query",
    "agents.query",
    "agents.link_creation",
    "agents.inference",
    "agents.evolution",
    "agents.context",
    "agents.atomdb",
    "agents.command_router",
    "environment",
)

AGENTS_SCHEMA_VERSION = "1.1"

LOADERS = {
    "metta": {"image": "trueagi/das:1.0.0-metta-parser"},
    "morkdb": {"image": "trueagi/das:mork-loader-1.1.0"},
}

ATOMDB_TEMPLATES = {
    "redismongodb": {
        "atomdb_type": "redismongodb",
        "redis_endpoint": "localhost",
        "redis_port": 40020,
        "mongo_endpoint": "localhost",
        "mongo_port": 40021,
        "mongo_username": "admin",
        "mongo_password": "admin",
        "redis_cluster": False,
        "mongo_cluster": False,
        "redis_nodes": [
            {"context": "default", "ip": "localhost", "username": "username"}
        ],
        "mongo_nodes": [
            {"context": "default", "ip": "localhost", "username": "username"}
        ],
    },
    "morkdb": {
        "atomdb_type": "morkdb",
        "mork_endpoint": "localhost",
        "mork_port": 40022,
        "mongo_endpoint": "localhost",
        "mongo_port": 40021,
        "mongo_username": "admin",
        "mongo_password": "admin",
        "mongo_cluster": False,
        "mongo_nodes": [
            {"context": "default", "ip": "localhost", "username": "username"}
        ],
    },
    "inmemorydb": {
        "atomdb_type": "inmemorydb",
    },
    "remotedb": {
        "atomdb_type": "remotedb",
        "remote_peers": [
            {
                "uid": "peer1",
                "type": "redismongodb",
                "context": "remotedb_test_peer1_",
                "mongodb": {
                    "endpoint": "localhost:40021",
                    "username": "admin",
                    "password": "admin",
                },
                "redis": {
                    "endpoint": "localhost:40020",
                    "cluster": False,
                },
                "local_persistence": {
                    "type": "morkdb",
                    "context": "remotedb_test_peer1_local_",
                    "mongodb": {
                        "endpoint": "localhost:40021",
                        "username": "admin",
                        "password": "admin",
                    },
                    "morkdb": {"endpoint": "localhost:40022"},
                },
            },
            {
                "uid": "peer2",
                "type": "inmemorydb",
                "context": "remotedb_test_peer2_",
                "local_persistence": {
                    "type": "inmemorydb",
                    "context": "remotedb_test_peer2_local_",
                },
            },
        ],
    },
    "adapterdb": {
        "atomdb_type": "adapterdb",
        "adapter_type": "postgres",
        "adapter_endpoint": "localhost",
        "adapter_port": 40023,
        "db_host": "chado.flybase.org",
        "db_port": 5432,
        "db_name": "flybase",
        "db_username": "flybase",
        "db_password": "",
        "context_mapping_path": "",
        "export_metta_enabled": True,
        "export_metta_output_dir": WORKSPACE_METTA_OUTPUT,
        "persistence_reuse_mongodb": True,
        "atomdb_backend": {
            "type": "morkdb",
            "mork_endpoint": "localhost",
            "mork_port": 40022,
            "mongo_endpoint": "localhost",
            "mongo_port": 40021,
            "mongo_username": "admin",
            "mongo_password": "admin",
            "mongo_cluster": False,
            "mongo_nodes": [
                {"context": "default", "ip": "localhost", "username": "username"}
            ],
        },
    },
}

CONSTANTS = {
    "atomdb": ATOMDB_TEMPLATES["redismongodb"],
    "agents.attention": {
        "endpoint": "localhost:40001",
    },
    "agents.base_query": {
        "unique_assignment_flag": False,
        "attention_update": 0,
        "attention_correlation": 0,
        "max_bundle_size": 1000,
        "max_answers": 0,
        "use_link_template_cache": False,
        "populate_metta_mapping": False,
        "use_metta_as_query_tokens": False,
        "allow_incomplete_chain_path": False,
    },
    "agents.query": {
        "endpoint": "localhost:40002",
        "ports_range": "42000:42999",
        "positive_importance_flag": False,
        "disregard_importance_flag": False,
        "unique_value_flag": False,
        "count_flag": False,
    },
    "agents.link_creation": {
        "endpoint": "localhost:40003",
        "ports_range": "43000:43999",
        "max_answers": 10,
        "repeat_count": 1,
        "context": "context",
        "attention_update": 0,
        "attention_correlation": 0,
        "positive_importance_flag": True,
        "query_interval": 0,
        "query_timeout": 0,
        "use_metta_as_query_tokens": False,
    },
    "agents.inference": {
        "endpoint": "localhost:40004",
        "ports_range": "44000:44999",
        "inference_request_timeout": 86400,
        "repeat_count": 5,
        "max_answers": 150,
    },
    "agents.evolution": {
        "endpoint": "localhost:40005",
        "ports_range": "45000:45999",
        "population_size": 1000,
        "max_generations": 100,
        "elitism_rate": 0.01,
        "selection_rate": 0.1,
    },
    "agents.context": {
        "endpoint": "localhost:40006",
        "ports_range": "46000:46999",
        "context": "context",
        "use_cache": True,
        "enforce_cache_recreation": False,
        "initial_rent_rate": 0.75,
        "initial_spreading_rate_lowerbound": 0.1,
        "initial_spreading_rate_upperbound": 0.1,
    },
    "agents.atomdb": {
        "endpoint": "localhost:40007",
        "ports_range": "47000:47999",
    },
    "agents.command_router": {
        "endpoint": "localhost:40008",
        "ports_range": "48000:48999",
    },
    "environment": {
        "jupyter_endpoint": "localhost:40019",
    },
}
