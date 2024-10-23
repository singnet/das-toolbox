import configparser
import tempfile

from typing import AnyStr, Union, Dict

from common import Container, ContainerManager
from config import (
    DATABASE_ADAPTER_CLIENT_IMAGE_NAME,
    DATABASE_ADAPTER_CLIENT_IMAGE_VERSION,
)


class DatabaseAdapterClientContainerManager(ContainerManager):
    def __init__(
        self,
        container_name,
        options: Dict,
        exec_context: Union[AnyStr, None] = None,
    ) -> None:
        container = Container(
            container_name,
            DATABASE_ADAPTER_CLIENT_IMAGE_NAME,
            DATABASE_ADAPTER_CLIENT_IMAGE_VERSION,
        )

        super().__init__(container, exec_context)
        self._options = options

    def _get_secrets_file(self, username: str, password: str):
        secrets = configparser.ConfigParser()

        secrets["postgres"] = {
            "username": username,
            "password": password,
        }

        return secrets

    def _store_secrets_file_temporarily(self, secrets: configparser.ConfigParser):
        file = tempfile.NamedTemporaryFile("+w", delete=True)
        secrets.write(file)
        file.flush()
        file.seek(0)

        return file

    def start_container(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str,
    ):
        self.raise_running_container()

        secrets = self._get_secrets_file(username, password)

        with self._store_secrets_file_temporarily(secrets) as file:
            secrets_file_name = "secrets.ini"

            command_params = [
                "--node-id",
                "localhost:30200",
                "--server-id",
                "localhost:30100",
                "--postgres-hostname",
                hostname,
                "--postgres-port",
                str(port),
                "--secrets-file",
                secrets_file_name,
            ]

            return self._start_container(
                command=command_params,
                volumes={
                    secrets_file_name: {
                        "bind": file.name,
                        "mode": "ro",
                    }
                },
                ports={
                    "30200/tcp": self._options.get("adapter_client_port"),
                },
            )
