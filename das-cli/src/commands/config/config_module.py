import os

from common import Module, Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .config_cli import ConfigCli
from .default_config_provider import DefaultConfigProvider


class ConfigModule(Module):
    _instance = ConfigCli

    def __init__(self):
        super().__init__()
        self._dependecy_injection = [
            (Settings, self._settings_factory),
            (DefaultConfigProvider, self._default_config_provider_factory),
        ]

    def _settings_factory(self) -> Settings:
        return Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def _default_config_provider_factory(self) -> DefaultConfigProvider:
        return DefaultConfigProvider(self._settings_factory())
