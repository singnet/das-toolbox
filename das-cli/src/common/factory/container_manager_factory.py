import os
from enum import Enum

from common import Settings
from common.config.store import JsonConfigStore
from common.docker.container_manager import (
    Container,
    ContainerImageMetadata,
    ContainerManager,
    ContainerMetadata,
)
from settings.config import DAS_IMAGE_NAME, DAS_IMAGE_VERSION, SECRETS_PATH


class AtomDbBrokerContainerManager(ContainerManager):
    pass


class ContextBrokerContainerManager(ContainerManager):
    pass


class LCAContainerManager(ContainerManager):
    pass


class EvolutionAgentContainerManager(ContainerManager):
    pass


class InferenceAgentContainerManager(ContainerManager):
    pass


class QueryAgentContainerManager(ContainerManager):
    pass


class ContainerTypes(Enum):
    CONTEXT_BROKER = ContextBrokerContainerManager
    ATOMDB_BROKER = AtomDbBrokerContainerManager
    LINK_CREATION_AGENT = LCAContainerManager
    EVOLUTION_AGENT = EvolutionAgentContainerManager
    INFERENCE_AGENT = InferenceAgentContainerManager
    QUERY_AGENT = QueryAgentContainerManager


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
