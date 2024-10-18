from common import Module

from .db_adapter_cli import (
    DbAdapterCli,
    DatabaseAdapterServerContainerManager,
    Settings,
)


class DbAdapterModule(Module):
    _instance = DbAdapterCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

        self._dependecy_injection = [
            (
                DatabaseAdapterServerContainerManager,
                self._database_adapter_server_container_manager_factory,
            )
        ]

    def _database_adapter_server_container_manager_factory(
        self,
    ) -> DatabaseAdapterServerContainerManager:
        container_name = self._settings.get("database_adapter.container_name")
        mongodb_hostname = self._settings.get("mongodb.nodes")[0]
        mongodb_port = self._settings.get("mongodb.port")
        redis_hostname = self._settings.get("redis.nodes")[0]
        redis_port = self._settings.get("redis.port")

        return DatabaseAdapterServerContainerManager(
            container_name,
            options={
                "mongodb_hostname": mongodb_hostname,
                "mongodb_port": mongodb_port,
                "redis_hostname": redis_hostname,
                "redis_port": redis_port,
            },
        )
