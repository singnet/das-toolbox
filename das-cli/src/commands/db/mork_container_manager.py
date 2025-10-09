from typing import Dict

from common import Container, ContainerManager
from common.docker.exceptions import DockerError
from settings.config import MORK_SERVER_IMAGE_NAME, MORK_SERVER_IMAGE_VERSION


class MorkContainerManager(ContainerManager):
    def __init__(
        self,
        mork_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            mork_container_name,
            metadata={
                "port": options.get("mork_port"),
                "image": {
                    "name": MORK_SERVER_IMAGE_NAME,
                    "version": MORK_SERVER_IMAGE_VERSION,
                },
            },
        )

        super().__init__(container)
        self._options = options

    def start_container(
        self,
        port: int,
    ):
        self.raise_running_container()

        container = self._start_container(
            # command=["/mork-server"],
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                f"{port}/tcp": port,
            },
            environment={
                "MORK_SERVER_ADDR": self._options.get("mork_hostname", "0.0.0.0"),
                "MORK_SERVER_PORT": port,
                "MORK_SERVER_DIR": "/tmp",
            },
        )

        if not self.wait_for_container(container):
            raise DockerError("Timeout waiting for MORK container to start.")

        return container
