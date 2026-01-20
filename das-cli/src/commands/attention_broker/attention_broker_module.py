import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .attention_broker_cli import AttentionBrokerCli, AttentionBrokerManager, Settings

from common.factory.attention_broker_manager_factory import AttentionBrokerManagerFactory


class AttentionBrokerModule(Module):
    _instance = AttentionBrokerCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependency_list = [
            (
                AttentionBrokerManager,
                AttentionBrokerManagerFactory().build()
            ),
            (
                Settings,
                self._settings,
            ),
        ]
