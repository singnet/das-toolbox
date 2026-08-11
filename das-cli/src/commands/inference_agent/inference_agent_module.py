import os

from common import Module
from common.config.store import JsonConfigStore
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.factory.busnode_manager_factory import BusNodeContainerManager
from common.factory.busnode_manager_factory import BusNodeContainerManagerFactory
from common.container_manager.agents.generic_agent_containers import QueryAgentContainerManager, ContainerTypes
from common.factory.container_manager_factory import ContainerManagerFactory
from settings.config import SECRETS_PATH

from .inference_agent_cli import InferenceAgentCli, Settings


class InferenceAgentModule(Module):
    _instance = InferenceAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()
        self._container_manager_factory = ContainerManagerFactory()

        self._dependency_list = [
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings_from="agents.inference", service_name="inference-agent"
                ),
            ),
            (
                QueryAgentContainerManager,
                self._container_manager_factory.build(ContainerTypes.QUERY_ENGINE)
            ),
            (
                Settings,
                self._settings,
            ),
        ]
