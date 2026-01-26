import os

from common import Module
from common.config.store import JsonConfigStore
from common.container_manager.agents.attention_broker_container_manager import (
    AttentionBrokerManager,
)
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager
from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from common.factory.atomdb.mongodb_manager_factory import MongoDbContainerManagerFactory
from common.factory.atomdb.redis_manager_factory import RedisContainerManagerFactory
from common.factory.attention_broker_manager_factory import AttentionBrokerManagerFactory
from common.factory.container_manager_factory import (
    ContainerManagerFactory,
    ContainerTypes,
    ContextBrokerContainerManager,
    EvolutionAgentContainerManager,
    InferenceAgentContainerManager,
    LCAContainerManager,
    QueryAgentContainerManager,
)
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
                RedisContainerManagerFactory().build(),
            ),
            (
                MongodbContainerManager,
                MongoDbContainerManagerFactory().build(),
            ),
            (
                AttentionBrokerManager,
                AttentionBrokerManagerFactory().build(),
            ),
            (
                QueryAgentContainerManager,
                container_factory.build(type=ContainerTypes.QUERY_AGENT),
            ),
            (
                LCAContainerManager,
                container_factory.build(type=ContainerTypes.LINK_CREATION_AGENT),
            ),
            (
                InferenceAgentContainerManager,
                container_factory.build(type=ContainerTypes.INFERENCE_AGENT),
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
