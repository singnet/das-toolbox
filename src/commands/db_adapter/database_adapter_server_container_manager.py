from typing import AnyStr, Union

from common import Container, ContainerManager
from config import DATABASE_ADAPTER_IMAGE_NAME, DATABASE_ADAPTER_IMAGE_VERSION


class DatabaseAdapterServerContainerManager(ContainerManager):
    def __init__(
        self,
        database_adapter_container_name,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        container = Container(
            database_adapter_container_name,
            DATABASE_ADAPTER_IMAGE_NAME,
            DATABASE_ADAPTER_IMAGE_VERSION,
        )

        super().__init__(container, exec_context)

    def start_container(self, port: int):
        self.raise_running_container()

        command_params = [
            "--server-id localhost:30100 --mongo-hostname localhost --mongo-port 27017 --redis-hostname localhost --redis-port 6379"
        ]

        return self._start_container(
            command=command_params,
            ports={
                "30100/tcp": port,
            },
        )
