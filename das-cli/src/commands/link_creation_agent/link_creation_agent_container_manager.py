import tempfile
import docker

from typing import Dict

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import LINK_CREATION_AGENT_IMAGE_NAME, LINK_CREATION_AGENT_IMAGE_VERSION


class LinkCreationAgentContainerManager(ContainerManager):
    def __init__(
        self,
        link_creation_agent_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            link_creation_agent_container_name,
            metadata={
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

    def _create_temp_config_file(self, query_agent_hostname: str, query_agent_port: int) -> str:
        query_agent_address = f"{query_agent_hostname}:{query_agent_port}"

        config_data = f"""
requests_interval_seconds = 10
link_creation_agent_thread_count = 5
query_agent_server_id = {query_agent_address}

query_agent_client_id = localhost:9001
link_creation_agent_server_id = localhost:9080
das_agent_client_id = localhost:9090
das_agent_server_id = localhost:9091
requests_buffer_file = ./buffer
"""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".conf") as temp_file:
            temp_file.write(config_data)
            return temp_file.name

    def start_container(self):
        self.raise_running_container()
        self.raise_on_port_in_use([
            9080,
            9001,
            9090,
        ])

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        query_agent_hostname = self._options.get("query_agent_hostname")
        query_agent_port = self._options.get("query_agent_port")

        config_file_path = self._create_temp_config_file(
            query_agent_hostname,
            query_agent_port,
        )

        try:
            volumes = {
                config_file_path: {
                    "bind": config_file_path,
                    "mode": "ro",
                }
            }

            exec_command = f"--type server --config_file {config_file_path}"

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
