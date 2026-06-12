import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.metta.database_loader_container_manager import (
    DatabaseLoaderContainerManager,
)
from common.settings import get_core_defaults_dict
from common.utils import extract_service_port
from settings.config import SECRETS_PATH


class DatabaseLoaderContainerManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._default = get_core_defaults_dict()

    def build(self):
        container_name = "das-cli-metta-loader"

        return DatabaseLoaderContainerManager(
            container_name,
            options={},
        )
