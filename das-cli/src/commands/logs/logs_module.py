import os
from typing_extensions import Annotated

from common.factory.generic_manager_factory import GenericContainerManagerFactory
from common.docker.container_manager import ContainerManager

from common.factory.atomdb.mongodb_manager_factory import MongoDbContainerManagerFactory
from common.factory.atomdb.redis_manager_factory import RedisContainerManagerFactory

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

        AttentionBrokerManager = Annotated[ContainerManager, "attention_broker"]
        QueryAgentContainerManager = Annotated[ContainerManager, "query_agent"]
        RedisContainerManager = Annotated[ContainerManager, "redis"]
        MongodbContainerManager = Annotated[ContainerManager, "mongodb"]
        AttentionBrokerManager = Annotated[ContainerManager, "attention_broker"]
        LinkCreationAgentContainerManager = Annotated[ContainerManager, "link_creation_agent"]
        InferenceAgentContainerManager = Annotated[ContainerManager, "inference_agent"]
        EvolutionAgentContainerManager = Annotated[ContainerManager, "evolution_agent"]
        ContextBrokerContainerManager = Annotated[ContainerManager, "context_broker"]

        self._dependecy_injection = [
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
                GenericContainerManagerFactory().build(service_name="attention_broker")
            ),
            (
                QueryAgentContainerManager,
                GenericContainerManagerFactory().build(service_name="query_agent")
            ),
            (
                LinkCreationAgentContainerManager,
                GenericContainerManagerFactory().build(service_name="link_creation_agent")
            ),
            (
                InferenceAgentContainerManager,
                GenericContainerManagerFactory().build(service_name="inference_agent")
            ),
            (
                EvolutionAgentContainerManager,
                GenericContainerManagerFactory().build(service_name="evolution_agent")
            ),
            (
                ContextBrokerContainerManager,
                GenericContainerManagerFactory().build(service_name="context_broker")
            ),
        ]