import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.agents.link_creation_agent_container_manager import (
    LinkCreationAgentContainerManager,
)
from settings.config import SECRETS_PATH


class LinkCreationAgentManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        container_name = self._settings.get("services.link_creation_agent.container_name")

        return LinkCreationAgentContainerManager(container_name, options={})
