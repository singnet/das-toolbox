import os
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from common.docker.container_manager import ContainerManager


class AttentionBrokerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        container_name = self._settings.get("services.attention_broker.container_name")
        attention_broker_port = self._settings.get("services.attention_broker.port")

        return ContainerManager(
            container={
                "name": container_name,
                "metadata": {
                    "port": attention_broker_port
                }
            }
        )