import os
from typing import List

from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .metta_cli import MettaCli, MettaLoaderContainerManager, Settings

from commands.db.atomdb_backend import (
    AtomdbBackend,
    BackendProvider,
    MongoDBRedisBackend,
    MorkMongoDBBackend,
)


class MettaModule(Module):
    _instance = MettaCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(
            store=JsonConfigStore(os.path.expanduser(SECRETS_PATH))
        )
        self._mongodb_manager = self._mongodb_container_manager_factory()
        self._redis_manager = self._redis_container_manager_factory()

        self._dependecy_injection = [
            (
                AtomdbBackend,
                self._atomdb_backend_factory,
            ),
            (
                MettaLoaderContainerManager,
                self._metta_loader_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _atomdb_backend_factory(self) -> AtomdbBackend:
        backend_name = self._settings.get("services.database.atomdb_backend")
        providers: List[BackendProvider] = []

        if backend_name == "redis_mongodb":
            providers.append(
                MongoDBRedisBackend(
                    self._mongodb_manager,
                    self._redis_manager,
                ),
            )
        elif backend_name == "mork_mongodb":
            providers.append(MorkMongoDBBackend(self._mongodb_manager))

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

    def _metta_loader_container_manager_factory(self) -> MettaLoaderContainerManager:
        container_name = self._settings.get("services.loader.container_name")
        mongodb_hostname = self._settings.get("services.mongodb.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")
        redis_hostname = self._settings.get("services.redis.container_name")
        redis_port = self._settings.get("services.redis.port")
        atomdb_backend = self._settings.get("services.database.atomdb_backend")

        return MettaLoaderContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "atomdb_backend": atomdb_backend,
            },
        )
