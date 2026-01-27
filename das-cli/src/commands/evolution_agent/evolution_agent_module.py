import os

from common import Module
from common.config.store import JsonConfigStore
from common.container_manager.agents.generic_agent_containers import QueryAgentContainerManager
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.factory.busnode_manager_factory import BusNodeContainerManagerFactory
from common.factory.container_manager_factory import (
    ContainerManagerFactory,
    ContainerTypes,
)
from settings.config import SECRETS_PATH

from .evolution_agent_cli import EvolutionAgentCli, Settings


class EvolutionAgentModule(Module):
    _instance = EvolutionAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependency_list = [
            (
                QueryAgentContainerManager,
                ContainerManagerFactory().build(type=ContainerTypes.QUERY_AGENT),
            ),
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings="evolution_agent", service_name="evolution-agent"
                ),
            ),
            (
                Settings,
                self._settings,
            ),
        ]
