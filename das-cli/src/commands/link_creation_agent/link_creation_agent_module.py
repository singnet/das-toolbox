import os

from common.container_manager.query_agent_container_manager import QueryAgentContainerManager
from common import Module
from common.bus_node.busnode_container_manager import BusNodeContainerManager
from common.bus_node.busnode_manager_factory import BusNodeContainerManagerFactory
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .link_creation_agent_cli import (
    LinkCreationAgentCli,
    Settings,
)
from common.container_manager.link_creation_agent_container_manager import LinkCreationAgentContainerManager

from common.factory.generic_manager_factory import GenericContainerManagerFactory
from common.docker.container_manager import ContainerManager

from typing_extensions import Annotated

class LinkCreationAgentModule(Module):
    _instance = LinkCreationAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        QueryAgentContainerManager = Annotated[ContainerManager, "query_agent"]

        self._dependecy_injection = [
            (
                QueryAgentContainerManager,
                GenericContainerManagerFactory().build(service_name="query_agent")
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