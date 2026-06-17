CONSTANTS = {
  "atomdb.type": "redismongodb",
  "atomdb.redis.image": "redis:7.2.3-alpine",
  "atomdb.redis.endpoint": "localhost:40020",
  "atomdb.redis.cluster": True,
  "atomdb.redis.nodes": [
    {
      "context": "default",
      "ip": "localhost",
      "username": "arturgontijo"
    }
  ],
  "atomdb.mongodb.image": "mongodb/mongodb-community-server:8.2-ubuntu2204",
  "atomdb.mongodb.endpoint": "localhost:40021",
  "atomdb.mongodb.username": "admin",
  "atomdb.mongodb.password": "admin",
  "atomdb.mongodb.cluster": False,
  "atomdb.mongodb.cluster_secret_key": "8UDJSgpUCaVOTQG",
  "atomdb.mongodb.nodes": [
    {
      "context": "default",
      "ip": "localhost",
      "username": "arturgontijo"
    }
  ],
  "atomdb.adapterdb.endpoint": "localhost:40023",
  "atomdb.adapterdb.type": "postgres",
  "atomdb.adapterdb.database_credentials.host": "chado.flybase.org",
  "atomdb.adapterdb.database_credentials.port": 5432,
  "atomdb.adapterdb.database_credentials.username": "flybase",
  "atomdb.adapterdb.database_credentials.password": "",
  "atomdb.adapterdb.database_credentials.database": "flybase",
  "atomdb.adapterdb.context_mapping_paths": [
    "./simple_test.sql",
    "./tables.json"
  ],
  "atomdb.adapterdb.export_metta_on_mapping.enabled": True,
  "atomdb.adapterdb.export_metta_on_mapping.output_dir": "./mapped_metta/",
  "atomdb.adapterdb.persistence.reuse_mongodb": True,
  "atomdb.adapterdb.atomdb_backend.type": "morkdb",
  "atomdb.adapterdb.atomdb_backend.mongodb.endpoint": "localhost:40021",
  "atomdb.adapterdb.atomdb_backend.mongodb.username": "admin",
  "atomdb.adapterdb.atomdb_backend.mongodb.password": "admin",
  "atomdb.adapterdb.atomdb_backend.mongodb.cluster": False,
  "atomdb.adapterdb.atomdb_backend.mongodb.cluster_secret_key": "None",
  "atomdb.adapterdb.atomdb_backend.mongodb.nodes": [
    {
      "context": "default",
      "ip": "localhost",
      "username": "username"
    }
  ],
  "atomdb.adapterdb.atomdb_backend.morkdb.endpoint": "localhost:40022",
  "atomdb.morkdb.image": "trueagi/das:mork-server-1.0.4",
  "atomdb.morkdb.endpoint": "localhost:40022",
  "atomdb.remote_peers": [
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
        "cluster": False
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
  ],
  "loaders.metta.image": "trueagi/das:1.0.0-metta-parser",
  "loaders.morkdb.image": "rueagi/das:mork-loader-1.0.4",
  "agents.schema_version": "1.1",
  "agents.attention.endpoint": "localhost:40001",
  "agents.base_query.params.unique_assignment_flag": False,
  "agents.base_query.params.attention_update": 0,
  "agents.base_query.params.attention_correlation": 0,
  "agents.base_query.params.max_bundle_size": 1000,
  "agents.base_query.params.max_answers": 0,
  "agents.base_query.params.use_link_template_cache": False,
  "agents.base_query.params.populate_metta_mapping": False,
  "agents.base_query.params.use_metta_as_query_tokens": False,
  "agents.base_query.params.allow_incomplete_chain_path": False,
  "agents.query.endpoint": "localhost:40002",
  "agents.query.ports_range": "42000:42999",
  "agents.query.params.positive_importance_flag": False,
  "agents.query.params.disregard_importance_flag": False,
  "agents.query.params.unique_value_flag": False,
  "agents.query.params.count_flag": False,
  "agents.link_creation.endpoint": "localhost:40003",
  "agents.link_creation.ports_range": "43000:43999",
  "agents.link_creation.params.max_answers": 10,
  "agents.link_creation.params.repeat_count": 1,
  "agents.link_creation.params.context": "context",
  "agents.link_creation.params.attention_update": 0,
  "agents.link_creation.params.attention_correlation": 0,
  "agents.link_creation.params.positive_importance_flag": True,
  "agents.link_creation.params.query_interval": 0,
  "agents.link_creation.params.query_timeout": 0,
  "agents.link_creation.params.use_metta_as_query_tokens": False,
  "agents.inference.endpoint": "localhost:40004",
  "agents.inference.ports_range": "44000:44999",
  "agents.inference.params.inference_request_timeout": 86400,
  "agents.inference.params.repeat_count": 5,
  "agents.inference.params.max_answers": 150,
  "agents.evolution.endpoint": "localhost:40005",
  "agents.evolution.ports_range": "45000:45999",
  "agents.evolution.params.population_size": 1000,
  "agents.evolution.params.max_generations": 100,
  "agents.evolution.params.elitism_rate": 0.01,
  "agents.evolution.params.selection_rate": 0.1,
  "agents.context.endpoint": "localhost:40006",
  "agents.context.ports_range": "46000:46999",
  "agents.context.params.context": "context",
  "agents.context.params.use_cache": True,
  "agents.context.params.enforce_cache_recreation": False,
  "agents.context.params.initial_rent_rate": 0.75,
  "agents.context.params.initial_spreading_rate_lowerbound": 0.1,
  "agents.context.params.initial_spreading_rate_upperbound": 0.1,
  "agents.atomdb.endpoint": "localhost:40007",
  "agents.atomdb.ports_range": "47000:47999",
  "agents.command_router.endpoint": "localhost:40008",
  "agents.command_router.ports_range": "48000:48999",
  "environment.jupyter.endpoint": "localhost:40019"
}