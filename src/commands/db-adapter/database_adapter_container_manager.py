from typing import AnyStr, Union

from common import Container, ContainerManager
from config import DATABASE_ADAPTER_IMAGE_NAME, DATABASE_ADAPTER_IMAGE_VERSION


class DatabaseAdapterContainerManager(ContainerManager):
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

    def start_container(self):
        self.raise_running_container()

        command_params = []

        return self._start_container(
            command=command_params,
            network_mode="host",
        )
