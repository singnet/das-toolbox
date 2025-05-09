from commands.config.config_cli import Settings
from common import Module

from .jupyter_notebook_cli import JupyterNotebookCli
from .jupyter_notebook_container_manager import JupyterNotebookContainerManager


class JupyterNotebookModule(Module):
    _instance = JupyterNotebookCli

    def __init__(self) -> None:
        super().__init__()

        self._settings = Settings()

        self._dependecy_injection = [
            (
                JupyterNotebookContainerManager,
                self._jupyter_notebook_container_manager_factory,
            )
        ]

    def _jupyter_notebook_container_manager_factory(
        self,
    ) -> JupyterNotebookContainerManager:
        container_name = self._settings.get("jupyter_notebook.container_name")
        jupyter_notebook_port = self._settings.get("jupyter_notebook.port")

        return JupyterNotebookContainerManager(
            container_name,
            options={
                "jupyter_notebook_port": jupyter_notebook_port,
            },
        )
