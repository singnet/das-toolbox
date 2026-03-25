import os

from common import Settings
from common.config.core import get_core_defaults_dict
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager
from common.utils import extract_service_port
from settings.config import SECRETS_PATH


class MorkDbContainerManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()

    def build(self):
        morkdb_port = extract_service_port(self._settings.get("atomdb.morkdb.endpoint"))

        container_name = f"das-cli-morkdb-{morkdb_port}"
        return MorkdbContainerManager(
            container_name,
            options={"morkdb_port": morkdb_port, "morkdb_hostname": "0.0.0.0"},
        )
