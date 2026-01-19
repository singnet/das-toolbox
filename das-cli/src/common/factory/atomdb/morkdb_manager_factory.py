from common import Settings
from common.config.store import JsonConfigStore
import os
from common.container_manager.morkdb_container_manager import MorkdbContainerManager
from settings.config import SECRETS_PATH

class MorkDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        container_name = self._settings.get("services.morkdb.container_name")
        morkdb_port = self._settings.get("services.morkdb.port")
        return MorkdbContainerManager(
            container_name,
            options={
                "morkdb_port": morkdb_port,
            },
        )