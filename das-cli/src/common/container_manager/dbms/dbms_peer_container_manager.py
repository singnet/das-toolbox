import configparser
import os
import tempfile
from typing import Dict, Union

from common import Container, ContainerManager
from common.docker.exceptions import DockerError
from settings.config import DBMS_PEER_IMAGE_NAME, DBMS_PEER_IMAGE_VERSION


class DbmsPeerContainerManager(ContainerManager):
    def __init__(
        self,
        container_name,
        options: Dict = {},
        exec_context: Union[str, None] = None,
    ) -> None:
        container = Container(
            container_name,
            metadata={
                "port": None,
                "image": {
                    "name": DBMS_PEER_IMAGE_NAME,
                    "version": DBMS_PEER_IMAGE_VERSION,
                },
            },
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
        file = tempfile.NamedTemporaryFile("+w", delete=True, suffix=".txt")
        secrets.write(file)
        file.flush()
        file.seek(0)

        return file

    def _handle_post_start(self, container, show_logs: bool) -> None:
        if not show_logs:
            if not self.wait_for_container(container):
                raise DockerError("DBMS peer could not be started")
            return

        self.logs(follow=True)
        exit_code = self.get_container_exit_status(container)
        self.stop()

        if exit_code != 0:
            raise DockerError("DBMS peer could not be started")

    def start_container(
        self,
        context: str,
        hostname: str,
        port: int,
        username: str,
        password: str,
        database: str,
        show_logs: bool = True,
    ):
        self.raise_running_container()

        secrets = self._get_secrets_file(username, password)
        das_peer_port = self._options.get("das_peer_port")

        with self._store_secrets_file_temporarily(secrets) as file:
            secrets_target_path = "/tmp/secrets.ini"
            context_target_path = f"/tmp/{os.path.basename(context)}"

            command_params = [
                "--node-id",
                "localhost:30200",
                "--server-id",
                f"localhost:{das_peer_port}",
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

            volumes = {
                file.name: {
                    "bind": secrets_target_path,
                    "mode": "ro",
                },
                context: {
                    "bind": context_target_path,
                    "mode": "ro",
                },
            }

            container = self._start_container(
                command=command_params,
                volumes=volumes,
            )

            self._handle_post_start(container, show_logs)
