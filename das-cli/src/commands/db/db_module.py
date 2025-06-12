from common import Module

from .db_cli import DbCli, MongodbContainerManager, RedisContainerManager, Settings


class DbModule(Module):
    _instance = DbCli

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
        ]

    def _redis_container_manager_factory(self) -> RedisContainerManager:
        container_name = self._settings.get("service.redis.container_name")
        redis_port = self._settings.get("service.redis.port")

        return RedisContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
            },
        )

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        container_name = self._settings.get("service.mongodb.container_name")
        mongodb_port = self._settings.get("service.mongodb.port")
        mongodb_username = self._settings.get("service.mongodb.username")
        mongodb_password = self._settings.get("service.mongodb.password")

        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )
