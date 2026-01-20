import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.agents.evolution_agent_container_manager import (
    EvolutionAgentContainerManager,
)
from settings.config import SECRETS_PATH


class EvolutionAgentManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        container_name = self._settings.get("services.evolution_agent.container_name")

        return EvolutionAgentContainerManager(container_name, options={})
