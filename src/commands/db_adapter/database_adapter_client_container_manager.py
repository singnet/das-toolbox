import os
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
        file = tempfile.NamedTemporaryFile("+w", delete=False, suffix=".txt")
        secrets.write(file)
        file.flush()
        file.seek(0)

        return file

    def start_container(
        self,
        context: str,
        hostname: str,
        port: int,
        username: str,
        password: str,
        database: str,
    ):
        self.raise_running_container()

        secrets = self._get_secrets_file(username, password)

        with self._store_secrets_file_temporarily(secrets) as file:
            secrets_target_path = "/tmp/secrets.ini"
            context_target_path = f"/tmp/{os.path.basename(context)}"

            command_params = [
                "--node-id",
                "localhost:30200",
                "--server-id",
                "localhost:30100",
                "--postgres-hostname",
                hostname,
                "--postgres-port",
                str(port),
                "--postgres-database",
                database,
                "--secrets-file",
                secrets_target_path,
                "--context",
                context_target_path,
            ]

            return self._start_container(
                command=command_params,
                volumes={
                    file.name: {
                        "bind": secrets_target_path,
                        "mode": "ro",
                    },
                    context: {
                        "bind": context_target_path,
                        "mode": "ro",
                    },
                },
                ports={
                    "30200/tcp": self._options.get("adapter_client_port"),
                },
            )
