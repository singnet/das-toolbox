import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.config.core import get_core_defaults_dict
from settings.config import SECRETS_PATH
from common.utils import extract_service_port

class MongoDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()


    def build(self):
        mongodb_port = extract_service_port(self._settings.get("atomdb.mongodb.endpoint"))

        mongodb_username = self._settings.get("atomdb.mongodb.username")
        mongodb_password = self._settings.get("atomdb.mongodb.password")
        container_name = f"das-cli-mongodb-{mongodb_port}"
        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )
