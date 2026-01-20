import os

from common import Module
from common.container_manager.busnode_container_manager import BusNodeContainerManager
from common.factory.busnode_manager_factory import BusNodeContainerManagerFactory
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .inference_agent_cli import (
    AttentionBrokerManager,
    InferenceAgentCli,
    Settings,
)

from common.container_manager.agents.inference_agent_container_manager import InferenceAgentContainerManager

from common.factory.attention_broker_manager_factory import AttentionBrokerManagerFactory


class InferenceAgentModule(Module):
    _instance = InferenceAgentCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
        self._bus_node_factory = BusNodeContainerManagerFactory()

        self._dependency_list = [
            (
                BusNodeContainerManager,
                self._bus_node_factory.build(
                    use_settings="inference_agent", service_name="inference-agent"
                ),
            ),
            (
                AttentionBrokerManager,
                AttentionBrokerManagerFactory().build(),
            ),
            (
                Settings,
                self._settings,
            ),
        ]
