import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.metta.database_loader_container_manager import (
    DatabaseLoaderContainerManager,
)
from settings.config import SECRETS_PATH


class DatabaseLoaderContainerManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        container_name = "das-cli-metta-loader"

        return DatabaseLoaderContainerManager(
            container_name,
            options={
                "service_name": "Metta Loader",
                "service_command_label": "metta",
            },
        )
