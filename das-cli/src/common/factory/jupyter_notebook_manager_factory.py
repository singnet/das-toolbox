import os
from common.container_manager.jupyter_notebook_container_manager import JupyterNotebookContainerManager
from settings.config import SECRETS_PATH
from common import Settings
from common.config.store import JsonConfigStore
from common.docker.container_manager import ContainerManager

class JupyterNotebookManagerFactory:

    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        
        container_name = self._settings.get("services.jupyter_notebook.container_name")
        jupyter_notebook_port = self._settings.get("services.jupyter_notebook.port")
        jupyter_notebook_hostname = "0.0.0.0"

        return JupyterNotebookContainerManager(
            container_name,
            options={
                "jupyter_notebook_port": jupyter_notebook_port,
                "jupyter_notebook_hostname": jupyter_notebook_hostname,
            },
        )