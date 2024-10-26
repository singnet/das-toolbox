from typing import AnyStr, Union, Dict

from common import Container, ContainerManager
from config import DAS_PEER_IMAGE_NAME, DAS_PEER_IMAGE_VERSION


class DasPeerContainerManager(ContainerManager):
    def __init__(
        self,
        container_name,
        options: Dict,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        container = Container(
            container_name,
            DAS_PEER_IMAGE_NAME,
            DAS_PEER_IMAGE_VERSION,
        )

        super().__init__(container, exec_context)
        self._options = options

    def start_container(self):
        self.raise_running_container()

        command_params = [
            "--server-id",
            "localhost:30100",
            "--mongo-hostname",
            self._options.get("mongodb_hostname"),
            "--mongo-port",
            str(self._options.get("mongodb_port")),
            "--mongo-username",
            self._options.get("mongodb_username"),
            "--mongo-password",
            self._options.get("mongodb_password"),
            "--redis-hostname",
            self._options.get("redis_hostname"),
            "--redis-port",
            str(self._options.get("redis_port")),
        ]

        return self._start_container(
            command=command_params,
            extra_hosts={"localhost": "172.17.0.1"},  # TODO: GET THE USERS IP
            ports={
                "30100/tcp": self._options.get("das_peer_port"),
            },
        )

    def get_port(self) -> int:
        return self._options.get("das_peer_port")
