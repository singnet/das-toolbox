import os

from common import Settings
from common.config.store import JsonConfigStore
from common.container_manager.agents.jupyter_notebook_container_manager import (
    JupyterNotebookContainerManager,
)
from settings.config import SECRETS_PATH
from common.utils import extract_service_port


class JupyterNotebookManagerFactory:
    def __init__(self):
        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    def build(self):
        jupyter_notebook_port = extract_service_port(self._settings.get("environment.jupyter.endpoint"))
        jupyter_notebook_hostname = "0.0.0.0"

        container_name = f"das-cli-jupyter-notebook-{jupyter_notebook_port}"

        return JupyterNotebookContainerManager(
            container_name,
            options={
                "jupyter_notebook_port": jupyter_notebook_port,
                "jupyter_notebook_hostname": jupyter_notebook_hostname,
            },
        )
