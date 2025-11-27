from common import Module, Settings
from common.config.store import JsonConfigStore
import os
from settings.config import SECRETS_PATH
from .busnode_cli import BusNodeCli
from .busnode_container_manager import BusNodeContainerManager

class BusNodeModule(Module):
    _instance = BusNodeCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                Settings,
                self._settings,
            ),
            (
                BusNodeContainerManager,
                self._busnode_container_manager_factory,
            )
        ]

    def _busnode_container_manager_factory(self) -> BusNodeContainerManager:
        default_container_name = "das-cli-busnode"

        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")
        mongodb_hostname = "0.0.0.0"

        redis_port = self._settings.get("services.redis.port")
        redis_hostname = "0.0.0.0"
        redis_use_cluster = self._settings.get("services.redis.cluster")

        return BusNodeContainerManager(
            default_container_name,
            options= {
                "mongodb_hostname": mongodb_hostname,
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "redis_port": redis_port,
                "redis_hostname": redis_hostname,
                "redis_use_cluster": redis_use_cluster,
            },
        )