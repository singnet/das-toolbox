from abc import ABC, abstractmethod
from typing import Any, Dict, List

from common import IntRange
from common.command import Command
from common.prompt_types import ValidUsername
from common.config.core import (
    database_adapter_server_port,
    default_port_atomdb_broker,
    default_port_attention_broker,
    default_port_context_broker,
    default_port_evolution_agent,
    default_port_inference_agent,
    default_port_jupyter,
    default_port_link_agent,
    default_port_mongodb,
    default_port_morkdb,
    default_port_query_agent,
    default_port_redis,
    get_core_defaults_dict,
)
from common.docker.remote_context_manager import RemoteContextManager, Server
from common.network import get_public_ip
from common.prompt_types import ReachableIpAddress
from common.settings import Settings
from common.utils import get_rand_token, get_server_username


class ConfigProvider(ABC):
    def __init__(self, settings: Settings):
        super().__init__()

        self._settings = settings

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

    def _get_core_defaults(self) -> Dict[str, Any]:
        core_defaults = get_core_defaults_dict()

        core_defaults.update(
            {
                "services.redis.port": lambda settings: settings.get(
                    "services.redis.port",
                    default_port_redis,
                ),
                "services.redis.container_name": lambda settings: f"das-cli-redis-{settings.get('services.redis.port', default_port_redis)}",
                "services.redis.nodes": self._default_redis_nodes,
                "services.mongodb.port": lambda settings: settings.get(
                    "services.mongodb.port",
                    default_port_mongodb,
                ),
                "services.mongodb.container_name": lambda settings: f"das-cli-mongodb-{settings.get('services.mongodb.port', default_port_mongodb)}",
                "services.mongodb.nodes": self._default_mongodb_nodes,
                "services.morkdb.port": lambda settings: settings.get(
                    "services.morkdb.port",
                    default_port_morkdb,
                ),
                "services.morkdb.container_name": lambda settings: f"das-cli-morkdb-{settings.get('services.morkdb.port', default_port_morkdb)}",
                "services.das_peer.port": lambda settings: settings.get(
                    "services.das_peer.port",
                    database_adapter_server_port,
                ),
                "services.das_peer.container_name": lambda settings: f"das-cli-das-peer-{settings.get('services.das_peer.port', database_adapter_server_port)}",
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
                "services.atomdb_broker.port": lambda settings: settings.get(
                    "services.atomdb_broker.port", default_port_atomdb_broker
                ),
                "services.atomdb_broker.container_name": lambda settings: f"das-cli-atomdb-broker-{settings.get('services.atomdb_broker.port', default_port_atomdb_broker)}",
            }
        )

        return core_defaults

    @abstractmethod
    def get_all_configs(self) -> Dict[str, Any]:
        pass

    def raise_property_invalid(self, key: str) -> None:
        default_mappings = self._get_core_defaults()

        if key not in default_mappings.keys():
            raise AttributeError(f"'{key}' is not a valid configuration property.")

    def apply_default_values(self, default_mappings: Dict):
        for default_key, default_value_or_func in default_mappings.items():
            if callable(default_value_or_func):
                if "nodes" in default_key:
                    calculated_value = default_value_or_func(self._settings)
                    self._settings.set(default_key, calculated_value)
                continue
            else:
                self._settings.set(default_key, default_value_or_func)

    def recalculate_config_dynamic_values(
        self,
        default_mappings: Dict,
    ):
        for default_key, default_value_or_func in default_mappings.items():
            if callable(default_value_or_func):
                if "nodes" in default_key or default_key == "schema_hash":
                    continue

                calculated_value = default_value_or_func(self._settings)

                self._settings.set(default_key, calculated_value)


