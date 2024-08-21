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
        container_name = self._settings.get("redis.container_name")
        return RedisContainerManager(container_name)

    def _mongodb_container_manager_factory(self) -> MongodbContainerManager:
        container_name = self._settings.get("mongodb.container_name")
        return MongodbContainerManager(container_name)
