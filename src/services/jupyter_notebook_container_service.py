import docker
from services.container_service import Container, ContainerService
from config import JUPYTER_NOTEBOOK_IMAGE_NAME, JUPYTER_NOTEBOOK_IMAGE_VERSION
from exceptions import ContainerAlreadyRunningException, DockerException


class JupyterNotebookContainerService(ContainerService):
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
        if self.get_container().is_running():
            raise ContainerAlreadyRunningException()

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
            # print(e.explanation) # TODO: ADD TO LOGGING FILE

            raise DockerException(e.explanation)
