import os

from commands.db.mongodb_container_manager import MongodbContainerManager
from commands.db.redis_container_manager import RedisContainerManager
from commands.db.mork_container_manager import MorkContainerManager

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .metta_cli import MettaCli, MettaLoaderContainerManager, Settings, MorkLoaderContainerManager



class MettaModule(Module):
    _instance = MettaCli

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
                MorkContainerManager,
                self._mork_container_manager_factory,
            ),
            (
                MettaLoaderContainerManager,
                self._metta_loader_container_manager_factory,
            ),
            (
                MorkLoaderContainerManager,
                self._mork_loader_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

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

    def _mork_container_manager_factory(self) -> MorkContainerManager:
        container_name = self._settings.get("services.mork.container_name", "das-cli-mork-8000")
        mork_hostname = self._settings.get("services.mork.hostname", "0.0.0.0")
        mork_port = self._settings.get("services.mork.port", 8000)

        return MorkContainerManager(
            container_name,
            options={
                "mork_hostname": mork_hostname,
                "mork_port": mork_port,
            },
        )

    def _metta_loader_container_manager_factory(self) -> MettaLoaderContainerManager:
        container_name = self._settings.get("services.loader.container_name")
        mongodb_hostname = self._settings.get("services.mongodb.hostname")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")
        redis_hostname = self._settings.get("services.redis.hostname")
        redis_port = self._settings.get("services.redis.port")

        return MettaLoaderContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )

    def _mork_loader_container_manager_factory(self) -> MorkLoaderContainerManager:
        container_name = self._settings.get("services.mork_loader.container_name", "das-cli-mork-loader-9000")
        hostname = self._settings.get("services.mork_loader.hostname", "0.0.0.0")
        port = self._settings.get("services.mork_loader.port", 9000)

        return MorkLoaderContainerManager(
            container_name,
            options={
                "mork_loader_hostname": hostname,
                "mork_loader_port": port,
            },
        )
