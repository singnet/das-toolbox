import os
from common import Module

from .logs_cli import LogsCli, Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH


class LogsModule(Module):
    _instance = LogsCli


    def __init__(self):
        super().__init__()
        self._dependecy_injection = [
            (Settings, self._settings_factory),
        ]

    def _settings_factory(self) -> Settings:
        return Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
