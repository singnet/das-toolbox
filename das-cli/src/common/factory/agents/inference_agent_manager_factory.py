import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.agents.inference_agent_container_manager import (
    InferenceAgentContainerManager,
)
from settings.config import SECRETS_PATH


class InferenceAgentManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        container_name = self._settings.get("services.inference_agent.container_name")

        return InferenceAgentContainerManager(container_name, options={})
