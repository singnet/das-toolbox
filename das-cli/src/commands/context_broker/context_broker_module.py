import os

from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .context_broker_cli import ContextBrokerCli, ContextBrokerContainerManager, Settings


class ContextBrokerModule(Module):
    _instance = ContextBrokerCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

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
                Settings,
                self._settings,
            ),
        ]

    def _query_agent_container_manager_factory(self) -> QueryAgentContainerManager:
        query_agent_hostname = self._settings.get("services.query_agent.hostname")
        query_agent_port = str(self._settings.get("services.query_agent.port"))

        mongodb_hostname = self._settings.get("services.mongodb.hostname")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = self._settings.get("services.redis.hostname")

        attention_broker_hostname = self._settings.get("services.attention_broker.hostname")
        attention_broker_port = self._settings.get("services.attention_broker.port")

        container_name = self._settings.get("services.query_agent.container_name")

        return QueryAgentContainerManager(
            container_name,
            options={
                "query_agent_port": query_agent_port,
                "query_agent_hostname": query_agent_hostname,
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "attention_broker_hostname": attention_broker_hostname,
                "attention_broker_port": attention_broker_port,
            },
        )

    def _context_broker_container_manager_factory(self) -> ContextBrokerContainerManager:
        context_broker_hostname = self._settings.get("services.context_broker.hostname")
        context_broker_port = self._settings.get("services.context_broker.port")

        attention_broker_hostname = self._settings.get("services.attention_broker.hostname")
        attention_broker_port = self._settings.get("services.attention_broker.port")

        mongodb_hostname = self._settings.get("services.mongodb.hostname")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = self._settings.get("services.redis.hostname")

        container_name = self._settings.get("services.context_broker.container_name")

        return ContextBrokerContainerManager(
            container_name,
            options={
                "context_broker_hostname": context_broker_hostname,
                "context_broker_port": context_broker_port,
                "attention_broker_hostname": attention_broker_hostname,
                "attention_broker_port": attention_broker_port,
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )
