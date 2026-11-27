from enum import Enum

from common.docker.container_manager import ContainerManager


class MongoDbContainerManager(ContainerManager):
    pass

class RedisContainerManager(ContainerManager):
    pass

class MorkDbContainerManager(ContainerManager):
    pass

class AttentionBrokerContainerManager(ContainerManager):
    pass

class AtomDbBrokerContainerManager(ContainerManager):
    pass

class ContextBrokerContainerManager(ContainerManager):
    pass

class LCAContainerManager(ContainerManager):
    pass

class EvolutionAgentContainerManager(ContainerManager):
    pass

class QueryAgentContainerManager(ContainerManager):
    pass

class CommandRouterContainerManager(ContainerManager):
    pass

class ContainerTypes(Enum):
    MONGODB = (MongoDbContainerManager, "atomdb.mongodb")
    REDIS = (RedisContainerManager, "atomdb.redis")
    MORK = (MorkDbContainerManager, "atomdb.morkdb")
    ATTENTION_BROKER = (AttentionBrokerContainerManager, "agents.attention")
    CONTEXT_BROKER = (ContextBrokerContainerManager, "agents.context")
    ATOMDB_BROKER = (AtomDbBrokerContainerManager, "agents.atomdb")
    LINK_CREATION_AGENT = (LCAContainerManager, "agents.link_creation")
    EVOLUTION_AGENT = (EvolutionAgentContainerManager, "agents.evolution")
    QUERY_ENGINE = (QueryAgentContainerManager, "agents.query")
    COMMAND_ROUTER = (CommandRouterContainerManager, "agents.command_router")

    def __init__(self, manager_type, settings):
        self.manager_type = manager_type
        self.settings_path = settings
