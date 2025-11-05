from typing import Any, Dict
from common.utils import calculate_schema_hash, get_rand_token

default_atomdb_backend = "redis_mongodb"
default_port_redis = 40020
default_port_mongodb = 40021
default_port_jupyter = 40019
database_adapter_server_port = 40018
default_port_attention_broker = 40001
default_port_query_agent = 40002
default_port_link_agent = 40003
default_port_inference_agent = 40004
default_port_evolution_agent = 40005
default_port_context_broker = 40006
default_port_morkdb = 40022

def get_core_defaults_dict() -> Dict[str, Any]:
    core_defaults = {
        "schema_hash": None,
        "services.database.atomdb_backend": default_atomdb_backend,
        "services.redis.port": default_port_redis,
        "services.redis.container_name": f"das-cli-redis-{default_port_redis}",
        "services.redis.cluster": False,
        "services.redis.nodes": [],
        "services.mongodb.port": default_port_mongodb,
        "services.mongodb.container_name": f"das-cli-mongodb-{default_port_mongodb}",
        "services.mongodb.username": "admin",
        "services.mongodb.password": "admin",
        "services.mongodb.cluster": False,
        "services.mongodb.cluster_secret_key": get_rand_token(16),
        "services.mongodb.nodes": [],
        "services.morkdb.port": default_port_morkdb,
        "services.morkdb.container_name": f"das-cli-morkdb-{default_port_morkdb}",
        "services.loader.container_name": "das-cli-loader",
        "services.das_peer.port": database_adapter_server_port,
        "services.das_peer.container_name": f"das-cli-das-peer-{database_adapter_server_port}",
        "services.dbms_peer.container_name": "das-cli-dbms-peer",
        "services.jupyter_notebook.port": default_port_jupyter,
        "services.jupyter_notebook.container_name": f"das-cli-jupyter-notebook-{default_port_jupyter}",
        "services.attention_broker.port": default_port_attention_broker,
        "services.attention_broker.container_name": f"das-cli-attention-broker-{default_port_attention_broker}",
        "services.query_agent.port": default_port_query_agent,
        "services.query_agent.container_name": f"das-cli-query-agent-{default_port_query_agent}",
        "services.link_creation_agent.port": default_port_link_agent,
        "services.link_creation_agent.container_name": f"das-cli-link-creation-agent-{default_port_link_agent}",
        "services.inference_agent.port": default_port_inference_agent,
        "services.inference_agent.container_name": f"das-cli-inference-agent-{default_port_inference_agent}",
        "services.evolution_agent.port": default_port_evolution_agent,
        "services.evolution_agent.container_name": f"das-cli-evolution-agent-{default_port_evolution_agent}",
        "services.context_broker.port": default_port_context_broker,
        "services.context_broker.container_name": f"das-cli-context-broker-{default_port_context_broker}",
    }

    schema_hash_value = calculate_schema_hash(core_defaults)
    core_defaults["schema_hash"] = schema_hash_value

    return core_defaults
