import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager

from .context_agent_cli import ContextAgentCli, ContextAgentContainerManager, Settings


class ContextAgentModule(Module):
    _instance = ContextAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                QueryAgentContainerManager,
                self._query_agent_container_manager_factory,
            ),
            (
                ContextAgentContainerManager,
                self._context_agent_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _query_agent_container_manager_factory(self) -> QueryAgentContainerManager:
        query_agent_port = str(self._settings.get("services.query_agent.port"))
        mongodb_hostname = self._settings.get("services.mongodb.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = self._settings.get("services.redis.container_name")

        attention_broker_hostname = self._settings.get("services.attention_broker.container_name")
        attention_broker_port = self._settings.get("services.attention_broker.port")

        container_name = self._settings.get("services.query_agent.container_name")

        return QueryAgentContainerManager(
            container_name,
            options={
                "query_agent_port": query_agent_port,
                "query_agent_hostname": container_name,
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


    def _context_agent_container_manager_factory(self) -> ContextAgentContainerManager:
        context_agent_port = self._settings.get("services.context_agent.port")

        attention_broker_hostname = self._settings.get("services.attention_broker.container_name")
        attention_broker_port = self._settings.get("services.attention_broker.port")

        mongodb_hostname = self._settings.get("services.mongodb.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = self._settings.get("services.redis.container_name")

        container_name = self._settings.get("services.context_agent.container_name")

        return ContextAgentContainerManager(
            container_name,
            options={
                "context_agent_port": context_agent_port,
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
