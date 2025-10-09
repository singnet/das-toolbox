import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .db_cli import DbCli, MongodbContainerManager, RedisContainerManager, Settings, MorkContainerManager


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
                MorkContainerManager,
                self._mork_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        redis_hostname = self._settings.get("services.redis.hostname")
        container_name = self._settings.get("services.redis.container_name")
        redis_port = self._settings.get("services.redis.port")

        return RedisContainerManager(
            container_name,
            options={
                "redis_hostname": redis_hostname,
                "redis_port": redis_port,
            },
        )

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        mongodb_hostname = self._settings.get("services.mongodb.hostname")
        container_name = self._settings.get("services.mongodb.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_hostname": mongodb_hostname,
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
