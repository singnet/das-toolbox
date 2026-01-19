import os
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from common.docker.container_manager import ContainerManager


class GenericContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self, service_name: str):

        container_name = self._settings.get(f"services.{service_name}.container_name")

        return ContainerManager(
            container= {
                "name": container_name,
                "metadata": None,
            }
        )