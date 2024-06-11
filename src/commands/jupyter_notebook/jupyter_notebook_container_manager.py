import docker
from common import Container, ContainerManager
from config import JUPYTER_NOTEBOOK_IMAGE_NAME, JUPYTER_NOTEBOOK_IMAGE_VERSION
from common.docker.exceptions import DockerError


class JupyterNotebookContainerManager(ContainerManager):
    def __init__(self, jupyter_container_name) -> None:
        container = Container(
            jupyter_container_name,
            JUPYTER_NOTEBOOK_IMAGE_NAME,
            JUPYTER_NOTEBOOK_IMAGE_VERSION,
        )

        super().__init__(container)

    def start_container(
        self,
        port: int,
    ):
        self.raise_running_container()

        try:
            container = self._start_container(
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                ports={
                    "8888/tcp": port,
                },
            )

            return container
        except docker.errors.APIError as e:
            raise DockerError(e.explanation)
