import os

from common import Module
from common.config.store import JsonConfigStore
from commands.attention_broker.attention_broker_container_manager import (
    AttentionBrokerManager,
)
from settings.config import SECRETS_PATH

from .logs_cli import LogsCli, Settings


class LogsModule(Module):
    _instance = LogsCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(
            store=JsonConfigStore(
                os.path.expanduser(SECRETS_PATH),
            )
        )

        self._dependecy_injection = [
            (
                Settings,
                self._settings,
            ),
            (
                AttentionBrokerManager,
                self._attention_broker_manager_factory,
            ),
        ]

    def _attention_broker_manager_factory(self) -> AttentionBrokerManager:
        attention_broker_container = self._settings.get(
            "services.attention_broker.container_name"
        )
        attention_broker_port = self._settings.get("services.attention_broker.port")

        return AttentionBrokerManager(
            attention_broker_container,
            options={
                "attention_broker_port": attention_broker_port,
            },
        )
