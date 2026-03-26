import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.agents.generic_agent_containers import ContainerTypes
from common.docker.container_manager import Container, ContainerImageMetadata, ContainerMetadata
from common.utils import extract_service_port
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION, SECRETS_PATH


class ContainerManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def _gen_container_name(self, type: ContainerTypes, port: int | None):
        return f"das-{type.name.lower().replace('_', '-')}-{port}"

    def build(self, type: ContainerTypes):
        settings_key = type.settings_path

        container_port = extract_service_port(self._settings.get(f"{settings_key}.endpoint"))

        container_name = self._gen_container_name(type, container_port)

        container_image_metadata: ContainerImageMetadata = {
            "name": DAS_IMAGE_NAME,
            "version": DAS_IMAGE_VERSION,
        }

        container_data: ContainerMetadata = {
            "port": container_port,
            "image": container_image_metadata,
        }

        container = Container(name=container_name, metadata=container_data)

        return type.manager_type(container, exec_context=None)
