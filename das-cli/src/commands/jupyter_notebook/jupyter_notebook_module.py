import os

from commands.config.config_cli import Settings
from common import Module
from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .jupyter_notebook_cli import JupyterNotebookCli
from common.container_manager.jupyter_notebook_container_manager import JupyterNotebookContainerManager
from common.factory.jupyter_notebook_manager_factory import JupyterNotebookManagerFactory


class JupyterNotebookModule(Module):
    _instance = JupyterNotebookCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

        self._dependecy_injection = [
            (
                JupyterNotebookContainerManager,
                JupyterNotebookManagerFactory().build()
            ),
            (
                Settings,
                self._settings,
            ),
        ]
