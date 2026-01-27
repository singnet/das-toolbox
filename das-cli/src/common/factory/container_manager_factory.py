import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.agents.generic_agent_containers import ContainerTypes
from common.docker.container_manager import (
    Container,
    ContainerImageMetadata,
    ContainerMetadata,
)
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION, SECRETS_PATH


class ContainerManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self, type: ContainerTypes):

        settings_key = type.name.lower()

        container_name = self._settings.get(f"services.{settings_key}.container_name")
        container_port = self._settings.get(f"services.{settings_key}.port")

        container_image_metadata: ContainerImageMetadata = {
            "name": DAS_IMAGE_NAME,
            "version": DAS_IMAGE_VERSION,
        }

        container_data: ContainerMetadata = {
            "port": container_port,
            "image": container_image_metadata,
        }

        container = Container(name=container_name, metadata=container_data)

        return type.value(container, exec_context=None)
