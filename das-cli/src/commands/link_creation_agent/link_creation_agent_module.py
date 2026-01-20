import os

from common import Module
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.factory.busnode_manager_factory import BusNodeContainerManagerFactory
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .link_creation_agent_cli import (
    LinkCreationAgentCli,
    Settings,
)
from common.container_manager.agents.query_agent_container_manager import QueryAgentContainerManager
from common.factory.agents.query_agent_manager_factory import QueryAgentManagerFactory

class LinkCreationAgentModule(Module):

    _instance = LinkCreationAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependecy_injection = [
            (
                QueryAgentContainerManager,
                QueryAgentManagerFactory().build()
            ),
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings="link_creation_agent", service_name="link-creation-agent"
                ),
            ),
            (
                Settings,
                self._settings,
            ),
        ]