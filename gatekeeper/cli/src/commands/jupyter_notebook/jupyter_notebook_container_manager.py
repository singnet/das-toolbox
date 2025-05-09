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

        super().__init__(container)

    def start_container(
        self,
        port: int,
        working_dir: str | None = None,
    ):
        self.raise_running_container()

        volumes = {(working_dir or os.getcwd()): {"bind": "/home/jovyan/work", "mode": "rw"}}

        try:
            container = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                ports={
                    "8888/tcp": port,
                },
                volumes=volumes,
            )

            return container
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)
