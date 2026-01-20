import os
from common.container_manager.agents.jupyter_notebook_container_manager import JupyterNotebookContainerManager
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore

from common.container_manager.system_containers_manager import SystemContainersManager

class SystemContainerManagerFactory():

    def __init__(self):
        self._settings = JsonConfigStore(file_path=SECRETS_PATH)
        
    def build(self):

        return SystemContainersManager(
            settings=self._settings,
        )