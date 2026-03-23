from typing import Any, Dict

def get_core_defaults_dict() -> Dict[str, Any]:
    core_defaults: Dict[str, Any] = {
        "schema_version": "1.0",
        "atomdb": {
            "type": "redismongodb",
            "redis": {
                "endpoint": "localhost:40020",
                "cluster": "false",
                "nodes": []
            },
            "mongodb": {
                "endpoint": "localhost:40021",
                "username": "admin",
                "password": "admin",
                "cluster": "false",
                "cluster_secret_key": "8UDJSgpUCaVOTQG",
                "nodes": []
            },
            "morkdb": {
                "endpoint": "localhost:40022"
            },
            "remote_peers": [
                {
                    "uid": "peer1",
                    "type": "redismongodb",
                    "context": "remotedb_test_peer1_",
                    "mongodb": {
                        "endpoint": "localhost:40021",
                        "username": "admin",
                        "password": "admin"
                    },
                    "redis": {
                        "endpoint": "localhost:40020",
                        "cluster": "false"
                    },
                    "local_persistence": {
                        "type": "morkdb",
                        "context": "remotedb_test_peer1_local_",
                        "mongodb": {
                            "endpoint": "localhost:40021",
                            "username": "admin",
                            "password": "admin"
                        },
                        "morkdb": {
                            "endpoint": "localhost:40022"
                        }
                    }
                },
                {
                    "uid": "peer2",
                    "type": "inmemorydb",
                    "context": "remotedb_test_peer2_",
                    "local_persistence": {
                        "type": "inmemorydb",
                        "context": "remotedb_test_peer2_local_"
                    }
                }
            ]
        },
        "agents": {
            "query": {
                "endpoint": "localhost:40002",
                "ports_range": "42000:42999"
            },
            "link_creation": {
                "endpoint": "localhost:40003",
                "ports_range": "43000:43999"
            },
            "inference": {
                "endpoint": "localhost:40004",
                "ports_range": "44000:44999"
            },
            "evolution": {
                "endpoint": "localhost:40005",
                "ports_range": "45000:45999"
            }
        },
        "brokers": {
            "attention": {
                "endpoint": "localhost:40001"
            },
            "context": {
                "endpoint": "localhost:40006",
                "ports_range": "46000:46999"
            },
            "atomdb": {
                "endpoint": "localhost:40007",
                "ports_range": "47000:47999"
            }
        },
        "params": {
            "query": {
                "max_answers": 100,
                "max_bundle_size": 1000,
                "count_flag": "false",
                "attention_update_flag": "false",
                "unique_assignment_flag": "true",
                "positive_importance_flag": "false",
                "populate_metta_mapping": "true",
                "use_metta_as_query_tokens": "true"
            },
            "link_creation": {
                "repeat_count": 1,
                "query_interval": 0,
                "query_timeout": 0
            },
            "evolution": {
                "elitism_rate": 0.08,
                "max_generations": 10,
                "population_size": 50,
                "selection_rate": 0.1,
                "total_attention_tokens": 100000
            },
            "context": {
                "context": "context",
                "use_cache": "true",
                "enforce_cache_recreation": "false",
                "initial_rent_rate": 0.25,
                "initial_spreading_rate_lowerbound": 0.5,
                "initial_spreading_rate_upperbound": 0.7
            }
        },
        "environment": {
            "jupyter": {
                "endpoint": "localhost:40019"
            }
        }
    }

    return core_defaults
