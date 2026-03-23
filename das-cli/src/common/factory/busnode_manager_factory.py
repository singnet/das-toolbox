import os

from common import Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH
from common.utils import extract_service_port

from ..container_manager.busnode_container_manager import BusNodeContainerManager


class BusNodeContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self, use_settings_from: str, service_name: str) -> BusNodeContainerManager:

        service_port = extract_service_port(self._settings.get(f"{use_settings_from}.port"))
        service_endpoint = f"0.0.0.0:{service_port}"

        attention_broker_port = extract_service_port(self._settings.get("brokers.attention_broker.endpoint"))

        default_container_name = f"das-{service_name}-{service_port}"

        return BusNodeContainerManager(
            default_container_name,
            options={
                "service": service_name,
                "service_port": service_port,
                "service_endpoint": service_endpoint,
                "attention_broker_hostname": "0.0.0.0",
                "attention_broker_port": attention_broker_port,
            },
        )
