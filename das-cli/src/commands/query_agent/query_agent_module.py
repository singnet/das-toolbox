import os
from typing import List

from commands.attention_broker.attention_broker_container_manager import AttentionBrokerManager
from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from commands.db.morkdb_container_manager import MorkdbContainerManager
from commands.db.atomdb_backend import AtomdbBackend
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .query_agent_cli import QueryAgentCli, QueryAgentContainerManager, Settings

from commands.db.atomdb_backend import (
    AtomdbBackend,
    BackendProvider,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
)

class QueryAgentModule(Module):
    _instance = QueryAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

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
                AtomdbBackend,
                self._atomdb_backend_factory,
            ),
            (
                AttentionBrokerManager,
                self._attention_broker_container_manager_factory,
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

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        container_name = self._settings.get("services.redis.container_name")
        redis_port = self._settings.get("services.redis.port")

        return RedisContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
            },
        )

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        container_name = self._settings.get("services.mongodb.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )

    def _attention_broker_container_manager_factory(self) -> AttentionBrokerManager:
        attention_broker_port = str(self._settings.get("services.attention_broker.port"))

        container_name = self._settings.get("services.attention_broker.container_name")

        return AttentionBrokerManager(
            container_name,
            options={
                "attention_broker_port": attention_broker_port,
            },
        )


    def _atomdb_backend_factory(self) -> AtomdbBackend:
        backend_name = self._settings.get("services.database.atomdb_backend")
        providers: List[BackendProvider] = []

        if backend_name == "redis_mongodb":
            providers.append(
                MongoDBRedisBackend(
                    self._mongodb_container_manager_factory(),
                    self._redis_container_manager_factory(),
                ),
            )
        elif backend_name == "mork_mongodb":
            providers.append(
                MorkMongoDBBackend(
                    self._morkdb_container_manager_factory(),
                    self._mongodb_container_manager_factory(),
                )
            )

        return AtomdbBackend(providers)


    def _morkdb_container_manager_factory(self) -> MorkdbContainerManager:
        container_name = self._settings.get("services.morkdb.container_name")
        morkdb_port = self._settings.get("services.morkdb.port")

        return MorkdbContainerManager(
            container_name,
            options={
                "morkdb_port": morkdb_port,
            },
        )
