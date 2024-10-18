from typing import AnyStr, Union, Dict

from common import Container, ContainerManager
from config import DATABASE_ADAPTER_IMAGE_NAME, DATABASE_ADAPTER_IMAGE_VERSION


class DatabaseAdapterServerContainerManager(ContainerManager):
    def __init__(
        self,
        container_name,
        options: Dict,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        container = Container(
            container_name,
            DATABASE_ADAPTER_IMAGE_NAME,
            DATABASE_ADAPTER_IMAGE_VERSION,
        )

        super().__init__(container, exec_context)
        self._options = options

    def start_container(
        self,
        hostname: str,
        port: int,
        password: str,
    ):
        self.raise_running_container()

        command_params = [
            "--server-id",
            f"{hostname}:{port}",
            "--mongo-hostname",
            self._options.get("mongodb_hostname"),
            "--mongo-port",
            self._options.get("mongodb_port"),
            "--redis-hostname",
            self._options.get("redis_hostname"),
            "--redis-port",
            self._options.get("redis_port"),
        ]

        return self._start_container(
            command=command_params,
            ports={
                "30100/tcp": port,
            },
        )
