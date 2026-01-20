import os
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.query_agent_container_manager import QueryAgentContainerManager


class QueryAgentManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):

        container_name = self._settings.get(f"services.query_agent.container_name")

        return QueryAgentContainerManager(
            container_name,
            options={} 
        )