from common import Module

from .query_agent_cli import QueryAgentCli, QueryAgentContainerManager, Settings
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager


class QueryAgentModule(Module):
    _instance = QueryAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

        self._dependecy_injection = [
            (
                QueryAgentContainerManager,
                self._query_agent_container_manager_factory,
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
                self._attention_broker_container_manager_factory,
            ),
        ]

    def _query_agent_container_manager_factory(self) -> QueryAgentContainerManager:
        query_agent_port = str(self._settings.get("query_agent.port"))
        mongodb_hostname = "localhost"
        mongodb_port = self._settings.get("mongodb.port")
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")

        redis_port = self._settings.get("redis.port")
        redis_hostname = "localhost"

        attention_broker_hostname = "localhost"
        attention_broker_port = self._settings.get("attention_broker.port")

        container_name = self._settings.get("query_agent.container_name")

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
                "attention_broker_hostname": attention_broker_hostname,
                "attention_broker_port": attention_broker_port,
            },
        )

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        container_name = self._settings.get("redis.container_name")
        redis_port = self._settings.get("redis.port")

        return RedisContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
            },
        )

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        container_name = self._settings.get("mongodb.container_name")
        mongodb_port = self._settings.get("mongodb.port")
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")

        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )

    def _attention_broker_container_manager_factory(self) -> AttentionBrokerManager:
        attention_broker_port = str(self._settings.get("attention_broker.port"))

        container_name = self._settings.get("attention_broker.container_name")

        return AttentionBrokerManager(
            container_name,
            options={
                "attention_broker_port": attention_broker_port,
            },
        )
