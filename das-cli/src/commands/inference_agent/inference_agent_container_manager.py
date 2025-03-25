import tempfile
from typing import Dict

import docker

from common import Container, ContainerImageMetadata, ContainerManager
from common.docker.exceptions import DockerContainerNotFoundError, DockerError
from settings.config import INFERENCE_AGENT_IMAGE_NAME, INFERENCE_AGENT_IMAGE_VERSION


class InferenceAgentContainerManager(ContainerManager):
    def __init__(
        self,
        inference_agent_container_name: str,
        options: Dict = {},
    ) -> None:
        container = Container(
            inference_agent_container_name,
            metadata={
                "port": options.get("inference_agent_server_port"),
                "image": ContainerImageMetadata(
                    {
                        "name": INFERENCE_AGENT_IMAGE_NAME,
                        "version": INFERENCE_AGENT_IMAGE_VERSION,
                    }
                ),
            },
        )
        self._options = options

        super().__init__(container)

    def _create_temp_config_file(self) -> str:

        config_data = f"""
inference_node_id = "localhost:8080"
link_creation_agent_client_id = "localhost:8081"
link_creation_agent_server_id = "localhost:8082"
das_client_id = "localhost:8083"
das_server_id = "localhost:8084"
distributed_inference_control_node_id = "localhost:8085"
distributed_inference_control_node_server_id = "localhost:8086"
"""
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".conf") as temp_file:
            temp_file.write(config_data)
            return temp_file.name

    def start_container(self):
        self.raise_running_container()

        try:
            self.stop()
        except (DockerContainerNotFoundError, DockerError):
            pass

        config_file_path = self._create_temp_config_file()

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
                raise DockerContainerNotFoundError( f"The docker image {self.get_container().image} for the inference agent could not be found!"
                )

            raise DockerError(e.explanation)
