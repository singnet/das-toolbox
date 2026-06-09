import os

from common import Settings
from common.config.core import get_core_defaults_dict
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.redis_container_manager import (
    RedisContainerManager,
)
from common.utils import extract_service_port
from settings.config import SECRETS_PATH


class RedisContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(
            store=JsonConfigStore(os.path.expanduser(SECRETS_PATH))
        )
        self._default = get_core_defaults_dict()

    def _get_backend_path(self) -> str:
        if self._settings.get("atomdb.type") == "adapterdb":
            return "atomdb.adapterdb.atomdb_backend.redis"

        return "atomdb.redis"

    def build(self):
        backend_path = self._get_backend_path()

        redis_endpoint = self._settings.get(f"{backend_path}.endpoint")
        redis_port = extract_service_port(redis_endpoint)

        redis_nodes = self._settings.get(f"{backend_path}.nodes", [])
        redis_cluster = self._settings.get(f"{backend_path}.cluster", False)

        container_name = f"das-cli-redis-{redis_port}"

        return RedisContainerManager(
            container_name,
            options={
                "redis_endpoint": redis_endpoint,
                "redis_port": redis_port,
                "redis_nodes": redis_nodes,
                "redis_cluster": redis_cluster,
            },
        )