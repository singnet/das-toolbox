import os

from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from common.bus_node.busnode_container_manager import BusNodeContainerManager
from common.bus_node.busnode_manager_factory import BusNodeContainerManagerFactory

from .context_broker_cli import ContextBrokerCli, Settings
from .context_broker_container_manager import ContextBrokerContainerManager


class ContextBrokerModule(Module):
    _instance = ContextBrokerCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependecy_injection = [
            (
                QueryAgentContainerManager,
                self._query_agent_container_manager_factory,
            ),
            (
                ContextBrokerContainerManager,
                self._context_broker_container_manager_factory,
            ),
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(use_settings="context_broker", service_name="context-broker")
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _query_agent_container_manager_factory(self) -> QueryAgentContainerManager:
        query_agent_port = str(self._settings.get("services.query_agent.port"))
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")

        attention_broker_port = self._settings.get("services.attention_broker.port")

        container_name = self._settings.get("services.query_agent.container_name")

        return QueryAgentContainerManager(
            container_name,
            options={
                "query_agent_port": query_agent_port,
                "query_agent_hostname": "0.0.0.0",
                "redis_port": redis_port,
                "redis_hostname": "0.0.0.0",
                "mongodb_port": mongodb_port,
                "mongodb_hostname": "0.0.0.0",
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "attention_broker_hostname": "0.0.0.0",
                "attention_broker_port": attention_broker_port,
            },
        )

    def _context_broker_container_manager_factory(self) -> ContextBrokerContainerManager:
        context_broker_port = self._settings.get("services.context_broker.port")

        attention_broker_port = self._settings.get("services.attention_broker.port")

        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        mork_port = self._settings.get("services.morkdb.port")

        atomdb_backend = self._settings.get("services.database.atomdb_backend")

        container_name = self._settings.get("services.context_broker.container_name")

        return ContextBrokerContainerManager(
            container_name,
            options={
                "context_broker_hostname": "0.0.0.0",
                "context_broker_port": context_broker_port,
                "context_broker_hostname": "0.0.0.0",
                "attention_broker_hostname": "0.0.0.0",
                "attention_broker_port": attention_broker_port,
                "redis_port": redis_port,
                "redis_hostname": "0.0.0.0",
                "mongodb_port": mongodb_port,
                "mongodb_hostname": "0.0.0.0",
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "atomdb_backend": atomdb_backend,
                "morkdb_port": mork_port,
                "morkdb_hostname": "0.0.0.0",
            },
        )

