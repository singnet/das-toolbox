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

    def _evolution_agent_container_manager_factory(self) -> EvolutionAgentContainerManager:
        evolution_agent_port = str(self._settings.get("services.evolution_agent.port"))

        container_name = self._settings.get("services.evolution_agent.container_name")

        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")

        morkdb_port = self._settings.get("services.morkdb.port")

        atomdb_backend = self._settings.get("services.database.atomdb_backend")

        attention_broker_port = self._settings.get("services.attention_broker.port")

        query_agent_port = str(self._settings.get("services.query_agent.port"))

        return EvolutionAgentContainerManager(
            container_name,
            options={
                "evolution_agent_port": evolution_agent_port,
                "evolution_agent_hostname": "0.0.0.0",
                "redis_port": redis_port,
                "redis_hostname": "0.0.0.0",
                "mongodb_port": mongodb_port,
                "mongodb_hostname": "0.0.0.0",
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "attention_broker_hostname": "0.0.0.0",
                "attention_broker_port": attention_broker_port,
                "query_agent_port": query_agent_port,
                "query_agent_hostname": "0.0.0.0",
                "atomdb_backend": atomdb_backend,
                "morkdb_port": morkdb_port,
                "morkdb_hostname": "0.0.0.0",
            },
        )
