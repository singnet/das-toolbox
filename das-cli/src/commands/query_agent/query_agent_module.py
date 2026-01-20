import os
from typing import List

from common.container_manager.agents.attention_broker_container_manager import AttentionBrokerManager
from common.factory.atomdb.atomdb_backend import (
    AtomdbBackend,
)

from common import Module
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.factory.busnode_manager_factory import BusNodeContainerManagerFactory
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .query_agent_cli import QueryAgentCli, Settings

from common.container_manager.atomdb.redis_container_manager import RedisContainerManager
from common.container_manager.atomdb.mongodb_container_manager import MongodbContainerManager

from common.factory.atomdb.atomdb_factory import AtomDbContainerManagerFactory
from common.factory.atomdb.redis_manager_factory import RedisContainerManagerFactory
from common.factory.atomdb.mongodb_manager_factory import MongoDbContainerManagerFactory
from common.factory.attention_broker_manager_factory import AttentionBrokerManagerFactory

class QueryAgentModule(Module):
    _instance = QueryAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependency_list = [
            (
                RedisContainerManager,
                AtomDbContainerManagerFactory().build()
            ),
            (
                MongodbContainerManager,
                MongoDbContainerManagerFactory().build(),
            ),
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings="query_agent", service_name="query-engine"
                ),
            ),
            (
                AtomdbBackend,
                AtomDbContainerManagerFactory().build(),
            ),
            (
                AttentionBrokerManager,
                AttentionBrokerManagerFactory().build()
            ),
            (
                Settings,
                self._settings,
            ),
        ]
