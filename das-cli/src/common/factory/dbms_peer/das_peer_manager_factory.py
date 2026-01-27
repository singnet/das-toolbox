import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.dbms.das_peer_container_manager import DasPeerContainerManager
from settings.config import SECRETS_PATH


class DasPeerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        container_name = self._settings.get("services.das_peer.container_name")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")
        mongodb_port = self._settings.get("services.mongodb.port")
        redis_port = self._settings.get("services.redis.port")

        adapter_server_port = 30100

        return DasPeerContainerManager(
            container_name,
            options={
                "das_peer_port": adapter_server_port,
                "mongodb_hostname": "0.0.0.0",
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "redis_hostname": "0.0.0.0",
                "redis_port": redis_port,
            },
        )
