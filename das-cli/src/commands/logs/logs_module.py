import os

from common import Module
from common.config.store import JsonConfigStore

from common.container_manager.agents.generic_agent_containers import (
    AtomDbBrokerContainerManager,
    AttentionBrokerContainerManager,
    ContextBrokerContainerManager,
    EvolutionAgentContainerManager,
    LCAContainerManager,
    QueryAgentContainerManager,
    MongoDbContainerManager,
    RedisContainerManager,
    MorkDbContainerManager,
)

from common.factory.container_manager_factory import ContainerManagerFactory, ContainerTypes
from settings.config import SECRETS_PATH

from .logs_cli import LogsCli, Settings


class LogsModule(Module):
    _instance = LogsCli

    def __init__(self):
        super().__init__()

        self._settings = Settings(
            store=JsonConfigStore(
                os.path.expanduser(SECRETS_PATH),
            )
        )

        container_factory = ContainerManagerFactory()

        self._dependency_list = [
            (
                Settings,
                self._settings,
            ),
            (
                RedisContainerManager,
                container_factory.build(type=ContainerTypes.REDIS),
            ),
            (
                MongoDbContainerManager,
                container_factory.build(type=ContainerTypes.MONGODB),
            ),
            (
                MorkDbContainerManager,
                container_factory.build(type=ContainerTypes.MORK),
            ),
            (
                AttentionBrokerContainerManager,
                container_factory.build(type=ContainerTypes.ATTENTION_BROKER),
            ),
            (
                AtomDbBrokerContainerManager,
                container_factory.build(type=ContainerTypes.ATOMDB_BROKER),
            ),
            (
                QueryAgentContainerManager,
                container_factory.build(type=ContainerTypes.QUERY_ENGINE),
            ),
            (
                LCAContainerManager,
                container_factory.build(type=ContainerTypes.LINK_CREATION_AGENT),
            ),
            (
                EvolutionAgentContainerManager,
                container_factory.build(type=ContainerTypes.EVOLUTION_AGENT),
            ),
            (
                ContextBrokerContainerManager,
                container_factory.build(type=ContainerTypes.CONTEXT_BROKER),
            ),
        ]
