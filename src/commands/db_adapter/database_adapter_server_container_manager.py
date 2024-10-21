from typing import AnyStr, Union, Dict
from uuid import uuid4

from common import Container, ContainerManager
from config import DATABASE_ADAPTER_SERVER_IMAGE_VERSION, DATABASE_ADAPTER_SERVER_IMAGE_NAME

class DatabaseAdapterServerContainerManager(ContainerManager):
    def __init__(
        self,
        container_name,
        options: Dict,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        container = Container(
            container_name,
            DATABASE_ADAPTER_SERVER_IMAGE_NAME,
            DATABASE_ADAPTER_SERVER_IMAGE_VERSION,
        )

        super().__init__(container, exec_context)
        self._options = options

    def start_container(self):
        self.raise_running_container()

        command_params = [
            "--server-id",
            str(uuid4()),
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
            ports={
                "30100/tcp": self._options.get("adapter_server_port"),
            },
        )

    def get_port(self) -> int:
        return self._options.get("adapter_server_port")
