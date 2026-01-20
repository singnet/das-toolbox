
import os

from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.metta_loader_container_manager import MettaLoaderContainerManager

class MettaLoaderManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        
        container_name = self._settings.get("services.loader.container_name")
        mongodb_port = self._settings.get("services.mongodb.port")
        mongodb_username = self._settings.get("services.mongodb.username")
        mongodb_password = self._settings.get("services.mongodb.password")
        redis_port = self._settings.get("services.redis.port")
        atomdb_backend = self._settings.get("services.database.atomdb_backend")

        return MettaLoaderContainerManager(
            container_name,
            options={
                "redis_port": redis_port,
                "redis_hostname": "0.0.0.0",
                "mongodb_hostname": "0.0.0.0",
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
                "atomdb_backend": atomdb_backend,
            },
        )