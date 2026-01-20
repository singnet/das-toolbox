import os
from common.container_manager.dbms.dbms_peer_container_manager import DbmsPeerContainerManager
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore

class DbmsPeerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        container_name = self._settings.get("services.dbms_peer.container_name")
        adapter_server_port = 30100

        return DbmsPeerContainerManager(
            container_name,
            options={
                "das_peer_port": adapter_server_port,
            },
        )