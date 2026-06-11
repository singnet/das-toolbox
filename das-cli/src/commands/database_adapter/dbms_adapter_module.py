import os

from common import Module, Settings
from common.config.store import JsonConfigStore
from common.container_manager.dbms.database_adapter_container_manager import (
    DatabaseAdapterContainerManager,
)
from common.factory.atomdb.atomdb_backend import AtomdbBackend
from common.factory.atomdb.atomdb_factory import AtomDbContainerManagerFactory
from common.factory.database_adapter.database_adapter_factory import DatabaseAdapterFactory
from settings.config import SECRETS_PATH

from .dbms_adapter_cli import DatabaseAdapterCli


class DatabaseAdapterModule(Module):
    _instance = DatabaseAdapterCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._database_adapter_factory = DatabaseAdapterFactory()

        self._dependency_list = [
            (
                AtomdbBackend,
                AtomDbContainerManagerFactory().build(),
            ),
            (DatabaseAdapterContainerManager, self._database_adapter_factory.build()),
            (
                Settings,
                self._settings,
            ),
        ]
