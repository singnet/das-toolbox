from common import Module

from .db_adapter_cli import DbAdapterCli, DatabaseAdapterServerContainerManager, Settings


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

        return DatabaseAdapterServerContainerManager(container_name)
