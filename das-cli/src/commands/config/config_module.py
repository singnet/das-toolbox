import os

from common import Module, Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .config_cli import ConfigCli


class ConfigModule(Module):
    _instance = ConfigCli

    def __init__(self):
        super().__init__()
        self._dependecy_injection = [
            (Settings, self._settings_factory),
        ]

    def _settings_factory(self) -> Settings:
        return Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
