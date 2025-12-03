import os

from common import Settings
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .busnode_container_manager import BusNodeContainerManager


class BusNodeContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self, use_settings: str, service_name: str) -> BusNodeContainerManager:

        default_container_name = self._settings.get(f"services.{use_settings}.container_name")

        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")

        redis_port = self._settings.get("services.redis.port")

        morkdb_hostname = "0.0.0.0"
        morkdb_port = self._settings.get("services.morkdb.port")

        service_port = self._settings.get(f"services.{use_settings}.port")
        service_endpoint = f"0.0.0.0:{service_port}"

        attention_broker_port = self._settings.get("services.attention_broker.port")

        return BusNodeContainerManager(
            default_container_name,
            options={
                "service": service_name,
                "service_port": service_port,
                "service_endpoint": service_endpoint,
                "redis_hostname": "0.0.0.0",
                "redis_port": redis_port,
                "mongodb_port": mongodb_port,
                "mongodb_hostname": "0.0.0.0",
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "morkdb_hostname": morkdb_hostname,
                "morkdb_port": morkdb_port,
                "attention_broker_hostname": "0.0.0.0",
                "attention_broker_port": attention_broker_port,
            },
        )
