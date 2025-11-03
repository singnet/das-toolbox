from typing import Dict

from common import Container, ContainerManager
from settings.config import DAS_MORK_IMAGE_NAME, DAS_MORK_IMAGE_VERSION


class MorkdbContainerManager(ContainerManager):
    def __init__(
        self,
        morkdb_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            morkdb_container_name,
            metadata={
                "port": options.get("morkdb_port"),
                "image": {
                    "name": DAS_MORK_IMAGE_NAME,
                    "version": DAS_MORK_IMAGE_VERSION,
                },
            },
        )

        super().__init__(container)
        self._options = options

    def start_container(self):
        self.raise_running_container()

        port = self._options.get("morkdb_port", 40022)

        container = self._start_container(
            restart_policy={
                "Name": "on-failure",
                "MaximumRetryCount": 5,
            },
            ports={
                f"{port}/tcp": "8000",
            },
        )

        return container
