import os

from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .evolution_agent_cli import EvolutionAgentCli, EvolutionAgentContainerManager, Settings


class EvolutionAgentModule(Module):
    _instance = EvolutionAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                QueryAgentContainerManager,
                self._query_agent_container_manager_factory,
            ),
            (
                EvolutionAgentContainerManager,
                self._evolution_agent_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _query_agent_container_manager_factory(self) -> QueryAgentContainerManager:
        query_agent_port = str(self._settings.get("services.query_agent.port"))
        mongodb_hostname = "localhost"
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = "localhost"

        attention_agent_hostname = "localhost"
        attention_agent_port = self._settings.get("services.attention_agent.port")

        container_name = self._settings.get("services.query_agent.container_name")

        return QueryAgentContainerManager(
            container_name,
            options={
                "query_agent_port": query_agent_port,
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "attention_agent_hostname": attention_agent_hostname,
                "attention_agent_port": attention_agent_port,
            },
        )

    def _evolution_agent_container_manager_factory(self) -> EvolutionAgentContainerManager:
        evolution_agent_port = str(self._settings.get("services.evolution_agent.port"))

        container_name = self._settings.get("services.evolution_agent.container_name")

        mongodb_hostname = "localhost"
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = "localhost"

        attention_agent_hostname = "localhost"
        attention_agent_port = self._settings.get("services.attention_agent.port")

        return EvolutionAgentContainerManager(
            container_name,
            options={
                "evolution_agent_port": evolution_agent_port,
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "attention_agent_hostname": attention_agent_hostname,
                "attention_agent_port": attention_agent_port,
            },
        )
