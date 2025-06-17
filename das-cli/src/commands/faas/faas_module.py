import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .faas_cli import FaaSCli, Settings


class FaaSModule(Module):
    _instance = FaaSCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                Settings,
                self._settings,
            )
        ]
