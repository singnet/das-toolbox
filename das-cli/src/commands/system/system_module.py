import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .system_cli import SystemCli, SystemContainersManager
from .system_containers_manager import Settings


class SystemModule(Module):
    _instance = SystemCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(
            store=JsonConfigStore(os.path.expanduser(SECRETS_PATH))
        )

        self._dependecy_injection = [
            (
                SystemContainersManager,
                self._system_containers_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _system_containers_manager_factory(self) -> SystemContainersManager:
        return SystemContainersManager(
            settings=self._settings,
        )
