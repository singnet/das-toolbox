from typing import AnyStr, Union, Dict

from common import Container, ContainerManager
from config import DATABASE_ADAPTER_IMAGE_NAME, DATABASE_ADAPTER_IMAGE_VERSION


class DatabaseAdapterClientContainerManager(ContainerManager):
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
        port: int,
        username: str,
        password: str,
    ):
        self.raise_running_container()

        command_params = [
            "--postgres-username",
            username,
            "--postgres-password",
            password,
            
        ]

        return self._start_container(
            command=command_params,
            ports={
                "30100/tcp": port,
            },
        )
