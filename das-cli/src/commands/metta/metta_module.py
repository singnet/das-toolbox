from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from common import Module

from .metta_cli import MettaCli, MettaLoaderContainerManager, Settings


class MettaModule(Module):
    _instance = MettaCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

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
                MettaLoaderContainerManager,
                self._metta_loader_container_manager_factory,
            ),
        ]

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

    def _metta_loader_container_manager_factory(self) -> MettaLoaderContainerManager:
        container_name = self._settings.get("loader.container_name")
        mongodb_port = self._settings.get("mongodb.port")
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")
        redis_port = self._settings.get("redis.port")

        return MettaLoaderContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
                "redis_hostname": "localhost",
                "mongodb_hostname": "localhost",
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )
