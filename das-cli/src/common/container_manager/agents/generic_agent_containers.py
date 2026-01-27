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
    CONTEXT_BROKER = ContextBrokerContainerManager
    ATOMDB_BROKER = AtomDbBrokerContainerManager
    LINK_CREATION_AGENT = LCAContainerManager
    EVOLUTION_AGENT = EvolutionAgentContainerManager
    INFERENCE_AGENT = InferenceAgentContainerManager
    QUERY_AGENT = QueryAgentContainerManager
