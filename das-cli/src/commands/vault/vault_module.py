import os

from common import Module, Settings
from common.config.store import JsonConfigStore
from common.container_manager.vault_container_manager import VaultContainerManager
from common.factory.vault_manager_factory import VaultManagerFactory
from settings.config import SECRETS_PATH

from .vault_cli import VaultCli


class VaultModule(Module):
    _instance = VaultCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependency_list = [
            (VaultContainerManager, VaultManagerFactory().build()),
            (
                Settings,
                self._settings,
            ),
        ]
