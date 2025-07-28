import os

from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from commands.evolution_agent.evolution_agent_container_manager import (
    EvolutionAgentContainerManager,
)
from commands.inference_agent.inference_agent_container_manager import (
    InferenceAgentContainerManager,
)
from commands.link_creation_agent.link_creation_agent_container_manager import (
    LinkCreationAgentContainerManager,
)
from commands.query_agent.query_agent_container_manager import QueryAgentContainerManager
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .logs_cli import LogsCli, Settings


class LogsModule(Module):
    _instance = LogsCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(
            store=JsonConfigStore(
                os.path.expanduser(SECRETS_PATH),
            )
        )

        self._dependecy_injection = [
            (
                Settings,
                self._settings,
            ),
            (
                RedisContainerManager,
                self._redis_container_manager_factory,
            ),
            (
                MongodbContainerManager,
                self._mongodb_container_manager_factory,
            ),
            (
                AttentionBrokerManager,
                self._attention_broker_manager_factory,
            ),
            (
                QueryAgentContainerManager,
                self._query_agent_container_manager_factory,
            ),
            (
                LinkCreationAgentContainerManager,
                self._link_creation_agent_container_manager_factory,
            ),
            (
                InferenceAgentContainerManager,
                self._inference_agent_container_manager_factory,
            ),
            (
                EvolutionAgentContainerManager,
                self._evolution_agent_container_manager_factory,
            ),
        ]

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        mongodb_container_name = self._settings.get("services.mongodb.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")

        return MongodbContainerManager(
            mongodb_container_name,
            options={
                "mongodb_port": mongodb_port,
            },
        )

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        redis_container_name = self._settings.get("services.redis.container_name")
        redis_port = self._settings.get("services.redis.port")

        return RedisContainerManager(
            redis_container_name,
            options={
                "redis_port": redis_port,
            },
        )

    def _inference_agent_container_manager_factory(
        self,
    ) -> InferenceAgentContainerManager:
        inference_agent_container_name = self._settings.get(
            "services.inference_agent.container_name"
        )
        inference_agent_port = self._settings.get("services.inference_agent.port")

        return InferenceAgentContainerManager(
            inference_agent_container_name,
            options={
                "inference_agent_port": inference_agent_port,
            },
        )

    def _link_creation_agent_container_manager_factory(
        self,
    ) -> LinkCreationAgentContainerManager:
        link_creation_agent_container_name = self._settings.get(
            "services.link_creation_agent.container_name"
        )
        link_creation_agent_port = self._settings.get("services.link_creation_agent.port")

        return LinkCreationAgentContainerManager(
            link_creation_agent_container_name,
            options={
                "link_creation_agent_server_port": link_creation_agent_port,
            },
        )

    def _query_agent_container_manager_factory(self) -> QueryAgentContainerManager:
        query_agent_container_name = self._settings.get("services.query_agent.container_name")
        query_agent_port = self._settings.get("services.query_agent.port")

        return QueryAgentContainerManager(
            query_agent_container_name,
            options={
                "query_agent_port": query_agent_port,
            },
        )

    def _attention_broker_manager_factory(self) -> AttentionBrokerManager:
        attention_broker_container = self._settings.get("services.attention_broker.container_name")
        attention_broker_port = self._settings.get("services.attention_broker.port")

        return AttentionBrokerManager(
            attention_broker_container,
            options={
                "attention_broker_port": attention_broker_port,
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

        attention_broker_hostname = "localhost"
        attention_broker_port = self._settings.get("services.attention_broker.port")

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
                "attention_broker_hostname": attention_broker_hostname,
                "attention_broker_port": attention_broker_port,
            },
        )
