from typing import Dict, List
from common.utils import get_server_username, get_rand_token, calculate_schema_hash
from common.docker.remote_context_manager import Server
from common.settings import Settings


class DefaultConfigProvider:
    def _default_redis_nodes(self, _: Settings) -> List[Dict]:
        return self._build_localhost_node()

    def _default_mongodb_nodes(self, _: Settings) -> List[Dict]:
        return self._build_localhost_node()

    def _build_localhost_node(self, ip: str = "localhost") -> List[Dict]:
        server_user = get_server_username()

        node = Server(
            {
                "ip": ip,
                "username": server_user,
            }
        )

        return [
            {
                "context": "default",
                **node,
            }
        ]

    def get_all_default_mappings(self) -> Dict:
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

        core_defaults = {
            "schema_hash": None,
            "services.database.atomdb_backend": "redis_mongodb",
            "services.redis.port": lambda settings: settings.get(
                "services.redis.port",
                default_port_redis,
            ),
            "services.redis.container_name": lambda settings: f"das-cli-redis-{settings.get('services.redis.port', default_port_redis)}",
            "services.redis.cluster": False,
            "services.redis.nodes": self._default_redis_nodes,
            "services.mongodb.port": lambda settings: settings.get(
                "services.mongodb.port",
                default_port_mongodb,
            ),
            "services.mongodb.container_name": lambda settings: f"das-cli-mongodb-{settings.get('services.mongodb.port', default_port_mongodb)}",
            "services.mongodb.username": "admin",
            "services.mongodb.password": "admin",
            "services.mongodb.cluster": False,
            "services.mongodb.cluster_secret_key": get_rand_token(num_bytes=15),
            "services.mongodb.nodes": self._default_mongodb_nodes,
            "services.morkdb.port": lambda settings: settings.get(
                "services.morkdb.port", default_port_morkdb
            ),
            "services.morkdb.container_name": lambda settings: f"das-cli-morkdb-{settings.get('services.morkdb.port', default_port_morkdb)}",
            "services.loader.container_name": "das-cli-loader",
            "services.das_peer.port": lambda settings: settings.get(
                "services.das_peer.port",
                database_adapter_server_port,
            ),
            "services.das_peer.container_name": lambda settings: f"das-cli-das-peer-{settings.get('services.das_peer.port', database_adapter_server_port)}",
            "services.dbms_peer.container_name": "das-cli-dbms-peer",
            "services.jupyter_notebook.port": lambda settings: settings.get(
                "services.jupyter_notebook.port",
                default_port_jupyter,
            ),
            "services.jupyter_notebook.container_name": lambda settings: f"das-cli-jupyter-notebook-{settings.get('services.jupyter_notebook.port', default_port_jupyter)}",
            "services.attention_broker.port": lambda settings: settings.get(
                "services.attention_broker.port",
                default_port_attention_broker,
            ),
            "services.attention_broker.container_name": lambda settings: f"das-cli-attention-broker-{settings.get('services.attention_broker.port', default_port_attention_broker)}",
            "services.query_agent.port": lambda settings: settings.get(
                "services.query_agent.port",
                default_port_query_agent,
            ),
            "services.query_agent.container_name": lambda settings: f"das-cli-query-agent-{settings.get('services.query_agent.port', default_port_query_agent)}",
            "services.link_creation_agent.port": lambda settings: settings.get(
                "services.link_creation_agent.port",
                default_port_link_agent,
            ),
            "services.link_creation_agent.container_name": lambda settings: f"das-cli-link-creation-agent-{settings.get('services.link_creation_agent.port', default_port_link_agent)}",
            "services.inference_agent.port": lambda settings: settings.get(
                "services.inference_agent.port",
                default_port_inference_agent,
            ),
            "services.inference_agent.container_name": lambda settings: f"das-cli-inference-agent-{settings.get('services.inference_agent.port', default_port_inference_agent)}",
            "services.evolution_agent.port": lambda settings: settings.get(
                "services.evolution_agent.port",
                default_port_evolution_agent,
            ),
            "services.evolution_agent.container_name": lambda settings: f"das-cli-evolution-agent-{settings.get('services.evolution_agent.port', default_port_evolution_agent)}",
            "services.context_broker.port": lambda settings: settings.get(
                "services.context_broker.port",
                default_port_context_broker,
            ),
            "services.context_broker.container_name": lambda settings: f"das-cli-context-broker-{settings.get('services.context_broker.port', default_port_context_broker)}",
        }

        schema_hash_value = calculate_schema_hash(core_defaults)
        core_defaults["schema_hash"] = schema_hash_value

        return core_defaults
