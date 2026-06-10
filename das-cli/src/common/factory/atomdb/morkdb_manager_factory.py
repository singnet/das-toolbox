import os

from common import Settings
from common.config.core import get_core_defaults_dict
from common.config.store import JsonConfigStore
from common.container_manager.atomdb.morkdb_container_manager import MorkdbContainerManager
from common.utils import extract_service_hostname, extract_service_port
from settings.config import SECRETS_PATH


class MorkDbContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()

    def _get_backend_path(self) -> str:
        if self._settings.get("atomdb.type") == "adapterdb":
            return "atomdb.adapterdb.atomdb_backend.morkdb"

        return "atomdb.morkdb"

    def build(self):
        backend_path = self._get_backend_path()

        morkdb_endpoint = self._settings.get(f"{backend_path}.endpoint")
        morkdb_port = extract_service_port(morkdb_endpoint)
        morkdb_hostname = extract_service_hostname(morkdb_endpoint)

        container_name = f"das-cli-morkdb-{morkdb_port}"

        return MorkdbContainerManager(
            container_name,
            options={
                "morkdb_endpoint": morkdb_endpoint,
                "morkdb_port": morkdb_port,
                "morkdb_hostname": morkdb_hostname,
            },
        )
