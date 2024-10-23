from common import Module

from .db_adapter_cli import (
    DbAdapterCli,
    DatabaseAdapterServerContainerManager,
    DatabaseAdapterClientContainerManager,
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
            ),
            (
                DatabaseAdapterClientContainerManager,
                self._database_adapter_client_container_manager_factory,
            ),
        ]

    def _database_adapter_server_container_manager_factory(
        self,
    ) -> DatabaseAdapterServerContainerManager:
        container_name = self._settings.get("database_adapter.server_container_name")
        mongodb_nodes = self._settings.get("mongodb.nodes")
        mongodb_hostname = mongodb_nodes[0]["ip"] if mongodb_nodes else "localhost"
        mongodb_username = self._settings.get("mongodb.username")
        mongodb_password = self._settings.get("mongodb.password")
        mongodb_port = self._settings.get("mongodb.port")
        redis_nodes = self._settings.get("redis.nodes")
        redis_hostname = redis_nodes[0]["ip"] if redis_nodes else "localhost"
        redis_port = self._settings.get("redis.port")

        adapter_server_port = self._settings.get("database_adapter.server_port")

        return DatabaseAdapterServerContainerManager(
            container_name,
            options={
                "adapter_server_port": adapter_server_port,
                "mongodb_hostname": mongodb_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "redis_hostname": redis_hostname,
                "redis_port": redis_port,
            },
        )

    def _database_adapter_client_container_manager_factory(
        self,
    ) -> DatabaseAdapterClientContainerManager:
        container_name = self._settings.get("database_adapter.container_name")
        adapter_client_port = self._settings.get("database_adapter.client_port")

        return DatabaseAdapterClientContainerManager(
            container_name,
            options={
                "adapter_client_port": adapter_client_port,
            },
        )
