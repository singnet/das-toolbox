import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.config.core import get_core_defaults_dict
from settings.config import SECRETS_PATH
from ..shared.shared_utils import safe_extract_value, extract_port

class MongoDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()


    def build(self):
        mongodb_port = extract_port(safe_extract_value(self._settings, self._default, "atomdb.mongodb.endpoint"))

        mongodb_username = safe_extract_value(self._settings, self._default, "atomdb.mongodb.username")
        mongodb_password = safe_extract_value(self._settings, self._default, "atomdb.mongodb.password")
        container_name = f"das-cli-mongodb-{mongodb_port}"
        return MongodbContainerManager(
            container_name,
            options={
                "mongodb_port": mongodb_port,
                "mongodb_username": mongodb_username,
                "mongodb_password": mongodb_password,
            },
        )
