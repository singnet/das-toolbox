import os
from typing import Annotated

from common import Module
from common.bus_node.busnode_container_manager import BusNodeContainerManager
from common.bus_node.busnode_manager_factory import BusNodeContainerManagerFactory
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .evolution_agent_cli import EvolutionAgentCli, Settings

from common.factory.agents.query_agent_manager_factory import QueryAgentManagerFactory
from common.container_manager.query_agent_container_manager import QueryAgentContainerManager

class EvolutionAgentModule(Module):
    _instance = EvolutionAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependecy_injection = [
            (
                QueryAgentContainerManager,
                QueryAgentManagerFactory().build(),
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
