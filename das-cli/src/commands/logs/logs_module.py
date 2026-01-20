import os

from common.factory.atomdb.mongodb_manager_factory import MongoDbContainerManagerFactory
from common.factory.atomdb.redis_manager_factory import RedisContainerManagerFactory
from common.factory.agents.evolution_agent_manager_factory import EvolutionAgentContainerManager
from common.factory.agents.query_agent_manager_factory import QueryAgentManagerFactory
from common.factory.agents.evolution_agent_manager_factory import EvolutionAgentManagerFactory
from common.factory.attention_broker_manager_factory import AttentionBrokerManagerFactory
from common.factory.agents.link_creation_manager_factory import LinkCreationAgentManagerFactory
from common.factory.agents.inference_agent_manager_factory import InferenceAgentManagerFactory
from common.factory.agents.context_broker_manager_factory import ContextBrokerManagerFactory

from common.container_manager.mongodb_container_manager import MongodbContainerManager
from common.container_manager.redis_container_manager import RedisContainerManager
from common.container_manager.attention_broker_container_manager import AttentionBrokerManager
from common.container_manager.query_agent_container_manager import QueryAgentContainerManager
from common.container_manager.link_creation_agent_container_manager import LinkCreationAgentContainerManager
from common.container_manager.inference_agent_container_manager import InferenceAgentContainerManager
from common.container_manager.context_broker_container_manager import ContextBrokerContainerManager

from common import Module
from common.config.store import JsonConfigStore
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

        self._dependecy_injection = [
            (
                Settings,
                self._settings,
            ),
            (
                RedisContainerManager,
                lambda: RedisContainerManagerFactory().build(),
            ),
            (
                MongodbContainerManager,
                lambda: MongoDbContainerManagerFactory().build(),
            ),
            (
                AttentionBrokerManager,
                lambda: AttentionBrokerManagerFactory().build(),
            ),
            (
                QueryAgentContainerManager,
                lambda: QueryAgentManagerFactory().build(),
            ),
            (
                LinkCreationAgentContainerManager,
                lambda: LinkCreationAgentManagerFactory().build(),
            ),
            (
                InferenceAgentContainerManager,
                lambda: InferenceAgentManagerFactory().build(),
            ),
            (
                EvolutionAgentContainerManager,
                lambda: EvolutionAgentManagerFactory().build(),
            ),
            (
                ContextBrokerContainerManager,
                lambda: ContextBrokerManagerFactory().build(),
            ),
        ]
