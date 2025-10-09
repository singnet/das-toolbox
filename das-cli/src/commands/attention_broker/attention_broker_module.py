import os

from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .attention_broker_cli import AttentionBrokerCli, AttentionBrokerManager, Settings


class AttentionBrokerModule(Module):
    _instance = AttentionBrokerCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                AttentionBrokerManager,
                self._attention_broker_container_manager_factory,
            ),
            (
                Settings,
                self._settings,
            ),
        ]

    def _attention_broker_container_manager_factory(self) -> AttentionBrokerManager:
        attention_broker_port = str(self._settings.get("services.attention_broker.port"))

        attention_broker_hostname = self._settings.get("services.attention_broker.hostname")
        container_name = self._settings.get("services.attention_broker.container_name")

        return AttentionBrokerManager(
            container_name,
            options={
                "attention_broker_port": attention_broker_port,
                "attention_broker_hostname": attention_broker_hostname,
            },
        )
