import os

from common import Module, Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .config_cli import ConfigCli, RemoteContextManager
from .config_provider import InteractiveConfigProvider, NonInteractiveConfigProvider


class ConfigModule(Module):
    _instance = ConfigCli

    def __init__(self):
        super().__init__()

        self._settings = self._settings_factory()
        self._remote_context_manager = RemoteContextManager()

        self._dependecy_injection = [
            (Settings, lambda: self._settings),
            (NonInteractiveConfigProvider, self._non_interactive_config_provider_factory),
            (InteractiveConfigProvider, self._interactive_config_provider_factory),
            (RemoteContextManager, self._remote_context_manager),
        ]

    def _settings_factory(self) -> Settings:
        return Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def _non_interactive_config_provider_factory(self) -> NonInteractiveConfigProvider:
        return NonInteractiveConfigProvider(self._settings)

    def _interactive_config_provider_factory(self) -> InteractiveConfigProvider:
        return InteractiveConfigProvider(self._settings, self._remote_context_manager)
