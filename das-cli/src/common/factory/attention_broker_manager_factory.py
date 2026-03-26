import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.agents.attention_broker_container_manager import (
    AttentionBrokerManager,
)
from common.utils import extract_service_port
from settings.config import SECRETS_PATH


class AttentionBrokerManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        attention_broker_port = extract_service_port(
            self._settings.get("brokers.attention.endpoint")
        )
        container_name = f"das-attention-broker-{attention_broker_port}"

        return AttentionBrokerManager(
            container_name,
            options={
                "attention_broker_hostname": "0.0.0.0",
                "attention_broker_port": attention_broker_port,
            },
        )
