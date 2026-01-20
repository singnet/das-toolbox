import os
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.link_creation_agent_container_manager import LinkCreationAgentContainerManager


class LinkCreationAgentManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        container_name = self._settings.get(f"services.link_creation_agent.container_name")

        return LinkCreationAgentContainerManager(
            container_name,
            options={}
        )