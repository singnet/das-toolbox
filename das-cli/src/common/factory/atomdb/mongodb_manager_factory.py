import os

from common import Settings
from common.config.core import get_core_defaults_dict
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.mongodb_container_manager import (
    MongodbContainerManager,
)
from common.utils import extract_service_port
from settings.config import SECRETS_PATH


class MongoDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()

    def _get_backend_path(self) -> str:
        if self._settings.get("atomdb.type") == "adapterdb":
            return "atomdb.adapterdb.atomdb_backend.mongodb"

        return "atomdb.mongodb"

    def build(self):
        backend_path = self._get_backend_path()

        mongodb_endpoint = self._settings.get(f"{backend_path}.endpoint")
        mongodb_port = extract_service_port(mongodb_endpoint)

        mongodb_username = self._settings.get(f"{backend_path}.username")
        mongodb_password = self._settings.get(f"{backend_path}.password")

        mongodb_nodes = self._settings.get(f"{backend_path}.nodes", [])

        mongodb_cluster = self._settings.get(f"{backend_path}.cluster", False)
        mongodb_cluster_secret_key = self._settings.get(f"{backend_path}.cluster_secret_key", None)

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
