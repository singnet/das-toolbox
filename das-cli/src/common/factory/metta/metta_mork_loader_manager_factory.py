import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.metta.metta_mork_loader_container_manager import (
    MettaMorkLoaderContainerManager,
)
from settings.config import SECRETS_PATH


class MettaMorkLoaderManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        container_name = self._settings.get("services.morkdb_loader.container_name")
        morkdb_port = self._settings.get("services.morkdb.port", 40022)
        morkdb_hostname = "0.0.0.0"

        return MettaMorkLoaderContainerManager(
            container_name,
            options={
                "morkdb_port": morkdb_port,
                "morkdb_hostname": morkdb_hostname,
            },
        )
