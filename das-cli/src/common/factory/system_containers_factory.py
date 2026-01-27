import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.system_containers_manager import SystemContainersManager
from settings.config import SECRETS_PATH


class SystemContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        return SystemContainersManager(
            settings=self._settings,
        )
