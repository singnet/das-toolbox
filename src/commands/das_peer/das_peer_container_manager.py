from typing import AnyStr, Union, Dict

from common import Container, ContainerManager, retry
from config import DAS_PEER_IMAGE_NAME, DAS_PEER_IMAGE_VERSION
from common.docker.exceptions import DockerError


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

    def raise_container_unhealthy(self, container) -> None:
        is_healthy = self.is_container_healthy(container)

        if not is_healthy:
            raise DockerError(
                "The service could not be initated, please check if the database is up running the command `das-cli db start` or the required ports are available"
            )

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

        container = self._start_container(
            command=command_params,
            healthcheck={
                "Test": [
                    "CMD-SHELL",
                    "pgrep -f 'python /app/scripts/python/das_node_server.py' || exit 1",
                ],
            },
            extra_hosts={
                "host.docker.internal": "172.17.0.11",  # docker interface
            },
            ports={
                "30100/tcp": self._options.get("das_peer_port"),
            },
        )

        retry(
            lambda: self.raise_container_unhealthy(container),
            interval=10,
            max_retries=5,
        )

        return container

    def get_port(self) -> int:
        return self._options.get("das_peer_port")
