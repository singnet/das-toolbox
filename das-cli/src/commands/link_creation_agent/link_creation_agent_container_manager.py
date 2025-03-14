import tempfile
from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import (
    LINK_CREATION_AGENT_IMAGE_NAME,
    LINK_CREATION_AGENT_IMAGE_VERSION,
)


class LinkCreationAgentContainerManager(ContainerManager):
    def __init__(
        self,
        link_creation_agent_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            link_creation_agent_container_name,
            metadata={
                "port": options.get("link_creation_agent_server_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": LINK_CREATION_AGENT_IMAGE_NAME,
                        "version": LINK_CREATION_AGENT_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)

    def _create_temp_config_file(
        self,
        query_agent_server_hostname: str,
        query_agent_server_port: str,
        query_agent_client_hostname: str,
        query_agent_client_port: str,
        link_creation_agent_server_hostname: str,
        link_creation_agent_server_port: str,
        das_agent_client_hostname: str,
        das_agent_client_port: str,
        das_agent_server_hostname: str,
        das_agent_server_port: str,
    ) -> str:
        query_agent_server_address = (
            f"{query_agent_server_hostname}:{query_agent_server_port}"
        )
        link_creation_agent_server_address = (
            f"{link_creation_agent_server_hostname}:{link_creation_agent_server_port}"
        )
        query_agent_client_address = (
            f"{query_agent_client_hostname}:{query_agent_client_port}"
        )
        das_agent_client_address = (
            f"{das_agent_client_hostname}:{das_agent_client_port}"
        )
        das_agent_server_address = (
            f"{das_agent_server_hostname}:{das_agent_server_port}"
        )

        config_data = f"""
requests_interval_seconds = 10
link_creation_agent_thread_count = 5
query_agent_server_id = {query_agent_server_address}
query_agent_client_id = {query_agent_client_address}

link_creation_agent_server_id = {link_creation_agent_server_address}
das_agent_client_id = {das_agent_client_address}
das_agent_server_id = {das_agent_server_address}

requests_buffer_file = ./buffer
"""
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".conf"
        ) as temp_file:
            temp_file.write(config_data)
            return temp_file.name

    def get_ports_in_use(self):
        return [
            self._options.get("link_creation_agent_server_port"),
            self._options.get("query_agent_client_port"),
            self._options.get("das_agent_client_port"),
        ]

    def start_container(self):
        self.raise_running_container()
        self.raise_on_port_in_use(self.get_ports_in_use())

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        config_file_path = self._create_temp_config_file(
            query_agent_server_hostname=self._options.get(
                "query_agent_server_hostname"
            ),
            query_agent_server_port=self._options.get("query_agent_server_port"),
            query_agent_client_hostname=self._options.get(
                "query_agent_client_hostname"
            ),
            query_agent_client_port=self._options.get("query_agent_client_port"),
            das_agent_client_hostname=self._options.get("das_agent_client_hostname"),
            das_agent_client_port=self._options.get("das_agent_client_port"),
            das_agent_server_hostname=self._options.get("das_agent_server_hostname"),
            das_agent_server_port=self._options.get("das_agent_server_port"),
            link_creation_agent_server_hostname=self._options.get(
                "link_creation_agent_server_hostname"
            ),
            link_creation_agent_server_port=self._options.get(
                "link_creation_agent_server_port"
            ),
        )

        try:
            volumes = {
                config_file_path: {
                    "bind": config_file_path,
                    "mode": "ro",
                }
            }

            exec_command = f"--config_file {config_file_path}"

            container_id = self._start_container(
                network_mode="host",
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 5,
                },
                command=exec_command,
                volumes=volumes,
                stdin_open=True,
                tty=True,
            )

            return container_id
        except docker.errors.APIError as e:
            if e.response.reason == "Not Found":
                raise DockerContainerNotFoundError(
                    f"The docker image {self.get_container().image} for the link creation agent could not be found!"
                )

            raise DockerError(e.explanation)
