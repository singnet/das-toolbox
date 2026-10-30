import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.mongodb_container_manager import (
    MongodbContainerManager,
)
from common.utils import extract_service_port
from settings.config import SECRETS_PATH


class MongoDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def _get_backend_path(self) -> str:
        if self._settings.get("atomdb.type") == "adapterdb":
            return "atomdb.adapterdb.atomdb_backend.mongodb"

        return "atomdb.mongodb"

    def build(self, section: dict = {}):
        if len(section.items()) == 0:
            section = self._settings.get(self._get_backend_path(), {}) or {}

        mongodb_endpoint: str = section.get("endpoint", "")
        mongodb_port = extract_service_port(mongodb_endpoint)

        mongodb_username = section.get("username")
        mongodb_password = section.get("password")

        mongodb_nodes = section.get("nodes", []) or []

        mongodb_cluster = section.get("cluster", False)
        mongodb_cluster_secret_key = section.get("cluster_secret_key", None)

        container_name = f"das-cli-mongodb-{mongodb_port}"

        return MongodbContainerManager(
            container_name,
            options={
                "service_name": "MongoDB",
                "service_command_label": "db",
                "mongodb_endpoint": mongodb_endpoint,
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "mongodb_nodes": mongodb_nodes,
                "mongodb_cluster": mongodb_cluster,
                "mongodb_cluster_secret_key": mongodb_cluster_secret_key,
            },
        )
