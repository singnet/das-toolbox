import os
from typing import List

from commands.db.atomdb_backend import (
    AtomdbBackend,
    BackendProvider,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
)
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .db_cli import (
    DbCli,
    MongodbContainerManager,
    MorkdbContainerManager,
    RedisContainerManager,
    Settings,
)


class DbModule(Module):
    _instance = DbCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
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
                Settings,
                self._settings,
            ),
            (
                MorkdbContainerManager,
                self._morkdb_container_manager_factory,
            ),
        ]

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

    def _morkdb_container_manager_factory(self) -> MorkdbContainerManager:
        container_name = self._settings.get("services.morkdb.container_name")
        morkdb_port = self._settings.get("services.morkdb.port")

        return MorkdbContainerManager(
            container_name,
            options={
                "morkdb_port": morkdb_port,
            },
        )
