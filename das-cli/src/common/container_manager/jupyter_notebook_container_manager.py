import os
from typing import Dict

import docker

from common import Container, ContainerManager
from common.docker.exceptions import DockerError
from settings.config import JUPYTER_NOTEBOOK_IMAGE_NAME, JUPYTER_NOTEBOOK_IMAGE_VERSION


class JupyterNotebookContainerManager(ContainerManager):
    def __init__(
        self,
        jupyter_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            jupyter_container_name,
            metadata={
                "port": options.get("jupyter_notebook_port"),
                "image": {
                    "name": JUPYTER_NOTEBOOK_IMAGE_NAME,
                    "version": JUPYTER_NOTEBOOK_IMAGE_VERSION,
                },
            },
        )

        self._options = options

        super().__init__(container)

    def _gen_jupyter_notebook_command(self) -> str:
        port = self._options.get("jupyter_notebook_port")
        hostname = self._options.get("jupyter_notebook_hostname")

        return f"jupyter notebook --ip={hostname} --port={port} --no-browser"

    def start_container(
        self,
        working_dir: str | None = None,
    ):
        self.raise_running_container()

        volumes = {(working_dir or os.getcwd()): {"bind": "/home/jovyan/work", "mode": "rw"}}

        try:
            container = self._start_container(
                command=self._gen_jupyter_notebook_command(),
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                volumes=volumes,
            )

            return container
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)
