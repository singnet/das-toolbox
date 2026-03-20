import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager
from settings.config import SECRETS_PATH
from ..shared.shared_utils import safe_extract_value, extract_port
from common.config.core import get_core_defaults_dict


class MorkDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()


    def build(self):
        morkdb_port = extract_port(safe_extract_value(self._settings, self._default, "atomdb.morkdb.endpoint"))

        container_name = f"das-cli-morkdb-{morkdb_port}"
        return MorkdbContainerManager(
            container_name,
            options={"morkdb_port": morkdb_port, "morkdb_hostname": "0.0.0.0"},
        )
