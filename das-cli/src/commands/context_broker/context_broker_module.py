import os

from common import Module
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.factory.busnode_manager_factory import BusNodeContainerManagerFactory
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .context_broker_cli import ContextBrokerCli, Settings

from common.container_manager.agents.query_agent_container_manager import QueryAgentContainerManager
from common.factory.agents.query_agent_manager_factory import QueryAgentManagerFactory

class ContextBrokerModule(Module):
    _instance = ContextBrokerCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependency_list = [
            (
                QueryAgentContainerManager,
                QueryAgentManagerFactory().build()
            ),
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings="context_broker", service_name="context-broker"
                ),
            ),
            (
                Settings,
                self._settings,
            ),
        ]
