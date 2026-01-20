import os
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.agents.attention_broker_container_manager import AttentionBrokerManager


class AttentionBrokerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        container_name = self._settings.get("services.attention_broker.container_name")
        attention_broker_port = self._settings.get("services.attention_broker.port")

        return AttentionBrokerManager(
            container_name,
            options={
                "attention_broker_hostname": "0.0.0.0",
                "attention_broker_port": attention_broker_port
            }
        )