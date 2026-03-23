import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.metta.metta_mork_loader_container_manager import (
    MettaMorkLoaderContainerManager,
)
from settings.config import SECRETS_PATH
from common.utils import extract_service_port
from common.settings import get_core_defaults_dict

class MettaMorkLoaderManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()

    def build(self):

        morkdb_port = extract_service_port(self._settings.get("atomdb.morkdb.endpoint"))
        morkdb_hostname = "0.0.0.0"
        container_name = "das-cli-metta-mork-loader"

        return MettaMorkLoaderContainerManager(
            container_name,
            options={
                "morkdb_port": morkdb_port,
                "morkdb_hostname": morkdb_hostname,
            },
        )
