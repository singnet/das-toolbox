from enum import Enum

from common.docker.container_manager import ContainerManager


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

    CONTEXT_BROKER = (ContextBrokerContainerManager, "brokers.context")
    ATOMDB_BROKER = (AtomDbBrokerContainerManager, "brokers.atomdb")
    LINK_CREATION_AGENT = (LCAContainerManager, "agents.link_creation")
    EVOLUTION_AGENT = (EvolutionAgentContainerManager, "agents.evolution")
    INFERENCE_AGENT = (InferenceAgentContainerManager, "agents.inference")
    QUERY_ENGINE = (QueryAgentContainerManager, "agents.query")

    def __init__(self, manager_type, settings):
        self.manager_type = manager_type
        self.settings_path = settings