class InteractiveConfigProvider(ConfigProvider):
    def __init__(
        self,
        settings: Settings,
        remote_context_manager: RemoteContextManager,
    ):
        super().__init__(settings)

        self._settings = settings
        self._remote_context_manager = remote_context_manager

    def _build_localhost_node(
        self,
        ip: str = "localhost",
        use_default_as_context: bool = True,
    ) -> List[Dict]:
        server_user = get_server_username()

        node = Server(
            {
                "ip": ip,
                "username": server_user,
            }
        )

        if not use_default_as_context:
            return self._remote_context_manager.create_servers_context([node])

        return [
            {
                "context": "default",
                **node,
            }
        ]

    def _build_nodes(self, is_cluster: bool, port: int) -> List[Dict]:
        if not is_cluster:
            return self._build_localhost_node()

        nodes = []

        join_current_server = Command.confirm(
            "Do you want to join the current server as an actual node on the network?",
            default=True,
        )

        if join_current_server:
            server_public_ip = get_public_ip()

            if server_public_ip is None:
                raise Exception(
                    "The server's public ip could not be solved. Make sure it has internet access."
                )

            nodes += self._build_localhost_node(
                server_public_ip,
                use_default_as_context=True,
            )

        nodes += self._build_cluster(port, min_nodes=3 - len(nodes))

        return nodes

    def _build_cluster(
        self,
        port: int,
        min_nodes: int = 3,
    ) -> List[Dict]:
        current_nodes = self._settings.get("services.redis.nodes", [])
        current_total_nodes = len(current_nodes)
        total_nodes_default = current_total_nodes if current_total_nodes > 3 else 3

        total_nodes = Command.prompt(
            f"Enter the total number of nodes for the cluster (>= {min_nodes})",
            hide_input=False,
            type=IntRange(min_nodes),
            default=total_nodes_default,
        )

        servers: List[Server] = []
        for i in range(0, total_nodes):

            server_username_default = (
                current_nodes[i]["username"] if i < len(current_nodes) else None
            )

            server_username = Command.prompt(
                f"Enter the server username for the server-{i + 1}",
                hide_input=False,
                type=ValidUsername(),
                default=server_username_default,
            )

            server_ip_default = current_nodes[i]["ip"] if i < len(current_nodes) else None

            server_ip = Command.prompt(
                f"Enter the ip address for the server-{i + 1}",
                hide_input=False,
                type=ReachableIpAddress(server_username, port),
                default=server_ip_default,
            )

            servers.append(
                {
                    "ip": server_ip,
                    "username": server_username,
                }
            )

        return self._remote_context_manager.create_servers_context(servers)

    def _destroy_contexts(self, servers: List[Dict]):
        server_contexts = [server.get("context", "") for server in servers]
        self._remote_context_manager.remove_servers_context(server_contexts)

    def _redis_nodes(self, redis_cluster, redis_port) -> List[Dict]:
        redis_nodes = self._build_nodes(redis_cluster, redis_port)

        self._destroy_contexts(
            servers=self._settings.get("services.redis.nodes", []),
        )

        return redis_nodes

    def _redis(self) -> Dict:
        redis_port = Command.prompt(
            "Enter Redis port",
            default=self._settings.get("services.redis.port", 40020),
            type=int,
        )
        cluster_default_value = self._settings.get("services.redis.cluster", False)
        redis_cluster = Command.confirm(
            "Is it a Redis cluster?",
            default=cluster_default_value,
        )
        return {
            "services.redis.port": redis_port,
            "services.redis.cluster": redis_cluster,
            "services.redis.nodes": self._redis_nodes(
                redis_cluster,
                redis_port,
            ),
        }

    def _mongodb_nodes(self, mongodb_cluster, mongodb_port) -> List[Dict]:
        mongodb_nodes = self._build_nodes(mongodb_cluster, mongodb_port)

        self._destroy_contexts(
            servers=self._settings.get("services.mongodb.nodes", []),
        )

        return mongodb_nodes

    def _mongodb(self) -> dict:
        mongodb_port = Command.prompt(
            "Enter MongoDB port",
            default=self._settings.get("services.mongodb.port", 40021),
            type=int,
        )
        mongodb_username = Command.prompt(
            "Enter MongoDB username",
            default=self._settings.get("services.mongodb.username", "admin"),
        )
        mongodb_password = Command.prompt(
            "Enter MongoDB password",
            # hide_input=True, # When hide_input is set I cannot set the answers based on a text file making impossible to test this command
            default=self._settings.get("services.mongodb.password", "admin"),
        )
        cluster_default_value = self._settings.get("services.mongodb.cluster", False)
        is_mongodb_cluster = Command.confirm(
            "Is it a MongoDB cluster?",
            default=cluster_default_value,
        )
        cluster_secret_key = self._settings.get(
            "services.mongodb.cluster_secret_key",
            get_rand_token(num_bytes=15),
        )
        return {
            "services.mongodb.port": mongodb_port,
            "services.mongodb.username": mongodb_username,
            "services.mongodb.password": mongodb_password,
            "services.mongodb.cluster": is_mongodb_cluster,
            "services.mongodb.nodes": lambda _: self._mongodb_nodes(
                is_mongodb_cluster,
                mongodb_port,
            ),
            "services.mongodb.cluster_secret_key": cluster_secret_key,
        }

    def _das_peer(self) -> dict:
        database_adapter_server_port = 40018

        return {
            "services.das_peer.port": database_adapter_server_port,
        }

    def _jupyter_notebook(self) -> dict:
        jupyter_notebook_port = Command.prompt(
            "Enter Jupyter Notebook port",
            default=self._settings.get("services.jupyter.port", 40019),
        )

        return {
            "services.jupyter_notebook.port": jupyter_notebook_port,
        }

    def _attention_broker(self) -> dict:
        attention_broker_port = Command.prompt(
            "Enter the Attention Broker port",
            default=self._settings.get("services.attention_broker.port", 40001),
        )

        return {
            "services.attention_broker.port": attention_broker_port,
        }

    def _query_agent(self) -> dict:
        query_agent_port = Command.prompt(
            "Enter the Query Agent port",
            default=self._settings.get("services.query_agent.port", 40002),
        )

        return {
            "services.query_agent.port": query_agent_port,
        }

    def _link_creation_agent(self) -> dict:
        link_creation_agent_port = Command.prompt(
            "Enter the Link Creation Agent Server port",
            default=self._settings.get("services.link_creation_agent.port", 40003),
        )

        return {
            "services.link_creation_agent.port": link_creation_agent_port,
        }

    def _inference_agent(self) -> dict:
        inference_agent_port = Command.prompt(
            "Enter the Inference Agent port",
            default=self._settings.get("services.inference_agent.port", 40004),
        )

        return {
            "services.inference_agent.port": inference_agent_port,
        }

    def _evolution_agent(self) -> dict:
        evolution_agent_port = Command.prompt(
            "Enter the Evolution agent port",
            default=self._settings.get("services.evolution_agent.port", 40005),
        )

        return {
            "services.evolution_agent.port": evolution_agent_port,
        }

    def _context_broker(self) -> dict:
        context_broker_port = Command.prompt(
            "Enter the Context Broker port",
            default=self._settings.get("services.context_broker.port", 40006),
        )

        return {
            "services.context_broker.port": context_broker_port,
        }

    def _atomdb_backend(self) -> dict:
        backends = {
            "redis_mongodb": (
                self._mongodb,
                self._redis,
            ),
            "mork_mongodb": (
                self._mongodb,
                self._morkdb,
            ),
        }

        atomdb_backend = Command.select(
            text="Choose the AtomDB backend: ",
            options={
                "MongoDB + Redis": "redis_mongodb",
                "MongoDB + Mork": "mork_mongodb",
            },
            default=self._settings.get("services.database.atomdb_backend", "redis_mongodb"),
        )

        backend = backends.get(atomdb_backend) or backends["redis_mongodb"]
        backend_configs = [func() for func in backend]
        merged_config = {
            "services.database.atomdb_backend": atomdb_backend,
        }
        for config in backend_configs:
            merged_config.update(config)

        return merged_config

    def _get_jupyter_notebook(self) -> Dict[str, Any]:
        jupyter_notebook_port = Command.prompt(
            "Enter Jupyter Notebook port",
            default=self._settings.get("services.jupyter.port", 40019),
        )

        return {
            "services.jupyter_notebook.port": jupyter_notebook_port,
        }

    def _morkdb(self) -> Dict:
        morkdb_port = Command.prompt(
            "Enter the MorkDB port",
            default=self._settings.get("services.morkdb.port", 40022),
        )

        return {
            "services.morkdb.port": morkdb_port,
        }

    def _atomdb_broker(self) -> Dict:
        atomdb_broker_port = Command.prompt(
            "Enter the AtomDb Broker port",
            default=self._settings.get("services.atomdb_broker.port", 40007),
        )

        return {"services.atomdb_broker.port": atomdb_broker_port}

    def get_all_configs(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {}

        config_steps = [
            self._atomdb_backend,
            self._das_peer,
            self._jupyter_notebook,
            self._attention_broker,
            self._query_agent,
            self._link_creation_agent,
            self._inference_agent,
            self._evolution_agent,
            self._context_broker,
            self._atomdb_broker,
        ]

        for config_step in config_steps:
            config.update(config_step())

        final_config = {**self._get_core_defaults(), **config}

        return final_config


class NonInteractiveConfigProvider(ConfigProvider):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self._settings = settings

    def get_all_configs(self) -> Dict[str, Any]:
        default_mappings = self._get_core_defaults()

        return default_mappings
